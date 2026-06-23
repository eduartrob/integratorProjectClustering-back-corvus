from fastapi import APIRouter, HTTPException
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
