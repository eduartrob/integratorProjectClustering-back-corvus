import asyncio
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks, Form
from pydantic import BaseModel
from typing import List
import fitz
import pymupdf4llm
import io
import os
import json
import numpy as np

from app.services.drive_service import drive_service
from app.services.nlp_service import nlp_service
from app.services.chroma_service import chroma_service
from app.services.cluster_logic import cluster_logic
from app.services.rabbitmq_service import rabbitmq_service
from app.services.llm_client import llm_client as ollama_service
from app.services.inference_log_service import log_inference, get_history

router = APIRouter()

progress_store = {}
analysis_progress_store = {}
analysis_result_store = {}
active_analysis_tasks = {}
analysis_lock = asyncio.Lock()

_MANDATORY_SECTIONS = [
    {
        "name": "Metas u Objetivos",
        "keywords": ["objetivo", "objetivos", "propósito", "metas", "visión", "misión", "qué buscamos", "solución propuesta", "propuesta de valor", "optimización"],
    },
    {
        "name": "Justificación o Problemática",
        "keywords": ["justificación", "justificacion", "problemática", "problematica", "planteamiento del problema", "contexto", "necesidad", "situación actual", "por qué", "descripción del proyecto", "descripcion"],
    },
    {
        "name": "Alcance o Requerimientos Técnicos",
        "keywords": ["alcance", "funcionalidades", "entregables", "límites", "requerimientos", "requisitos", "casos de uso", "arquitectura", "diseño del sistema", "variables", "entradas", "salidas", "datos", "dataset", "base de conocimientos", "modelo"],
    },
]

_OPTIONAL_SECTIONS = [
    {"name": "Objetivos Específicos",  "keywords": ["objetivos específicos", "objetivos especificos"], "points": 15},
    {"name": "Introducción",           "keywords": ["introducción", "introduccion"],                  "points": 10},
    {"name": "Metodología",            "keywords": ["metodología", "metodologia"],                    "points": 10},
    {"name": "Stack / Tecnologías",    "keywords": ["tecnologías", "tecnologias", "stack tecnológico", "lista de tecnologías"], "points": 10},
    {"name": "Usuarios Finales",       "keywords": ["usuarios finales", "usuario final"],              "points": 10},
    {"name": "Resumen o Abstract",     "keywords": ["resumen", "abstract"],                           "points":  5},
    {"name": "Categoría / Área",       "keywords": ["categoría", "categoria", "área", "area"],        "points":  5},
    {"name": "Bibliografía",           "keywords": ["bibliografía", "bibliografia", "referencias"],   "points":  5},
]

def _validate_project_sections(text: str) -> dict:
    
    t = text.lower()
    missing_mandatory = []
    for section in _MANDATORY_SECTIONS:
        if not any(kw in t for kw in section["keywords"]):
            missing_mandatory.append(section["name"])

    optional_score = 0
    found_optional = []
    for section in _OPTIONAL_SECTIONS:
        if any(kw in t for kw in section["keywords"]):
            optional_score += section["points"]
            found_optional.append(section["name"])

    return {
        "ok": len(missing_mandatory) == 0,
        "missing_mandatory": missing_mandatory,
        "optional_score": min(optional_score, 70),
        "found_optional": found_optional,
    }

class ProcessFolderRequest(BaseModel):
    folder_id: str
    access_token: str
    user_id: str

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "integratorProjectClustering"}

