from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from app.services.visualization_service import visualization_service
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

from typing import Optional, List, Dict

@router.get("/careers", tags=["Admin Panel"])
async def get_careers():
    from app.services.qdrant_service import qdrant_service
    try:
        _, payloads = qdrant_service.get_all_embeddings()
        careers = {}
        if payloads:
            for meta in payloads:
                u_id = meta.get("university_id")
                c_id = meta.get("career_id")
                if u_id and c_id:
                    if u_id not in careers:
                        careers[u_id] = set()
                    careers[u_id].add(c_id)
        
        result = []
        for u, cs in careers.items():
            result.append({
                "university_id": u,
                "careers": list(cs)
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters-3d", response_class=HTMLResponse, tags=["Admin Panel"])
async def get_clusters_3d_html(filter_cluster_id: Optional[str] = None, university_id: Optional[str] = None, career_id: Optional[str] = None):
    
    try:
        html_content = visualization_service.generate_3d_html(filter_cluster_id=filter_cluster_id, university_id=university_id, career_id=career_id)
        if "<h1>Error" in html_content:
            return HTMLResponse(content=html_content, status_code=500)
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters-2d-html", response_class=HTMLResponse, tags=["Admin Panel"])
async def get_clusters_2d_html(filter_cluster_id: Optional[str] = None, university_id: Optional[str] = None, career_id: Optional[str] = None):
    try:
        html_content = visualization_service.generate_2d_html(filter_cluster_id=filter_cluster_id, university_id=university_id, career_id=career_id)
        if "<h1>Error" in html_content:
            return HTMLResponse(content=html_content, status_code=500)
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters-2d", tags=["Admin Panel"])
async def get_clusters_2d():
    
    try:
        data = visualization_service.get_2d_scatter_data()
        return data
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{tb}")

@router.get("/clusters-stats", tags=["Admin Panel"])
async def get_clusters_stats(university_id: Optional[str] = None, career_id: Optional[str] = None):
    
    try:
        from app.services.clustering_service import clustering_engine
        stats = visualization_service.get_cluster_stats(university_id=university_id, career_id=career_id)
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        stats["is_clustering_running"] = clustering_engine.is_running
        stats["last_error"] = clustering_engine.last_error
        return stats
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{tb}")

@router.get("/projects-count", tags=["Admin Panel"])
async def get_projects_count():
    
    from app.services.qdrant_service import qdrant_service
    try:
        _, payloads = qdrant_service.get_all_embeddings()
        if not payloads:
            return {"count": 0}
            
        unique_projects = set(meta['project_id'] for meta in payloads if 'project_id' in meta)
        return {"count": len(unique_projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-projects-count", tags=["Admin Panel"])
async def get_pending_projects_count():
    from app.services.qdrant_service import qdrant_service
    from app.services.pending_projects_db import pending_projects_db
    try:
        _, payloads = qdrant_service.get_all_embeddings()
        vectorized_count = 0
        if payloads:
            vectorized_count = len(set(meta['project_id'] for meta in payloads if 'project_id' in meta))

        pending_count = pending_projects_db.get_pending_count()
        total_detected = vectorized_count + pending_count
        pct = 0.0
        if total_detected > 0:
            pct = round((pending_count / total_detected) * 100, 1)

        return {
            "pending_count": pending_count,
            "total_detected": total_detected,
            "vectorized_count": vectorized_count,
            "pending_percentage": pct
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-data", tags=["Admin Panel"])
async def reset_all_data():
    """Borra TODOS los vectores de Qdrant para empezar desde cero.
    Úsalo antes de volver a sincronizar la carpeta de Drive."""
    from app.services.qdrant_service import qdrant_service
    from qdrant_client.models import VectorParams, Distance
    try:
        client = qdrant_service.client
        collection_name = "integrator_projects"
        client.delete_collection(collection_name=collection_name)
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        return {
            "status": "ok",
            "message": "✅ Qdrant limpiado exitosamente. Ahora sincroniza la carpeta de Drive para cargar los nuevos proyectos."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", tags=["Admin Panel"])
async def execute_clustering(background_tasks: BackgroundTasks):
    from app.services.clustering_service import clustering_engine
    from app.services.pending_projects_db import pending_projects_db
    from app.services.qdrant_service import qdrant_service
    from app.services.nlp_service import nlp_service

    async def run_clustering():
        try:
            pending = pending_projects_db.get_all_pending()
            print(f"Vectorizando {len(pending)} proyectos pendientes antes de clusterizar...", flush=True)
            for p in pending:
                try:
                    raw_text = pending_projects_db.read_project_text(p["text_file"])
                    if raw_text:
                        clean_text = nlp_service.strip_structure(raw_text)
                        
                        # FASE 1: Filtros de Seguridad (Orden Corregido)
                        
                        # 1. Filtro ML (Regresión Logística)
                        ml_result = nlp_service.clasificar_propuesta_ml(clean_text)
                        if not ml_result.get("es_valido", False):
                            print(f"Proyecto {p['id']} rechazado por Clasificador ML: {ml_result.get('etiqueta')}")
                            pending_projects_db.pop_pending_project(p["id"])
                            continue
                            
                        # 2. Filtro Blacklist
                        bl_result = nlp_service.validar_blacklist_extendida(raw_text)
                        if not bl_result.get("ok", False):
                            print(f"Proyecto {p['id']} rechazado por Blacklist: {bl_result.get('palabra_bloqueada')}")
                            pending_projects_db.pop_pending_project(p["id"])
                            continue
                            

                        # 4. Filtro de Coherencia
                        coh_result = nlp_service.validar_coherencia_semantica(raw_text)
                        if not coh_result.get("ok", False):
                            print(f"Proyecto {p['id']} rechazado por Coherencia Semántica")
                            pending_projects_db.pop_pending_project(p["id"])
                            continue

                        # Aprobado: Vectorizar e insertar en Qdrant (sin cluster_id aún, se recalcula globalmente luego)
                        safe_text = nlp_service.anonymize_pii(clean_text)
                        chunks = nlp_service.chunk_text(safe_text)
                        embeddings = nlp_service.vectorize(chunks)
                        if embeddings:
                            qdrant_service.add_embeddings(
                                vectors=embeddings,
                                payloads=[{
                                    "project_id": p["id"],
                                    "text": chunk,
                                    "source_url": p["source_url"],
                                    "university_id": p.get("university_id"),
                                    "career_id": p.get("career_id")
                                } for chunk in chunks]
                            )
                    # Quitar de pendientes y borrar el txt temporal
                    pending_projects_db.pop_pending_project(p["id"])
                    import os
                    if os.path.exists(p["text_file"]):
                        os.remove(p["text_file"])
                except Exception as ex:
                    print(f"Error vectorizando pendiente {p['id']}: {ex}")
            
            print("Ejecutando clustering global...", flush=True)
            success = await clustering_engine.execute_global_clustering()
            if success:
                print("Clustering global ejecutado exitosamente.")
            else:
                print("Clustering cancelado: no hay suficientes datos.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error ejecutando clustering: {e}")

    background_tasks.add_task(run_clustering)
    return {"message": "Iniciando vectorización y clustering global en segundo plano. Esto puede tomar unos minutos."}

from fastapi import APIRouter, HTTPException, BackgroundTasks, Header, Response
from app.core.config_manager import config_manager
from pydantic import BaseModel
import hashlib
import json
import httpx
from typing import List, Dict, Any, Optional

class ConfigUpdateRequest(BaseModel):
    allowed_extensions: list[str]
    llm_provider: str = "ollama"
    drive_folder_id: str = ""
    accepted_drive_folders: List[Dict[str, str]] = []
    exclusion_rules: List[str] = []
    project_sections: List[Dict[str, Any]] = []
    min_team_members: int = 1
    max_team_members: int = 5
    authorName: Optional[str] = None
    authorPhotoUrl: Optional[str] = None
    authorId: Optional[str] = None

@router.get("/config")
async def get_system_config(
    response: Response, 
    projectId: Optional[str] = None, 
    if_none_match: Optional[str] = Header(None)
):
    config_data = config_manager.get_config(projectId)
    
    # Generate ETag
    config_json = json.dumps(config_data, sort_keys=True)
    etag = hashlib.md5(config_json.encode('utf-8')).hexdigest()
    
    if if_none_match == etag:
        response.status_code = 304
        return None
        
    response.headers["ETag"] = etag
    return config_data

@router.post("/config")
async def update_system_config(request: ConfigUpdateRequest, projectId: Optional[str] = None):
    old_config = config_manager.get_config(projectId)
    
    new_config = {
        "allowed_extensions": request.allowed_extensions,
        "llm_provider": request.llm_provider,
        "drive_folder_id": request.drive_folder_id,
        "accepted_drive_folders": request.accepted_drive_folders,
        "exclusion_rules": request.exclusion_rules,
        "project_sections": request.project_sections,
        "min_team_members": request.min_team_members,
        "max_team_members": request.max_team_members
    }
    
    # --- Generar notificación descriptiva ---
    title_parts = []
    body_parts = []
    
    old_rules = set(old_config.get("exclusion_rules", []))
    new_rules = set(request.exclusion_rules)
    blocked = new_rules - old_rules
    unblocked = old_rules - new_rules
    
    if blocked:
        body_parts.append(f"Se han bloqueado los temas: {', '.join(blocked)}")
    if unblocked:
        body_parts.append(f"Se han desbloqueado los temas: {', '.join(unblocked)}")
        
    if blocked or unblocked:
        title_parts.append("Se han actualizado los Temas para Proyecto")
        
    old_sec_names = set(s.get("nombre", "") for s in old_config.get("project_sections", []))
    new_sec_names = set(s.get("nombre", "") for s in request.project_sections)
    
    added_sections = new_sec_names - old_sec_names
    removed_sections = old_sec_names - new_sec_names
    
    if added_sections:
        body_parts.append(f"Secciones añadidas: {', '.join(added_sections)}")
    if removed_sections:
        body_parts.append(f"Secciones eliminadas: {', '.join(removed_sections)}")
        
    if added_sections or removed_sections:
        title_parts.append("Se ha actualizado la Estructura de Proyecto")

    old_min = old_config.get("min_team_members", 1)
    old_max = old_config.get("max_team_members", 5)
    if old_min != request.min_team_members or old_max != request.max_team_members:
        body_parts.append(f"Nuevo límite de integrantes de equipo: {request.min_team_members} a {request.max_team_members} alumnos")
        if "Se ha actualizado la Estructura de Proyecto" not in title_parts:
            title_parts.append("Se ha actualizado la Estructura de Proyecto")
        
    if not title_parts:
        title = "Nuevas reglas y estructura de proyecto"
    else:
        title = " y ".join(title_parts)
        
    if not body_parts:
        body = "Los profesores han actualizado las reglas de evaluación. ¡Entra a revisarlas!"
    else:
        body = ". ".join(body_parts) + "."
        
    # ----------------------------------------

    success = config_manager.save_config(new_config, projectId)
    if success:
        # Log to ActivityLog if authorId is provided
        if request.authorId and body_parts:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    await client.post(
                        "http://authentication-back-corvus:3000/internal/activity-log",
                        json={
                            "userId": request.authorId,
                            "action": "UPDATE_RULES",
                            "detail": body
                        },
                        timeout=5.0
                    )
            except Exception as e:
                print(f"Failed to log ActivityLog: {e}")

        # Trigger silent notification after saving
        await notify_rules(title=title, body=body, authorName=request.authorName, authorPhotoUrl=request.authorPhotoUrl)
        return {"message": "Configuración actualizada con éxito.", "config": new_config}
    raise HTTPException(status_code=500, detail="Error al actualizar la configuración.")

@router.post("/generate-sections", tags=["Admin Panel"])
async def generate_sections():
    from app.services.llm_client import llm_client
    prompt = (
        "Actúa como un comité académico experto. "
        "Lista únicamente las secciones esenciales que debe contener un documento formal de propuesta de proyecto integrador universitario. "
        "Para cada sección, proporciona su nombre corto y una lista de 3 a 5 palabras clave que suelan encontrarse en dicha sección. "
        "Devuelve EXCLUSIVAMENTE un arreglo JSON con el formato: [{\"nombre\": \"NombreSeccion\", \"keywords\": [\"kw1\", \"kw2\"], \"obligatoria\": true}]. "
        "No incluyas texto adicional ni markdown."
    )
    
    response_text = await llm_client.generate(prompt)
    if response_text:
        import re
        try:
            clean_text = re.sub(r'```(?:json)?', '', response_text).strip()
            sections = json.loads(clean_text)
            return {"sections": sections}
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="El modelo no devolvió un JSON válido.")
    raise HTTPException(status_code=500, detail="Fallo en la generación con IA.")

@router.post("/notify-rules", tags=["Admin Panel"])
async def notify_rules(title: str = "Nuevas reglas y estructura de proyecto", body: str = "Los profesores han actualizado las reglas de evaluación. ¡Entra a revisarlas!", authorName: Optional[str] = None, authorPhotoUrl: Optional[str] = None):
    print("📢 Intentando notificar a los dispositivos móviles (Push Visible)...", flush=True)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://notifications-service:3001/api/notifications/topic/push",
                json={
                    "topic": "config_updates",
                    "title": title,
                    "body": body,
                    "data": {
                        "type": "CONFIG_UPDATED",
                        "authorName": authorName or "",
                        "authorPhotoUrl": authorPhotoUrl or ""
                    }
                }
            )
            if resp.status_code == 200:
                print("✅ Notificación enviada correctamente al servidor de Node.")
                return {"message": "Notificación enviada a los dispositivos."}
            else:
                print(f"❌ Error al notificar: Código {resp.status_code}, Body: {resp.text}")
                return {"message": "Config guardada, pero falló la notificación."}
    except Exception as e:
        print(f"❌ Error llamando al microservicio de notificaciones: {e}")
        return {"message": "Falló la comunicación con notifications-service."}


@router.get("/recent-projects", tags=["Admin Panel"])
async def get_recent_projects(limit: int = 50):
    
    from app.services.visualization_service import visualization_service
    from app.services.qdrant_service import qdrant_service
    from app.services.pending_projects_db import pending_projects_db
    try:
        projects_list = []
        
        # 1. Agregar pendientes primero
        pending = pending_projects_db.get_all_pending()
        for p in pending:
            projects_list.append({
                "id": p["id"],
                "name": p["name"],
                "major": "Ingeniería" if "ing" in p["name"].lower() else "Multidisciplinario",
                "date": "Pendiente",
                "status": "Pendiente (No Vectorizado)",
                "statusClass": "bg-outline-variant/30 text-on-surface-variant"
            })
            
        # 2. Agregar clusterizados/vectorizados
        _, payloads = qdrant_service.get_all_embeddings()
        cluster_names = visualization_service.get_cluster_names()
        
        unique_projects = {}
        if payloads:
            for meta in payloads:
                p_id = meta.get('project_id')
                if p_id and p_id not in unique_projects:
                    name = p_id.replace('proyecto_', '').replace('_', ' ').title()
                    
                    status = "Vectorizado"
                    status_class = "bg-surface-variant text-on-surface-variant"
                    
                    if 'is_blue_ocean' in meta and meta['is_blue_ocean']:
                        status = "Océano Azul"
                        status_class = "bg-error-container/20 text-error"
                    elif 'cluster_id' in meta:
                        cid = meta['cluster_id']
                        c_name = cluster_names.get(cid, f"Clúster {cid}")
                        status = f"Tema: {c_name}"
                        status_class = "bg-primary-container/20 text-primary"
                    else:
                        status = "Vectorizado"
                        status_class = "bg-surface-variant text-on-surface-variant"
                        
                    unique_projects[p_id] = {
                        "id": p_id,
                        "name": name,
                        "major": "Ingeniería" if "ing" in name.lower() else "Multidisciplinario",
                        "date": "Reciente",
                        "status": status,
                        "statusClass": status_class
                    }
                    
        vectorized_list = list(unique_projects.values())
        vectorized_list.reverse()
        projects_list.extend(vectorized_list)
        return projects_list[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drive/invitations")
async def get_drive_invitations():
    from app.services.drive_service import DriveService
    try:
        drive_service = DriveService()
        folders = drive_service.get_shared_folders()
        
        current_config = config_manager.get_config()
        accepted_folders = current_config.get("accepted_drive_folders", [])
        accepted_ids = [f["id"] for f in accepted_folders]
        
        result = []
        for folder in folders:
            is_accepted = folder["id"] in accepted_ids
            result.append({
                "id": folder["id"],
                "name": folder.get("name", "Carpeta sin nombre"),
                "sharingUser": folder.get("sharingUser", {}),
                "is_accepted": is_accepted
            })
            
        return result
    except Exception as e:
        logger.error(f"Error fetching drive invitations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class AcceptDriveFolderRequest(BaseModel):
    folder_id: str

@router.post("/drive/accept")
async def accept_drive_folder(request: AcceptDriveFolderRequest):
    from app.services.drive_service import DriveService
    from app.core.config import settings
    try:
        drive_service = DriveService()
        folder_info = drive_service.get_folder_info(request.folder_id)
        if not folder_info:
            raise HTTPException(status_code=404, detail="Carpeta no encontrada o sin acceso")

        # --- Extraer el correo del propietario de la carpeta ---
        sharing_user = folder_info.get("sharingUser", {})
        owner_email = sharing_user.get("emailAddress", "")

        if not owner_email:
            raise HTTPException(
                status_code=400,
                detail="No se pudo determinar el correo del propietario de la carpeta."
            )

        # --- Verificar que el correo pertenece a un profesor en el sistema ---
        professor_info = None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/admin/find-professor-by-email",
                    params={"email": owner_email},
                    timeout=5.0
                )
                if resp.status_code == 200:
                    professor_info = resp.json()
        except Exception as auth_err:
            logger.error(f"Error contacting auth service: {auth_err}")

        if not professor_info:
            raise HTTPException(
                status_code=403,
                detail=f"El correo '{owner_email}' no pertenece a ningún profesor registrado en Corvus. "
                       f"El profesor debe compartir la carpeta con el mismo correo con el que se registró (principal o secundario)."
            )

        current_config = config_manager.get_config()
        accepted_folders = current_config.get("accepted_drive_folders", [])

        # Actualizar si ya existía o agregar nuevo
        existing_idx = next((i for i, f in enumerate(accepted_folders) if f["id"] == request.folder_id), -1)
        folder_record = {
            "id": folder_info["id"],
            "name": folder_info.get("name", "Carpeta sin nombre"),
            "sharingUser": sharing_user,
            "professor_id": professor_info.get("id"),
            "professor_name": professor_info.get("full_name") or professor_info.get("email"),
            "university_id": professor_info.get("university_id"),
            "career_id": professor_info.get("career_id"),
        }

        if existing_idx >= 0:
            accepted_folders[existing_idx] = folder_record
        else:
            accepted_folders.append(folder_record)

        current_config["accepted_drive_folders"] = accepted_folders
        if config_manager.save_config(current_config):
            return {
                "message": "Carpeta aceptada con éxito",
                "professor": professor_info.get("full_name") or professor_info.get("email"),
                "university_id": professor_info.get("university_id"),
                "career_id": professor_info.get("career_id"),
            }
        else:
            raise HTTPException(status_code=500, detail="Error al guardar configuración")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting drive folder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drive/professor-folders")
async def get_professor_folders(professor_id: str):
    """
    Returns the accepted Drive folders that belong to a specific professor.
    Called by the Auth service when the professor views their profile.
    """
    try:
        current_config = config_manager.get_config()
        accepted_folders = current_config.get("accepted_drive_folders", [])
        professor_folders = [
            {
                "folder_id": f["id"],
                "folder_name": f["name"],
                "status": "synced",
                "university_id": f.get("university_id"),
                "career_id": f.get("career_id"),
            }
            for f in accepted_folders
            if f.get("professor_id") == professor_id
        ]
        return professor_folders
    except Exception as e:
        logger.error(f"Error fetching professor folders: {e}")
        raise HTTPException(status_code=500, detail=str(e))
