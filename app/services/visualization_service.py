import numpy as np
import joblib
import umap
import plotly.graph_objects as go
from collections import Counter
from app.services.chroma_service import chroma_service
from app.core.config import settings
import os

class VisualizationService:
    def __init__(self):
        self.umap_model_path = os.path.join(settings.MODELS_DIR, "umap_50d_model.joblib")
        # Colores consistentes
        self.cluster_colors = [
            '#4FC3F7', '#FFB74D', '#81C784', '#F06292', '#CE93D8',
            '#80DEEA', '#FFCC02', '#FF8A65', '#A5D6A7', '#90CAF9'
        ]

    def _get_data_from_db(self):
        """Extrae los proyectos y sus embeddings de ChromaDB."""
        results = chroma_service.collection.get(include=["embeddings", "metadatas"])
        if not results or not results['embeddings']:
            return None, None, None, None

        projects_data = {}
        for i, meta in enumerate(results['metadatas']):
            p_id = meta['project_id']
            if p_id not in projects_data:
                projects_data[p_id] = {
                    'embeddings': [],
                    'cluster_id': meta.get('cluster_id', 0),
                    'is_blue_ocean': meta.get('is_blue_ocean', False)
                }
            projects_data[p_id]['embeddings'].append(results['embeddings'][i])

        unique_ids = sorted(projects_data.keys())
        aggregated_embeddings = [np.mean(projects_data[p]['embeddings'], axis=0) for p in unique_ids]
        labels = [projects_data[p]['cluster_id'] for p in unique_ids]
        
        return unique_ids, np.array(aggregated_embeddings), labels, projects_data

    def get_cluster_stats(self):
        """Genera estadisticas basicas de los clusters para el panel de admin."""
        unique_ids, _, labels, projects_data = self._get_data_from_db()
        if not unique_ids:
            return {"error": "No hay datos en la base de datos"}

        cluster_counts = Counter(labels)
        total_projects = len(unique_ids)
        blue_oceans = cluster_counts.get(-1, 0)
        
        clusters_info = []
        for cid, count in cluster_counts.items():
            if cid != -1:
                clusters_info.append({"cluster_id": cid, "project_count": count})

        return {
            "total_projects": total_projects,
            "total_clusters": len(clusters_info),
            "blue_oceans": blue_oceans,
            "clusters_detail": sorted(clusters_info, key=lambda x: x['cluster_id'])
        }

    def generate_3d_html(self):
        """Genera el HTML de la grafica 3D interactiva."""
        if not os.path.exists(self.umap_model_path):
            return "<html><body><h1>Error</h1><p>Modelo UMAP no encontrado. Ejecuta visualize_clusters.py primero.</p></body></html>"

        unique_ids, embeddings_384d, labels, _ = self._get_data_from_db()
        if not unique_ids:
            return "<html><body><h1>Error</h1><p>No hay datos suficientes en ChromaDB.</p></body></html>"

        try:
            reducer_clustering = joblib.load(self.umap_model_path)
            embeddings_20d = reducer_clustering.transform(embeddings_384d)
            
            # Proyectar a 3D
            reducer_3d = umap.UMAP(n_components=3, n_neighbors=12, min_dist=0.05, metric='euclidean', random_state=42)
            embeddings_3d = reducer_3d.fit_transform(embeddings_20d)
        except Exception as e:
            return f"<html><body><h1>Error de proyeccion</h1><p>{str(e)}</p></body></html>"

        fig = go.Figure()
        unique_labels = sorted(set(labels))
        cluster_labels_valid = [l for l in unique_labels if l != -1]

        # Dibujar clusters normales
        for cluster_id in cluster_labels_valid:
            indices = [i for i, l in enumerate(labels) if l == cluster_id]
            x, y, z = embeddings_3d[indices, 0], embeddings_3d[indices, 1], embeddings_3d[indices, 2]

            hover_texts = [
                f"<b>{unique_ids[i].replace('_', ' ').title()}</b><br>Cluster: {cluster_id}"
                for i in indices
            ]
            color = self.cluster_colors[cluster_id % len(self.cluster_colors)]

            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z, mode='markers+text',
                name=f'Cluster {cluster_id} ({len(indices)} proy.)',
                marker=dict(size=10, color=color, opacity=0.9, line=dict(color='white', width=1.5), symbol='circle'),
                text=[str(i+1) for i in indices], textposition='top center',
                textfont=dict(size=9, color='white'),
                hovertext=hover_texts, hoverinfo='text',
            ))

        # Dibujar Oceanos Azules
        blue_ocean_indices = [i for i, l in enumerate(labels) if l == -1]
        if blue_ocean_indices:
            x_oa, y_oa, z_oa = embeddings_3d[blue_ocean_indices, 0], embeddings_3d[blue_ocean_indices, 1], embeddings_3d[blue_ocean_indices, 2]
            hover_oa = [f"<b>🌊 OCEANO AZUL</b><br><b>{unique_ids[i].replace('_', ' ').title()}</b>" for i in blue_ocean_indices]

            fig.add_trace(go.Scatter3d(
                x=x_oa, y=y_oa, z=z_oa, mode='markers+text',
                name=f'Oceano Azul ({len(blue_ocean_indices)} proy.)',
                marker=dict(size=14, color='#FF4444', opacity=1.0, line=dict(color='white', width=2), symbol='diamond'),
                text=[str(i+1) for i in blue_ocean_indices], textposition='top center',
                textfont=dict(size=10, color='#FF4444'), hovertext=hover_oa, hoverinfo='text',
            ))

        fig.update_layout(
            title=dict(
                text="<b>Corvus — Mapa Topologico 3D de Proyectos</b><br><sup>Arrastra para rotar, scroll para zoom</sup>",
                x=0.5, font=dict(size=16, color='white')
            ),
            scene=dict(
                xaxis=dict(title=dict(text='UMAP 1', font=dict(color='#8899bb')), backgroundcolor='#0a0f2e', gridcolor='#1f295c', zerolinecolor='#1f295c', tickfont=dict(color='#8899bb')),
                yaxis=dict(title=dict(text='UMAP 2', font=dict(color='#8899bb')), backgroundcolor='#0a0f2e', gridcolor='#1f295c', zerolinecolor='#1f295c', tickfont=dict(color='#8899bb')),
                zaxis=dict(title=dict(text='UMAP 3', font=dict(color='#8899bb')), backgroundcolor='#0a0f2e', gridcolor='#1f295c', zerolinecolor='#1f295c', tickfont=dict(color='#8899bb')),
                bgcolor='#0a0f2e'
            ),
            paper_bgcolor='#060b1a', plot_bgcolor='#060b1a',
            legend=dict(font=dict(color='white', size=11), bgcolor='rgba(10,15,46,0.8)', bordercolor='#1f295c', borderwidth=1),
            margin=dict(l=0, r=0, t=80, b=0),
            hoverlabel=dict(bgcolor='#0a0f2e', font=dict(color='white', size=13))
        )

        return fig.to_html(include_plotlyjs='cdn', full_html=True)

visualization_service = VisualizationService()