def process_folder_background(folder_id: str, access_token: str, user_id: str):
    print(f"================ INICIANDO TAREA DE BACKGROUND PARA FOLDER {folder_id} ================", flush=True)
    progress_store[folder_id] = {"progress": 0, "total": 100, "message": "Iniciando..."}
    try:
        files = drive_service.get_files_in_folder(folder_id, access_token)
        total_files = len(files)
        total_progress = total_files * 100 if total_files > 0 else 100
        
        progress_store[folder_id] = {"progress": 0, "total": total_progress, "message": f"Se encontraron {total_files} archivos"}
        print(f"BACKGROUND TASK: Total de archivos detectados = {total_files}", flush=True)
        if total_files == 0:
            print("BACKGROUND TASK: Abortando porque no hay archivos", flush=True)
            rabbitmq_service.publish_progress(
                user_id=user_id,
                type_event="sync_complete",
                progress=100,
                total=100,
                message="Carpeta vinculada (0 PDFs encontrados)."
            )
            return

        for i, file_info in enumerate(files):
            file_id = file_info.get("id")
            file_name = file_info.get("name")
            base_progress = i * 100
            
            progress_store[folder_id] = {
                "progress": base_progress + 5,
                "total": total_progress,
                "message": f"[{i+1}/{total_files}] Descargando {file_name}..."
            }
            
            try:
                text = drive_service.process_drive_file(file_id, file_name, access_token)
                if not text or not nlp_service.is_valid_project(text):
                    continue
                
                clean_text = nlp_service.strip_structure(text)
                safe_text = nlp_service.anonymize_pii(clean_text)
                chunks = nlp_service.chunk_text(safe_text)
                total_chunks = len(chunks)
                
                embeddings = []
                batch_size = 3
                for j in range(0, total_chunks, batch_size):
                    batch = chunks[j:j+batch_size]
                    
                    fraction = (j / total_chunks) if total_chunks > 0 else 1
                    sub_progress = int(10 + (fraction * 80))
                    
                    progress_store[folder_id] = {
                        "progress": base_progress + sub_progress,
                        "total": total_progress,
                        "message": f"[{i+1}/{total_files}] Vectorizando: {j}/{total_chunks} fragmentos"
                    }
                    
                    batch_embeddings = nlp_service.vectorize(batch)
                    embeddings.extend(batch_embeddings)
                
                
                progress_store[folder_id] = {
                    "progress": base_progress + 95,
                    "total": total_progress,
                    "message": f"[{i+1}/{total_files}] Guardando proyecto en BD..."
                }
                
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
                
        progress_store[folder_id] = {
            "progress": total_progress,
            "total": total_progress,
            "message": "¡Sincronización completada!"
        }
        
        rabbitmq_service.publish_progress(
            user_id=user_id,
            type_event="sync_complete",
            progress=total_progress,
            total=total_progress,
            message="¡Archivos sincronizados y vectorizados en Corvus!"
        )
        
        
    except Exception as e:
        print(f"ERROR FATAL DE SINCRONIZACIÓN: {str(e)}")
        import traceback
        traceback.print_exc()
        rabbitmq_service.publish_progress(
            user_id=user_id,
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
    
    try:
        import requests
        from app.core.config import settings
        
        auth_url = f"{settings.AUTH_SERVICE_URL}/folders/check/{request.folder_id}"
        response = requests.get(auth_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("exists") is True:
                return {"message": "La carpeta ya se encuentra sincronizada.", "sync_skipped": True}
                
    except Exception as e:
        print(f"Error verificando carpeta con Auth Service: {e}")

    background_tasks.add_task(process_folder_background, request.folder_id, request.access_token, request.user_id)
    return {"message": "Sincronización iniciada en segundo plano.", "sync_skipped": False}

@router.get("/sync-status/{folder_id}")
async def get_sync_status(folder_id: str):
    
    if folder_id in progress_store:
        return progress_store[folder_id]
    return {"progress": 0, "total": 100, "message": "Esperando inicialización..."}

@router.get("/blue-ocean/{project_id}")
async def check_blue_ocean(project_id: str):
    
    try:
        all_data = chroma_service.get_all_embeddings()
        embeddings = all_data.get("embeddings")
        metadatas = all_data.get("metadatas")
        documents = all_data.get("documents")

        if embeddings is None or len(embeddings) == 0:
            raise HTTPException(status_code=404, detail="No hay historial de proyectos para comparar.")

        projects_texts = {}
        projects_embeddings = {}
        
        for i, meta in enumerate(metadatas):
            p_id = meta["project_id"]
            if p_id not in projects_texts:
                projects_texts[p_id] = ""
                projects_embeddings[p_id] = []
            
            projects_texts[p_id] += documents[i] + " "
            projects_embeddings[p_id].append(embeddings[i])

        if project_id not in projects_texts:
            raise HTTPException(status_code=404, detail="404: El proyecto no ha sido procesado aún. Mándalo a minería primero.")

        new_project_text = projects_texts[project_id]
        new_project_embedding = np.mean(projects_embeddings[project_id], axis=0).tolist()
        
        history_names = []
        history_texts = []
        history_embeddings = []
        
        for p_id, text in projects_texts.items():
            if p_id != project_id:
                history_names.append(p_id)
                history_texts.append(text)
                history_embeddings.append(np.mean(projects_embeddings[p_id], axis=0).tolist())

        result = cluster_logic.find_blue_oceans_hybrid(
            new_project_text=new_project_text,
            existing_texts=history_texts,
            new_project_embedding=new_project_embedding,
            existing_embeddings=history_embeddings,
            existing_names=history_names
        )

        result["project_id"] = project_id
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blue-ocean-niches")
async def get_blue_ocean_niches():
    
    from app.services.chroma_service import chroma_service
    from app.services.blue_ocean_db import blue_ocean_db
    import time

    
    niches = []
    try:
        results = chroma_service.collection.get(include=["metadatas"])
        
        unique_projects = {}
        if results and results.get('metadatas'):
            for meta in results['metadatas']:
                if meta and meta.get('is_blue_ocean'):
                    p_id = meta.get('project_id')
                    if p_id and p_id not in unique_projects:
                        unique_projects[p_id] = meta
        
        for p_id, meta in unique_projects.items():
            name = p_id.replace('proyecto_', '').replace('.md', '').replace('.pdf', '').replace('_', ' ').title()
            
            blue_ocean_db.register_niche_if_not_exists(p_id)
            niche_state = blue_ocean_db.get_niche(p_id)
            
            hours_since_creation = (time.time() - niche_state.get('created_at', time.time())) / 3600.0
            views = niche_state.get('view_count', 0)
            gravity_score = (views + 1) / ((hours_since_creation + 2) ** 1.5)
            
            niches.append({
                "id": p_id,
                "category": "INNOVACIÓN ACADÉMICA",
                "tag": "Océano Azul Real",
                "title": name,
                "description": "Este proyecto ha sido clasificado como una anomalía semántica de alta varianza, indicando un enfoque único e inexplorado respecto a todos los demás trabajos en la base de datos.",
                "view_count": views,
                "recent_viewers": niche_state.get('recent_viewers', []),
                "analysis_status": niche_state.get('analysis_status', 'pending'),
                "_gravity_score": gravity_score
            })
            
        niches.sort(key=lambda x: x['_gravity_score'], reverse=True)
        
        for niche in niches:
            niche.pop('_gravity_score', None)
            
    except Exception as e:
        print(f"Error extrayendo los océanos azules desde ChromaDB: {e}")
        
    if not niches:
        niches = [
            {
                "category": "MÉTRICA VACÍA",
                "tag": "Requiere Ejecución",
                "title": "Aún no hay Océanos Azules",
                "description": "El algoritmo de clustering global aún no ha detectado proyectos con suficiente originalidad semántica o se requiere ejecutar un análisis con un mayor volumen de documentos."
            }
        ]

    return {
        "title": "Océanos Azules (Proyectos Reales)",
        "description": "Descubre los verdaderos océanos azules en la intersección de la tecnología y la academia, calculados en tiempo real por Corvus HDBSCAN.",
        "niches": niches
    }

from pydantic import BaseModel

class NicheViewRequest(BaseModel):
    user_avatar: str = None

@router.post("/blue-ocean-niches/{niche_id}/view")
async def track_niche_view(niche_id: str, payload: NicheViewRequest):
    
    from app.services.blue_ocean_db import blue_ocean_db
    
    niche_state = blue_ocean_db.track_view(niche_id, payload.user_avatar)
    
    return {
        "status": "success",
        "niche_id": niche_id,
        "view_count": niche_state.get("view_count", 0),
        "analysis_status": niche_state.get("analysis_status"),
        "analysis_data": niche_state.get("analysis_data")
    }

from fastapi import Header

@router.post("/populate-from-local-folder")
async def populate_from_local_folder(x_api_key: str = Header(default=None)):
    
    import os
    from pathlib import Path
    
    projects_dir = Path(__file__).resolve().parent.parent.parent / "projectsTests"
    
    if x_api_key != "admin-corvus-123":
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere clave de administrador para evitar el envenenamiento de datos.")
    
    if not projects_dir.exists() or not projects_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"No se encontró la carpeta: {projects_dir}")
        
    results = []
    
    for filename in os.listdir(projects_dir):
        if not filename.lower().endswith(('.pdf', '.md', '.txt')):
            continue
            
        file_path = projects_dir / filename
        project_id = filename.lower().replace('.pdf', '').replace('.txt', '').replace('.md', '')
        
        try:
            full_text = ""
            if filename.lower().endswith('.pdf'):
                doc = fitz.open(file_path)
                full_text = pymupdf4llm.to_markdown(doc)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    full_text = f.read()
                    
            if not full_text:
                results.append({"file": filename, "status": "error", "message": "Texto vacío"})
                continue
                
            clean_text = nlp_service.strip_structure(full_text)
            safe_text = nlp_service.anonymize_pii(clean_text)
            
            chunks = nlp_service.chunk_text(safe_text)
            embeddings = nlp_service.vectorize(chunks)
            
            if embeddings is None or len(embeddings) == 0:
                results.append({"file": filename, "status": "error", "message": "Fallo vectorización"})
                continue
                
            chroma_service.add_vectors(
                project_id=project_id,
                texts=chunks,
                embeddings=embeddings,
                url_drive=f"local://projectsTests/{filename}"
            )
            
            results.append({"file": filename, "status": "success", "chunks": len(chunks)})
        except Exception as e:
            results.append({"file": filename, "status": "error", "message": str(e)})
            
    return {
        "message": "Procesamiento de carpeta finalizado",
        "total_archivos_intentados": len(results),
        "resultados": results
    }

DRAFTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "drafts")
os.makedirs(DRAFTS_DIR, exist_ok=True)

