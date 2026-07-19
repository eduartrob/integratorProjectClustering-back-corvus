"""
clustering_service.py — Motor de clustering con K-Means validado.
Reemplaza el HDBSCAN+UMAP anterior que generaba clusters incorrectos.
Usa el mismo embedding model que nlp_service y almacena en Qdrant.
"""
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)

_BASE_DIR   = Path(__file__).resolve().parent.parent.parent
_NOTEBOOKS  = _BASE_DIR / "notebooks"
_MODELO_PKL = _NOTEBOOKS / "models" / "modelo_clasificacion_embeddings.pkl"
_CSV_ECO    = _NOTEBOOKS / "data" / "proyectos_aprobados_filtrados.csv"
_EMB_MODEL  = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Rango de K para el método del codo
_K_MIN, _K_MAX = 3, 12


class ClusteringEngineService:
    """
    Motor de clustering basado en K-Means sobre embeddings de SentenceTransformer.
    Carga el ecosistema de proyectos validados (CSV) y asigna el nuevo proyecto
    al clúster más cercano, calculando su posición relativa al centroide.
    """

    def __init__(self):
        self._emb_model   = None   # carga lazy
        self._df_eco      = None   # ecosistema de proyectos
        self._embeddings  = None   # vectores del ecosistema (numpy)
        self._kmeans      = None   # modelo K-Means entrenado
        
        # Métricas de deriva (Drift Monitoring)
        self.total_new_projects = 0
        self.sse_anomalies_count = 0
        
        self._pca         = None   # PCA 2D para visualización
        self._embeddings_2d = None
        self.is_running   = False
        self.last_error   = None

    # ── Carga lazy del modelo de embeddings ──────────────────────────────────

    def _get_emb_model(self):
        if self._emb_model is None:
            from fastembed import TextEmbedding
            self._emb_model = TextEmbedding(model_name=_EMB_MODEL)
            logger.info("[Clustering] Modelo de embeddings cargado.")
        return self._emb_model

    # ── Cargar ecosistema de proyectos ───────────────────────────────────────

    def _cargar_ecosistema(self):
        """Carga el CSV de proyectos aprobados y vectoriza su contenido."""
        if self._embeddings is not None:
            return   # ya cargado

        if not _CSV_ECO.exists():
            logger.error(f"[Clustering] No se encontró el ecosistema: {_CSV_ECO}")
            return

        emb = self._get_emb_model()
        df  = pd.read_csv(_CSV_ECO)

        col_texto = next((c for c in ["propuesta_limpia", "texto_limpio", "texto", "contenido"]
                          if c in df.columns), None)
        if col_texto is None:
            logger.error("[Clustering] El CSV no tiene columna de texto reconocida.")
            return

        df = df.dropna(subset=[col_texto]).reset_index(drop=True)
        textos = df[col_texto].astype(str).tolist()

        logger.info(f"[Clustering] Vectorizando {len(textos)} proyectos del ecosistema...")
        vecs = np.array(list(emb.embed(textos)))

        self._df_eco     = df
        self._embeddings = vecs
        logger.info("[Clustering] Ecosistema cargado.")

    # ── Método del codo para elegir K ────────────────────────────────────────

    def _elegir_k(self, X: np.ndarray) -> int:
        """Elige K óptimo con el método del codo (mayor cambio de inercia)."""
        k_range = range(_K_MIN, min(_K_MAX + 1, len(X)))
        inercias = []
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init="auto")
            km.fit(X)
            inercias.append(km.inertia_)

        # Mayor diferencia de segunda derivada → codo
        deltas = np.diff(inercias)
        accel  = np.diff(deltas)
        k_opt  = list(k_range)[np.argmax(np.abs(accel)) + 1] if len(accel) else _K_MIN
        logger.info(f"[Clustering] K óptimo por codo: {k_opt}")
        return k_opt

    # ── Pipeline de clustering para un nuevo proyecto ────────────────────────

    def asignar_cluster(self, vector_nuevo: list) -> dict:
        """
        Dado el vector del nuevo proyecto, entrena K-Means sobre el ecosistema
        y asigna el proyecto al clúster más cercano.

        Retorna:
          cluster_id      : int — clúster asignado (0-indexed)
          cluster_total   : int — total de clústeres
          posicion_pct    : float — posición dentro del radio del clúster (0-100)
          innovacion_pct  : float — inverso de la posición (qué tan alejado del centro)
          proyectos_cercanos: list — proyectos del mismo clúster
        """
        from app.services.visualization_service import visualization_service
        unique_ids, embeddings_384d, labels, projects_data = visualization_service._get_data_from_db()
        if not unique_ids:
            return {"error": "Ecosistema no disponible en Qdrant", "cluster_id": -1, "innovacion_pct": 50.0}

        vec_nuevo = np.array(vector_nuevo).reshape(1, -1)

        unique_labels = sorted(set(labels))
        valid_labels = [l for l in unique_labels if str(l) != "-1"]
        
        if not valid_labels:
            return {"error": "No hay clusters válidos en Qdrant", "cluster_id": -1, "innovacion_pct": 50.0}

        centroids = []
        for l in valid_labels:
            indices = [i for i, label in enumerate(labels) if label == l]
            centroids.append(np.mean(embeddings_384d[indices], axis=0))
            
        centroids = np.array(centroids)
        distances = np.linalg.norm(centroids - vec_nuevo, axis=1)
        closest_idx = int(np.argmin(distances))
        cluster_id = str(valid_labels[closest_idx])
        centroide = centroids[closest_idx]
        
        k = len(valid_labels)

        # Calcular posición relativa al radio del clúster
        dist_nuevo = float(np.min(distances))
        indices_cluster = [i for i, label in enumerate(labels) if label == cluster_id]
        if len(indices_cluster) > 0:
            dists_miembros = np.linalg.norm(
                embeddings_384d[indices_cluster] - centroide, axis=1
            )
            radio = float(np.max(dists_miembros)) if len(dists_miembros) else dist_nuevo
        else:
            radio = dist_nuevo if dist_nuevo > 0 else 1.0

        # Monitoreo de Deriva (Drift)
        self.total_new_projects += 1
        if dist_nuevo > (radio * 1.5):
            self.sse_anomalies_count += 1
            logger.warning(f"⚠️ Anomalía SSE detectada. Distancia: {dist_nuevo:.2f} (Radio: {radio:.2f})")
            
        tasa_anomalia = (self.sse_anomalies_count / self.total_new_projects) * 100
        if tasa_anomalia >= 15.0 and self.total_new_projects >= 3:
            logger.warning(f"⚠️ ALERTA DE DERIVA: Tasa de anomalías alcanzó {tasa_anomalia:.1f}%. Se recomienda ejecutar el Clustering Global.")
            try:
                from app.services.rabbitmq_service import rabbitmq_service
                rabbitmq_service.publish_progress(
                    user_id="admin_all",
                    type_event="drift_alert",
                    progress=100,
                    total=100,
                    message=f"Tasa de Deriva Crítica ({tasa_anomalia:.1f}%). Ejecute el Clustering para re-balancear los mapas."
                )
            except Exception as ex:
                logger.error(f"Error enviando alerta de deriva a RabbitMQ: {ex}")

        posicion_pct   = round(min((dist_nuevo / radio) * 100, 100), 1) if radio > 0 else 0.0
        innovacion_pct = round(100 - posicion_pct, 1)

        # Proyectos cercanos del mismo clúster (los 5 más cercanos)
        proyectos_cercanos = []
        if len(indices_cluster) > 0:
            miembros_dists = np.linalg.norm(embeddings_384d[indices_cluster] - vec_nuevo, axis=1)
            closest_miembros_indices = np.argsort(miembros_dists)[:5]
            for idx in closest_miembros_indices:
                p_id = unique_ids[indices_cluster[idx]]
                proyectos_cercanos.append(p_id.replace('_', ' ').title())

        # No pasamos coord_2d de PCA porque no alinea con UMAP.
        coord_nuevo_2d = [0.0, 0.0]

        logger.info(f"[Clustering] Clúster asignado: {cluster_id}/{k} | Posición: {posicion_pct}%")
        return {
            "cluster_id"       : cluster_id,
            "cluster_total"    : k,
            "posicion_pct"     : posicion_pct,
            "innovacion_pct"   : innovacion_pct,
            "proyectos_cercanos": proyectos_cercanos,
            "coord_2d"         : coord_nuevo_2d,
        }

    # ── Clustering global (para re-indexar todo el corpus de profesores) ─────

    async def execute_global_clustering(self) -> bool:
        """
        Re-entrena el K-Means con todos los proyectos del corpus vivos en Qdrant,
        calculando todo dinámicamente: K óptimo, Isolation Forest para océanos azules, y LLM para nombres.
        Los clusters que ya tienen nombre y cuyo centroide es similar al nuevo (coseno ≥ 0.88)
        conservan su nombre SIN llamar al LLM. Solo los clusters genuinamente nuevos piden nombre.
        """
        if self.is_running:
            logger.warning("[Clustering] Clustering ya está en ejecución.")
            return False
            
        self.is_running = True
        self.last_error = None
        
        # Resetear métricas de deriva
        self.total_new_projects = 0
        self.sse_anomalies_count = 0
        
        try:
            logger.info("[Clustering] Iniciando Clustering Global...")
            
            # 1. Extraer todo de Qdrant (usando la lógica de visualization_service)
            from app.services.qdrant_service import qdrant_service
            vectors, payloads = qdrant_service.get_all_embeddings()
            if not vectors or len(vectors) == 0:
                logger.warning("[Clustering] Qdrant está vacío.")
                return False

            projects_data = {}
            for i, meta in enumerate(payloads):
                p_id = meta.get('project_id')
                if not p_id:
                    continue
                if p_id not in projects_data:
                    projects_data[p_id] = {
                        'embeddings': [],
                        'text': meta.get('text', ''),
                        'career_id': meta.get('career_id', 'global'),
                        'prev_cluster_name': meta.get('cluster_name', '')  # nombre previo
                    }
                projects_data[p_id]['embeddings'].append(vectors[i])
                if len(projects_data[p_id]['text']) < 1500:
                    projects_data[p_id]['text'] += " " + meta.get('text', '')

            # Group by career_id
            careers_dict = {}
            for p_id, p_data in projects_data.items():
                c_id = p_data['career_id']
                if c_id not in careers_dict:
                    careers_dict[c_id] = []
                careers_dict[c_id].append(p_id)

            for career, unique_ids in careers_dict.items():
                unique_ids = sorted(unique_ids)
                if len(unique_ids) < 2:
                    logger.warning(f"[Clustering] No hay suficientes proyectos para la carrera {career}.")
                    for p_id in unique_ids:
                        from app.services.qdrant_service import qdrant_service
                        qdrant_service.update_project_payload(
                            project_id=p_id,
                            payload_data={
                                "cluster_id": f"{career}_0",
                                "cluster_name": "Proyectos Iniciales",
                                "is_blue_ocean": False
                            }
                        )
                    continue

                aggregated_embeddings = [np.mean(projects_data[p]['embeddings'], axis=0) for p in unique_ids]
                X = np.array(aggregated_embeddings)

                logger.info(f"[Clustering] Aplicando PCA para carrera {career}...")
                pca_dim = min(10, len(X) - 1)
                if pca_dim < 2:
                    pca_dim = 2
                pca = PCA(n_components=pca_dim, random_state=42)
                X_pca = pca.fit_transform(X)

                logger.info(f"[Clustering] Buscando K óptimo para carrera {career}...")
                siluetas = []
                max_k = min(20, max(3, len(X) // 2))
                rango_k = range(2, max_k + 1)
                
                if len(X) > 2:
                    for k in rango_k:
                        kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
                        kmeans_temp.fit(X_pca)
                        siluetas.append(silhouette_score(X_pca, kmeans_temp.labels_))
                    k_optimo = rango_k[np.argmax(siluetas)]
                else:
                    k_optimo = 2
                    
                logger.info(f"[Clustering] K óptimo calculado para {career}: {k_optimo}")

                self._kmeans = KMeans(n_clusters=k_optimo, random_state=42, n_init=10)
                labels = self._kmeans.fit_predict(X_pca)
                centroids = self._kmeans.cluster_centers_

                from sklearn.ensemble import IsolationForest
                iso_forest = IsolationForest(contamination='auto', random_state=42, n_estimators=200)
                etiquetas_iso = iso_forest.fit_predict(X)

                # ── Recuperar nombres existentes (en espacio 384d) para reutilizar ──
                existing_named_clusters = self._extract_existing_cluster_names(
                    projects_data, unique_ids, X
                )

                from app.services.llm_client import llm_client
                nombres_clusters = {}
                for i in range(k_optimo):
                    puntos_cluster_idx = [idx for idx, label in enumerate(labels) if label == i]
                    if not puntos_cluster_idx:
                        nombres_clusters[i] = f"Clúster {i}"
                        continue
                    
                    # Centroide nuevo en espacio original 384d
                    centroide_384d = np.mean(X[puntos_cluster_idx], axis=0)
                    
                    # Intentar reutilizar nombre existente por similitud coseno (≥ 0.96)
                    nombre_reutilizado = self._match_existing_name(
                        centroide_384d, existing_named_clusters, threshold=0.96
                    )
                    
                    if nombre_reutilizado:
                        nombres_clusters[i] = nombre_reutilizado
                        logger.info(f"[Clustering] Clúster {i} ({career}) → nombre reutilizado: '{nombre_reutilizado}'")
                        continue
                        
                    # No hay match → pedir nombre nuevo al LLM solo para este grupo genuinamente nuevo
                    puntos_cluster = X_pca[puntos_cluster_idx]
                    distancias = np.linalg.norm(puntos_cluster - centroids[i], axis=1)
                    top_3_locales = np.argsort(distancias)[:3]
                    top_3_globales = [puntos_cluster_idx[idx] for idx in top_3_locales]
                    
                    textos_cercanos = [projects_data[unique_ids[idx]]['text'] for idx in top_3_globales]
                    nombre_generado = await llm_client.generate_cluster_name(textos_cercanos)
                    nombres_clusters[i] = nombre_generado
                    logger.info(f"[Clustering] Clúster {i} ({career}) → nuevo nombre LLM: '{nombre_generado}'")

                logger.info(f"[Clustering] Actualizando Qdrant payloads para carrera {career}...")
                for p_idx, p_id in enumerate(unique_ids):
                    local_c_id = int(labels[p_idx]) if str(labels[p_idx]).lstrip('-').isdigit() else labels[p_idx]
                    global_c_id = f"{career}_{local_c_id}"
                    c_name = nombres_clusters.get(local_c_id, nombres_clusters.get(str(local_c_id), f"Clúster {local_c_id}"))
                    is_blue_ocean = bool(etiquetas_iso[p_idx] == -1)
                    
                    from app.services.qdrant_service import qdrant_service
                    qdrant_service.update_project_payload(
                        project_id=p_id,
                        payload_data={
                            "cluster_id": global_c_id,
                            "cluster_name": c_name,
                            "is_blue_ocean": is_blue_ocean
                        }
                    )
                
            logger.info("[Clustering] Finalizado con éxito.")
            return True
        
        except Exception as e:
            logger.error(f"[Clustering] Error crítico durante clustering global: {e}")
            import traceback
            traceback.print_exc()
            self.last_error = str(e)
            return False
        finally:
            self.is_running = False

    # ── Auxiliares para nombres persistentes ──────────────────────────────────

    def _extract_existing_cluster_names(
        self, projects_data: dict, unique_ids: list, X: np.ndarray
    ) -> list:
        """
        Devuelve lista de (centroide_384d, nombre) agrupando los proyectos
        por su cluster_name previo almacenado en projects_data (antes del re-clustering).
        Solo incluye nombres que no sean genéricos ('Clúster N', 'Proyectos Iniciales').
        """
        cluster_groups = {}
        for p_idx, p_id in enumerate(unique_ids):
            prev_name = projects_data[p_id].get('prev_cluster_name', '').strip()
            # Filtra nombres genéricos
            if not prev_name or prev_name.startswith("Clúster ") or prev_name in ["Tema Tecnológico", "Océano Azul", "Proyectos Iniciales"]:
                continue
            if prev_name not in cluster_groups:
                cluster_groups[prev_name] = []
            cluster_groups[prev_name].append(X[p_idx])

        result = []
        for name, embs in cluster_groups.items():
            if embs:
                centroide = np.mean(embs, axis=0)
                result.append((centroide, name))

        logger.info(f"[Clustering] {len(result)} nombres de clusters existentes disponibles para reutilizar.")
        return result

    def _match_existing_name(
        self, new_centroid: np.ndarray, existing: list, threshold: float = 0.88
    ) -> "str | None":
        """
        Compara el centroide nuevo (384d) con los centroides de clusters existentes con nombre.
        Retorna el nombre si hay similitud coseno >= threshold, de lo contrario None.
        """
        if not existing:
            return None

        best_sim = -1.0
        best_name = None
        norm_new = float(np.linalg.norm(new_centroid))
        if norm_new == 0:
            return None

        for centroid_old, name in existing:
            norm_old = float(np.linalg.norm(centroid_old))
            if norm_old == 0:
                continue
            sim = float(np.dot(new_centroid, centroid_old) / (norm_new * norm_old))
            if sim > best_sim:
                best_sim = sim
                best_name = name

        if best_sim >= threshold:
            logger.info(f"[Clustering] Match de centroide encontrado (sim={best_sim:.3f}): '{best_name}'")
            return best_name
        return None

    # ── Compatibilidad con código viejo ──────────────────────────────────────
    def perform_clustering(self, embeddings, n_clusters=5):
        """Deprecated: usar asignar_cluster() para nuevos proyectos."""
        if not embeddings:
            return None
        X = np.array(embeddings)
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        km.fit(X)
        return {"labels": km.labels_.tolist(), "centroids": km.cluster_centers_.tolist()}

    def find_blue_oceans(self, *args, **kwargs):
        """Deprecated: la métrica de innovación viene de asignar_cluster()['innovacion_pct']."""
        return {"is_blue_ocean": False, "main_finding": "Usar asignar_cluster() para obtener métricas."}

    def get_drift_metrics(self) -> dict:
        """
        Retorna las métricas actuales de deriva para el dashboard de administración.
        """
        drift_rate = 0.0
        if self.total_new_projects > 0:
            drift_rate = round((self.sse_anomalies_count / self.total_new_projects) * 100, 2)
            
        is_alert = drift_rate >= 15.0 and self.total_new_projects >= 3
        
        return {
            "total_new_projects": self.total_new_projects,
            "sse_anomalies_count": self.sse_anomalies_count,
            "drift_rate_pct": drift_rate,
            "status": "alert" if is_alert else "normal",
            "message": "Se recomienda ejecutar Clustering Global." if is_alert else "Ecosistema estable."
        }

    def find_blue_oceans_hybrid(self, *args, **kwargs):
        """Deprecated."""
        return self.find_blue_oceans()


clustering_engine = ClusteringEngineService()
