import json
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.default_config_path = os.path.join(settings.CHROMA_DB_PATH, 'app_config.json')
        self._ensure_default_config()

    def _get_config_path(self, project_id: str = None) -> str:
        if not project_id:
            return self.default_config_path
        return os.path.join(settings.CHROMA_DB_PATH, f'app_config_{project_id}.json')

    def _ensure_default_config(self):
        if not os.path.exists(self.default_config_path):
            os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
            default_config = {
                "allowed_extensions": [".pdf", ".md", ".txt"],
                "llm_provider": "groq",
                "groq_model": "llama-3.1-8b-instant",
                "exclusion_rules": [],
                "project_sections": [],
                "min_team_members": 1,
                "max_team_members": 5
            }
            self.save_config(default_config)

    def get_config(self, project_id: str = None):
        config_path = self._get_config_path(project_id)
        
        is_fallback = False
        # Si la configuración del proyecto no existe, retornar la configuración global
        if project_id and not os.path.exists(config_path):
            config_path = self.default_config_path
            is_fallback = True

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if is_fallback:
                    data["project_sections"] = []
                    data["exclusion_rules"] = []
                return data
        except Exception as e:
            logger.error(f"Error leyendo config ({config_path}): {e}")
            return {
                "allowed_extensions": [".pdf", ".md", ".txt"],
                "llm_provider": "groq",
                "exclusion_rules": [],
                "project_sections": [],
                "min_team_members": 1,
                "max_team_members": 5
            }

    def save_config(self, config_data: dict, project_id: str = None):
        config_path = self._get_config_path(project_id)
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error guardando config ({config_path}): {e}")
            return False

    def get_allowed_extensions(self, project_id: str = None):
        return tuple(self.get_config(project_id).get("allowed_extensions", [".pdf", ".md", ".txt"]))

    def get_exclusion_rules(self, project_id: str = None):
        return self.get_config(project_id).get("exclusion_rules", [])


    def get_project_sections(self, project_id: str = None):
        return self.get_config(project_id).get("project_sections", [])

    def get_accepted_drive_folders(self, project_id: str = None):
        return self.get_config(project_id).get("accepted_drive_folders", [])

    def get_min_team_members(self, project_id: str = None):
        return self.get_config(project_id).get("min_team_members", 1)

    def get_max_team_members(self, project_id: str = None):
        return self.get_config(project_id).get("max_team_members", 5)

config_manager = ConfigManager()
