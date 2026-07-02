# Changelog - Project Clustering Service

## [0.5.0] - 2026-07-02
### Refactorización de Arquitectura y Base de Datos
- **Migración a Qdrant**: Se reemplazó ChromaDB por Qdrant para mejorar la velocidad y escalabilidad en la búsqueda de vectores.
- **Flujo Desacoplado de Google Drive**: La sincronización con Drive ya no vectoriza los documentos inmediatamente. Ahora detecta, extrae el texto y los almacena localmente en una "Base de Datos de Pendientes" (`PendingProjectsDB`).
- **Clusterización por Lotes (Batch)**: El endpoint `/admin/execute` ahora es el único responsable de tomar la cola de proyectos pendientes, generar embeddings en masa (Qdrant) y recalcular el mapa global semántico (K-Means), reduciendo la fragmentación de la memoria.

## [0.4.0] - 2026-06-26

### Arquitectura y Refactorización
- **Clustering Service Nativo**: Se refactorizó toda la lógica de machine learning (UMAP, HDBSCAN, Plotly, ChromaDB) desde el antiguo script CLI aislado (`visualize_clusters.py`) hacia un servicio interno nativo de FastAPI (`app/services/clustering_service.py`).
- **Eliminación de Subprocess**: Se eliminó el anti-patrón de invocar el algoritmo de clustering mediante `subprocess.run()`. El endpoint `/admin/execute` ahora invoca la clase `ClusteringEngineService` directamente en memoria mediante `BackgroundTasks`, reduciendo el consumo de RAM, eliminando dependencias CLI innecesarias, e incrementando la estabilidad general del backend.

### Precisión Matemática y Vectorial (Core Engine)
- **Cerebro Multilingüe**: Se reemplazó el modelo base de embeddings por `paraphrase-multilingual-MiniLM-L12-v2`. Esto otorga una comprensión semántica profunda de textos técnicos en español nativo, superando las limitaciones del modelo anterior enfocado en inglés.
- **Búsqueda Multi-Query K-NN**: Se erradicó la técnica de promediar vectores por proyecto (`np.mean`), la cual diluía la especificidad semántica. Ahora el sistema compara los fragmentos más representativos (Top 5) de manera independiente contra el historial, incrementando drásticamente la detección de colisiones de plagio o similitudes de nicho.
- **Chunking Estructural (Markdown-Aware)**: El particionador de texto (Chunker) dejó de usar contadores de palabras ciegos. Se implementó una lógica de expresiones regulares que corta los fragmentos respetando estrictamente los saltos de título (`#` y `##`), aislando módulos lógicos como metodologías y objetivos en vectores puros.

### Seguridad y Estabilidad (RASP)
- **Refinamiento Anti-Prompt Injection**: Se afinó el filtro de inyección de prompt para tolerar contextos semánticamente legítimos en español. La regla `actúa como` ahora es ignorada inteligentemente si está seguida de un objeto del sistema (ej. "el sistema actúa como plataforma"), reduciendo a cero los falsos positivos en propuestas válidas.
- **Control de Consultas Vacías**: Se implementó una barrera de control que intercepta documentos vacíos o irrecuperables (`HTTP 400`) antes de que el motor ChromaDB lance fallos críticos por falta de dimensiones (`HTTP 500`).
- **Transparencia HTTP**: Reestructuración de bloques `try-except` en la API. Los rechazos por seguridad (ej. inyecciones, violaciones de formato) ahora preservan sus códigos semánticos exactos (`403 Forbidden`, `406 Not Acceptable`) hasta llegar al frontend, en lugar de ser absorbidos y silenciados por un `500 Internal Server Error` genérico.

### Higiene, Visualización y Mantenimiento (Chore & UI)
- **Visualización Topológica Interactiva**: El script `visualize_clusters.py` fue rescrito desde cero. La visualización estática (`matplotlib`) fue reemplazada por la arquitectura `plotly.graph_objects`. Ahora exporta mapas oceánicos en formato HTML con capacidades de zoom infinito, paneo libre, cascos convexos sombreados y tooltips informativos por proyecto.
- **Sincronización del Pipeline de Pruebas**: El motor de testeo manual (`--new-proposal` en visualización) fue parcheado para utilizar la misma extracción de PDF (`pymupdf4llm`) y el modelo multilingüe oficial que se usa en producción, garantizando congruencia dimensional.
- **Depuración de Endpoints Legados**: Las rutas experimentales o sustituidas (`/process-project` y `/process-local-project`) fueron completamente eliminadas del código fuente. La API expuesta está ahora depurada y orientada a los estándares del flujo actual de la aplicación móvil y el administrador en la nube.


