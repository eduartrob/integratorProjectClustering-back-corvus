import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

# URL del microservicio LLM (configurada vía variable de entorno)
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:3003")


class LlmClient:
    """
    Cliente HTTP hacia llm-back-corvus.
    Reemplaza la llamada directa a Ollama que existía antes.
    """

    def check_health(self) -> bool:
        try:
            response = requests.get(f"{LLM_SERVICE_URL}/api/v1/llm/health", timeout=5)
            data = response.json()
            return response.status_code == 200 and data.get("ollama") == "connected"
        except Exception:
            return False

    def analyze_originality(self, proposal_text: str, similar_projects: list) -> dict:
        """
        Delega el análisis de originalidad al microservicio LLM.
        Mantiene la misma interfaz que el antiguo ollama_service.py.
        """
        try:
            logger.info(f"[LlmClient] Enviando propuesta a {LLM_SERVICE_URL}/api/v1/llm/analyze-proposal")
            response = requests.post(
                f"{LLM_SERVICE_URL}/api/v1/llm/analyze-proposal",
                json={
                    "proposal_text": proposal_text,
                    "similar_projects": similar_projects,
                },
                timeout=900,
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
