import numpy as np
import joblib
import umap
import plotly.graph_objects as go
from collections import Counter
from app.services.qdrant_service import qdrant_service
from app.core.config import settings
import os

class VisualizationService:
    def __init__(self):
        self.umap_model_path = os.path.join(settings.MODELS_DIR, "umap_50d_model.joblib")
        self.cluster_colors = [
            '#4FC3F7', '#FFB74D', '#81C784', '#F06292', '#CE93D8',
            '#80DEEA', '#FFCC02', '#FF8A65', '#A5D6A7', '#90CAF9'
        ]

    def _get_data_from_db(self):
        
        vectors, payloads = qdrant_service.get_all_embeddings()
        if not vectors or len(vectors) == 0:
            return None, None, None, None

        projects_data = {}
        for i, meta in enumerate(payloads):
            p_id = meta.get('project_id')
            if not p_id:
                continue
            if p_id not in projects_data:
                projects_data[p_id] = {
                    'embeddings': [],
                    'cluster_id': meta.get('cluster_id', 0),
                    'is_blue_ocean': meta.get('is_blue_ocean', False)
                }
            projects_data[p_id]['embeddings'].append(vectors[i])

        unique_ids = sorted(projects_data.keys())
        aggregated_embeddings = [np.mean(projects_data[p]['embeddings'], axis=0) for p in unique_ids]
        labels = [projects_data[p]['cluster_id'] for p in unique_ids]
        
        return unique_ids, np.array(aggregated_embeddings), labels, projects_data

    def get_cluster_names(self):
        
        unique_ids, _, labels, _ = self._get_data_from_db()
        if not unique_ids:
            return {}

        cluster_counts = Counter(labels)
        stopwords = {'de', 'la', 'el', 'en', 'y', 'para', 'con', 'los', 'las', 'un', 'una', 'del', 'al', 'proyecto', 'md', 'pdf'}
        
        cluster_names = {}
        for cid in cluster_counts.keys():
            if cid == -1:
                cluster_names[cid] = "Océano Azul"
                continue
            
            p_ids = [unique_ids[i] for i in range(len(unique_ids)) if labels[i] == cid]
            words = []
            for pid in p_ids:
                clean_pid = pid.lower().replace('.md', '').replace('.pdf', '').replace('_', ' ').replace('-', ' ')
                words.extend([w for w in clean_pid.split() if w not in stopwords and len(w) > 2])
            
            if words:
                common_words = [w[0].title() for w in Counter(words).most_common(2)]
                cluster_names[cid] = " / ".join(common_words)
            else:
                cluster_names[cid] = f"Clúster {cid}"
                
        return cluster_names

    def get_cluster_stats(self):
        
        unique_ids, _, labels, projects_data = self._get_data_from_db()
        if not unique_ids:
            return {"error": "No hay datos en la base de datos"}

        cluster_counts = Counter(labels)
        total_projects = len(unique_ids)
        blue_oceans = cluster_counts.get(-1, 0)
        
        cluster_names = self.get_cluster_names()
        
        clusters_info = []
        for cid, count in cluster_counts.items():
            if cid != -1:
                clusters_info.append({
                    "cluster_id": cid, 
                    "project_count": count,
                    "cluster_name": cluster_names.get(cid, f"Clúster {cid}")
                })

        return {
            "total_projects": total_projects,
            "total_clusters": len(clusters_info),
            "blue_oceans": blue_oceans,
            "clusters_detail": sorted(clusters_info, key=lambda x: x['cluster_id']),
            "cluster_names": cluster_names
        }

    def get_2d_scatter_data(self):
        
        if not os.path.exists(self.umap_model_path):
            return []

        unique_ids, embeddings_384d, labels, _ = self._get_data_from_db()
        if not unique_ids:
            return []

        try:
            reducer_clustering = joblib.load(self.umap_model_path)
            embeddings_20d = reducer_clustering.transform(embeddings_384d)
            
            reducer_2d = umap.UMAP(n_components=2, n_neighbors=12, min_dist=0.05, metric='euclidean', random_state=42)
            embeddings_2d = reducer_2d.fit_transform(embeddings_20d)
        except Exception:
            return []

        scatter_data = []
        for i in range(len(unique_ids)):
            scatter_data.append({
                "x": float(embeddings_2d[i, 0]),
                "y": float(embeddings_2d[i, 1]),
                "label": int(labels[i]),
                "name": unique_ids[i].replace('_', ' ').title()
            })
            
        return scatter_data

    def generate_3d_html(self):
        
        if not os.path.exists(self.umap_model_path):
            return "<html><body><h1>Error</h1><p>Modelo UMAP no encontrado. Ejecuta visualize_clusters.py primero.</p></body></html>"

        unique_ids, embeddings_384d, labels, _ = self._get_data_from_db()
        if not unique_ids:
            return "<html><body><h1>Error</h1><p>No hay datos suficientes en ChromaDB.</p></body></html>"

        try:
            reducer_clustering = joblib.load(self.umap_model_path)
            embeddings_20d = reducer_clustering.transform(embeddings_384d)
            
            reducer_3d = umap.UMAP(n_components=3, n_neighbors=12, min_dist=0.05, metric='euclidean', random_state=42)
            embeddings_3d = reducer_3d.fit_transform(embeddings_20d)
        except Exception as e:
            return f"<html><body><h1>Error de proyeccion</h1><p>{str(e)}</p></body></html>"

        fig = go.Figure()
        unique_labels = sorted(set(labels))
        cluster_labels_valid = [l for l in unique_labels if l != -1]

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

    def generate_2d_html(self):
        if not os.path.exists(self.umap_model_path):
            return "<html><body><h1>Error</h1><p>Modelo UMAP no encontrado.</p></body></html>"

        unique_ids, embeddings_384d, labels, _ = self._get_data_from_db()
        if not unique_ids:
            return "<html><body><h1>Error</h1><p>No hay datos en ChromaDB.</p></body></html>"

        try:
            reducer_clustering = joblib.load(self.umap_model_path)
            embeddings_20d = reducer_clustering.transform(embeddings_384d)
            reducer_2d = umap.UMAP(n_components=2, n_neighbors=12, min_dist=0.05, metric='euclidean', random_state=42)
            embeddings_2d = reducer_2d.fit_transform(embeddings_20d)
        except Exception as e:
            return f"<html><body><h1>Error de proyeccion</h1><p>{str(e)}</p></body></html>"

        import math

        def hex_to_rgba(hex_color, alpha):
            h = hex_color.lstrip('#')
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f'rgba({r},{g},{b},{alpha})'

        def ellipse_points(cx, cy, sx, sy, n=60):
            return (
                [cx + sx * math.cos(2 * math.pi * i / n) for i in range(n + 1)],
                [cy + sy * math.sin(2 * math.pi * i / n) for i in range(n + 1)]
            )

        fig = go.Figure()
        unique_labels = sorted(set(labels))
        cluster_labels_valid = [l for l in unique_labels if l != -1]

        # Outer + inner ellipses per cluster (KDE-style)
        for cluster_id in cluster_labels_valid:
            indices = [i for i, l in enumerate(labels) if l == cluster_id]
            if len(indices) < 3:
                continue
            pts = embeddings_2d[indices]
            color = self.cluster_colors[cluster_id % len(self.cluster_colors)]
            cx, cy = float(pts[:, 0].mean()), float(pts[:, 1].mean())
            sx = float(pts[:, 0].std()) * 2.4
            sy = float(pts[:, 1].std()) * 2.4
            # Outer halo
            ex, ey = ellipse_points(cx, cy, sx, sy)
            fig.add_trace(go.Scatter(x=ex, y=ey, fill='toself',
                fillcolor=hex_to_rgba(color, 0.13),
                line=dict(color='rgba(0,0,0,0)', width=0),
                showlegend=False, hoverinfo='skip', mode='lines'))
            # Inner core
            ex2, ey2 = ellipse_points(cx, cy, sx * 0.52, sy * 0.52)
            fig.add_trace(go.Scatter(x=ex2, y=ey2, fill='toself',
                fillcolor=hex_to_rgba(color, 0.30),
                line=dict(color=hex_to_rgba(color, 0.55), width=1.2),
                showlegend=False, hoverinfo='skip', mode='lines'))

        # Cluster points
        for cluster_id in cluster_labels_valid:
            indices = [i for i, l in enumerate(labels) if l == cluster_id]
            x, y = embeddings_2d[indices, 0], embeddings_2d[indices, 1]
            color = self.cluster_colors[cluster_id % len(self.cluster_colors)]
            hover_texts = [
                f"<b>{unique_ids[i].replace('_', ' ').title()}</b><br>Clúster: {cluster_id}"
                for i in indices
            ]
            fig.add_trace(go.Scatter(x=x, y=y, mode='markers',
                name=f'Clúster {cluster_id} ({len(indices)} proy.)',
                marker=dict(size=12, color=color, opacity=0.92,
                            line=dict(color='white', width=1.2)),
                hovertext=hover_texts, hoverinfo='text'))

        # Blue Oceans as red stars
        blue_ocean_indices = [i for i, l in enumerate(labels) if l == -1]
        if blue_ocean_indices:
            x_oa = embeddings_2d[blue_ocean_indices, 0]
            y_oa = embeddings_2d[blue_ocean_indices, 1]
            hover_oa = [
                f"<b>🌊 OCÉANO AZUL</b><br><b>{unique_ids[i].replace('_', ' ').title()}</b>"
                for i in blue_ocean_indices
            ]
            fig.add_trace(go.Scatter(x=x_oa, y=y_oa, mode='markers',
                name=f'🌊 Océano Azul ({len(blue_ocean_indices)} proy.)',
                marker=dict(size=20, color='#FF3333', symbol='star',
                            line=dict(color='darkred', width=1.5), opacity=1.0),
                hovertext=hover_oa, hoverinfo='text'))

        fig.update_layout(
            title=dict(text="<b>Mapa Semántico 2D — Clústeres HDBSCAN</b>",
                       x=0.5, font=dict(size=16, color='#1a1a2e')),
            xaxis=dict(title='UMAP Dim 1', gridcolor='#e8edf5', zerolinecolor='#d0d7e3',
                       tickfont=dict(color='#444')),
            yaxis=dict(title='UMAP Dim 2', gridcolor='#e8edf5', zerolinecolor='#d0d7e3',
                       tickfont=dict(color='#444')),
            paper_bgcolor='white', plot_bgcolor='#fafbff',
            legend=dict(font=dict(color='#222', size=11), bordercolor='#dde3ef',
                        borderwidth=1, bgcolor='white'),
            margin=dict(l=40, r=20, t=60, b=40),
            hoverlabel=dict(bgcolor='white', font=dict(color='black', size=13))
        )

        return fig.to_html(include_plotlyjs='cdn', full_html=True)




visualization_service = VisualizationService()
