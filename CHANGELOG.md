# Changelog - Project Clustering Service

## [0.2.0] - 2026-06-23

### 🚀 Mejoras y Nuevas Características (Features)
- **Refactorización del Motor de Clustering**: Se corrigió el cálculo de Océanos Azules para utilizar correctamente el modelo HDBSCAN sobre una reducción intermedia de UMAP a 20 dimensiones, en lugar de 2 dimensiones, garantizando resultados deterministas y de alta precisión.
- **Formato de Respuesta de API**: Se actualizó el esquema de respuesta JSON del endpoint `/api/v1/process-local-project` para alinear los campos (`indice_innovacion`, `metricas_calidad`, `riesgo_colision`, `recomendaciones_ia`) estrictamente con los diseños visuales del frontend.
- **Módulo de Administrador (Admin API)**: 
  - Se creó el endpoint `GET /api/v1/admin/clusters-3d` que sirve directamente el HTML de la gráfica topológica interactiva 3D generada con Plotly.
  - Se creó el endpoint `GET /api/v1/admin/clusters-stats` para servir tarjetas de resumen (KPIs) con el conteo total de proyectos, clústeres y océanos azules.

### 🧹 Higiene y Mantenimiento (Chore)
- Limpieza del repositorio raíz: Movidos los scripts de análisis manual (`visualize_3d.py`, `preview_project.py`, `ingest_folder.py`, etc.) al repositorio del panel de administración para mantener el backend de producción puro.
- Eliminación de archivos temporales Markdown utilizados durante las pruebas de validación de Océanos Azules.

## [0.1.0] - Versión Inicial
- Implementación inicial del motor de modelos (SentenceTransformers + UMAP + HDBSCAN).
- Conexión con base de datos ChromaDB.
