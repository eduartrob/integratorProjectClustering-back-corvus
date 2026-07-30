# Integrator Project Clustering Service — Corvus Platform

Este microservicio pertenece a la plataforma **CORVUS**. Es el motor de **Inteligencia Artificial y Análisis Vectorial** encargado del descubrimiento de nichos, análisis de Océanos Azules y prevención de colisión semántica en proyectos integradores universitarios.

---

## 🎯 Función en el Ecosistema CORVUS
* **Análisis Vectorial:** Embeddings semánticos para evaluar la originalidad de propuestas de proyectos.
* **Mapa de Océanos Azules:** Clasificación de nichos para evitar duplicidad entre equipos y semestres.
* **Gestión de Proyectos:** Administración del ciclo de vida de proyectos asignados a profesores y alumnos.
* **Base de Datos Dedicada:** Opera sobre su base de datos PostgreSQL aislada **`corvus_integrator_project_db`**.

---

## ⚙️ Tecnologías
* **Lenguaje & Framework:** Python 3.10+, FastAPI, Uvicorn.
* **IA & ML:** Scikit-Learn, HDBSCAN, Sentence-Transformers, ChromaDB / Qdrant.
* **ORM:** SQLAlchemy.
* **Base de Datos:** PostgreSQL (`corvus_integrator_project_db`).

---

## 🛠️ Ejecución Local Independiente

### 1. Entorno Virtual & Dependencias
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Variables de Entorno
Crea un archivo `.env` basado en `.env.example`:
```env
PORT=8002
DATABASE_URL="postgresql://corvus_user:password@localhost:5432/corvus_integrator_project_db"
```

### 3. Iniciar Servidor en Desarrollo
```bash
uvicorn app.main:app --reload --port 8002
```
La documentación interactiva OpenAPI/Swagger estará disponible en `http://localhost:8002/docs`.

---

## 🐳 Ejecución con Docker

```bash
docker build -t corvus-integrator-clustering .
docker run -p 8002:8002 --env-file .env corvus-integrator-clustering
```

---

## 🔗 Integración con la Orquestación de CORVUS
En el entorno completo, este servicio es administrado por **`orchestration-back-corvus`** y sus rutas son consumidas a través del API Gateway (`/api/v1/projects`).