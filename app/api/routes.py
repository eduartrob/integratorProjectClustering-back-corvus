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
import httpx

from app.services.drive_service import drive_service
from app.services.nlp_service import nlp_service
from app.services.qdrant_service import qdrant_service
from app.services.clustering_service import clustering_engine
from app.services.rabbitmq_service import rabbitmq_service
from app.services.llm_client import llm_client as ollama_service
from app.services.inference_log_service import log_inference, get_history

router = APIRouter()

progress_store = {}
analysis_progress_store = {}
analysis_result_store = {}
active_analysis_tasks = {}
analysis_lock = asyncio.Lock()

# Las secciones de validación y la blacklist ahora viven en nlp_service.py
# (validar_secciones_profesor, validar_blacklist_extendida, validar_coherencia_semantica)

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
            base_progress = int((i / total_files) * 100)
            
            progress_store[folder_id] = {
                "progress": base_progress,
                "total": 100,
                "message": f"[{i+1}/{total_files}] Detectando y extrayendo texto de {file_name}..."
            }
            
            try:
                # 1. Download and extract raw text
                text = drive_service.process_drive_file(file_id, file_name, access_token)
                if not text or not nlp_service.is_valid_project(text):
                    continue
                
                # 2. Guardar en la DB de proyectos pendientes
                project_id = file_name.replace(".pdf", "").replace(".PDF", "").strip().lower()
                url_drive = f"https://drive.google.com/file/d/{file_id}/view"
                
                from app.services.pending_projects_db import pending_projects_db
                from app.core.config_manager import config_manager
                
                # Obtener career_id y university_id desde la config para este folder
                current_config = config_manager.get_config()
                accepted_folders = current_config.get("accepted_drive_folders", [])
                folder_info_cfg = next((f for f in accepted_folders if f.get("id") == folder_id), {})
                career_id = folder_info_cfg.get("career_id")
                university_id = folder_info_cfg.get("university_id")

                pending_projects_db.add_pending_project(
                    project_id=project_id,
                    name=file_name.replace(".pdf", "").replace(".PDF", "").strip().title(),
                    raw_text=text,
                    source_url=url_drive,
                    university_id=university_id,
                    career_id=career_id
                )
                print(f"✅ Documento marcado como pendiente: {project_id} (Carrera: {career_id})", flush=True)
            except Exception as e:
                print(f"❌ Error guardando {file_name} como pendiente: {e}", flush=True)
                continue
                
        progress_store[folder_id] = {
            "progress": 100,
            "total": 100,
            "message": "¡Escaneo completado! Proyectos listos para clusterización global."
        }
        
        rabbitmq_service.publish_progress(
            user_id=user_id,
            type_event="sync_complete",
            progress=100,
            total=100,
            message="¡Archivos detectados en Drive y puestos en cola para tratamiento!"
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
        embeddings, metadatas = qdrant_service.get_all_embeddings()
        documents = [meta.get("text", "") for meta in metadatas] if metadatas else []

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
async def get_blue_ocean_niches(page: int = 1, limit: int = 10):
    
    from app.services.qdrant_service import qdrant_service
    from app.services.blue_ocean_db import blue_ocean_db
    import time

    
    niches = []
    try:
        vectors, payloads = qdrant_service.get_all_embeddings()
        
        unique_projects = {}
        if payloads:
            for meta in payloads:
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
                "analysis_data": niche_state.get('analysis_data'),
                "_gravity_score": gravity_score
            })
            

        niches.sort(key=lambda x: x['_gravity_score'], reverse=True)
        
        for niche in niches:
            niche.pop('_gravity_score', None)
            
        # Paginación
        total = len(niches)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        niches = niches[start_idx:end_idx]
        
    except Exception as e:

        print(f"Error extrayendo los océanos azules desde ChromaDB: {e}")
    if not niches and page == 1:
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

