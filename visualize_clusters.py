import os
import sys
import chromadb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import hdbscan
import umap
import joblib
import hashlib
import json
import argparse
from pathlib import Path
from scipy.spatial import ConvexHull
from collections import Counter

# --- 0. ARGUMENTOS DE LÍNEA DE COMANDOS ---
parser = argparse.ArgumentParser(description="Visualizador de Clústeres HDBSCAN")
parser.add_argument("--new-proposal", type=str, help="Ruta a un archivo .txt con una propuesta nueva para ubicarla en el mapa", default=None)
args = parser.parse_args()

# Si hay propuesta nueva, vectorizarla de inmediato
new_proposal_embedding = None
if args.new_proposal:
    print(f"Vectorizando propuesta nueva: {args.new_proposal}...")
    from sentence_transformers import SentenceTransformer
    import fitz
    import pymupdf4llm
    
    print("Cargando modelo multilingüe...")
    model_st = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    file_path = args.new_proposal.lower()
    text = ""
    if file_path.endswith('.pdf'):
        doc = fitz.open(args.new_proposal)
        text = pymupdf4llm.to_markdown(doc)
    else:
        text = Path(args.new_proposal).read_text(encoding='utf-8', errors='ignore')
        
    new_proposal_embedding = model_st.encode(text)

# --- 1. CONFIGURACIÓN DE RUTAS ---
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "app" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODELS_DIR / "hdbscan_model.joblib"

print("Iniciando extracción desde ChromaDB...")

# --- 2. EXTRACCIÓN DE DATOS ---
client = chromadb.PersistentClient(path=str(BASE_DIR / "chroma_data"))
collection = client.get_collection("integrator_projects")

results = collection.get(include=["embeddings", "metadatas", "documents"])

# Filtrar para tener solo 1 chunk por proyecto (promediado) para el clustering real de proyectos
# Si ChromaDB tiene múltiples chunks por proyecto, debemos promediarlos primero
projects_data = {}
for i, meta in enumerate(results['metadatas']):
    p_id = meta['project_id']
    if p_id not in projects_data:
        projects_data[p_id] = {'embeddings': [], 'id_to_update': []}
    projects_data[p_id]['embeddings'].append(results['embeddings'][i])
    projects_data[p_id]['id_to_update'].append(results['ids'][i])

unique_project_ids = sorted(list(projects_data.keys()))
aggregated_embeddings = []

for p_id in unique_project_ids:
    avg_emb = np.mean(projects_data[p_id]['embeddings'], axis=0)
    aggregated_embeddings.append(avg_emb)

embeddings_384d = np.array(aggregated_embeddings)

if len(embeddings_384d) < 3:
    print("¡Sube al menos 3 proyectos diferentes para poder entrenar el clusterer!")
    sys.exit(1)

UMAP_MODEL_PATH = MODELS_DIR / "umap_50d_model.joblib"
HASH_PATH = MODELS_DIR / "data_hash.txt"
current_hash = hashlib.md5(np.ascontiguousarray(embeddings_384d).tobytes()).hexdigest()

force_retrain = False
if MODEL_PATH.exists() and UMAP_MODEL_PATH.exists() and HASH_PATH.exists():
    if HASH_PATH.read_text() == current_hash:
        print("Modelos vigentes y datos sin cambios. Cargando sin re-entrenar...")
        reducer_clustering = joblib.load(UMAP_MODEL_PATH)
        clusterer = joblib.load(MODEL_PATH)
        embeddings_50d = reducer_clustering.transform(embeddings_384d)
        labels = clusterer.labels_
    else:
        print("Los datos cambiaron. Re-entrenando modelos...")
        force_retrain = True
else:
    print("Modelos no encontrados. Entrenando desde cero...")
    force_retrain = True

