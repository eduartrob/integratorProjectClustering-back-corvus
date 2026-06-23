# Corvus — Integrator Project Clustering Service

Este es el microservicio de **Inteligencia Artificial** de Corvus, responsable de recibir documentos PDF (propuestas de proyectos), vectorizarlos usando LLMs (SentenceTransformers) y clasificarlos en un espacio semántico para determinar su originalidad, viabilidad y riesgo de plagio/colisión usando UMAP y HDBSCAN.

## 🚀 Arquitectura
- **Framework**: FastAPI (Python)
- **Modelos**: `intfloat/multilingual-e5-small` (RAG), UMAP (Reducción de Dimensionalidad 384D -> 20D), HDBSCAN (Clustering Topológico).
- **Base de Datos**: ChromaDB (Vector Database) para guardar los embeddings de los proyectos.

## 📡 Endpoints Principales

### Core API
- `POST /api/v1/process-project`: Procesa un proyecto desde la nube o bucket (producción).
- `POST /api/v1/process-local-project`: Endpoint para desarrollo/pruebas locales que acepta la carga de un archivo PDF vía Multipart Form.

### Admin API (Dashboard)
- `GET /api/v1/admin/clusters-3d`: Devuelve el HTML estático interactivo generado con Plotly con la representación topológica de 3 dimensiones de todos los proyectos alojados. Diseñado para consumirse a través de un `<iframe>` en el Frontend de administración.
- `GET /api/v1/admin/clusters-stats`: Devuelve estadísticas rápidas de ChromaDB (Total de Océanos azules, Proyectos Activos, etc.).

## ⚙️ Desarrollo
1. Crear entorno virtual: `python -m venv venv`
2. Activar entorno e instalar dependencias: `pip install -r requirements.txt`
3. Arrancar servidor en modo dev: `uvicorn app.main:app --reload --port 8000`
