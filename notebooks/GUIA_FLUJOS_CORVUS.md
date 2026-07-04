# 🦅 CORVUS — Guía de Flujos

Hay **dos flujos** en el sistema. Uno se corre una sola vez (o cuando hay datos nuevos),
el otro se corre cada vez que un alumno sube su PDF.

---

## FLUJO A — Batch: Entrenamiento + Ecosistema + K-Means

> Corre este flujo cuando cambias el dataset de entrenamiento o agregas
> nuevos proyectos sintéticos de referencia.

```
antigravity_dataset_50.csv          proyectos_sinteticos.csv
(1,069 filas: Exc / Reg / Ruido)    (329 proyectos de la uni)
        │                                    │
        ▼                                    │
01_entrenar_clasificador.py                  │
   → Aprende a distinguir propuestas         │
   → Guarda: modelo_clasificacion_           │
             embeddings.pkl  ───────────────►│
                                             ▼
                               02_filtrar_proyectos_sinteticos.py
                                  → Pasa los 329 por el modelo
                                  → Guarda solo Excelente + Regular
                                  → Salida: proyectos_aprobados_
                                            filtrados.csv
                                             │
                                             ▼
                               03_descubrir_clusters.py
                                  → Método del codo + Silueta
                                  → Encuentra K óptimo
                                  → Salida: analisis_clusters.png
                                             │
                                             ▼
                               04_nombrar_clusters.py
                                  → PCA 384D → 10D
                                  → K-Means con K óptimo
                                  → Salida: proyectos_clusterizados.csv
                                             │
                              ┌──────────────┘
                              ▼
               05_visualizar_clusters.py
                  → t-SNE 10D → 2D
                  → Mapa general de todos los clústeres
                  → Mapas individuales por clúster
                  → Salidas: mapa_oceanos_azules.png
                             mapas_individuales.png
                              │
                              ▼
               06_detectar_nichos.py
                  → Isolation Forest
                  → Clasifica: Mainstream vs Nicho
                  → Salida: mapa_nichos.png
                             proyectos_con_nichos.csv
```

### Comandos (en orden):

```bash
python 01_entrenar_clasificador.py
python 02_filtrar_proyectos_sinteticos.py
python 03_descubrir_clusters.py
python 04_nombrar_clusters.py
python 05_visualizar_clusters.py
python 06_detectar_nichos.py
```

---

## FLUJO B — Producción: PDF de alumno → Análisis completo

> Corre este flujo cada vez que un alumno sube su propuesta.
> Requiere que el Flujo A ya se haya ejecutado al menos una vez.

```
mi_propuesta.pdf
        │
        ▼
[PASO 1] Extracción PDF
         pdfplumber → texto crudo de todas las páginas
        │
        ▼
[PASO 2] Limpieza de texto
         → minúsculas, espacios, caracteres especiales
        │
        ▼
[PASO 3] Clasificación (la "barrera")
         modelo_clasificacion_embeddings.pkl
         → Excelente / Regular → CONTINÚA ✅
         → Ruido               → RECHAZADO 🚫 (termina aquí)
        │
        ▼
[PASO 4] Cargar ecosistema de referencia
         proyectos_aprobados_filtrados.csv
         (los proyectos de la uni ya filtrados)
        │
        ▼
[PASO 5] PCA 384D → 10D + K-Means
         → Agrupa el ecosistema
         → Asigna el PDF al clúster más cercano
         → Calcula distancia al centroide (% posición)
        │
        ▼
[PASO 6] t-SNE 10D → 2D + Visualización
         → Mapa global: todos los clústeres + ⭐ (tu PDF)
         → Zoom del clúster asignado + ⭐ + línea al centro
         → Salidas: mapa_pipeline_resultado.png
                    mapa_zoom_cluster_N.png
```

### Comando:

```bash
python pipeline_corvus.py --pdf mi_propuesta.pdf
```

---

## Resumen de archivos

| Archivo | Flujo | Descripción |
| :--- | :---: | :--- |
| `01_entrenar_clasificador.py` | A | Entrena el clasificador Exc/Reg/Ruido con antigravity_dataset_50.csv |
| `02_filtrar_proyectos_sinteticos.py` | A | Filtra proyectos_sinteticos.csv con el modelo → ecosistema K-Means |
| `03_descubrir_clusters.py` | A | Encuentra K óptimo con codo + silueta |
| `04_nombrar_clusters.py` | A | K-Means + PCA, asigna clúster a cada proyecto |
| `05_visualizar_clusters.py` | A | Mapa t-SNE del ecosistema completo |
| `06_detectar_nichos.py` | A | Detecta proyectos innovadores vs. convencionales |
| `pipeline_corvus.py` | B | Pipeline completo para un PDF real de alumno |
| `test_limpieza.py` | ref | Referencia de funciones de limpieza de texto |

## Archivos de datos

| Archivo | Generado por | Usado en |
| :--- | :--- | :--- |
| `antigravity_dataset_50.csv` | (manual) | `01_entrenar_clasificador.py` |
| `proyectos_sinteticos.csv` | (manual) | `02_filtrar_proyectos_sinteticos.py` |
| `modelo_clasificacion_embeddings.pkl` | `01_...` | `02_...`, `pipeline_corvus.py` |
| `proyectos_aprobados_filtrados.csv` | `02_...` | `03_...`, `pipeline_corvus.py` |
| `proyectos_clusterizados.csv` | `04_...` | `05_...`, `06_...` |
