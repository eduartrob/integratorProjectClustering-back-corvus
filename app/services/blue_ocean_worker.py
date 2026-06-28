import asyncio
import aiohttp
import json
import logging
from app.services.blue_ocean_db import blue_ocean_db

logger = logging.getLogger(__name__)

# URL del LLM Service (interno en la red de Docker / Local)
LLM_SERVICE_URL = "http://localhost:8002/api/v1/analyze-blue-ocean" # Ajustar según el puerto real del llm-back-corvus

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
        while self._is_running:
            try:
                # 1. Obtener nichos pendientes
                pending = blue_ocean_db.get_pending_niches()
                
                if pending:
                    # Procesamos solo uno por ciclo para no saturar Ollama
                    niche_id = pending[0]
                    logger.info(f"Worker: Procesando análisis para el nicho {niche_id}")
                    
                    # Extraer info base del nicho desde ChromaDB (Aquí simulamos la extracción)
                    # Idealmente el Integrador ya tiene los metadatos.
                    # Por simplicidad, el worker le pide al DB local que solo guarda el ID, 
                    # así que necesitamos los metadatos reales. En producción se obtendrían de Chroma.
                    # Asumimos que los metadatos se pueden reconstruir o ya están.
                    
                    # Para mantener el desacople, usaremos un nombre derivado del ID
                    title = niche_id.replace('proyecto_', '').replace('.md', '').replace('.pdf', '').replace('_', ' ').title()
                    description = "Nicho inexplorado detectado por baja colisión semántica."
                    category = "INNOVACIÓN ACADÉMICA"
                    
                    # 2. Llamar al LLM Service
                    analysis_data = await self._call_llm_service(title, description, category)
                    
                    if analysis_data:
                        # 3. Guardar en BD
                        blue_ocean_db.update_analysis(niche_id, analysis_data)
                        logger.info(f"Worker: Análisis completado y guardado para {niche_id}")
                    else:
                        logger.warning(f"Worker: Falló el análisis para {niche_id}. Se reintentará luego.")
                        
                # Esperar antes del siguiente ciclo. 
                # Si hay pendientes, espera poco (10s), si no hay, espera más (60s)
                await asyncio.sleep(10 if pending else 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en Blue Ocean Worker loop: {e}")
                await asyncio.sleep(30) # Pausa por error

    async def _call_llm_service(self, title: str, description: str, category: str) -> dict:
        payload = {
            "title": title,
            "description": description,
            "category": category
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(LLM_SERVICE_URL, json=payload, timeout=120) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        text = await response.text()
                        logger.error(f"LLM Service devolvió status {response.status}: {text}")
                        return None
        except Exception as e:
            logger.error(f"Error conectando con LLM Service: {e}")
            return None

blue_ocean_worker = BlueOceanWorker()
