import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:3003")

class LlmClient:
    

    def check_health(self) -> bool:
        try:
            response = requests.get(f"{LLM_SERVICE_URL}/api/v1/llm/health", timeout=5)
            data = response.json()
            return response.status_code == 200 and data.get("ollama") == "connected"
        except Exception:
            return False

    def analyze_originality(self, proposal_text: str, similar_projects: list,
                             max_sim_pct: float = 0.0, risk_level: str = "Bajo",
                             project_name: str = "NUEVA_PROPUESTA", top_project_name: str = "Ninguno") -> dict:
        try:
            from app.core.config_manager import config_manager
            current_config = config_manager.get_config()
            llm_provider = current_config.get("llm_provider", "ollama")

            logger.info(f"[LlmClient] Enviando propuesta a {LLM_SERVICE_URL}/api/v1/llm/analyze-proposal (Provider: {llm_provider})")
            response = requests.post(
                f"{LLM_SERVICE_URL}/api/v1/llm/analyze-proposal",
                json={
                    "proposal_text": proposal_text,
                    "similar_projects": similar_projects,
                    "max_sim_pct": max_sim_pct,
                    "risk_level": risk_level,
                    "project_name": project_name,
                    "top_project_name": top_project_name,
                    "provider": llm_provider,
                },
                timeout=150,
            )

            if response.status_code == 503:
                return {
                    "status": "warning",
                    "message": "El motor de IA no está disponible en este momento.",
                    "similar_projects": [p.get("title") for p in similar_projects],
                }

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
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

llm_client = LlmClient()
