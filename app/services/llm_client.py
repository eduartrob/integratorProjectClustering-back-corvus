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
                    },
                )

                if response.status_code == 503:
                    return {
                        "status": "warning",
                        "message": "El motor de IA no está disponible en este momento.",
                        "similar_projects": [p.get("title") for p in similar_projects],
                    }

                response.raise_for_status()
                return response.json()

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

            prompt = (
                "Eres un experto en taxonomía de proyectos de software. "
                "Analiza estos fragmentos de proyectos de software y devuelve ÚNICAMENTE "
                "un nombre de máximo 4 palabras que describa su temática principal en común. "
                "No uses comillas, no des explicaciones. Solo el nombre.\n\n"
            )
            for i, text in enumerate(sample_texts):
                prompt += f"Proyecto {i+1}: {text[:500]}...\n\n"

            # Assuming llm-service has an endpoint for raw prompt/chat or we can use the provider directly
            # Wait, the llm-service may only have analyze-proposal.
            # I will check if there is a raw prompt endpoint. If not, I can just use ollama_service directly if local.
            # But wait, we can just send it to analyze-proposal? No, that's a specific schema.
            # Let's create an endpoint in llm-service if it doesn't exist, OR check if we have a direct ollama client.
            logger.info(f"[LlmClient] Generando nombre de cluster con {llm_provider}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.LLM_SERVICE_URL}/api/v1/llm/generate-name",
                    json={"prompt": prompt, "provider": llm_provider}
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("name", "Tema Tecnológico").strip('"\' ')
                
            return "Tema Tecnológico"
        except Exception as e:
            logger.error(f"[LlmClient] Error al generar nombre de cluster: {e}")
            return "Tema Tecnológico"

llm_client = LlmClient()