from typing import Optional
class NicheViewRequest(BaseModel):
    user_avatar: Optional[str] = None

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
async def populate_from_local_folder(
    x_api_key: str = Header(default=None),
    university_id: str = Form(default="General"),
    career_id: str = Form(default="General"),
    professor_id: str = Form(default="General"),
):
    
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
                
            qdrant_service.add_embeddings(
                vectors=embeddings,
                payloads=[{
                    "project_id": project_id,
                    "text": chunk,
                    "source_url": f"local://projectsTests/{filename}",
                    "university_id": university_id,
                    "career_id": career_id,
                    "professor_id": professor_id,
                    "source": "google_drive_import"
                } for chunk in chunks]
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
async def pre_validate_proposal(background_tasks: BackgroundTasks, user_id: str = Form(...), team_id: str = Form(None), project_id: str = Form(None), uploaded_by: str = Form(None), university_id: str = Form(default=None), career_id: str = Form(default=None), file: UploadFile = File(...)):
    file_bytes = await file.read()
    filename_lower = file.filename.lower()
    filename_real = file.filename
    
    target_id = team_id if team_id else user_id
    
    analysis_progress_store[target_id] = {"phase": 1, "message": "Iniciando pre-validación...", "uploaded_by": uploaded_by}
    background_tasks.add_task(pre_validate_background, target_id, user_id, file_bytes, filename_lower, filename_real, uploaded_by, university_id, career_id, project_id)
    
    return {"status": "pending", "message": "Pre-validación iniciada"}

async def pre_validate_background(target_id: str, user_id: str, file_bytes: bytes, filename_lower: str, filename_real: str, uploaded_by: str = None, university_id: str = None, career_id: str = None, project_id: str = None):
    try:
        active_analysis_tasks[target_id] = asyncio.current_task()
        
        def _cpu_bound():
            if not filename_lower.endswith(('.pdf', '.md', '.txt')):
                raise Exception("El archivo debe ser PDF, MD o TXT")

            analysis_progress_store[target_id] = {"phase": 1, "message": "Extrayendo texto del documento...", "uploaded_by": uploaded_by}
            full_text = ""
            if filename_lower.endswith('.pdf'):
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                full_text = pymupdf4llm.to_markdown(doc)
            else:
                full_text = file_bytes.decode('utf-8')

            if not full_text or len(full_text.strip()) < 50:
                raise Exception("El documento no parece ser una propuesta de proyecto integrador. No se pudo extraer texto.")

            if nlp_service.detect_prompt_injection(full_text):
                raise Exception("ALERTA: Se detectó un intento de inyección de prompt.")

            analysis_progress_store[target_id] = {"phase": 2, "message": "Ejecutando modelo clasificador...", "uploaded_by": uploaded_by}
            texto_limpio = nlp_service.strip_structure(full_text)
            texto_limpio = nlp_service.normalize_homoglyphs(texto_limpio)
            resultado_ml = nlp_service.clasificar_propuesta_ml(texto_limpio)
            calidad_vocabulario_pct = resultado_ml["probabilidades"].get(resultado_ml["etiqueta"], 0.0)
            vector_nuevo = resultado_ml["vector"]

            # Validación de temas bloqueados usando Clustering K-Means
            from app.services.visualization_service import visualization_service
            from app.core.config_manager import config_manager
            
            resultado_cluster = clustering_engine.asignar_cluster(vector_nuevo)
            cluster_id = resultado_cluster.get("cluster_id", -1)
            
            if cluster_id != -1:
                cluster_names = visualization_service.get_cluster_names()
                assigned_cluster_name = cluster_names.get(str(cluster_id)) or cluster_names.get(cluster_id, f"Cluster {cluster_id}")
                
                exclusion_rules = config_manager.get_exclusion_rules(project_id)
                
                import unicodedata
                def normalize_name(text):
                    if not text: return ""
                    t = str(text).lower().strip()
                    return ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
                
                assigned_norm = normalize_name(assigned_cluster_name)
                exclusion_rules_norm = [normalize_name(r) for r in exclusion_rules]
                
                if assigned_norm in exclusion_rules_norm:
                    raise Exception(f"[Filtro 2A] Tu propuesta fue clasificada semánticamente en el tema '{assigned_cluster_name}', el cual ha sido bloqueado por los profesores.")

            analysis_progress_store[target_id] = {"phase": 3, "message": "Validando secciones obligatorias...", "uploaded_by": uploaded_by}
            resultado_blacklist = nlp_service.validar_blacklist_extendida(full_text)
            if not resultado_blacklist["ok"]:
                raise Exception(f"[Filtro 2A] El documento contiene contenido no permitido ('{resultado_blacklist['palabra_bloqueada']}'). Sube tu propuesta de proyecto, no un CV o manual.")

            resultado_secciones = nlp_service.validar_secciones_profesor(full_text)
            completitud_pct = resultado_secciones["completitud_pct"]
            if not resultado_secciones["ok"]:
                faltantes_str = ", ".join(f"'{s}'" for s in resultado_secciones["faltantes"])
                raise Exception(f"[Filtro 2B] Tu propuesta está incompleta. Falta información sobre: {faltantes_str}.")

            resultado_coherencia = nlp_service.validar_coherencia_semantica(full_text)
            coherencia_pct = resultado_coherencia["coherencia_pct"]
            if not resultado_coherencia["ok"]:
                pares_str = "; ".join(p["par"] for p in resultado_coherencia["pares_invalidos"])
                raise Exception(f"[Filtro 3] Las secciones de tu propuesta no son coherentes entre sí ({pares_str}). Asegúrate de que el Problema, el Objetivo y la Justificación hablen del mismo proyecto.")

            analysis_progress_store[target_id] = {"phase": 4, "message": "Buscando colisiones en Qdrant...", "uploaded_by": uploaded_by}
            safe_text = nlp_service.anonymize_pii(texto_limpio)
            chunks = nlp_service.chunk_text(safe_text)
            embeddings = nlp_service.vectorize(chunks)

            # Context filtering parameters (university_id, career_id) will be passed directly

            max_similitud_pct = 0.0
            similar_projects = []
            if embeddings and len(embeddings) > 0:
                query_subset = embeddings[:5] if len(embeddings) > 5 else embeddings
                search_results = qdrant_service.search_similar_multi(
                    query_embeddings=query_subset, n_results=3,
                    filter_university_id=university_id,
                    filter_career_id=career_id
                )
                if search_results and search_results.get("documents"):
                    grouped_projects = {}
                    for q_idx in range(len(search_results["documents"])):
                        docs  = search_results["documents"][q_idx]
                        metas = search_results["metadatas"][q_idx]
                        dists = search_results["distances"][q_idx]
                        for doc, meta, dist in zip(docs, metas, dists):
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

            # --- BLOQUEO INMEDIATO: Propuesta ya registrada (duplicado) ---
            DUPLICATE_THRESHOLD = 85.0
            if max_similitud_pct >= DUPLICATE_THRESHOLD:
                raise Exception(
                    f"[Filtro Antiplagio] Tu propuesta es un duplicado de un proyecto ya registrado "
                    f"({max_similitud_pct:.1f}% de similitud). No está permitido subir una propuesta "
                    f"igual o casi idéntica a una ya enviada anteriormente."
                )

            resultado_cluster = {"cluster_id": -1, "cluster_total": 0,
                                 "innovacion_pct": 50.0, "posicion_pct": 50.0,
                                 "proyectos_cercanos": []}
            if embeddings and len(embeddings) > 0:
                vector_qdrant = np.mean(embeddings, axis=0).tolist()
                try:
                    resultado_cluster = clustering_engine.asignar_cluster(vector_qdrant)
                except Exception as ce:
                    pass

            return (full_text, max_similitud_pct, similar_projects,
                    resultado_secciones, chunks, calidad_vocabulario_pct,
                    completitud_pct, coherencia_pct, resultado_cluster)

        (full_text, max_similitud_pct, similar_projects,
         resultado_secciones, chunks, calidad_vocabulario_pct,
         completitud_pct, coherencia_pct, resultado_cluster) = await asyncio.to_thread(_cpu_bound)

        cluster_id    = resultado_cluster.get("cluster_id", -1)
        cluster_total = resultado_cluster.get("cluster_total", 0)
        innovacion_pct = resultado_cluster.get("innovacion_pct", 50.0)

        collision_risk_level = (
            "Alto"  if max_similitud_pct > 50 else
            "Medio" if max_similitud_pct > 20 else
            "Bajo"
        )

        quick_analysis = {
            "status"  : "success",
            "estado"  : "APROBADO",
            "metricas": {
                "calidad_vocabulario_pct"  : round(calidad_vocabulario_pct, 1),
                "completitud_formato_pct" : round(completitud_pct, 1),
                "coherencia_semantica_pct": round(coherencia_pct, 1),
                "innovacion_originalidad_pct": round(innovacion_pct, 1),
            },
            "cluster": {
                "id"   : cluster_id,
                "total": cluster_total,
            },
            "colision": {
                "porcentaje": round(max_similitud_pct, 1),
                "nivel"     : collision_risk_level,
            },
            "proyectos_similares": similar_projects,
            "secciones_encontradas": resultado_secciones.get("encontradas", []),
            "academic_alignment"   : round(completitud_pct, 1),
            "collision_risk_pct"   : round(max_similitud_pct, 1),
            "collision_risk_level" : collision_risk_level,
            "positive_feedback"    : [
                f"Filtro ML: {calidad_vocabulario_pct:.1f}% seguridad de que es una propuesta válida.",
                f"Estructura completa: {len(resultado_secciones.get('encontradas', []))} secciones detectadas.",
                f"Coherencia semántica: {coherencia_pct:.1f}% de consistencia entre Problemática, Objetivo y Justificación.",
            ],
            "areas_of_improvement" : [
                f"Similitud con proyectos existentes: {max_similitud_pct:.1f}%" if max_similitud_pct > 0 else "No se encontraron colisiones con proyectos anteriores."
            ],
        }

        try:
            log_inference(
                user_id=user_id,
                filename=filename_real,
                score_colision=max_similitud_pct,
                nivel_riesgo=collision_risk_level,
                academic_alignment=min(100, quick_analysis["academic_alignment"]),
                secciones_opcionales=resultado_secciones.get("encontradas", []),
                cluster_id=cluster_id,
            )
        except Exception as log_err:
            pass

        try:
            from app.config.settings import settings
            async with httpx.AsyncClient() as client:
                await client.post(f"{settings.AUTH_SERVICE_URL}/admin/activity", json={
                    "userId": user_id,
                    "action": "UPLOAD_DOCUMENT",
                    "detail": f"Proyecto: {filename_real}",
                    "ipAddress": "127.0.0.1"
                }, timeout=3.0)
                
                if collision_risk_level in ["Alto", "Medio"] or max_similitud_pct > 30:
                    await client.post(f"{settings.AUTH_SERVICE_URL}/admin/activity", json={
                        "userId": None,
                        "action": "SYSTEM_ALERT",
                        "detail": f"Riesgo {collision_risk_level} ({max_similitud_pct}%) en {filename_real}",
                        "ipAddress": "127.0.0.1"
                    }, timeout=3.0)
        except Exception as e:
            pass

        draft_path = os.path.join(DRAFTS_DIR, f"{target_id}_draft.json")
        quick_analysis["filename"] = filename_real
        quick_analysis["uploaded_by"] = uploaded_by
        draft_data = {
            "chunks": chunks,
            "similar_projects": similar_projects,
            "quick_analysis": quick_analysis,
            "uploaded_by": uploaded_by,
            "project_id": project_id
        }
        with open(draft_path, "w", encoding="utf-8") as f:
            json.dump(draft_data, f, ensure_ascii=False)

        analysis_result_store[target_id] = quick_analysis
        analysis_progress_store[target_id] = {"phase": 9, "message": "Pre-validación exitosa", "uploaded_by": uploaded_by}

    except Exception as e:
        import traceback
        full_trace = traceback.format_exc()
        logger.error(f"[pre_validate_background] ERROR COMPLETO:\n{full_trace}")
        error_msg = f"{str(e)}\n\nTraceback:\n{full_trace}"
        analysis_progress_store[target_id] = {"phase": -1, "message": error_msg, "uploaded_by": uploaded_by}
    finally:
        active_analysis_tasks.pop(target_id, None)


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
            qa = draft_data.get("quick_analysis", {})
            qa["uploaded_by"] = draft_data.get("uploaded_by")
            return qa
        except:
            return {"status": "not_found"}
    return {"status": "not_found"}

@router.get("/drift-metrics")
async def get_drift_metrics():
    """
    Retorna las métricas actuales de deriva y cuenta de proyectos nuevos.
    """
    return clustering_engine.get_drift_metrics()

@router.get("/analysis-status/{user_id}")
async def get_analysis_status(user_id: str):
    if user_id in analysis_progress_store:
        return analysis_progress_store[user_id]
    return {"phase": 0, "message": ""}

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
            for p in similar_projects:
                if "content" in p and p["content"]:
                    p["content"] = p["content"][:1500] + "..." if len(p["content"]) > 1500 else p["content"]
            quick_analysis = draft_data.get("quick_analysis", {})
            project_id = draft_data.get("project_id")

            full_proposal_text = " ".join(chunks)
            proposal_text = full_proposal_text[:12000] if len(full_proposal_text) > 12000 else full_proposal_text

            max_sim_pct = quick_analysis.get("collision_risk_pct", 0.0)
            top_project_name = similar_projects[0]["title"] if similar_projects else "Ninguno"
            risk_level = "Alto" if max_sim_pct > 50 else ("Medio" if max_sim_pct > 20 else "Bajo")

            if not await ollama_service.check_health():
                analysis_result_store[user_id] = {
                    "status": "warning",
                    "message": "El motor de IA no está disponible en este momento.",
                    "similar_projects": [p["title"] for p in similar_projects]
                }
                analysis_progress_store[user_id] = {"phase": -1, "message": "El motor de IA no está disponible."}
                return

            analysis_progress_store[user_id] = {"phase": 6, "message": "El comité académico está redactando el dictamen..."}

            await asyncio.sleep(0)
            llm_verdict = await ollama_service.analyze_originality(
                proposal_text=proposal_text,
                similar_projects=similar_projects,
                max_sim_pct=round(max_sim_pct, 1),
                risk_level=risk_level,
                project_name="PROPUESTA_DEL_ALUMNO",
                top_project_name=top_project_name,
                project_id=project_id
            )

            analysis_progress_store[user_id] = {"phase": 7, "message": "Generando recomendaciones técnicas..."}

            analysis_progress_store[user_id] = {"phase": 7, "message": "Generando recomendaciones técnicas..."}

            analysis_progress_store[user_id] = {"phase": 8, "message": "Afinando veredicto final..."}

            final_result = {
                "status": "success",
                "message": "Análisis completado con Llama 3.2 3B",
                "similar_projects_found": len(similar_projects),
                "ollama_analysis": llm_verdict,
                "uploaded_by": draft_data.get("uploaded_by")
            }
            analysis_result_store[user_id] = final_result
            analysis_progress_store[user_id] = {"phase": 9, "message": "Análisis completado. Recuperando resultado...", "uploaded_by": draft_data.get("uploaded_by")}

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
        
        # IMPORTANTE: NO borrar el borrador aquí. 
        # El alumno lo necesita para continuar con el "Análisis exhaustivo".
        # Solo se borrará cuando llame explícitamente a DELETE /draft-proposal/{user_id}
        # o cuando termine el análisis exhaustivo.
            
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
        
        search_results = qdrant_service.search_similar_multi(query_embeddings=query_subset, n_results=3)
        
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
        
        try:
            is_healthy = await ollama_service.check_health()
        except Exception:
            is_healthy = False
            
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

@router.get("/admin/minimap-data")
def minimap_data():
    """
    Retorna los centroides de los clústeres para animar la ubicación
    de una inferencia en el historial de manera ligera en el Frontend.
    """
    try:
        from app.services.visualization_service import visualization_service
        data = visualization_service.get_minimap_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ValidateIdeaRequest(BaseModel):
    idea: str

@router.post("/validate-idea")
async def validate_idea_endpoint(req: ValidateIdeaRequest):
    """
    Rápida validación de una idea de propuesta consultando el servicio LLM, 
    las reglas del profesor y proyectos similares.
    """
    import httpx
    
    # 1. Obtener reglas bloqueadas
    from app.core.config_manager import config_manager
    config = config_manager.get_config()
    blocked_topics = config.get("blocked_topics", [])
    blocked_techs = config.get("blocked_technologies", [])
    
    # 2. Buscar similares en Qdrant
    similar_projects = []
    try:
        chunks = nlp_service.chunk_text(req.idea)
        embeddings = nlp_service.vectorize(chunks)
        if embeddings and len(embeddings) > 0:
            query_subset = embeddings[:1]
            search_results = qdrant_service.search_similar_multi(
                query_embeddings=query_subset, n_results=2
            )
            if search_results and search_results.get("documents"):
                for q_idx in range(len(search_results["documents"])):
                    docs  = search_results["documents"][q_idx]
                    metas = search_results["metadatas"][q_idx]
                    for doc, meta in zip(docs, metas):
                        p_id = meta.get("project_id", "Desconocido")
                        similar_projects.append({
                            "title": f"Proyecto {p_id}",
                            "description": doc[:200]
                        })
    except Exception as e:
        print(f"Error al buscar similares: {e}")

    # 3. Llamar al servicio LLM
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            llm_url = "http://corvus_llm_service:3003/api/v1/llm/validate-idea-quick"
            payload = {
                "idea": req.idea,
                "blocked_topics": blocked_topics,
                "blocked_techs": blocked_techs,
                "similar_projects": similar_projects,
                "provider": config.get("llm_provider", "ollama")
            }
            resp = await client.post(llm_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {"result": data.get("result", "Sin respuesta.")}
    except Exception as e:
        print(f"Error llamando al LLM: {e}")
        return {"result": "El servicio de validación no está disponible en este momento."}


@router.post("/register-historical-proposal")
async def register_historical_proposal(
    target_id: str = Form(...), # team_id or user_id
    university_id: str = Form(default="General"),
    career_id: str = Form(default="General"),
    professor_id: str = Form(default="General"),
    status: str = Form(...) # 'aprobado' or 'rechazado'
):
    """
    Called by orchestration when a professor accepts/rejects a proposal.
    Permanently registers the proposal vectors in Qdrant for future plagiarism detection.
    """
    draft_path = os.path.join(DRAFTS_DIR, f"{target_id}_draft.json")
    if not os.path.exists(draft_path):
        raise HTTPException(status_code=404, detail="No se encontró el borrador de esta propuesta.")

    try:
        with open(draft_path, "r", encoding="utf-8") as f:
            draft_data = json.load(f)

        chunks = draft_data.get("chunks", [])
        if not chunks:
            raise HTTPException(status_code=400, detail="El borrador no tiene fragmentos de texto (chunks).")

        embeddings = nlp_service.vectorize(chunks)
        
        if embeddings is None or len(embeddings) == 0:
            raise HTTPException(status_code=500, detail="Fallo al vectorizar la propuesta.")
            
        qdrant_service.add_embeddings(
            vectors=embeddings,
            payloads=[{
                "project_id": target_id,
                "text": chunk,
                "source_url": f"corvus://student_submission/{target_id}",
                "university_id": university_id,
                "career_id": career_id,
                "professor_id": professor_id,
                "source": "student_submission",
                "status": status
            } for chunk in chunks]
        )
        
        return {"status": "success", "message": "Propuesta registrada exitosamente en el historial."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