@router.post("/pre-validate-proposal")
async def pre_validate_proposal(user_id: str = Form(...), file: UploadFile = File(...)):
    
    try:
        filename_lower = file.filename.lower()
        if not filename_lower.endswith(('.pdf', '.md', '.txt')):
            raise HTTPException(status_code=400, detail="El archivo debe ser PDF, MD o TXT")
            
        file_bytes = await file.read()
        full_text = ""
        if filename_lower.endswith('.pdf'):
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            full_text = pymupdf4llm.to_markdown(doc)
        else:
            full_text = file_bytes.decode('utf-8')
                    
        if not full_text or len(full_text.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="El documento no parece ser una propuesta de proyecto integrador. No se pudo extraer texto (podría ser un documento escaneado o contener muy poco texto)."
            )

        if not nlp_service.is_valid_project(full_text):
            raise HTTPException(
                status_code=400,
                detail="Este documento no parece ser una propuesta de proyecto tecnológico o de software. Por favor, sube el documento correcto."
            )

        section_check = _validate_project_sections(full_text)
        if not section_check["ok"]:
            missing = ", ".join(f"'{s}'" for s in section_check["missing_mandatory"])
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Tu propuesta es válida, pero olvidaste incluir información sobre: {missing}. "
                    f"Asegúrate de explicar tus objetivos, el problema que resuelves y los requerimientos técnicos."
                )
            )

        if nlp_service.detect_prompt_injection(full_text):
            raise HTTPException(status_code=403, detail="ALERTA: Se detectó un intento de inyección de prompt.")

        clean_text = nlp_service.strip_structure(full_text)
        clean_text = nlp_service.normalize_homoglyphs(clean_text)
        safe_text = nlp_service.anonymize_pii(clean_text)

        chunks = nlp_service.chunk_text(safe_text)
        embeddings = nlp_service.vectorize(chunks)
        
        if embeddings is None or len(embeddings) == 0:
            raise HTTPException(status_code=400, detail="El documento no tiene contenido suficiente.")
        
        query_subset = embeddings[:5] if len(embeddings) > 5 else embeddings
        search_results = chroma_service.search_similar_multi(query_embeddings=query_subset, n_results=3)
        
        max_similitud_pct = 0.0
        similar_projects = []
        if search_results and "documents" in search_results and search_results["documents"]:
            grouped_projects = {}
            for q_idx in range(len(search_results["documents"])):
                docs = search_results["documents"][q_idx]
                metas = search_results["metadatas"][q_idx]
                distances = search_results["distances"][q_idx] if "distances" in search_results else [0]*len(docs)
                
                for doc, meta, dist in zip(docs, metas, distances):
                    p_id = meta.get("project_id", "Desconocido")
                    if p_id not in grouped_projects:
                        grouped_projects[p_id] = {"chunks": [], "min_distance": float('inf')}
                    if doc not in grouped_projects[p_id]["chunks"]:
                        grouped_projects[p_id]["chunks"].append(doc)
                    if dist < grouped_projects[p_id]["min_distance"]:
                        grouped_projects[p_id]["min_distance"] = dist
            
            sorted_projects = sorted(grouped_projects.items(), key=lambda x: x[1]["min_distance"])[:3]
            for p_id, p_data in sorted_projects:
                dist = p_data["min_distance"]
                sim_factor = 1.0 - (dist / 0.4)
                similitud_pct = max(0, min(100, sim_factor * 100))
                if similitud_pct > max_similitud_pct:
                    max_similitud_pct = similitud_pct
                similar_projects.append({
                    "title": p_id.upper(),
                    "content": " ".join(p_data["chunks"][:3]),
                    "similarity_pct": similitud_pct
                })

        words_count = len(full_text.split())
        academic_alignment = 10
        areas_of_improvement = []
        positive_feedback = []
        
        text_lower = full_text.lower()
        
        if words_count >= 500:
            academic_alignment += 20
            positive_feedback.append("Formato adecuado. La longitud del documento es óptima para una propuesta inicial.")
        else:
            areas_of_improvement.append("El documento tiene menos de 500 palabras. Te sugerimos expandir tu marco teórico y estado del arte.")
            
        has_intro = "introducción" in text_lower or "introduccion" in text_lower
        has_method = "metodología" in text_lower or "metodologia" in text_lower
        has_biblio = "bibliografía" in text_lower or "referencias" in text_lower
        
        if has_intro and has_method and has_biblio:
            academic_alignment += 30
            positive_feedback.append("Estructura impecable. Las secciones clave (Introducción, Metodología, Bibliografía) están presentes.")
            
        if not ("conclusiones" in text_lower or "resultados esperados" in text_lower):
            areas_of_improvement.append("No se detectó un apartado de 'Conclusiones' o 'Resultados esperados'.")
            
        if not ("resumen" in text_lower or "abstract" in text_lower):
            areas_of_improvement.append("Falta el 'Resumen' o 'Abstract' al inicio de tu documento.")
            
        if not ("objetivo" in text_lower):
            areas_of_improvement.append("No se encontró una sección explícita de 'Objetivos'. Recuerda definir tu Objetivo General y Específicos.")
        else:
            academic_alignment += 20
            
        if has_biblio:
            academic_alignment += 20
        else:
            areas_of_improvement.append("No se detectó la sección de 'Bibliografía'. Una propuesta sin sustento teórico puede ser rechazada.")
            
        import re
        citas = re.findall(r'\[\d+\]|\(\w+,\s*\d{4}\)', full_text)
        if len(citas) < 2 and not has_biblio:
            areas_of_improvement.append("Se detectaron pocas menciones bibliográficas en el texto. Recuerda citar tus fuentes (APA/IEEE) en el marco teórico.")

        collision_risk_level = "Bajo"
        
        if max_similitud_pct > 50:
            collision_risk_level = "Alto"
            top_project = similar_projects[0]["title"].replace("PROYECTO_", "") if similar_projects else "otro proyecto"
            areas_of_improvement.insert(0, f"Riesgo de colisión alto ({round(max_similitud_pct)}%). La idea central coincide fuertemente con el proyecto '{top_project}' de la generación anterior. ¡Cuidado con el plagio!")
        elif max_similitud_pct > 20:
            collision_risk_level = "Medio"
            top_project = similar_projects[0]["title"].replace("PROYECTO_", "") if similar_projects else "otro proyecto"
            areas_of_improvement.insert(0, f"Similitud moderada. Tu proyecto comparte tecnologías o metodologías con el proyecto '{top_project}' del semestre pasado. Asegúrate de destacar tu diferenciador.")
        else:
            collision_risk_level = "Bajo"
            if max_similitud_pct < 5:
                positive_feedback.insert(0, "Originalidad alta. No se encontraron proyectos similares en el repositorio histórico de la universidad.")
            else:
                positive_feedback.insert(0, "¡Excelente planteamiento! Tu propuesta tecnológica parece única frente a generaciones anteriores.")

        quick_analysis = {
            "status": "success",
            "academic_alignment": min(100, academic_alignment),
            "collision_risk_pct": round(max_similitud_pct, 1),
            "collision_risk_level": collision_risk_level,
            "positive_feedback": positive_feedback,
            "areas_of_improvement": areas_of_improvement
        }

        try:
            log_inference(
                user_id=user_id,
                filename=file.filename,
                score_colision=max_similitud_pct,
                nivel_riesgo=collision_risk_level,
                academic_alignment=min(100, academic_alignment),
                secciones_opcionales=section_check.get("found_optional", []),
            )
        except Exception as log_err:
            print(f"[WARN] No se pudo guardar en inference_log: {log_err}")

        draft_path = os.path.join(DRAFTS_DIR, f"{user_id}_draft.json")
        draft_data = {
            "chunks": chunks,
            "similar_projects": similar_projects,
            "quick_analysis": quick_analysis
        }
        with open(draft_path, "w", encoding="utf-8") as f:
            json.dump(draft_data, f, ensure_ascii=False)

        return quick_analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inference-history")
