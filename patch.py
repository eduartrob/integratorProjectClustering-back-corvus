import re

with open("app/services/llm_client.py", "r") as f:
    content = f.read()

# Modify the signature of analyze_originality
content = content.replace(
    'async def analyze_originality(self, proposal_text: str, similar_projects: list,\n                             max_sim_pct: float = 0.0, risk_level: str = "Bajo",\n                             project_name: str = "NUEVA_PROPUESTA", top_project_name: str = "Ninguno") -> dict:',
    'async def analyze_originality(self, proposal_text: str, similar_projects: list,\n                             max_sim_pct: float = 0.0, risk_level: str = "Bajo",\n                             project_name: str = "NUEVA_PROPUESTA", top_project_name: str = "Ninguno", project_id: str = None) -> dict:'
)

# Modify how config is retrieved
content = content.replace(
    'current_config = config_manager.get_config()\n            llm_provider = current_config.get("llm_provider", "ollama")',
    'current_config = config_manager.get_config(project_id)\n            llm_provider = current_config.get("llm_provider", "ollama")'
)

with open("app/services/llm_client.py", "w") as f:
    f.write(content)