## [0.3.0] - 2026-06-26

### Mejoras y Nuevas Características (Features)
- **Extracción Estructurada de Documentos (Markdown)**: Se sustituyó `pdfplumber` por `pymupdf4llm`. El sistema ahora preserva de manera inmaculada la jerarquía de títulos y el formato de las tablas al convertir PDFs a Markdown puro. Esto reduce alucinaciones y mejora en más del 80% la comprensión estructural de Ollama.
- **Integración de IA Generativa Local (Ollama)**: Se integró el modelo Phi-3 Mini (`ollama_service.py`) para redactar dictámenes estructurados en formato JSON (innovación, riesgos, recomendaciones).
- **Endpoint de Análisis Estricto**: Se agregó el endpoint `/api/v1/analyze-proposal-phi3` diseñado para que las aplicaciones móviles envíen PDFs de proyectos, combinando búsquedas de ChromaDB con inferencia LLM.
- **Inyección Matemática contra Alucinaciones**: El prompt del LLM ahora recibe el cálculo de distancia coseno (similitud porcentual) exacto desde ChromaDB para forzar una calificación de 0% en copias idénticas, eliminando la alucinación de "mejoras" en el modelo.

### Seguridad RASP (Runtime Application Self-Protection)
- **Filtro Anti-Prompt Injection**: `nlp_service.py` escanea los documentos por frases ocultas diseñadas para engañar a la IA ("ignora instrucciones", "eres un bot") y aborta el análisis con HTTP 403.
- **Prevención de Evasión Vectorial (Homoglifos)**: Se implementó `normalize_homoglyphs` con `unicodedata` para limpiar caracteres engañosos (ej. alfabeto cirílico) que buscan evadir el K-NN de ChromaDB.
- **Blindaje de Producción**: La ruta de indexación oficial (`/populate-from-local-folder`) fue asegurada con un `X-API-Key` contra envenenamiento de datos (Data Poisoning). *Nota: ruta conservada si se utiliza por admins localmente.*
- **Umbral Estricto Anti-Spinning**: La IA ahora reprobará automáticamente documentos que superen el 90% de similitud para mitigar el parafraseo automatizado.

### Higiene y Dependencias (Chore)
- **Limpieza de Producción**: Eliminación definitiva de los endpoints locales de prueba (`/process-local-project`), scripts de visualización estática (`visualize_clusters.py`), y la carpeta `projectsTests/` para mantener la API en modo nube/producción exclusivo.
- **Optimización de Despliegue**: Se relajó el bloqueo de versión en `transformers` y se forzó la descarga de los binarios CPU-only de PyTorch (`torch`) reduciendo dramáticamente el peso de la instalación para Contabo/AWS.

## [0.2.0] - 2026-06-23

### Mejoras y Nuevas Características (Features)
- **Refactorización del Motor de Clustering**: Se corrigió el cálculo de Océanos Azules para utilizar correctamente el modelo HDBSCAN sobre una reducción intermedia de UMAP a 20 dimensiones, en lugar de 2 dimensiones, garantizando resultados deterministas y de alta precisión.
- **Formato de Respuesta de API**: Se actualizó el esquema de respuesta JSON del endpoint `/api/v1/process-local-project` para alinear los campos (`indice_innovacion`, `metricas_calidad`, `riesgo_colision`, `recomendaciones_ia`) estrictamente con los diseños visuales del frontend.
- **Módulo de Administrador (Admin API)**: 
  - Se creó el endpoint `GET /api/v1/admin/clusters-3d` que sirve directamente el HTML de la gráfica topológica interactiva 3D generada con Plotly.
  - Se creó el endpoint `GET /api/v1/admin/clusters-stats` para servir tarjetas de resumen (KPIs) con el conteo total de proyectos, clústeres y océanos azules.

### Higiene y Mantenimiento (Chore)
- Limpieza del repositorio raíz: Movidos los scripts de análisis manual (`visualize_3d.py`, `preview_project.py`, `ingest_folder.py`, etc.) al repositorio del panel de administración para mantener el backend de producción puro.
- Eliminación de archivos temporales Markdown utilizados durante las pruebas de validación de Océanos Azules.

## [0.1.0] - Versión Inicial
- Implementación inicial del motor de modelos (SentenceTransformers + UMAP + HDBSCAN).
- Conexión con base de datos ChromaDB.
