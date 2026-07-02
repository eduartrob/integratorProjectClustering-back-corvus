from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from app.services.visualization_service import visualization_service

router = APIRouter()

@router.get("/clusters-3d", response_class=HTMLResponse, tags=["Admin Panel"])
async def get_clusters_3d_html():
    
    try:
        html_content = visualization_service.generate_3d_html()
        if "<h1>Error" in html_content:
            return HTMLResponse(content=html_content, status_code=500)
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters-2d-html", response_class=HTMLResponse, tags=["Admin Panel"])
async def get_clusters_2d_html():
    try:
        html_content = visualization_service.generate_2d_html()
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
async def get_clusters_stats():
    
    try:
        stats = visualization_service.get_cluster_stats()
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
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

    def run_clustering():
        try:
            pending = pending_projects_db.get_all_pending()
            print(f"Vectorizando {len(pending)} proyectos pendientes antes de clusterizar...", flush=True)
            for p in pending:
                try:
                    raw_text = pending_projects_db.read_project_text(p["text_file"])
                    if raw_text:
                        clean_text = nlp_service.strip_structure(raw_text)
                        safe_text = nlp_service.anonymize_pii(clean_text)
                        chunks = nlp_service.chunk_text(safe_text)
                        embeddings = nlp_service.vectorize(chunks)
                        if embeddings:
                            qdrant_service.add_embeddings(
                                vectors=embeddings,
                                payloads=[{
                                    "project_id": p["id"],
                                    "text": chunk,
                                    "source_url": p["source_url"]
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
            success = clustering_engine.execute_global_clustering()
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

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.core.config_manager import config_manager
from pydantic import BaseModel

class ConfigUpdateRequest(BaseModel):
    allowed_extensions: list[str]
    llm_provider: str = "ollama"
    drive_folder_id: str = ""

@router.get("/config")
async def get_system_config():
    
    return config_manager.get_config()

@router.post("/config")
async def update_system_config(request: ConfigUpdateRequest):
    
    new_config = {
        "allowed_extensions": request.allowed_extensions,
        "llm_provider": request.llm_provider,
        "drive_folder_id": request.drive_folder_id
    }
    success = config_manager.save_config(new_config)
    if success:
        return {"message": "Configuración actualizada con éxito.", "config": new_config}
    raise HTTPException(status_code=500, detail="Error al actualizar la configuración.")

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