async def inference_history(limit: int = 50, offset: int = 0):
    
    return get_history(limit=limit, offset=offset)

@router.get("/draft-proposal/{user_id}")
async def get_draft_proposal(user_id: str):
    draft_path = os.path.join(DRAFTS_DIR, f"{user_id}_draft.json")
    if os.path.exists(draft_path):
        try:
            with open(draft_path, "r", encoding="utf-8") as f:
                draft_data = json.load(f)
            return draft_data.get("quick_analysis", {})
        except:
            return {"status": "not_found"}
    return {"status": "not_found"}

@router.get("/analysis-status/{user_id}")
async def get_analysis_status(user_id: str):
    
    if user_id in analysis_progress_store:
        return analysis_progress_store[user_id]
    return {"phase": 1, "message": "Procesando propuesta..."}

async def _run_analysis_background(user_id: str, draft_path: str):
    
    try:
        active_analysis_tasks[user_id] = asyncio.current_task()
        
        if analysis_lock.locked():
            analysis_progress_store[user_id] = {
                "phase": 5,
                "message": "En cola de espera: Hay otro análisis de IA en curso. Tu turno comenzará en un momento..."
            }

        async with analysis_lock:
            analysis_progress_store[user_id] = {"phase": 5, "message": "Calculando riesgo de colisión..."}

            with open(draft_path, "r", encoding="utf-8") as f:
                draft_data = json.load(f)

            chunks = draft_data.get("chunks", [])
            similar_projects = draft_data.get("similar_projects", [])
            quick_analysis = draft_data.get("quick_analysis", {})

            full_proposal_text = " ".join(chunks)
            proposal_text = full_proposal_text[:12000] if len(full_proposal_text) > 12000 else full_proposal_text

            max_sim_pct = quick_analysis.get("collision_risk_pct", 0.0)
            top_project_name = similar_projects[0]["title"] if similar_projects else "Ninguno"
            risk_level = "Alto" if max_sim_pct > 50 else ("Medio" if max_sim_pct > 20 else "Bajo")

            if not ollama_service.check_health():
                analysis_result_store[user_id] = {
                    "status": "warning",
                    "message": "El motor de IA no está disponible en este momento.",
                    "similar_projects": [p["title"] for p in similar_projects]
                }
                analysis_progress_store[user_id] = {"phase": -1, "message": "El motor de IA no está disponible."}
                return

            analysis_progress_store[user_id] = {"phase": 6, "message": "El comité académico está redactando el dictamen..."}

            await asyncio.sleep(0)
            llm_verdict = await asyncio.to_thread(
                ollama_service.analyze_originality,
                proposal_text=proposal_text,
                similar_projects=similar_projects,
                max_sim_pct=round(max_sim_pct, 1),
                risk_level=risk_level,
                project_name="PROPUESTA_DEL_ALUMNO",
                top_project_name=top_project_name,
            )

            analysis_progress_store[user_id] = {"phase": 7, "message": "Generando recomendaciones técnicas..."}

            analysis_progress_store[user_id] = {"phase": 7, "message": "Generando recomendaciones técnicas..."}

            analysis_progress_store[user_id] = {"phase": 8, "message": "Afinando veredicto final..."}

            final_result = {
                "status": "success",
                "message": "Análisis completado con Llama 3.2 3B",
                "similar_projects_found": len(similar_projects),
                "ollama_analysis": llm_verdict
            }
            analysis_result_store[user_id] = final_result
            analysis_progress_store[user_id] = {"phase": 9, "message": "Análisis completado. Recuperando resultado..."}

    except asyncio.CancelledError:
        print(f"BACKGROUND TASK: Análisis para {user_id} cancelado explícitamente.")
        analysis_progress_store.pop(user_id, None)
        analysis_result_store.pop(user_id, None)
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        analysis_progress_store[user_id] = {"phase": -1, "message": f"Error en el análisis: {str(e)}"}
    finally:
        active_analysis_tasks.pop(user_id, None)

