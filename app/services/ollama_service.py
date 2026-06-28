# ─────────────────────────────────────────────────────────────────────────────
# ARCHIVO DEPRECADO — NO USAR
# ─────────────────────────────────────────────────────────────────────────────
# Este archivo existía cuando el integrador llamaba a Ollama directamente.
# Ahora la arquitectura usa microservicios separados:
#
#   integratorProjectClustering-back-corvus
#       └─► llm_client.py  →  HTTP POST  →  llm-back-corvus (puerto 3003)
#                                               └─► ollama_client.py → Ollama
#
# El Prompt Magistral y toda la lógica de IA vive en:
#   llm-back-corvus/app/api/routes.py :: build_analysis_prompt()
#
# Para importar el cliente correcto usa:
#   from app.services.llm_client import llm_client as ollama_service
# ─────────────────────────────────────────────────────────────────────────────

from app.services.llm_client import llm_client as ollama_service  # noqa: F401

__all__ = ["ollama_service"]
