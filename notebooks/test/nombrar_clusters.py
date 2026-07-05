import pandas as pd
import numpy as np
from fastembed import TextEmbedding
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import warnings

warnings.filterwarnings("ignore")

def encontrar_k_optimo(vectores):
    siluetas = []
    rango_k = range(2, min(10, len(vectores)))
    for k in rango_k:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(vectores)
        siluetas.append(silhouette_score(vectores, kmeans.labels_))
    return rango_k[np.argmax(siluetas)]

if __name__ == "__main__":
    print("--- INICIANDO CENTROID SUMMARIZER (NOMBRADOR DE CLÚSTERES) ---")
    
    # 1. Cargar proyectos
    df = pd.read_csv("proyectos_aprobados_filtrados.csv")
    
    # 2. Vectorizar
    print("[INFO] Vectorizando textos para agruparlos...")
    embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectores = np.array(list(embedding_model.embed(df['texto_extraido'].tolist())))
    
    # IMPORTANTE: Aquí está la REDUCCIÓN DE DIMENSIONALIDAD (PCA)
    # Reducimos los vectores de 384 dimensiones a 10 para hacer las matemáticas más precisas y rápidas.
    print("[INFO] Aplicando Reducción de Dimensionalidad (PCA)...")
    pca = PCA(n_components=min(10, len(df)-1), random_state=42)
    vectores_optimizados = pca.fit_transform(vectores)
    
    # 3. Clustering
    k_optimo = encontrar_k_optimo(vectores_optimizados)
    print(f"[INFO] Ejecutando K-Means con {k_optimo} clústeres óptimos...")
    
    kmeans = KMeans(n_clusters=k_optimo, random_state=42, n_init=10)
    df['id_cluster'] = kmeans.fit_predict(vectores_optimizados)
    centroides = kmeans.cluster_centers_
    
    # 4. Encontrar los proyectos más cercanos al centroide y asignar nombres
    nombres_clusters = {}
    print("\n=== EXTRACCIÓN DE NÚCLEOS TEMÁTICOS ===")
    
    for i in range(k_optimo):
        # Calcular distancia de todos los puntos de este cluster hacia su centroide
        puntos_cluster_idx = df.index[df['id_cluster'] == i].tolist()
        puntos_cluster = vectores_optimizados[puntos_cluster_idx]
        
        # Distancia euclidiana al centroide
        distancias = np.linalg.norm(puntos_cluster - centroides[i], axis=1)
        
        # Obtener los índices de los 3 más cercanos
        top_3_locales = np.argsort(distancias)[:3]
        top_3_globales = [puntos_cluster_idx[idx] for idx in top_3_locales]
        
        textos_cercanos = df.loc[top_3_globales, 'texto_extraido'].tolist()
        
        # =====================================================================
        # TODO (INTEGRACIÓN LLM): 
        # Aquí enviaremos la variable 'textos_cercanos' a Ollama o OpenAI.
        # Ejemplo de prompt: "Analiza estos 3 proyectos y dales un nombre 
        # comercial de máximo 4 palabras que resuma su temática."
        # =====================================================================
        
        # MOCKUP (Simulación temporal de la respuesta del LLM basada en el ID)
        nombres_mock = [
            "Visión Artificial Edge", 
            "Sistemas Web Tradicionales", 
            "RAG y Búsqueda Semántica", 
            "IoT y Sensores MPU",
            "Gestión de Redes y Ciberseguridad",
            "Desarrollo Móvil Multiplataforma",
            "Analítica y Ciencia de Datos",
            "Blockchain y Web3",
            "Automatización de Infraestructura"
        ]
        
        nombre_asignado = nombres_mock[i] if i < len(nombres_mock) else f"Tema Tecnológico {i}"
        nombres_clusters[i] = nombre_asignado
        
        print(f"\n[CLÚSTER {i}] Nombre Asignado por el LLM: '{nombre_asignado}'")
        print(f"  -> Muestra núcleo 1: {textos_cercanos[0][:100]}...")
        print(f"  -> Muestra núcleo 2: {textos_cercanos[1][:100]}...")
        
    # 5. Guardar el resultado final
    df['nombre_cluster'] = df['id_cluster'].map(nombres_clusters)
    df.to_csv("proyectos_clusterizados.csv", index=False)
    print("\n[ÉXITO] Los proyectos con sus etiquetas semánticas se guardaron en 'proyectos_clusterizados.csv'.")
