import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fastembed import TextEmbedding
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import warnings

warnings.filterwarnings("ignore")

print("--- INICIANDO FASE DE DESCUBRIMIENTO DE CLÚSTERES (CORVUS) ---")

# 1. Cargar el oro puro (los proyectos que pasaron la barrera)
print("[INFO] Cargando proyectos aprobados...")
df = pd.read_csv("proyectos_aprobados_filtrados.csv")

# 2. Vectorizar los textos (Transformarlos a matemáticas)
print("[INFO] Generando embeddings densos con FastEmbed...")
embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vectores = np.array(list(embedding_model.embed(df['texto_extraido'].tolist())))

# 3. Reducción de Dimensionalidad (PCA)
# Reducimos de 384 dimensiones a un número más manejable (ej. 10) para que K-Means sea ultra rápido y preciso
print("[INFO] Aplicando PCA para optimizar la geometría de los vectores...")
pca = PCA(n_components=min(10, len(df)-1), random_state=42)
vectores_optimizados = pca.fit_transform(vectores)

# 4. Búsqueda del K Óptimo (Codo y Silueta)
print("[INFO] Ejecutando simulaciones para encontrar el número óptimo de grupos...")

inercia = []
siluetas = []
rango_k = range(2, min(10, len(df))) # Probamos de 2 hasta 9 grupos (ajustable según el volumen de datos)

for k in rango_k:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(vectores_optimizados)
    
    # Inercia (Para el método del codo: qué tan compactos son los grupos)
    inercia.append(kmeans.inertia_)
    
    # Silueta (Qué tan bien separados están los grupos entre sí)
    score = silhouette_score(vectores_optimizados, kmeans.labels_)
    siluetas.append(score)

# 5. Encontrar el mejor K basado en la Silueta más alta
mejor_k = rango_k[np.argmax(siluetas)]
mejor_score = max(siluetas)

print(f"\n[RESULTADO MATEMÁTICO]")
print(f"-> El número óptimo de grupos (áreas temáticas) es: {mejor_k}")
print(f"-> Score de Silueta máximo: {mejor_score:.4f} (Mientras más cerca de 1, mejor separados están)")

# 6. Graficar los resultados para validación visual
fig, ax1 = plt.subplots(figsize=(10, 5))

# Gráfica del Codo
ax1.set_xlabel('Número de Clústeres (k)')
ax1.set_ylabel('Inercia (Método del Codo)', color='tab:blue')
ax1.plot(rango_k, inercia, marker='o', color='tab:blue', linestyle='dashed')
ax1.tick_params(axis='y', labelcolor='tab:blue')

# Gráfica de Silueta
ax2 = ax1.twinx()  
ax2.set_ylabel('Puntuación de Silueta', color='tab:orange')
ax2.plot(rango_k, siluetas, marker='s', color='tab:orange')
ax2.tick_params(axis='y', labelcolor='tab:orange')

plt.title('Optimización de K-Means: Método del Codo vs Análisis de Silueta')
plt.axvline(x=mejor_k, color='red', linestyle='--', label=f'K Óptimo ({mejor_k})')
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('analisis_clusters.png')
print("\n[ÉXITO] Gráfica guardada como 'analisis_clusters.png'.")
