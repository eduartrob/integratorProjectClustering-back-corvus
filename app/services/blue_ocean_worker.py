import asyncio
import httpx
import json
import logging
from app.core.config import settings
from app.services.blue_ocean_db import blue_ocean_db
from app.api.routes import analysis_lock

logger = logging.getLogger(__name__)



class BlueOceanWorker:
    def __init__(self):
        self._is_running = False
        self._task = None

    def start(self):
        if not self._is_running:
            self._is_running = True
            self._task = asyncio.create_task(self._worker_loop())
            logger.info("Blue Ocean Worker started.")

    def stop(self):
        self._is_running = False
        if self._task:
            self._task.cancel()
            logger.info("Blue Ocean Worker stopped.")

    async def _worker_loop(self):
        from app.services.qdrant_service import qdrant_service
        
        while self._is_running:
            try:
                pending = blue_ocean_db.get_pending_niches()
                
                if not pending:
                    try:
                        vectors, payloads = qdrant_service.get_all_embeddings()
                        if payloads:
                            for meta in payloads:
                                if meta and meta.get('is_blue_ocean'):
                                    p_id = meta.get('project_id')
                                    if p_id:
                                        blue_ocean_db.register_niche_if_not_exists(p_id)
                                        
                        pending = blue_ocean_db.get_pending_niches()
                    except Exception as e:
                        logger.error(f"Worker: Error escaneando ChromaDB para auto-descubrimiento: {e}")
                
                if pending:
                    niche_id = pending[0]
                    logger.info(f"Worker: Procesando análisis para el nicho {niche_id}")
                    
                    title = niche_id.replace('proyecto_', '').replace('.md', '').replace('.pdf', '').replace('_', ' ').title()
                    description = "Nicho inexplorado detectado por baja colisión semántica."
                    category = "INNOVACIÓN ACADÉMICA"
                    
                    async with analysis_lock:
                        analysis_data = await self._call_llm_service(title, description, category)
                    
                    if analysis_data:
                        blue_ocean_db.update_analysis(niche_id, analysis_data)
                        logger.info(f"Worker: Análisis completado y guardado para {niche_id}")
                    else:
                        logger.warning(f"Worker: Falló el análisis para {niche_id}. Se reintentará luego.")
                        
                await asyncio.sleep(1 if pending else 30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en Blue Ocean Worker loop: {e}")
                await asyncio.sleep(30)

    async def _call_llm_service(self, title: str, description: str, category: str) -> dict:
        payload = {
            "title": title,
            "description": description,
            "category": category
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{settings.LLM_SERVICE_URL}/api/v1/llm/analyze-blue-ocean", json=payload, timeout=120.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"LLM Service devolvió status {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error conectando con LLM Service: {e}")
            return None

blue_ocean_worker = BlueOceanWorker()
