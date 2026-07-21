# Corvus — Integrator Project Clustering Service

Este es el microservicio de **Inteligencia Artificial** de Corvus, responsable de recibir documentos PDF (propuestas de proyectos), vectorizarlos usando LLMs (SentenceTransformers) y clasificarlos en un espacio semántico para determinar su originalidad, viabilidad y riesgo de plagio/colisión usando K-Means, PCA e Isolation Forest.

## 🚀 Arquitectura
- **Framework**: FastAPI (Python)
- **Modelos**: `paraphrase-multilingual-MiniLM-L12-v2` (embeddings 384D), K-Means (Clustering), PCA (reducción de dimensionalidad), Isolation Forest (detección de océanos azules).
- **Base de Datos**: Qdrant (Vector Database) para guardar los embeddings de los proyectos con persistencia en disco.

## 📡 Endpoints Principales

### Core API
- `POST /api/v1/pre-validate-proposal`: Pre-valida una propuesta de proyecto (PDF) aplicando filtros ML, blacklist, secciones del profesor, coherencia semántica y antiplagio.
- `POST /api/v1/analyze-draft-proposal`: Análisis profundo con LLM (Ollama/Groq) para dictamen de originalidad.
- `POST /api/v1/process-folder`: Sincroniza una carpeta de Google Drive en background.
- `GET /api/v1/blue-ocean-niches`: Lista de océanos azules detectados por Isolation Forest.

### Admin API (Dashboard)
- `GET /api/v1/admin/clusters-3d`: Devuelve el HTML estático interactivo generado con Plotly con la representación topológica de 3 dimensiones de todos los proyectos alojados. Diseñado para consumirse a través de un `<iframe>` en el Frontend de administración.
- `GET /api/v1/admin/clusters-2d-html`: Mapa semántico 2D con elipses KDE por clúster.
- `GET /api/v1/admin/clusters-stats`: Devuelve estadísticas rápidas de Qdrant (Total de Océanos azules, Proyectos Activos, etc.).
- `POST /api/v1/admin/execute`: Ejecuta clustering global (vectoriza pendientes + re-entrena K-Means + Isolation Forest).

## ⚙️ Desarrollo
1. Crear entorno virtual: `python -m venv venv`
2. Activar entorno e instalar dependencias: `pip install -r requirements.txt`
3. Arrancar servidor en modo dev: `uvicorn app.main:app --reload --port 8000`