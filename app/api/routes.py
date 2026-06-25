from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import List
import pdfplumber
import io
import numpy as np

from app.services.drive_service import drive_service
from app.services.nlp_service import nlp_service
from app.services.chroma_service import chroma_service
from app.services.cluster_logic import cluster_logic
from app.services.rabbitmq_service import rabbitmq_service

router = APIRouter()

# Global in-memory store for sync progress polling
progress_store = {}

class ProcessProjectRequest(BaseModel):
    project_id: str
    drive_file_id: str
    access_token: str # En producción esto vendría en los headers, lo dejamos aquí por practicidad ahora.
    url_drive: str

class ProcessFolderRequest(BaseModel):
    folder_id: str
    access_token: str

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "integratorProjectClustering"}

@router.post("/process-project")
async def process_project_document(request: ProcessProjectRequest):
    """
    Ruta Principal de Minería (Según tu diagrama):
    Descarga el PDF, lo parte, lo vectoriza y lo guarda en ChromaDB.
    """
    try:
        request.project_id = request.project_id.lower().strip()
        # 1. Extraer texto desde Google Drive a RAM
        text = drive_service.process_drive_file(request.drive_file_id, request.access_token)
        if not text:
            raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF")

        # 1.5 Filtro de Seguridad y Privacidad
        if not nlp_service.is_valid_project(text):
            raise HTTPException(status_code=406, detail="El documento fue rechazado porque no parece ser un proyecto académico válido (Ej. Currículums, Manuales).")
            
        # Limpiar estructura ANTES de anonimizar para que los regex funcionen
        # sobre texto original (bibliografía, sección info equipo, etc.)
        clean_text = nlp_service.strip_structure(text)
        safe_text = nlp_service.anonymize_pii(clean_text)

        # 2. Partir el texto con Spacy
        chunks = nlp_service.chunk_text(safe_text)
        
        # 3. Vectorizar con Sentence-Transformers
        embeddings = nlp_service.vectorize(chunks)

        # 4. Guardar en Base de Datos Vectorial
        chroma_service.add_vectors(
            project_id=request.project_id,
            texts=chunks,
            embeddings=embeddings,
            url_drive=request.url_drive
        )

        # 5. Ejecutar análisis automático de Océano Azul
        analysis = await check_blue_ocean(request.project_id)

        return {
            "message": "Proyecto procesado e indexado con éxito",
            "project_id": request.project_id,
            "chunks_processed": len(chunks),
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_folder_background(folder_id: str, access_token: str):
    print(f"================ INICIANDO TAREA DE BACKGROUND PARA FOLDER {folder_id} ================", flush=True)
    progress_store[folder_id] = {"progress": 0, "total": 100, "message": "Iniciando..."}
    try:
        files = drive_service.get_files_in_folder(folder_id, access_token)
        total = len(files)
        progress_store[folder_id] = {"progress": 0, "total": total if total > 0 else 100, "message": f"Se encontraron {total} archivos"}
        print(f"BACKGROUND TASK: Total de archivos detectados = {total}", flush=True)
        if total == 0:
            print("BACKGROUND TASK: Abortando porque no hay archivos", flush=True)
            rabbitmq_service.publish_progress(
                user_id="admin",
                type_event="sync_complete",
                progress=100,
                total=100,
                message="Carpeta vinculada (0 PDFs encontrados)."
            )
            return

        for i, file_info in enumerate(files):
            file_id = file_info.get("id")
            file_name = file_info.get("name")
            
            rabbitmq_service.publish_progress(
                user_id="admin",
                type_event="sync_progress",
                progress=i,
                total=total,
                message=f"Vectorizando {file_name}..."
            )
            
            progress_store[folder_id] = {
                "progress": i,
                "total": total,
                "message": f"Vectorizando {file_name}..."
            }
            
            try:
                text = drive_service.process_drive_file(file_id, file_name, access_token)
                if not text or not nlp_service.is_valid_project(text):
                    continue
                
                clean_text = nlp_service.strip_structure(text)
                safe_text = nlp_service.anonymize_pii(clean_text)
                
                chunks = nlp_service.chunk_text(safe_text)
                embeddings = nlp_service.vectorize(chunks)
                
                project_id = file_name.replace(".pdf", "").replace(".PDF", "").strip().lower()
                url_drive = f"https://drive.google.com/file/d/{file_id}/view"
                
                chroma_service.add_vectors(
                    project_id=project_id,
                    texts=chunks,
                    embeddings=embeddings,
                    url_drive=url_drive
                )
                print(f"✅ Vectorizado y guardado: {project_id} ({len(chunks)} chunks)", flush=True)
            except Exception as e:
                print(f"❌ Error procesando {file_name}: {e}", flush=True)
                continue
                
        rabbitmq_service.publish_progress(
            user_id="admin",
            type_event="sync_complete",
            progress=total,
            total=total,
            message="Sincronización de Océanos Azules completada."
        )
        
        progress_store[folder_id] = {
            "progress": total,
            "total": total,
            "message": "¡Sincronización completada!"
        }
        
        
    except Exception as e:
        print(f"ERROR FATAL DE SINCRONIZACIÓN: {str(e)}")
        import traceback
        traceback.print_exc()
        rabbitmq_service.publish_progress(
            user_id="admin",
            type_event="sync_error",
            progress=0,
            total=0,
            message=f"Error fatal: {str(e)}"
        )
        progress_store[folder_id] = {
            "progress": -1,
            "total": 100,
            "message": f"Error fatal: {str(e)}"
        }

@router.post("/process-folder", status_code=202)
async def process_folder(request: ProcessFolderRequest, background_tasks: BackgroundTasks):
    """
    Inicia la sincronización asíncrona de una carpeta entera de Google Drive.
    """
    try:
        import requests
        from app.core.config import settings
        
        # Validar si ya está sincronizada internamente llamando al Auth Service
        auth_url = f"{settings.AUTH_SERVICE_URL}/folders/check/{request.folder_id}"
        response = requests.get(auth_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("exists") is True:
                # Si ya existe, retornamos inmediatamente y NO iniciamos la tarea asíncrona
                return {"message": "La carpeta ya se encuentra sincronizada.", "sync_skipped": True}
                
    except Exception as e:
        print(f"Error verificando carpeta con Auth Service: {e}")
        # Si falla el servicio, continuamos con el flujo normal para no bloquear

    background_tasks.add_task(process_folder_background, request.folder_id, request.access_token)
    return {"message": "Sincronización iniciada en segundo plano.", "sync_skipped": False}

@router.get("/sync-status/{folder_id}")
async def get_sync_status(folder_id: str):
    """
    Devuelve el estado de la sincronización en progreso para el polling del móvil.
    """
    if folder_id in progress_store:
        return progress_store[folder_id]
    return {"progress": 0, "total": 100, "message": "Esperando inicialización..."}

@router.post("/process-local-project")
async def process_local_project_document(project_id: str, file: UploadFile = File(...)):
    """
    Ruta para hacer PRUEBAS LOCALES.
    Sube un PDF desde tu computadora, lo vectoriza y lo guarda en ChromaDB.
    """
    try:
        filename_lower = file.filename.lower()
        valid_extensions = ('.pdf', '.md', '.txt')
        if not filename_lower.endswith(valid_extensions):
            raise HTTPException(status_code=400, detail="El archivo debe ser PDF, MD o TXT")
            
        project_id = project_id.lower().strip()
        
        # 1. Extraer texto del archivo subido
        file_bytes = await file.read()
        
        full_text = ""
        if filename_lower.endswith('.pdf'):
            file_stream = io.BytesIO(file_bytes)
            with pdfplumber.open(file_stream) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
        else:
            # Es un archivo MD o TXT
            full_text = file_bytes.decode('utf-8')
                    
        if not full_text:
            raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF")

        # 1.5 Filtro de Seguridad y Privacidad
        if not nlp_service.is_valid_project(full_text):
            raise HTTPException(status_code=406, detail="El documento fue rechazado porque no parece ser un proyecto académico válido (Ej. Currículums, Manuales).")
            
        # Limpiar estructura ANTES de anonimizar para que los regex funcionen
        # sobre texto original (bibliografía, sección info equipo, etc.)
        clean_text = nlp_service.strip_structure(full_text)
        safe_text = nlp_service.anonymize_pii(clean_text)

        # 2. Partir el texto con Spacy
        chunks = nlp_service.chunk_text(safe_text)
        
        # 3. Vectorizar con Sentence-Transformers
        embeddings = nlp_service.vectorize(chunks)

        # 4. Obtener el historial existente (para comparar SIN guardar la prueba)
        all_data = chroma_service.get_all_embeddings()
        db_embeddings = all_data.get("embeddings")
        db_metadatas = all_data.get("metadatas")
        db_documents = all_data.get("documents")

        if db_embeddings is None or len(db_embeddings) == 0:
            raise HTTPException(status_code=404, detail="No hay historial en la base de datos para comparar.")

        # Reconstruir el historial agrupando por proyecto
        projects_texts = {}
        projects_embeddings = {}
        for i, meta in enumerate(db_metadatas):
            p_id = meta["project_id"]
            if p_id not in projects_texts:
                projects_texts[p_id] = ""
                projects_embeddings[p_id] = []
            projects_texts[p_id] += db_documents[i] + " "
            projects_embeddings[p_id].append(db_embeddings[i])

        history_names = []
        history_texts = []
        history_embeddings = []
        for p_id, text in projects_texts.items():
            history_names.append(p_id)
            history_texts.append(text)
            history_embeddings.append(np.mean(projects_embeddings[p_id], axis=0).tolist())

        # 5. Ejecutar análisis automático de Océano Azul SIN GUARDAR EN BD
        new_project_text = " ".join(chunks)
        new_project_embedding = np.mean(embeddings, axis=0).tolist()
        
        analysis = cluster_logic.find_blue_oceans_hybrid(
            new_project_text=new_project_text,
            existing_texts=history_texts,
            new_project_embedding=new_project_embedding,
            existing_embeddings=history_embeddings,
            existing_names=history_names
        )
        
        analysis["project_id"] = project_id

        return {
            "message": "PDF de prueba analizado con éxito (No se guardó en la base de datos)",
            "project_id": project_id,
            "chunks_processed": len(chunks),
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blue-ocean/{project_id}")
async def check_blue_ocean(project_id: str):
    """
    Verifica si un proyecto es un 'Océano Azul' calculando su distancia
    contra el historial de proyectos usando Scikit-Learn.
    """
    try:
        # Extraemos TODOS los vectores y DOCUMENTOS (texto puro) de ChromaDB
        all_data = chroma_service.get_all_embeddings()
        embeddings = all_data.get("embeddings")
        metadatas = all_data.get("metadatas")
        documents = all_data.get("documents")

        if embeddings is None or len(embeddings) == 0:
            raise HTTPException(status_code=404, detail="No hay historial de proyectos para comparar.")

        # 1. Agrupar fragmentos por proyecto (Texto e IDs)
        # Necesitamos reconstruir el texto completo de cada proyecto para el TF-IDF
        # y promediar los embeddings para la Búsqueda Semántica
        projects_texts = {}
        projects_embeddings = {}
        
        for i, meta in enumerate(metadatas):
            p_id = meta["project_id"]
            if p_id not in projects_texts:
                projects_texts[p_id] = ""
                projects_embeddings[p_id] = []
            
            # Juntamos los fragmentos de texto
            projects_texts[p_id] += documents[i] + " "
            # Juntamos los vectores
            projects_embeddings[p_id].append(embeddings[i])

        if project_id not in projects_texts:
            raise HTTPException(status_code=404, detail="404: El proyecto no ha sido procesado aún. Mándalo a minería primero.")

        new_project_text = projects_texts[project_id]
        new_project_embedding = np.mean(projects_embeddings[project_id], axis=0).tolist()
        
        # Filtramos el historial (todo menos el proyecto actual)
        history_names = []
        history_texts = []
        history_embeddings = []
        
        for p_id, text in projects_texts.items():
            if p_id != project_id:
                history_names.append(p_id)
                history_texts.append(text)
                # El vector del historial es el promedio de todos sus fragmentos
                history_embeddings.append(np.mean(projects_embeddings[p_id], axis=0).tolist())

        # 2. Correr la lógica de Océanos Azules usando Motor Híbrido (Denso + TF-IDF)
        result = cluster_logic.find_blue_oceans_hybrid(
            new_project_text=new_project_text,
            existing_texts=history_texts,
            new_project_embedding=new_project_embedding,
            existing_embeddings=history_embeddings,
            existing_names=history_names
            # Sin threshold fijo: cluster_logic usa umbral dinámico por percentil
        )

        # Agregamos el ID para claridad en el Frontend
        result["project_id"] = project_id
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blue-ocean-niches")
async def get_blue_ocean_niches():
    """
    Retorna una lista de nichos de mercado u 'Océanos Azules' inexplorados 
    basado en el análisis global de los proyectos (leído desde unexplored_topics.json).
    """
    import json
    from pathlib import Path
    
    niches = []
    try:
        model_dir = Path(__file__).resolve().parent.parent / "models"
        topics_path = model_dir / "unexplored_topics.json"
        
        if topics_path.exists():
            with open(topics_path, "r", encoding="utf-8") as f:
                topics = json.load(f)
                
            for t in topics:
                niches.append({
                    "category": "INNOVACIÓN DETECTADA",
                    "tag": "Área Inexplorada",
                    "title": t,
                    "description": "Área de oportunidad identificada matemáticamente a través de los vacíos en el grafo topológico HDBSCAN."
                })
    except Exception as e:
        print(f"Error cargando unexplored_topics.json en routes: {e}")
        
    # Fallback si falla o está vacío
    if not niches:
        niches = [
            {
                "category": "IA & Sostenibilidad",
                "tag": "Alto Potencial",
                "title": "IA en Agricultura de Precisión",
                "description": "Optimización de recursos hídricos y predicción de cosechas mediante modelos de RAG alimentados por datos climáticos en tiempo real y sensores IoT."
            },
            {
                "category": "Logística & Supply Chain",
                "tag": "Innovación",
                "title": "Logística Circular",
                "description": "Rediseño de cadenas de suministro para eliminar residuos, utilizando blockchain para trazabilidad de materiales reciclados."
            },
            {
                "category": "BIOTECH",
                "tag": "Futurista",
                "title": "Biomateriales de Construcción",
                "description": "Desarrollo de estructuras vivas y auto-reparables utilizando micelio fúngico integrado en arquitecturas modulares."
            },
            {
                "category": "FINTECH & QUANTUM",
                "tag": "Novedad Alta",
                "title": "Computación Cuántica en Finanzas",
                "description": "Modelado de riesgos hiper-complejos y optimización de carteras utilizando algoritmos cuánticos híbridos."
            }
        ]

    return {
        "title": "Temas Inexplorados",
        "description": "Descubre océanos azules en la intersección de la tecnología y la sociedad. Selecciona un área de innovación para comenzar tu investigación.",
        "niches": niches
    }
