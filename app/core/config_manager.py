import json
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.config_path = os.path.join(settings.CHROMA_DB_PATH, 'app_config.json')
        self._ensure_default_config()

    def _ensure_default_config(self):
        if not os.path.exists(self.config_path):
            os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
            default_config = {
                "allowed_extensions": [".pdf", ".md", ".txt"],
                "llm_provider": "ollama",
                "accepted_drive_folders": [],
                "exclusion_rules": [],
                "project_sections": []
            }
            self.save_config(default_config)

    def get_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo config: {e}")
            return {
                "allowed_extensions": [".pdf", ".md", ".txt"],
                "llm_provider": "ollama",
                "accepted_drive_folders": [],
                "exclusion_rules": [],
                "project_sections": []
            }

    def save_config(self, config_data: dict):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error guardando config: {e}")
            return False

    def get_allowed_extensions(self):
        return tuple(self.get_config().get("allowed_extensions", [".pdf", ".md", ".txt"]))

    def get_exclusion_rules(self):
        return self.get_config().get("exclusion_rules", [])

    def get_project_sections(self):
        return self.get_config().get("project_sections", [])

    def get_accepted_drive_folders(self):
        return self.get_config().get("accepted_drive_folders", [])

config_manager = ConfigManager()
