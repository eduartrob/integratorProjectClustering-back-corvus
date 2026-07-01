import os
import chromadb
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import hdbscan
import umap
import joblib
import hashlib
import json
from pathlib import Path
from scipy.spatial import ConvexHull
from collections import Counter

class ClusteringEngineService:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.models_dir = self.base_dir / "app" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_path = self.models_dir / "hdbscan_model.joblib"
        self.umap_model_path = self.models_dir / "umap_50d_model.joblib"
        self.hash_path = self.models_dir / "data_hash.txt"
        self.chroma_path = self.base_dir / "chroma_data"
        self.topics_path = self.models_dir / "unexplored_topics.json"
        self.html_out_path = self.base_dir / "clusters_interactivo.html"

    def execute_global_clustering(self):
        print("Iniciando extracción desde ChromaDB...")
        
        client = chromadb.PersistentClient(path=str(self.chroma_path))
        collection = client.get_collection("integrator_projects")

        results = collection.get(include=["embeddings", "metadatas", "documents"])

        projects_data = {}
        for i, meta in enumerate(results['metadatas']):
            p_id = meta.get('project_id')
            if not p_id:
                continue
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
            return False

        current_hash = hashlib.md5(np.ascontiguousarray(embeddings_384d).tobytes()).hexdigest()

        force_retrain = False
        if self.model_path.exists() and self.umap_model_path.exists() and self.hash_path.exists():
            if self.hash_path.read_text() == current_hash:
                print("Modelos vigentes y datos sin cambios. Cargando sin re-entrenar...")
                reducer_clustering = joblib.load(self.umap_model_path)
                clusterer = joblib.load(self.model_path)
                embeddings_50d = reducer_clustering.transform(embeddings_384d)
                labels = clusterer.labels_
            else:
                print("Los datos cambiaron. Re-entrenando modelos...")
                force_retrain = True
        else:
            print("Modelos no encontrados. Entrenando desde cero...")
            force_retrain = True

        if force_retrain:
            print("Reduciendo a 20D para HDBSCAN...")
            reducer_clustering = umap.UMAP(
                n_components=20,
                n_neighbors=15,
                min_dist=0.0,
                metric='cosine',
                random_state=42
            )
            embeddings_50d = reducer_clustering.fit_transform(embeddings_384d)

            joblib.dump(reducer_clustering, self.umap_model_path)
            print(f"Modelo UMAP guardado en: {self.umap_model_path}")

            print("Entrenando HDBSCAN...")
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=3,
                min_samples=2,
                metric='euclidean',
                cluster_selection_method='eom',
                prediction_data=True
            )
            labels = clusterer.fit_predict(embeddings_50d)

            joblib.dump(clusterer, self.model_path)
            self.hash_path.write_text(current_hash)
            print(f"Modelo HDBSCAN guardado en: {self.model_path}")

        n_noise = list(labels).count(-1)
        pct_noise = (n_noise / len(labels)) * 100
        print(f"Diagnóstico: {n_noise}/{len(labels)} proyectos ({pct_noise:.1f}%) fueron marcados como Océano Azul.")

        print("Actualizando metadatos en ChromaDB...")
        for i, p_id in enumerate(unique_project_ids):
            label = int(labels[i])
            is_ocean_blue = bool(label == -1)
            
            chunk_ids = projects_data[p_id]['id_to_update']
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

        print("Analizando clústeres para derivar temas inexplorados...")
        valid_labels = [l for l in labels if l != -1]
        unexplored_topics = []
        if valid_labels:
            cluster_sizes = Counter(valid_labels)
            smallest_clusters = [item[0] for item in cluster_sizes.most_common()[:-4:-1]]
            
            for cluster_id in smallest_clusters:
                projects_in_cluster = [unique_project_ids[i] for i, l in enumerate(labels) if l == cluster_id]
                if projects_in_cluster:
                    sample_project = projects_in_cluster[0].replace('proyecto_', '').replace('_', ' ').title()
                    unexplored_topics.append(f"Nuevos enfoques en: {sample_project}")
                    
            with open(self.topics_path, "w", encoding="utf-8") as f:
                json.dump(unexplored_topics, f, ensure_ascii=False, indent=2)
            print(f"Temas inexplorados guardados en {self.topics_path}")
        else:
            print("No se encontraron clústeres válidos para temas inexplorados.")

        print("Reduciendo dimensiones con UMAP a 2D SOLO para visualización...")
        reducer_viz = umap.UMAP(n_components=2, n_neighbors=10, min_dist=0.1, metric='euclidean', random_state=42)
        embeddings_2d = reducer_viz.fit_transform(embeddings_50d)

        df = pd.DataFrame({
            'X': embeddings_2d[:, 0],
            'Y': embeddings_2d[:, 1],
            'Label': labels,
            'Project ID': unique_project_ids,
            'Num': range(1, len(unique_project_ids) + 1)
        })

        print("Generando gráfica interactiva 'clusters_interactivo.html'...")
        fig = go.Figure()
        unique_labels = set(labels)
        cmap = px.colors.qualitative.Alphabet

        for label in unique_labels:
            if label == -1:
                continue
                
            cluster_points = df[df['Label'] == label]
            color = cmap[label % len(cmap)]
            
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
            
            pts = cluster_points[['X', 'Y']].values
            if len(pts) >= 3:
                hull = ConvexHull(pts)
                hull_pts = np.append(pts[hull.vertices], [pts[hull.vertices[0]]], axis=0)
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

        fig.write_html(str(self.html_out_path))
        print(f"¡Gráfica interactiva guardada en {self.html_out_path}!")
        print("¡Proceso completado exitosamente!")
        return True

clustering_engine = ClusteringEngineService()
