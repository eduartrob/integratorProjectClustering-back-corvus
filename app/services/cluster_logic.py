import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class ClusterLogic:
    def __init__(self):
        pass

    def perform_clustering(self, embeddings: list[list[float]], n_clusters: int = 5):
        """
        Agrupa los vectores en 'n_clusters' utilizando KMeans.
        Útil para categorizar automáticamente de qué tratan los proyectos del cuatrimestre.
        """
        if not embeddings or len(embeddings) < n_clusters:
            logger.warning("No hay suficientes datos para agrupar.")
            return None

        # Convertimos a arreglo matemático de NumPy
        X = np.array(embeddings)
        
        # Entrenamos el algoritmo K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        kmeans.fit(X)
        
        return {
            "labels": kmeans.labels_.tolist(),
            "centroids": kmeans.cluster_centers_.tolist()
        }

    def find_blue_oceans(self, new_project_embedding: list[float], existing_embeddings: list[list[float]], existing_names: list[str] = None, threshold: float = 0.3):
        """
        Calcula la distancia (similitud) del nuevo proyecto respecto al historial y genera métricas para la UI.
        """
        if not existing_embeddings:
            return {
                "is_blue_ocean": True,
                "main_finding": "¡Primer proyecto en el historial! Nadie ha tocado ningún tema aún, todo es Océano Azul.",
                "viability_metrics": {
                    "originality": 99,
                    "data_availability": 85,
                    "academic_relevance": 90
                },
                "closest_projects": [],
                "methodological_suggestions": [
                    {
                        "name": "Enfoque Mixto Exploratorio",
                        "description": "Al ser un tema totalmente nuevo, combina recolección cualitativa para entender el nicho y encuestas para medir el tamaño del mercado."
                    }
                ],
                "unexplored_topics": ["Cualquier intersección de tecnología y sociedad"]
            }

        X_new = np.array([new_project_embedding])
        X_existing = np.array(existing_embeddings)

        # Calculamos la distancia coseno
        distances = cosine_distances(X_new, X_existing)[0]
        
        # Encontramos la distancia al proyecto que más se le parece
        min_distance = float(np.min(distances))
        is_blue_ocean = min_distance > threshold
        
        # Obtenemos los 3 proyectos más cercanos
        closest_indices = np.argsort(distances)[:3]
        closest_projects = []
        if existing_names:
            closest_projects = [existing_names[i] for i in closest_indices if i < len(existing_names)]
            
        # Calcular scores
        # Distancia 0.0 -> Originality 0%
        # Distancia >= 0.6 -> Originality 99%
        originality = min(int((min_distance / 0.6) * 100), 99)
        
        # Valores simulados deterministas basados en el vector (para que no cambien en cada petición)
        data_av = 60 + (int(abs(sum(new_project_embedding[:5])) * 100) % 35)
        acad_rel = 70 + (int(abs(sum(new_project_embedding[5:10])) * 100) % 25)
        
        if is_blue_ocean:
            finding = f"Nadie ha tocado este tema desde un enfoque similar en los últimos proyectos analizados. Tu originalidad es altísima ({originality}%)."
        else:
            closest_name = closest_projects[0] if closest_projects else "otros proyectos"
            finding = f"Este tema ya fue explorado. Tu proyecto tiene una similitud alta con '{closest_name}'."
            
        closest_safe = closest_projects[0] if closest_projects else 'proyectos previos'
            
        return {
            "is_blue_ocean": is_blue_ocean,
            "main_finding": finding,
            "viability_metrics": {
                "originality": originality,
                "data_availability": data_av,
                "academic_relevance": acad_rel
            },
            "closest_projects": closest_projects,
            "methodological_suggestions": [
                {
                    "name": "Estudio de Caso Comparativo" if not is_blue_ocean else "Enfoque Mixto Secuencial",
                    "description": f"Contrasta tu enfoque con '{closest_safe}' para aislar las variables críticas que ellos no documentaron." if not is_blue_ocean else "Iniciar con recolección de datos cuantitativos macro, seguido de entrevistas a profundidad con actores clave locales."
                }
            ],
            "unexplored_topics": [
                "IA en Agricultura de Precisión",
                "Logística Circular",
                "Biomateriales de Construcción"
            ]
        }

    def find_blue_oceans_hybrid(self, new_project_text: str, existing_texts: list[str], new_project_embedding: list[float], existing_embeddings: list[list[float]], existing_names: list[str] = None, threshold: float = 0.45):
        """
        Búsqueda Híbrida: Combina la distancia Semántica (Contexto/Sinónimos vía Dense Embeddings) 
        con la distancia Léxica (Palabras Clave exclusivas vía TF-IDF).
        """
        if not existing_texts or not existing_embeddings:
            return self.find_blue_oceans(new_project_embedding, existing_embeddings, existing_names)
            
        import spacy
        try:
            nlp = spacy.load("es_core_news_md")
            spanish_stopwords = list(nlp.Defaults.stop_words)
        except:
            # Fallback robusto en caso de que spacy falle
            spanish_stopwords = [
                "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "o", "pero", "si",
                "por", "para", "como", "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde",
                "durante", "en", "entre", "hacia", "hasta", "mediante", "para", "por", "segun", "sin",
                "so", "sobre", "tras", "que", "del", "al", "se", "su", "sus", "mi", "mis", "tu", "tus",
                "es", "son", "fue", "fueron", "ser", "estar", "este", "esta", "estos", "estas", "ese",
                "esa", "esos", "esas", "aquel", "aquella", "aquellos", "aquellas", "lo", "le", "les",
                "me", "te", "nos", "os", "muy", "mas", "más", "ya", "muy", "tambien", "también", "no",
                "ni", "porque", "cuando", "donde", "quien", "quienes", "cual", "cuales"
            ]
            
        # Siempre agregar palabras estorbo académicas, cargue spacy o no
        academic_stopwords = [
            "proyecto", "sistema", "estimado", "objetivo", "desarrollo", "desarrollar", "implementar",
            "implementación", "general", "específico", "específicos", "justificación", "conclusión",
            "introducción", "propuesta", "análisis", "diseño", "aplicación", "web", "móvil", "app",
            "mediante", "uso", "utilizando", "basado", "evaluación", "metodología", "resultados"
        ]
        spanish_stopwords.extend(academic_stopwords)
        
        # 1. Distancia Léxica (TF-IDF) -> Ignora plantillas
        vectorizer = TfidfVectorizer(stop_words=spanish_stopwords, max_df=0.8)
        all_texts = existing_texts + [new_project_text]
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        X_new_tfidf = tfidf_matrix[-1]
        X_existing_tfidf = tfidf_matrix[:-1]
        
        tfidf_distances = cosine_distances(X_new_tfidf, X_existing_tfidf)[0]
        
        # 2. Distancia Semántica (Vectores Densos) -> Atrapa sinónimos y cambios de tono
        X_new_dense = np.array([new_project_embedding])
        X_existing_dense = np.array(existing_embeddings)
        dense_distances = cosine_distances(X_new_dense, X_existing_dense)[0]
        
        # 3. Fusión Híbrida con Peso ADAPTATIVO
        # Damos prioridad al CONTEXTO (Dense) sobre el Conteo de Palabras (TF-IDF).
        # Si el contexto es distinto aunque usen las mismas palabras, la red neuronal dominará.
        divergence = tfidf_distances - dense_distances  # Positivo = Dense más cercano
        
        # Base: 70% Contexto / 30% Palabras. Si hay divergencia (mismas palabras, distinto contexto),
        # subimos la autoridad del contexto al 90% para evitar falsos positivos por palabras genéricas como "estimado".
        weight_dense = np.where(divergence > 0.20, 0.90, 0.70)
        weight_tfidf = 1.0 - weight_dense
        
        hybrid_distances = (dense_distances * weight_dense) + (tfidf_distances * weight_tfidf)
        
        # Calculamos las métricas híbridas para encontrar al vecino más cercano
        # y poder dar feedback preciso incluso si IsolationForest determinó que es un inlier.
        mean_dist = float(np.mean(hybrid_distances))
        std_dist  = float(np.std(hybrid_distances))
        min_hybrid_distance = float(np.min(hybrid_distances))
        closest_idx = int(np.argmin(hybrid_distances))
        
        # Umbral estático solo para referencia en la UI
        effective_threshold = max(mean_dist - (1.8 * std_dist), 0.38)
        
        # 4. Machine Learning: HDBSCAN para Anomalías y Clústeres
        from pathlib import Path
        import joblib
        import hdbscan
        from sklearn.preprocessing import normalize
        
        is_blue_ocean = False
        try:
            model_dir = Path(__file__).resolve().parent.parent / "models"
            umap_path = model_dir / "umap_50d_model.joblib"
            hdbscan_path = model_dir / "hdbscan_model.joblib"
            
            reducer_clustering = joblib.load(umap_path)
            clusterer = joblib.load(hdbscan_path)
            
            # 1. Reducir el nuevo proyecto a 50D usando el modelo UMAP guardado
            X_new_50d = reducer_clustering.transform(X_new_dense)
            
            # 2. Predecir pertenencia a clústeres en 50D
            test_labels, strengths = hdbscan.approximate_predict(clusterer, X_new_50d)
            
            MIN_STRENGTH = 0.30
            if test_labels[0] == -1 or strengths[0] < MIN_STRENGTH:
                is_blue_ocean = True
            else:
                is_blue_ocean = False
                
        except Exception as e:
            logger.warning(f"Error prediciendo con HDBSCAN: {e}")
            # Fallback a umbral estático si falla
            is_blue_ocean = bool(min_hybrid_distance > effective_threshold)
        
        closest_indices = np.argsort(hybrid_distances)[:3]
        closest_projects = []
        if existing_names:
            closest_projects = [existing_names[i] for i in closest_indices if i < len(existing_names)]

        # 5. Extraer las palabras clave que REALMENTE COMPARTEN los dos proyectos
        # (términos con mayor TF-IDF en el proyecto nuevo que también aparecen en el más cercano)
        overlapping_keywords = []
        try:
            feature_names = vectorizer.get_feature_names_out()
            new_vec  = np.asarray(tfidf_matrix[-1].todense()).flatten()
            close_vec = np.asarray(tfidf_matrix[closest_idx].todense()).flatten()
            # Términos con peso > 0 en AMBOS documentos (bajamos el umbral para atrapar textos muy cortos)
            shared_mask = (new_vec > 0.0) & (close_vec > 0.0)
            shared_scores = (new_vec + close_vec) * shared_mask
            top_shared = np.argsort(shared_scores)[-8:][::-1]
            overlapping_keywords = [feature_names[i] for i in top_shared if shared_scores[i] > 0]
        except Exception as e:
            logger.warning(f"No se pudieron extraer keywords: {e}")
            
        # 6. Calcular el porcentaje de similitud REAL (no hardcoded "50%")
        similarity_pct = max(0, int((1 - min_hybrid_distance) * 100))
        originality    = min(int(max((min_hybrid_distance - 0.30) / 0.30, 0) * 100), 99)
        
        data_av  = 60 + (int(min_hybrid_distance * 1000) % 35)
        acad_rel = 70 + (int(min_hybrid_distance * 500)  % 25)
        
        closest_name = closest_projects[0] if closest_projects else "proyectos anteriores"
        closest_safe = closest_name
        
        if is_blue_ocean:
            finding = (
                f"✅ Proyecto innovador: tu propuesta es suficientemente distinta del corpus existente "
                f"({originality}% de originalidad). Distancia mínima al proyecto más cercano: "
                f"{min_hybrid_distance:.2f} (umbral: {effective_threshold:.2f})."
            )
        else:
            if overlapping_keywords:
                kw_str = ", ".join(overlapping_keywords[:5])
                finding = (
                    f"⚠️ Colisión semántica detectada ({similarity_pct}% de similitud) con "
                    f"'{closest_name}'. Los conceptos que se solapan son: {kw_str}. "
                    f"Distancia híbrida: {min_hybrid_distance:.2f} (umbral: {effective_threshold:.2f})."
                )
            else:
                finding = (
                    f"⚠️ Colisión estructural detectada ({similarity_pct}% de similitud) con "
                    f"'{closest_name}'. Aunque no usaron exactamente las mismas palabras técnicas, la Inteligencia Artificial "
                    f"determinó que la IDEA y el CONTEXTO del proyecto son casi idénticos. "
                    f"Distancia híbrida: {min_hybrid_distance:.2f} (umbral: {effective_threshold:.2f})."
                )
            
        # Sugerencia dinámica para que no salga vacía si no hay keywords
        if not is_blue_ocean:
            if overlapping_keywords:
                suggestion_desc = f"Tu proyecto comparte los conceptos '{', '.join(overlapping_keywords[:3])}' con '{closest_safe}'. Considera reforzar los elementos que te diferencian técnicamente."
            else:
                suggestion_desc = f"Tu proyecto persigue el mismo objetivo lógico que '{closest_safe}' (Ej. Rastreo, Ubicación o Gestión física). Modifica drásticamente tu propuesta de valor para que no se considere una copia."
        else:
            suggestion_desc = "Tu propuesta ocupa un espacio conceptual único. Documenta con detalle las características que la distinguen del estado del arte."
            
        return {
            "is_blue_ocean": is_blue_ocean,
            "main_finding": finding,
            "similarity_score": similarity_pct,
            "overlapping_keywords": overlapping_keywords,
            "viability_metrics": {
                "originality": originality,
                "data_availability": data_av,
                "academic_relevance": acad_rel
            },
            "closest_projects": closest_projects,
            "methodological_suggestions": [
                {
                    "name": "Diferenciación Técnica" if not is_blue_ocean else "Enfoque Innovador",
                    "description": suggestion_desc
                }
            ],
            "unexplored_topics": [
                "IA en Agricultura de Precisión",
                "Logística Circular",
                "Biomateriales de Construcción"
            ]
        }

cluster_logic = ClusterLogic()