@router.post("/analyze-draft-proposal")
async def analyze_draft_proposal(user_id: str = Form(...)):
    
    draft_path = os.path.join(DRAFTS_DIR, f"{user_id}_draft.json")
    if not os.path.exists(draft_path):
        raise HTTPException(status_code=404, detail="No se encontró borrador para este usuario.")

    analysis_result_store.pop(user_id, None)
    analysis_progress_store[user_id] = {"phase": 5, "message": "Iniciando análisis en segundo plano..."}

    asyncio.create_task(_run_analysis_background(user_id, draft_path))

    return {
        "status": "queued",
        "message": "Análisis iniciado en segundo plano. Usa /analysis-status/{user_id} para seguir el progreso."
    }

@router.get("/analysis-result/{user_id}")
async def get_analysis_result(user_id: str):
    
    if user_id in analysis_result_store:
        result = analysis_result_store.pop(user_id)
        analysis_progress_store.pop(user_id, None)
        
        draft_path = os.path.join(DRAFTS_DIR, f"{user_id}_draft.json")
        try:
            if os.path.exists(draft_path):
                os.remove(draft_path)
        except Exception:
            pass
            
        return result

    phase_info = analysis_progress_store.get(user_id, {})
    if phase_info.get("phase") == -1:
        return {"status": "error", "message": phase_info.get("message", "Error desconocido en el análisis.")}

    return {"status": "pending", "message": "El análisis aún está en progreso."}

