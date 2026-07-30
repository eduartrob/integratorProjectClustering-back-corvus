import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fastembed import TextEmbedding
from sklearn.ensemble import IsolationForest
from sklearn.manifold import TSNE
import warnings

warnings.filterwarnings("ignore")

def detectar_nichos_innovadores():
    print("--- INICIANDO CAZADOR DE NICHOS (ISOLATION FOREST) ---")
    
    # 1. Cargar Datos
    print("[INFO] Cargando ecosistema de proyectos...")
    try:
        df = pd.read_csv("proyectos_clusterizados.csv")
    except FileNotFoundError:
        print("[ERROR] No se encontró 'proyectos_clusterizados.csv'.")
        return
        
    # 2. Vectorizar
    print("[INFO] Vectorizando para el Bosque de Aislamiento...")
    embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectores = np.array(list(embedding_model.embed(df['texto_extraido'].tolist())))
    
    # 3. Isolation Forest (Detectar anomalías)
    print("[INFO] Entrenando Isolation Forest con contamination='auto'...")
    # 'auto' determinará matemáticamente la proporción de anomalías.
    iso_forest = IsolationForest(contamination='auto', random_state=42, n_estimators=200)
    
    # Predecir (-1 para Anomalía/Nicho, 1 para Normal/Mainstream)
    df['etiqueta_iso'] = iso_forest.fit_predict(vectores)
    
    # Mapear a lenguaje humano
    df['tipo_innovacion'] = df['etiqueta_iso'].map({1: 'Mainstream', -1: 'Nicho_Innovador'})
    
    n_mainstream = (df['tipo_innovacion'] == 'Mainstream').sum()
    n_nicho = (df['tipo_innovacion'] == 'Nicho_Innovador').sum()
    
    print("\n[RESULTADO MATEMÁTICO]")
    print(f"-> Proyectos Mainstream detectados: {n_mainstream}")
    print(f"-> Proyectos Nicho/Innovadores aislados: {n_nicho}")
    
    # Mostrar un par de ejemplos de los nichos encontrados
    print("\n[MUESTRAS DE NICHOS DESCUBIERTOS]")
    muestras = df[df['tipo_innovacion'] == 'Nicho_Innovador'].head(3)
    for idx, row in muestras.iterrows():
        print(f"- [Clúster: {row['nombre_cluster']}] {row['texto_extraido'][:80]}...")
        
    # 4. Visualización t-SNE
    print("\n[INFO] Generando radar de anomalías en 2D...")
    tsne = TSNE(n_components=2, perplexity=30, random_state=42)
    coord_2d = tsne.fit_transform(vectores)
    
    df['tsne_x'] = coord_2d[:, 0]
    df['tsne_y'] = coord_2d[:, 1]
    
    # Crear gráfica
    plt.figure(figsize=(14, 9))
    sns.set_theme(style="darkgrid")
    
    # Dividir datos para plotear diferente
    df_mainstream = df[df['tipo_innovacion'] == 'Mainstream']
    df_nicho = df[df['tipo_innovacion'] == 'Nicho_Innovador']
    
    # Capa 1: Densidad (Solo del mainstream para ver donde está el montón)
    sns.kdeplot(
        data=df_mainstream, x='tsne_x', y='tsne_y', 
        fill=True, thresh=0.01, levels=10, cmap="Purples", alpha=0.4
    )
    
    # Capa 2: Puntos Mainstream (Pequeños y opacos)
    sns.scatterplot(
        data=df_mainstream, x='tsne_x', y='tsne_y',
        color='gray', s=50, alpha=0.5, edgecolor=None, label='Mainstream (En el montón)'
    )
    
    # Capa 3: Puntos Nicho (Estrellas doradas gigantes)
    plt.scatter(
        x=df_nicho['tsne_x'], y=df_nicho['tsne_y'],
        color='gold', marker='*', s=800, edgecolor='black', linewidth=1.5, zorder=10,
        label='Nicho Innovador (Aislado)'
    )
    
    plt.title('Detección de Proyectos Nicho (Isolation Forest + t-SNE)', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Dimensión 1')
    plt.ylabel('Dimensión 2')
    plt.legend(fontsize=12, loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    plt.savefig('mapa_nichos.png', dpi=300, bbox_inches='tight')
    
    # 5. Guardar CSV
    df.to_csv("proyectos_con_nichos.csv", index=False)
    print("[ÉXITO] Archivos generados: 'mapa_nichos.png' y 'proyectos_con_nichos.csv'")

if __name__ == "__main__":
    detectar_nichos_innovadores()
