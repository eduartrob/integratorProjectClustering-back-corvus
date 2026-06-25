import json
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        # Usamos la ruta persistente de Chroma para guardar también la configuración
        self.config_path = os.path.join(settings.CHROMA_DB_PATH, 'app_config.json')
        self._ensure_default_config()

    def _ensure_default_config(self):
        if not os.path.exists(self.config_path):
            os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
            default_config = {
                "allowed_extensions": [".pdf", ".md", ".txt"]
            }
            self.save_config(default_config)

    def get_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo config: {e}")
            return {"allowed_extensions": [".pdf", ".md", ".txt"]}

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

config_manager = ConfigManager()
