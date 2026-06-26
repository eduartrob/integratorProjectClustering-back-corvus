# Changelog - Project Clustering Service

## [0.3.0] - 2026-06-26

### Mejoras y Nuevas Características (Features)
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
