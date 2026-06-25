from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from app.services.visualization_service import visualization_service

router = APIRouter()

@router.get("/clusters-3d", response_class=HTMLResponse, tags=["Admin Panel"])
async def get_clusters_3d_html():
    """
    Genera y devuelve la grafica 3D interactiva de los clusters.
    Se utiliza para incrustarla en un <iframe> dentro del panel de administrador.
    """
    try:
        html_content = visualization_service.generate_3d_html()
        if "<h1>Error" in html_content:
            return HTMLResponse(content=html_content, status_code=500)
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters-stats", tags=["Admin Panel"])
async def get_clusters_stats():
    """
    Devuelve las estadisticas basicas de los clusters para pintar tarjetas (KPIs) en el admin.
    """
    try:
        stats = visualization_service.get_cluster_stats()
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects-count", tags=["Admin Panel"])
async def get_projects_count():
    """
    Devuelve la cantidad total de proyectos subidos a la BD.
    """
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
    """
    Compara la cantidad total de proyectos en la base de datos relacional (Auth) 
    versus los que ya están vectorizados en ChromaDB.
    """
    from app.services.chroma_service import chroma_service
    import requests
    from app.core.config import settings
    try:
        # 1. Proyectos Vectorizados (En ChromaDB)
        results = chroma_service.collection.get(include=["metadatas"])
        if not results or not results['metadatas']:
            vectorized_count = 0
        else:
            vectorized_count = len(set(meta['project_id'] for meta in results['metadatas'] if 'project_id' in meta))

        # 2. Proyectos Detectados Total (En PostgreSQL via Auth Service)
        # NOTA ARQUITECTÓNICA: Como la tabla LinkedFolder actualmente no guarda el "total_files", 
        # asumiremos temporalmente que están todos vectorizados para no romper el dashboard con números falsos.
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
    """
    Ejecuta manualmente el algoritmo de clustering global.
    """
    import subprocess
    import os
    from app.core.config import settings

    def run_script():
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "visualize_clusters.py")
        try:
            # Ejecutar el script original que hace el trabajo pesado
            subprocess.run(["python3", script_path], check=True)
            print("Clustering global ejecutado exitosamente.")
        except Exception as e:
            print(f"Error ejecutando clustering: {e}")

    background_tasks.add_task(run_script)
    return {"message": "Clustering global iniciado en segundo plano. Esto puede tomar unos minutos."}

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.core.config_manager import config_manager
from pydantic import BaseModel

class ConfigUpdateRequest(BaseModel):
    allowed_extensions: list[str]

@router.get("/config")
async def get_system_config():
    """Devuelve la configuración actual del microservicio (extensiones, etc.)"""
    return config_manager.get_config()

@router.post("/config")
async def update_system_config(request: ConfigUpdateRequest):
    """Actualiza las extensiones permitidas (.pdf, .md, .txt)"""
    new_config = {"allowed_extensions": request.allowed_extensions}
    success = config_manager.save_config(new_config)
    if success:
        return {"message": "Configuración actualizada con éxito.", "config": new_config}
    raise HTTPException(status_code=500, detail="Error al actualizar la configuración.")

@router.get("/recent-projects", tags=["Admin Panel"])
async def get_recent_projects():
    """
    Devuelve la lista de proyectos recientes para la tabla del historial.
    """
    from app.services.chroma_service import chroma_service
    import datetime
    try:
        results = chroma_service.collection.get(include=["metadatas"])
        if not results or not results['metadatas']:
            return []
            
        unique_projects_map = {}
        for meta in results['metadatas']:
            pid = meta.get('project_id')
            if not pid or pid in unique_projects_map:
                continue
                
            raw_name = str(pid).replace('proyecto_', '').replace('_', ' ').title()
            
            cluster_id = meta.get('cluster_id')
            is_blue_ocean = meta.get('is_blue_ocean')
            
            if is_blue_ocean is True or cluster_id == -1:
                status = "Océano Azul"
                statusClass = "bg-error-container/20 text-error"
            elif cluster_id is not None:
                status = f"En Cluster {cluster_id}"
                statusClass = "bg-primary-container/20 text-primary"
            else:
                status = "Pendiente"
                statusClass = "bg-outline-variant text-on-surface-variant"
                
            unique_projects_map[pid] = {
                "name": raw_name[:45] + "..." if len(raw_name) > 45 else raw_name,
                "major": "Académico", # Fallback since Chroma DB doesn't store this natively
                "date": "Reciente",
                "status": status,
                "statusClass": statusClass
            }
            
        projects_list = list(unique_projects_map.values())
        projects_list.reverse() # Mostrar los últimos agregados primero
        return projects_list[:6]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