if force_retrain:
    # --- 3. REDUCCIÓN INTERMEDIA PARA CLUSTERING (UMAP 20D) ---
    print("Reduciendo a 20D para HDBSCAN...")
    reducer_clustering = umap.UMAP(
        n_components=20,
        n_neighbors=15, # Ajustado a 15 para obtener ~15-20% de Océanos Azules
        min_dist=0.0,
        metric='cosine',
        random_state=42
    )
    embeddings_50d = reducer_clustering.fit_transform(embeddings_384d)

    # Guardar el UMAP reductor de clustering para que FastAPI lo use
    joblib.dump(reducer_clustering, UMAP_MODEL_PATH)
    print(f"Modelo UMAP 50D guardado en: {UMAP_MODEL_PATH}")

    # --- 4. CLUSTERING EN 50D (HDBSCAN) ---
    print("Entrenando HDBSCAN en espacio de 50 dimensiones...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=3,
        min_samples=2,
        metric='euclidean',
        cluster_selection_epsilon=0.5,
        prediction_data=True
    )
    labels = clusterer.fit_predict(embeddings_50d)

    # Guardar el modelo HDBSCAN y hash
    joblib.dump(clusterer, MODEL_PATH)
    HASH_PATH.write_text(current_hash)
    print(f"Modelo HDBSCAN guardado en: {MODEL_PATH}")

# Revisar métricas de Outliers
n_noise = list(labels).count(-1)
pct_noise = (n_noise / len(labels)) * 100
print(f"Diagnóstico: {n_noise}/{len(labels)} proyectos ({pct_noise:.1f}%) fueron marcados como Océano Azul.")
if len(set(labels)) == 1 and labels[0] != -1:
    print("⚠️ ADVERTENCIA: Todos los proyectos cayeron en un solo clúster. Intenta bajar min_cluster_size o subir min_samples.")

# --- 5. ACTUALIZACIÓN DE CHROMADB (DRIFT POLICY) ---
print("Actualizando metadatos en ChromaDB...")
for i, p_id in enumerate(unique_project_ids):
    label = int(labels[i])
    is_ocean_blue = bool(label == -1)
    
    # Actualizar todos los chunks correspondientes a este proyecto
    chunk_ids = projects_data[p_id]['id_to_update']
    
    # Recuperar metadatos actuales de esos chunks para no sobrescribir info valiosa
    current_chunks = collection.get(ids=chunk_ids, include=["metadatas"])
    
    new_metadatas = []
    for meta in current_chunks['metadatas']:
        updated_meta = meta.copy()
        updated_meta['cluster_id'] = label
        updated_meta['is_blue_ocean'] = is_ocean_blue
        new_metadatas.append(updated_meta)
        
    collection.update(
        ids=chunk_ids,
        metadatas=new_metadatas
    )

print("¡Metadatos actualizados con éxito!")

# --- 5.5 GENERACIÓN DE TEMAS INEXPLORADOS ---
print("Analizando clústeres para derivar temas inexplorados...")
valid_labels = [l for l in labels if l != -1]
unexplored_topics = []
if valid_labels:
    cluster_sizes = Counter(valid_labels)
    # Tomar los 3 clústeres más pequeños (menor densidad = áreas con oportunidad)
    smallest_clusters = [item[0] for item in cluster_sizes.most_common()[:-4:-1]]
    
    for cluster_id in smallest_clusters:
        projects_in_cluster = [unique_project_ids[i] for i, l in enumerate(labels) if l == cluster_id]
        if projects_in_cluster:
            sample_project = projects_in_cluster[0].replace('proyecto_', '').replace('_', ' ').title()
            unexplored_topics.append(f"Nuevos enfoques en: {sample_project}")
            
    # Guardar en JSON
    topics_path = MODELS_DIR / "unexplored_topics.json"
    with open(topics_path, "w", encoding="utf-8") as f:
        json.dump(unexplored_topics, f, ensure_ascii=False, indent=2)
    print(f"Temas inexplorados guardados en {topics_path}")
else:
    print("No se encontraron clústeres válidos para temas inexplorados.")

# --- 6. REDUCCIÓN DIMENSIONAL PARA VISUALIZACIÓN (UMAP 2D) ---
print("Reduciendo dimensiones con UMAP a 2D SOLO para visualización...")
# Proyectar desde el espacio 20D (clustering) al espacio 2D
reducer_viz = umap.UMAP(n_components=2, n_neighbors=10, min_dist=0.1, metric='euclidean', random_state=42)
embeddings_2d = reducer_viz.fit_transform(embeddings_50d)

