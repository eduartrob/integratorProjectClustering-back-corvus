import json
import os
from app.core.config_manager import config_manager

# 1. Quitar la lógica que sobrescribe el modelo en llm_client.py
with open("app/services/llm_client.py", "r") as f:
    content = f.read()

# Remover las líneas problemáticas
target = """                if data.get("actual_model_used") and data["actual_model_used"] != groq_model:
                    current_config["groq_model"] = data["actual_model_used"]
                    config_manager.save_config(current_config)"""
content = content.replace(target, "")

target2 = """                    if data.get("actual_model_used") and data["actual_model_used"] != groq_model:
                        current_config["groq_model"] = data["actual_model_used"]
                        config_manager.save_config(current_config)"""
content = content.replace(target2, "")

with open("app/services/llm_client.py", "w") as f:
    f.write(content)

# 2. Restaurar el modelo en la configuración global
try:
    config = config_manager.get_config()
    config["groq_model"] = "llama-3.3-70b-versatile"
    config_manager.save_config(config)
    print("Configuración reseteada exitosamente")
except Exception as e:
    print(f"Error al resetear config: {e}")
