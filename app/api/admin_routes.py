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
