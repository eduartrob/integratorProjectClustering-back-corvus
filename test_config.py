import asyncio
from app.core.config_manager import config_manager
import sys

project_id = sys.argv[1] if len(sys.argv) > 1 else None
print(f"Testing for project_id: {project_id}")
config = config_manager.get_config(project_id)
print("Sections:")
for s in config.get("project_sections", []):
    print("- " + s.get("nombre", ""))
