# 🦅 Plan: Pipeline Monolítico Corvus (PDF → Clúster)

## Flujo actual (scripts separados, corrían sobre CSV)

```
proyectos_sinteticos.csv
        │
        ▼
test_limpieza.py          → Limpia texto del CSV
        │
        ▼
test_clasificacion_embeddings.py  → Clasifica (Excelente/Regular/Ruido)
        │                           Guarda: proyectos_aprobados_filtrados.csv
        ▼
descubrir_clusters.py     → Método del codo + Silueta → K óptimo
        │                   Guarda: analisis_clusters.png
        ▼
nombrar_clusters.py       → K-Means + PCA + nombres mock
        │                   Guarda: proyectos_clusterizados.csv
        ▼
visualizar_clusters.py    → t-SNE + mapa + gráficas individuales
        │                   Guarda: mapa_oceanos_azules.png, mapas_individuales.png
        ▼
detectar_nichos.py        → Isolation Forest → mainstream vs nicho
                            Guarda: mapa_nichos.png, proyectos_con_nichos.csv
```

---

## Flujo nuevo (pipeline unificado, recibe un PDF real)

```
mi_propuesta.pdf  (cargado por el usuario)
        │
        ▼
[PASO 1] Extracción PDF → texto crudo (PyMuPDF/pdfplumber)
        │
        ▼
[PASO 2] Limpieza (reutiliza limpiar_texto_transformer de test_limpieza.py)
        │
        ▼
[PASO 3] Clasificación con modelo ya entrenado
         → Carga modelo_clasificacion_embeddings.pkl
         → Si es "Ruido" → RECHAZADO (termina aquí)
         → Si es "Excelente" o "Regular" → APROBADO, continúa
        │
        ▼
[PASO 4] Cargar el ecosistema de referencia
         → proyectos_aprobados_filtrados.csv (los 631 aprobados)
         → Vectorizar TODO (ecosistema + propuesta nueva)
        │
        ▼
[PASO 5] K-Means con K óptimo (método del codo automático)
         → Entrena sobre el ecosistema
         → Asigna el PDF nuevo a su clúster
         → Calcula su distancia al centroide
        │
        ▼
[PASO 6] Visualización t-SNE
         → Muestra mapa con todos los puntos
         → La propuesta nueva aparece destacada (estrella roja)
         → Muestra a qué clúster pertenece y qué tan "innovadora" es
```

---

## Propuestas de Cambio

### [NEW] `pipeline_corvus.py`
Script único que reemplaza la ejecución manual de los 5 scripts.  
Acepta una ruta a PDF como argumento o usa un PDF de prueba.

```
python pipeline_corvus.py --pdf mi_propuesta.pdf
```

**Secciones internas:**
- `extraer_texto_pdf(ruta)` — nueva función con pdfplumber
- `limpiar_texto_transformer(texto)` — reutilizada de test_limpieza.py
- `clasificar_propuesta(texto)` — carga el .pkl ya entrenado
- `vectorizar_ecosistema(df, texto_nuevo)` — vectoriza todo junto
- `kmeans_con_codo(vectores)` — integra descubrir_clusters + nombrar_clusters
- `visualizar_con_propuesta_nueva(df, coord_2d, idx_nuevo)` — marca el PDF

### [MODIFY] Scripts existentes
Los scripts existentes **no se tocan** — quedan como están para referencia.  
El nuevo `pipeline_corvus.py` importa solo las funciones que necesita.

---

## Dependencias nuevas necesarias

| Librería | Para qué |
| :--- | :--- |
| `pdfplumber` | Extraer texto limpio de PDFs (mejor que PyPDF2 con tablas y columnas) |

---

## ⚠️ Pregunta de diseño

¿El PDF de prueba que cargaremos es:
- Una propuesta **real de un alumno** (archivo que tú tienes)?
- ¿O usamos uno de los proyectos del CSV para simular?

Esto afecta si necesitamos también detectar el idioma/formato del PDF.

---

## Verificación

Al final del pipeline se abrirá automáticamente una gráfica donde:
- 🔵 Puntos azules = todos los proyectos del ecosistema (por clúster)
- ⭐ Estrella roja = el PDF que acabamos de analizar
- Texto = nombre del clúster donde cayó + distancia al centro