@router.post("/cancel-analysis/{user_id}")
async def cancel_analysis(user_id: str):
    
    task = active_analysis_tasks.get(user_id)
    if task and not task.done():
        task.cancel()
        
    analysis_progress_store.pop(user_id, None)
    analysis_result_store.pop(user_id, None)
    
    draft_path = os.path.join(DRAFTS_DIR, f"{user_id}_draft.json")
    try:
        if os.path.exists(draft_path):
            os.remove(draft_path)
    except Exception:
        pass
        
    return {"status": "success", "message": "Análisis cancelado exitosamente."}

@router.post("/analyze-proposal-phi3")
async def analyze_proposal_phi3(file: UploadFile = File(...)):
    
    try:
        filename_lower = file.filename.lower()
        if not filename_lower.endswith(('.pdf', '.md', '.txt')):
            raise HTTPException(status_code=400, detail="El archivo debe ser PDF, MD o TXT")
            
        file_bytes = await file.read()
        full_text = ""
        if filename_lower.endswith('.pdf'):
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            full_text = pymupdf4llm.to_markdown(doc)
        else:
            full_text = file_bytes.decode('utf-8')
                    
        if not full_text:
            raise HTTPException(status_code=400, detail="No se pudo extraer texto del documento.")

        if not nlp_service.is_valid_project(full_text):
            raise HTTPException(
                status_code=400,
                detail="Este documento no parece ser una propuesta de proyecto tecnológico o de software. Por favor, sube el documento correcto."
            )

        section_check = _validate_project_sections(full_text)
        if not section_check["ok"]:
            missing = ", ".join(f"'{s}'" for s in section_check["missing_mandatory"])
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Tu propuesta es válida, pero olvidaste incluir información sobre: {missing}. "
                    f"Asegúrate de explicar tus objetivos, el problema que resuelves y los requerimientos técnicos."
                )
            )

        if nlp_service.detect_prompt_injection(full_text):
            raise HTTPException(status_code=403, detail="ALERTA: Se detectó un intento de inyección de prompt (Prompt Injection). El documento ha sido rechazado.")

        clean_text = nlp_service.strip_structure(full_text)
        
        clean_text = nlp_service.normalize_homoglyphs(clean_text)
        
        safe_text = nlp_service.anonymize_pii(clean_text)

        chunks = nlp_service.chunk_text(safe_text)
        embeddings = nlp_service.vectorize(chunks)
        
        if embeddings is None or len(embeddings) == 0:
            raise HTTPException(status_code=400, detail="El documento no tiene contenido suficiente para vectorizar.")
        
        query_subset = embeddings[:5] if len(embeddings) > 5 else embeddings
        
        search_results = chroma_service.search_similar_multi(query_embeddings=query_subset, n_results=3)
        
        similar_projects = []
        if search_results and "documents" in search_results and search_results["documents"]:
            grouped_projects = {}
            for q_idx in range(len(search_results["documents"])):
                docs = search_results["documents"][q_idx]
                metas = search_results["metadatas"][q_idx]
                distances = search_results["distances"][q_idx] if "distances" in search_results else [0]*len(docs)
                
                for doc, meta, dist in zip(docs, metas, distances):
                    p_id = meta.get("project_id", "Desconocido")
                    if p_id not in grouped_projects:
                        grouped_projects[p_id] = {"chunks": [], "min_distance": float('inf')}
                    if doc not in grouped_projects[p_id]["chunks"]:
                        grouped_projects[p_id]["chunks"].append(doc)
                    if dist < grouped_projects[p_id]["min_distance"]:
                        grouped_projects[p_id]["min_distance"] = dist
                
            sorted_projects = sorted(grouped_projects.items(), key=lambda x: x[1]["min_distance"])[:3]
            
            for p_id, p_data in sorted_projects:
                dist = p_data["min_distance"]
                similitud_pct = max(0, min(100, (1.0 - dist) * 100))
                
                similar_projects.append({
                    "title": p_id.upper(),
                    "content": " ".join(p_data["chunks"][:3]),
                    "similarity_pct": similitud_pct
                })

        proposal_text = " ".join(chunks)
        
        import asyncio
        is_healthy = await asyncio.to_thread(ollama_service.check_health)
        if not is_healthy:
             return {
                 "status": "warning",
                 "message": "Pipeline completado hasta Fase 4. El microservicio de LLM no está respondiendo.",
                 "similar_projects": [p["title"] for p in similar_projects]
             }

        llm_verdict = await asyncio.to_thread(
            ollama_service.analyze_originality,
            proposal_text=proposal_text,
            similar_projects=similar_projects
        )

        return {
            "status": "success",
            "message": "Análisis completado con Phi-3 Mini",
            "similar_projects_found": len(similar_projects),
            "ollama_analysis": llm_verdict
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
