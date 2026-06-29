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
    
    from app.services.chroma_service import chroma_service
    try:
        results = chroma_service.collection.get(include=["metadatas"])
        if not results or not results['metadatas']:
            return {"count": 0}
            
        unique_projects = set(meta['project_id'] for meta in results['metadatas'] if 'project_id' in meta)
        return {"count": len(unique_projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-projects-count", tags=["Admin Panel"])
async def get_pending_projects_count():
    
    from app.services.chroma_service import chroma_service
    import requests
    from app.core.config import settings
    try:
        results = chroma_service.collection.get(include=["metadatas"])
        if not results or not results['metadatas']:
            vectorized_count = 0
        else:
            vectorized_count = len(set(meta['project_id'] for meta in results['metadatas'] if 'project_id' in meta))

        total_detected = vectorized_count
        pending_count = total_detected - vectorized_count
        
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

@router.post("/execute", tags=["Admin Panel"])
async def execute_clustering(background_tasks: BackgroundTasks):
    
    from app.services.clustering_service import clustering_engine
    
    def run_clustering():
        try:
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
    return {"message": "Clustering global iniciado en segundo plano. Esto puede tomar unos minutos."}

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.core.config_manager import config_manager
from pydantic import BaseModel

class ConfigUpdateRequest(BaseModel):
    allowed_extensions: list[str]
    llm_provider: str = "ollama"

@router.get("/config")
async def get_system_config():
    
    return config_manager.get_config()

@router.post("/config")
async def update_system_config(request: ConfigUpdateRequest):
    
    new_config = {
        "allowed_extensions": request.allowed_extensions,
        "llm_provider": request.llm_provider
    }
    success = config_manager.save_config(new_config)
    if success:
        return {"message": "Configuración actualizada con éxito.", "config": new_config}
    raise HTTPException(status_code=500, detail="Error al actualizar la configuración.")

@router.get("/recent-projects", tags=["Admin Panel"])
async def get_recent_projects(limit: int = 50):
    
    from app.services.visualization_service import visualization_service
    from app.services.chroma_service import chroma_service
    try:
        results = chroma_service.collection.get(include=["metadatas"])
        cluster_names = visualization_service.get_cluster_names()
        
        unique_projects = {}
        if results and results['metadatas']:
            for meta in results['metadatas']:
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
                        status = "Pendiente"
                        status_class = "bg-outline-variant/30 text-on-surface-variant"
                        
                    unique_projects[p_id] = {
                        "id": p_id,
                        "name": name,
                        "major": "Ingeniería" if "ing" in name.lower() else "Multidisciplinario",
                        "date": "Reciente",
                        "status": status,
                        "statusClass": status_class
                    }
                    
        projects_list = list(unique_projects.values())
        projects_list.reverse()
        return projects_list[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
