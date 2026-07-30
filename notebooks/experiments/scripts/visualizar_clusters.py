import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fastembed import TextEmbedding
from sklearn.manifold import TSNE
import warnings

warnings.filterwarnings("ignore")

def generar_mapa_semantico():
    print("--- INICIANDO VISUALIZADOR DE OCÉANOS AZULES ---")
    
    # 1. Cargar datos finales
    print("[INFO] Cargando proyectos con sus nombres de clúster...")
    try:
        df = pd.read_csv("proyectos_clusterizados.csv")
    except FileNotFoundError:
        print("[ERROR] No se encontró 'proyectos_clusterizados.csv'. Ejecuta nombrar_clusters.py primero.")
        return
        
    # 2. Re-vectorizar (Rápido)
    print("[INFO] Generando vectores para mapa 2D...")
    embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectores = np.array(list(embedding_model.embed(df['texto_extraido'].tolist())))
    
    # 3. Reducción a exactamente 2 dimensiones usando t-SNE (Mejor separación visual que PCA)
    print("[INFO] Comprimiendo 384 dimensiones a 2 dimensiones (t-SNE)...")
    tsne = TSNE(n_components=2, perplexity=30, random_state=42)
    coordenadas_2d = tsne.fit_transform(vectores)
    
    df['x'] = coordenadas_2d[:, 0]
    df['y'] = coordenadas_2d[:, 1]
    
    # 4. Configurar la Gráfica
    print("[INFO] Dibujando el mapa semántico...")
    plt.figure(figsize=(14, 9))
    
    # Usar una paleta de colores vibrante
    sns.set_theme(style="white") # Fondo blanco limpio
    
    # 4.1 Añadir Mapa de Calor (Densidad) estilo curvas de nivel
    print("[INFO] Generando mapa de calor topográfico...")
    sns.kdeplot(
        data=df,
        x='x',
        y='y',
        fill=True,
        thresh=0.01,
        levels=12, # Niveles discretos como en la imagen
        cmap="Blues_r", # Tonos azules como la referencia
        alpha=0.6,
        zorder=0
    )

    
    scatter = sns.scatterplot(
        data=df,
        x='x', 
        y='y',
        hue='nombre_cluster',
        palette='tab10',
        s=100, # Tamaño de los puntos
        alpha=0.8,
        edgecolor='black'
    )
    
    # 4.5 Calcular y dibujar los centroides en 2D
    print("[INFO] Dibujando los centroides (núcleos)...")
    centroides_2d = df.groupby('nombre_cluster')[['x', 'y']].mean().reset_index()
    sns.scatterplot(
        data=centroides_2d,
        x='x',
        y='y',
        color='black',
        marker='X',
        s=400, # Cruz muy grande
        zorder=10, # Asegurar que quede por encima de los puntos
        label='Centroide (Núcleo)'
    )
    
    # Personalización del diseño
    plt.title('Mapa de Océanos Azules (Clústeres Semánticos Corvus)', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Dimensión Semántica 1', fontsize=12)
    plt.ylabel('Dimensión Semántica 2', fontsize=12)
    
    # Ajustar leyenda (fuera del gráfico para que no tape los puntos)
    plt.legend(title='Temáticas Descubiertas', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Guardar imagen global
    plt.savefig('mapa_oceanos_azules.png', dpi=300, bbox_inches='tight')
    print("\n[ÉXITO] ¡Mapa visual generado y guardado como 'mapa_oceanos_azules.png'!")
    
    # 5. Generar gráficas individuales (Grid 3x3)
    print("\n[INFO] Generando mapa desglosado (una gráfica por cada clúster)...")
    n_clusters = df['nombre_cluster'].nunique()
    n_cols = 3
    n_rows = (n_clusters + n_cols - 1) // n_cols 
    
    # Al quitar sharex y sharey, cada gráfica hace un "zoom" automático centrando al clúster
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(36, 12 * n_rows))
    axes = axes.flatten()
    
    clusters = sorted(df['nombre_cluster'].unique()) # Ordenados alfabéticamente
    
    for i, cluster_name in enumerate(clusters):
        ax = axes[i]
        df_cluster = df[df['nombre_cluster'] == cluster_name]
        
        # Mapa topográfico solo para este cluster
        sns.kdeplot(
            data=df_cluster,
            x='x', y='y',
            fill=True, thresh=0.01, levels=8, cmap="Blues_r", alpha=0.6, ax=ax
        )
        
        # Puntos del cluster
        sns.scatterplot(
            data=df_cluster,
            x='x', y='y',
            color='tab:orange', edgecolor='black', s=180, alpha=0.9, ax=ax
        )
        
        # Centroide
        centroide = df_cluster[['x', 'y']].mean()
        ax.scatter(centroide['x'], centroide['y'], color='black', marker='X', s=600, zorder=10)
        
        ax.set_title(cluster_name, fontsize=18, fontweight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel('')
        
    # Ocultar ejes vacíos si no es múltiplo de 3
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
        
    plt.tight_layout()
    plt.savefig('mapas_individuales.png', dpi=300, bbox_inches='tight')
    print("[ÉXITO] ¡Grid de gráficas individuales guardado como 'mapas_individuales.png'!")

if __name__ == "__main__":
    generar_mapa_semantico()