new_proposal_2d = None
if new_proposal_embedding is not None:
    print("Calculando coordenadas 2D para la propuesta nueva...")
    # Proyectar el embedding 384D de la nueva propuesta al espacio 50D de clustering
    new_proposal_50d = reducer_clustering.transform([new_proposal_embedding])
    # Proyectar del espacio 50D al espacio 2D de visualización
    new_proposal_2d = reducer_viz.transform(new_proposal_50d)

df = pd.DataFrame({
    'X': embeddings_2d[:, 0],
    'Y': embeddings_2d[:, 1],
    'Label': labels,
    'Project ID': unique_project_ids,
    'Num': range(1, len(unique_project_ids) + 1)
})

# --- 7. RENDERIZADO VISUAL INTERACTIVO (PLOTLY) ---
print("Generando gráfica interactiva 'clusters_interactivo.html'...")

# Crear figura de Plotly
fig = go.Figure()

# Dibujar Clústeres (Convex Hulls + Scatter)
unique_labels = set(labels)
cmap = px.colors.qualitative.Alphabet

for label in unique_labels:
    if label == -1:
        continue # Océanos azules aparte
        
    cluster_points = df[df['Label'] == label]
    color = cmap[label % len(cmap)]
    
    # Añadir los puntos del cluster
    fig.add_trace(go.Scatter(
        x=cluster_points['X'], y=cluster_points['Y'],
        mode='markers+text',
        marker=dict(size=12, color=color, line=dict(width=1, color='white')),
        text=cluster_points['Num'],
        textposition="bottom center",
        name=f'Clúster {label}',
        hoverinfo='text',
        hovertext=[f"ID: {pid}<br>Clúster: {label}" for pid in cluster_points['Project ID']]
    ))
    
    # Calcular y añadir Convex Hull si hay suficientes puntos
    pts = cluster_points[['X', 'Y']].values
    if len(pts) >= 3:
        hull = ConvexHull(pts)
        hull_pts = np.append(pts[hull.vertices], [pts[hull.vertices[0]]], axis=0) # Cerrar el polígono
        fig.add_trace(go.Scatter(
            x=hull_pts[:, 0], y=hull_pts[:, 1],
            mode='lines',
            fill='toself',
            fillcolor=color,
            line=dict(color=color, width=2),
            opacity=0.2,
            hoverinfo='skip',
            showlegend=False
        ))

# Dibujar Océanos Azules (Anomalías)
outliers = df[df['Label'] == -1]
if not outliers.empty:
    fig.add_trace(go.Scatter(
        x=outliers['X'], y=outliers['Y'],
        mode='markers+text',
        marker=dict(size=16, color='red', symbol='star', line=dict(width=1, color='black')),
        text=outliers['Num'],
        textfont=dict(color='white'),
        textposition="top center",
        name=f'Océano Azul Histórico ({len(outliers)})',
        hoverinfo='text',
        hovertext=[f"ID: {pid}<br>¡OCÉANO AZUL!" for pid in outliers['Project ID']]
    ))

# Dibujar LA NUEVA PROPUESTA
if new_proposal_2d is not None:
    px_val, py_val = new_proposal_2d[0, 0], new_proposal_2d[0, 1]
    fig.add_trace(go.Scatter(
        x=[px_val], y=[py_val],
        mode='markers+text',
        marker=dict(size=25, color='gold', symbol='star', line=dict(width=2, color='white')),
        text=["NUEVA PROPUESTA"],
        textposition="top center",
        textfont=dict(size=14, color='gold'),
        name='Tu Propuesta',
        hoverinfo='text',
        hovertext="¡AQUÍ ESTÁ TU PROYECTO!"
    ))

# Configurar el layout (Estética Marina/Oscura)
fig.update_layout(
    title="Clustering Topológico HDBSCAN + UMAP (Detección de Océanos Azules)",
    title_font=dict(size=20, color='white'),
    plot_bgcolor='#0a0f2e',
    paper_bgcolor='#0a0f2e',
    font=dict(color='white'),
    xaxis=dict(title="UMAP 1", showgrid=False, zeroline=False),
    yaxis=dict(title="UMAP 2", showgrid=False, zeroline=False),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='white')),
    hovermode='closest'
)

# Exportar HTML
out_path = BASE_DIR / 'clusters_interactivo.html'
fig.write_html(str(out_path))
print(f"¡Gráfica interactiva guardada en {out_path}!")
print("¡Proceso completado exitosamente!")
