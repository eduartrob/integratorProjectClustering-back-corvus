import json
import os
import time
from typing import Dict, Any, List

PENDING_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pending_projects')
os.makedirs(PENDING_DIR, exist_ok=True)
DB_FILE = os.path.join(PENDING_DIR, 'pending_projects_state.json')

class PendingProjectsDB:
    def __init__(self):
        self.state: Dict[str, Any] = self._load_db()

    def _load_db(self) -> Dict[str, Any]:
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading PendingProjectsDB: {e}")
                return {}
        return {}

    def _save_db(self):
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving PendingProjectsDB: {e}")

    def add_pending_project(self, project_id: str, name: str, raw_text: str, source_url: str):
        # Guardar el texto en un archivo aparte para no saturar el JSON
        text_file_path = os.path.join(PENDING_DIR, f"{project_id}.txt")
        try:
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(raw_text)
        except Exception as e:
            print(f"Error guardando texto de {project_id}: {e}")
            
        self.state[project_id] = {
            "id": project_id,
            "name": name,
            "source_url": source_url,
            "status": "Pendiente",
            "detected_at": time.time(),
            "text_file": text_file_path
        }
        self._save_db()

    def get_all_pending(self) -> List[Dict[str, Any]]:
        return list(self.state.values())

    def get_pending_count(self) -> int:
        return len(self.state)

    def pop_pending_project(self, project_id: str) -> Dict[str, Any]:
        project = self.state.pop(project_id, None)
        if project:
            self._save_db()
        return project

    def read_project_text(self, text_file_path: str) -> str:
        if os.path.exists(text_file_path):
            with open(text_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

pending_projects_db = PendingProjectsDB()
