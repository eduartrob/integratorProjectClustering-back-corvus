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
        self._cargar_ecosistema()
        if self._embeddings is None:
            return {"error": "Ecosistema no disponible", "cluster_id": -1}

        vec_nuevo = np.array(vector_nuevo).reshape(1, -1)
        X_total   = np.vstack([self._embeddings, vec_nuevo])

        # Entrenar K-Means si es necesario o reusar
        k = self._elegir_k(self._embeddings)
        if self._kmeans is None or self._kmeans.n_clusters != k:
            self._kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
            self._kmeans.fit(self._embeddings)
            logger.info(f"[Clustering] K-Means entrenado con K={k}.")

        cluster_id = int(self._kmeans.predict(vec_nuevo)[0])
        centroide  = self._kmeans.cluster_centers_[cluster_id]

        # Calcular posición relativa al radio del clúster
        dist_nuevo = float(np.linalg.norm(vec_nuevo[0] - centroide))
        indices_cluster = np.where(self._kmeans.labels_ == cluster_id)[0]
        if len(indices_cluster) > 0:
            dists_miembros = np.linalg.norm(
                self._embeddings[indices_cluster] - centroide, axis=1
            )
            radio = float(np.max(dists_miembros)) if len(dists_miembros) else dist_nuevo
        else:
            radio = dist_nuevo if dist_nuevo > 0 else 1.0

        posicion_pct   = round(min((dist_nuevo / radio) * 100, 100), 1) if radio > 0 else 0.0
        innovacion_pct = round(100 - posicion_pct, 1)

        # Proyectos cercanos del mismo clúster
        proyectos_cercanos = []
        if self._df_eco is not None and len(indices_cluster) > 0:
            col_nombre = next((c for c in ["nombre_proyecto", "titulo", "name", "proyecto"]
                               if c in self._df_eco.columns), None)
            if col_nombre:
                proyectos_cercanos = self._df_eco.iloc[indices_cluster][col_nombre].tolist()[:5]

        # PCA 2D para visualización (opcional, si el frontend lo pide)
        try:
            if self._pca is None:
                self._pca = PCA(n_components=2, random_state=42)
                self._embeddings_2d = self._pca.fit_transform(self._embeddings)
            coord_nuevo_2d = self._pca.transform(vec_nuevo)[0].tolist()
        except Exception:
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
        """
        if self.is_running:
            logger.warning("[Clustering] Clustering ya está en ejecución.")
            return False
            
        self.is_running = True
        self.last_error = None
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
                        'text': meta.get('text', '')  # Guarda texto para el LLM
                    }
                projects_data[p_id]['embeddings'].append(vectors[i])
                # Concatenar un poco de texto para el LLM si es muy corto
                if len(projects_data[p_id]['text']) < 1500:
                    projects_data[p_id]['text'] += " " + meta.get('text', '')

            unique_ids = sorted(projects_data.keys())
            if len(unique_ids) < 2:
                logger.warning("[Clustering] No hay suficientes proyectos únicos.")
                return False

            # Vector promedio por proyecto
            aggregated_embeddings = [np.mean(projects_data[p]['embeddings'], axis=0) for p in unique_ids]
            X = np.array(aggregated_embeddings)

            # 2. PCA: 384D -> 10D
            logger.info("[Clustering] Aplicando PCA...")
            pca_dim = min(10, len(X) - 1)
            if pca_dim < 2:
                pca_dim = 2
            pca = PCA(n_components=pca_dim, random_state=42)
            X_pca = pca.fit_transform(X)

            # 3. K Óptimo Dinámico (Silhouette + Elbow)
            logger.info("[Clustering] Buscando K óptimo...")
            siluetas = []
            # Límite superior matemático: no más de N/2, máximo 20 (dinámico sin límite de 9)
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
                
            logger.info(f"[Clustering] K óptimo calculado: {k_optimo}")

            # 4. K-Means Final
            logger.info("[Clustering] Entrenando K-Means...")
            self._kmeans = KMeans(n_clusters=k_optimo, random_state=42, n_init=10)
            labels = self._kmeans.fit_predict(X_pca)
            centroids = self._kmeans.cluster_centers_

            # 5. Isolation Forest (Océanos Azules)
            logger.info("[Clustering] Ejecutando Isolation Forest...")
            from sklearn.ensemble import IsolationForest
            # Usamos vectores originales para detectar nichos, igual que en su script
            iso_forest = IsolationForest(contamination='auto', random_state=42, n_estimators=200)
            etiquetas_iso = iso_forest.fit_predict(X)  # -1 (Nicho), 1 (Mainstream)

            # 6. Nombrar Clústeres (LLM)
            logger.info("[Clustering] Generando nombres de clústeres con LLM...")
            from app.services.llm_client import llm_client
            nombres_clusters = {}
            for i in range(k_optimo):
                puntos_cluster_idx = [idx for idx, label in enumerate(labels) if label == i]
                if not puntos_cluster_idx:
                    nombres_clusters[i] = f"Clúster {i}"
                    continue
                    
                puntos_cluster = X_pca[puntos_cluster_idx]
                distancias = np.linalg.norm(puntos_cluster - centroids[i], axis=1)
                top_3_locales = np.argsort(distancias)[:3]
                top_3_globales = [puntos_cluster_idx[idx] for idx in top_3_locales]
                
                textos_cercanos = [projects_data[unique_ids[idx]]['text'] for idx in top_3_globales]
                
                nombre_generado = await llm_client.generate_cluster_name(textos_cercanos)
                nombres_clusters[i] = nombre_generado
                logger.info(f"[Clustering] Clúster {i} nombrado: {nombre_generado}")

            # 7. Actualización Masiva en Qdrant (Set Payload)
            logger.info("[Clustering] Actualizando Qdrant payloads...")
            for p_idx, p_id in enumerate(unique_ids):
                c_id = int(labels[p_idx])
                c_name = nombres_clusters[c_id]
                is_blue_ocean = bool(etiquetas_iso[p_idx] == -1)
                
                qdrant_service.update_project_payload(
                    project_id=p_id,
                    payload_data={
                        "cluster_id": c_id,
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

    def find_blue_oceans_hybrid(self, *args, **kwargs):
        """Deprecated."""
        return self.find_blue_oceans()


clustering_engine = ClusteringEngineService()
