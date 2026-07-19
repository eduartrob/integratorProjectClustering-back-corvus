import os
import json
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)



class LlmClient:
    
    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.LLM_SERVICE_URL}/api/v1/llm/health", timeout=5.0)
                data = response.json()
                return response.status_code == 200 and data.get("ollama") == "connected"
        except Exception:
            return False

    async def analyze_originality(self, proposal_text: str, similar_projects: list,
                             max_sim_pct: float = 0.0, risk_level: str = "Bajo",
                             project_name: str = "NUEVA_PROPUESTA", top_project_name: str = "Ninguno") -> dict:
        try:
            from app.core.config_manager import config_manager
            current_config = config_manager.get_config()
            llm_provider = current_config.get("llm_provider", "ollama")
            groq_model = current_config.get("groq_model", "llama-3.1-8b-instant")

            logger.info(f"[LlmClient] Enviando propuesta a {settings.LLM_SERVICE_URL}/api/v1/llm/analyze-proposal (Provider: {llm_provider})")
            
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.post(
                    f"{settings.LLM_SERVICE_URL}/api/v1/llm/analyze-proposal",
                    json={
                        "proposal_text": proposal_text,
                        "similar_projects": similar_projects,
                        "max_sim_pct": max_sim_pct,
                        "risk_level": risk_level,
                        "project_name": project_name,
                        "top_project_name": top_project_name,
                        "provider": llm_provider,
                        "groq_model": groq_model,
                    },
                )

                if response.status_code == 503:
                    return {
                        "status": "warning",
                        "message": "El motor de IA no está disponible en este momento.",
                        "similar_projects": [p.get("title") for p in similar_projects],
                    }

                response.raise_for_status()
                data = response.json()
                
                if data.get("actual_model_used") and data["actual_model_used"] != groq_model:
                    logger.info(f"[LlmClient] Fallback model used: {data['actual_model_used']}. Updating config.")
                    current_config["groq_model"] = data["actual_model_used"]
                    config_manager.save_config(current_config)

                return data

        except httpx.TimeoutException:
            logger.error("[LlmClient] Timeout al conectar con llm-service")
            return {
                "status": "warning",
                "message": "El análisis de IA tardó demasiado. Intenta de nuevo.",
                "similar_projects": [p.get("title") for p in similar_projects],
            }
        except Exception as e:
            logger.error(f"[LlmClient] Error: {e}")
            return {
                "innovation_index": {"score": 0, "label": "Error"},
                "error": str(e),
                "verdict": "Error de conexión con el servicio de IA",
            }

    async def generate_cluster_name(self, sample_texts: list) -> str:
        try:
            from app.core.config_manager import config_manager
            current_config = config_manager.get_config()
            llm_provider = current_config.get("llm_provider", "ollama")
            groq_model = current_config.get("groq_model", "llama-3.1-8b-instant")

            prompt = (
                "Analiza estos fragmentos de proyectos académicos de ingeniería de software "
                "y devuelve ÚNICAMENTE 2 palabras en español que describan su área temática principal. "
                "NO devuelvas ninguna otra palabra, ni viñetas, ni prefijos.\n\n"
            )
            for i, text in enumerate(sample_texts):
                prompt += f"Fragmento {i+1}: {text[:300]}...\n\n"

            logger.info(f"[LlmClient] Generando nombre de cluster con {llm_provider}")
            
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.post(
                    f"{settings.LLM_SERVICE_URL}/api/v1/llm/generate-name",
                    json={"prompt": prompt, "provider": llm_provider, "groq_model": groq_model}
                )
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("actual_model_used") and data["actual_model_used"] != groq_model:
                        logger.info(f"[LlmClient] Fallback model used: {data['actual_model_used']}. Updating config.")
                        current_config["groq_model"] = data["actual_model_used"]
                        config_manager.save_config(current_config)
                        
                    raw_name = data.get("name", "Tema Tecnológico").strip('"\' *-\n')
                    import re
                    # Limpiar prefijos como "Proyecto 1:", "Fragmento 1:", "Tema:"
                    clean_name = re.sub(r'^(Fragmento|Proyecto|Tema)\s*\d*[:\-]?\s*', '', raw_name, flags=re.IGNORECASE)
                    clean_name = clean_name.split('\n')[0].strip('"\' *-\n')
                    if len(clean_name) < 3:
                        clean_name = "Tema Tecnológico"
                    return clean_name
                
            return "Tema Tecnológico"
        except Exception as e:
            logger.error(f"[LlmClient] Error al generar nombre de cluster: {e}")
            return "Tema Tecnológico"

llm_client = LlmClient()
