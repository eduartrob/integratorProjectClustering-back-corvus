"""
02_filtrar_proyectos_sinteticos.py
===================================
Paso 2 del flujo BATCH de Corvus.

Toma los proyectos sintéticos (que simulan las propuestas reales de la uni),
los pasa por el modelo clasificador ya entrenado (modelo_clasificacion_embeddings.pkl)
y guarda solo los que el modelo considera VÁLIDOS (Excelente o Regular).

INPUT:
    - proyectos_sinteticos.csv       (329 proyectos de referencia de la uni)
    - modelo_clasificacion_embeddings.pkl  (entrenado en 01_entrenar_clasificador.py)

OUTPUT:
    - proyectos_aprobados_filtrados.csv   (solo los que pasan la barrera)
      → Este archivo alimenta al paso 03_descubrir_clusters.py
"""

import pandas as pd
import numpy as np
import joblib
import warnings
from fastembed import TextEmbedding

warnings.filterwarnings("ignore")

SINTETICOS_CSV  = "proyectos_sinteticos.csv"
MODELO_PKL      = "modelo_clasificacion_embeddings.pkl"
SALIDA_CSV      = "proyectos_aprobados_filtrados.csv"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

if __name__ == "__main__":
    print("=" * 60)
    print("  PASO 2 — FILTRAR PROYECTOS SINTÉTICOS CON EL CLASIFICADOR")
    print("=" * 60)

    # 1. Cargar proyectos de referencia de la uni
    print(f"\n[INFO] Cargando: {SINTETICOS_CSV}")
    df = pd.read_csv(SINTETICOS_CSV)
    print(f"       Total proyectos de la uni: {len(df)}")
    print(f"       Distribución original:")
    print(df['categoria_calidad'].value_counts().to_string(header=False))

    # 2. Cargar el modelo entrenado
    print(f"\n[INFO] Cargando modelo: {MODELO_PKL}")
    clf = joblib.load(MODELO_PKL)

    # 3. Vectorizar textos
    print("[INFO] Cargando modelo de embeddings...")
    emb_model = TextEmbedding(model_name=EMBEDDING_MODEL)
    print("[INFO] Vectorizando proyectos sintéticos...")
    X = np.array(list(emb_model.embed(df['texto_extraido'].tolist())))

    # 4. Clasificar con el modelo (la barrera de calidad)
    print("[INFO] Clasificando con la barrera IA...")
    y_pred = clf.predict(X)
    df['prediccion_ia'] = y_pred

    # 5. Filtrar: solo los que pasan la barrera
    df_aprobados = df[df['prediccion_ia'].isin(['Excelente', 'Regular'])].copy()
    df_rechazados = df[~df['prediccion_ia'].isin(['Excelente', 'Regular'])]

    print("\n=== RESULTADO DEL FILTRO ===")
    print(f"  Total analizados:  {len(df)}")
    print(f"  ✅ Aprobados:      {len(df_aprobados)}  (Excelente + Regular)")
    print(f"  🚫 Rechazados:     {len(df_rechazados)}  (Ruido / Mal hecho)")
    print(f"\n  Predicciones:")
    print(df['prediccion_ia'].value_counts().to_string(header=False))

    # 6. Guardar el ecosistema de referencia
    df_aprobados.to_csv(SALIDA_CSV, index=False)
    print(f"\n[ÉXITO] Ecosistema guardado en: {SALIDA_CSV}")
    print(f"        {len(df_aprobados)} proyectos listos para K-Means (paso 03)")
