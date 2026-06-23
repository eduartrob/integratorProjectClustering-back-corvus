import os
import sys
import chromadb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import hdbscan
import umap
import joblib
from pathlib import Path
from scipy.spatial import ConvexHull

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
UMAP_MODEL_PATH = MODELS_DIR / "umap_50d_model.joblib"
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

# Guardar el modelo HDBSCAN
joblib.dump(clusterer, MODEL_PATH)
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

# --- 6. REDUCCIÓN DIMENSIONAL PARA VISUALIZACIÓN (UMAP 2D) ---
print("Reduciendo dimensiones con UMAP a 2D SOLO para visualización...")
reducer_viz = umap.UMAP(n_components=2, n_neighbors=10, min_dist=0.1, metric='cosine', random_state=42)
embeddings_2d = reducer_viz.fit_transform(embeddings_384d)

df = pd.DataFrame({
    'X': embeddings_2d[:, 0],
    'Y': embeddings_2d[:, 1],
    'Label': labels,
    'Project ID': unique_project_ids,
    'Num': range(1, len(unique_project_ids) + 1)
})

# --- 7. RENDERIZADO VISUAL ---
print("Generando gráfica 'clusters_visualizacion.png'...")

plt.figure(figsize=(18, 10))
ax = plt.gca()

# Fondo Oceánico
ax.set_facecolor('#0a0f2e')
plt.gcf().patch.set_facecolor('#0a0f2e')

# Colores categóricos
cmap = plt.cm.tab20
unique_labels = set(labels)

# Dibujar Clústeres (Convex Hulls)
for label in unique_labels:
    if label == -1:
        continue # Océanos azules no tienen hull
        
    cluster_points = df[df['Label'] == label][['X', 'Y']].values
    color = cmap(label % 20)
    
    # Puntos del cluster
    plt.scatter(cluster_points[:, 0], cluster_points[:, 1], 
                color=color, s=150, edgecolors='white', linewidths=1.5,
                label=f'Clúster {label} ({len(cluster_points)} proy.)')
                
    # Convex Hull (Sombras del clúster)
    if len(cluster_points) >= 3:
        hull = ConvexHull(cluster_points)
        # Expandir un poco el polígono para que no toque los centros exactos
        for simplex in hull.simplices:
            plt.plot(cluster_points[simplex, 0], cluster_points[simplex, 1], color=color, lw=2, alpha=0.5)
        plt.fill(cluster_points[hull.vertices, 0], cluster_points[hull.vertices, 1], color=color, alpha=0.2)
    elif len(cluster_points) == 2:
        # Si solo hay 2 puntos, dibujamos una línea gruesa entre ellos
        plt.plot(cluster_points[:, 0], cluster_points[:, 1], color=color, lw=10, alpha=0.2, solid_capstyle='round')

# Dibujar Océanos Azules (Anomalías)
outliers = df[df['Label'] == -1]
if not outliers.empty:
    plt.scatter(outliers['X'], outliers['Y'], 
                c='red', marker='*', s=300, edgecolors='black', linewidths=1.5, 
                label=f'Océano Azul ({len(outliers)} proy.)')

# Etiquetas (Números)
for i, row in df.iterrows():
    # Texto en blanco o negro dependiendo del fondo
    text_color = 'white' if row['Label'] == -1 else 'black'
    offset = 0 if row['Label'] != -1 else -0.3
    
    plt.annotate(str(row['Num']), (row['X'], row['Y'] + offset), 
                 fontsize=10, weight='bold', color=text_color, ha='center', va='center')

# Detalles estéticos
plt.title("Clustering Topológico HDBSCAN + UMAP\nDetección de Océanos Azules basada en Densidad", 
          fontsize=18, color='white', pad=20)
plt.xlabel("UMAP 1", color='white', fontsize=12)
plt.ylabel("UMAP 2", color='white', fontsize=12)

# Configurar Ejes
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_edgecolor('#1f295c')

# Leyenda
legend = plt.legend(loc='upper right', facecolor='#0a0f2e', edgecolor='#1f295c', labelcolor='white', fontsize=11)
frame = legend.get_frame()
frame.set_alpha(0.8)

# Panel Lateral de Referencias
text_str = "Referencias de Proyectos:\n\n"
for _, row in df.iterrows():
    name = row['Project ID'].replace('proyecto_', '').replace('_', ' ')
    if len(name) > 35: name = name[:32] + "..."
    tag = "[OCÉANO AZUL]" if row['Label'] == -1 else f"[Clúster {row['Label']}]"
    text_str += f"{row['Num']}. {tag} {name.title()}\n"

plt.gcf().text(1.02, 0.5, text_str, fontsize=10, color='white', 
               va='center', bbox=dict(boxstyle="round,pad=1", facecolor='#0a0f2e', edgecolor='#1f295c'))

plt.savefig(BASE_DIR / 'clusters_visualizacion.png', dpi=300, bbox_inches='tight', facecolor='#0a0f2e')
print("¡Proceso completado exitosamente!")
