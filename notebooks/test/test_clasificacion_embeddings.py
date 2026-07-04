import pandas as pd
import numpy as np
from fastembed import TextEmbedding
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split, GridSearchCV
import joblib
import warnings

# Suprimir advertencias de FastEmbed
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    print("--- INICIANDO PRUEBA: CLASIFICADOR BASADO EN EMBEDDINGS (STRATIFIED SPLIT) ---")
    
    # 1. Cargar el dataset consolidado
    print("\n[INFO] Cargando dataset completo para entrenamiento y prueba...")
    df = pd.read_csv("antigravity_dataset_50.csv")
    
    # 2. Cargar el modelo de Embeddings
    print("\n[INFO] Cargando modelo FastEmbed (multilingüe)...")
    embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    # 3. Vectorizar
    print("[INFO] Vectorizando textos...")
    X = np.array(list(embedding_model.embed(df['texto_extraido'].tolist())))
    y = df['categoria_calidad']
    
    # 4. Dividir datos (80/20 estratificado)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 5. Configurar GridSearchCV
    print("\n[INFO] Iniciando GridSearchCV para optimizar hiperparámetros...")
    param_grid = {
        'C': [0.1, 1, 10],
        'solver': ['lbfgs', 'liblinear']
    }
    
    base_clf = LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000)
    grid_search = GridSearchCV(base_clf, param_grid, cv=3, scoring='f1_weighted', verbose=1)
    
    grid_search.fit(X_train, y_train)
    
    print(f"[INFO] Mejores parámetros encontrados: {grid_search.best_params_}")
    
    # 6. Evaluar
    print("[INFO] Realizando inferencia sobre el set de prueba...")
    y_pred = grid_search.predict(X_test)
    
    print("\n=== REPORTE DE CLASIFICACIÓN (FASTEMBED + LOGREG + GRIDSEARCH) ===")
    print(classification_report(y_test, y_pred, zero_division=0))
    print("===============================================================")
    
    # ── Reporte del 20% de prueba (métricas honestas) ──────────────────────
    df_test_reporte = df.loc[y_test.index].copy()
    df_test_reporte['prediccion_ia'] = y_pred

    print("\n=== RESULTADO DE LA BARRERA (20% de prueba — métricas honestas) ===")
    print(f"Documentos evaluados:    {len(df_test_reporte)}")
    aprobados_test = df_test_reporte[df_test_reporte['prediccion_ia'].isin(['Excelente', 'Regular'])]
    print(f"Aprobados (Exc/Reg):     {len(aprobados_test)}")
    print(f"Rechazados (Ruido):      {len(df_test_reporte) - len(aprobados_test)}")

    # ── Re-entrenar con el 100% y guardar el modelo de producción ──────────
    print("\n[INFO] Re-entrenando con el 100% de datos (modelo de producción)...")
    mejor_C = grid_search.best_params_['C']
    mejor_solver = grid_search.best_params_['solver']
    clf_produccion = LogisticRegression(
        C=mejor_C, solver=mejor_solver,
        class_weight='balanced', max_iter=1000, random_state=42
    )
    clf_produccion.fit(X, y)  # 100% de antigravity_dataset_50.csv

    joblib.dump(clf_produccion, "modelo_clasificacion_embeddings.pkl")
    print("[EXITO] Modelo de producción guardado en: modelo_clasificacion_embeddings.pkl")
    print()
    print("NOTA: El ecosistema de referencia para K-Means es proyectos_sinteticos.csv")
    print("      (los proyectos ya aprobados de la universidad, filtrados a Excelente/Regular)")

