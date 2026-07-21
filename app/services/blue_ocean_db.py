import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'blue_ocean_state.json')

class BlueOceanDB:
    def __init__(self):
        self.state: Dict[str, Any] = self._load_db()

    def _load_db(self) -> Dict[str, Any]:
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading BlueOceanDB: {e}")
                return {}
        return {}

    def _save_db(self):
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving BlueOceanDB: {e}")

    def get_all(self) -> Dict[str, Any]:
        return self.state

    def get_niche(self, niche_id: str) -> Dict[str, Any]:
        return self.state.get(niche_id, self._create_default_niche(niche_id))

    def _create_default_niche(self, niche_id: str) -> Dict[str, Any]:
        return {
            "niche_id": niche_id,
            "view_count": 0,
            "recent_viewers": [],
            "analysis_status": "pending",
            "analysis_data": None,
            "created_at": time.time()
        }

    def register_niche_if_not_exists(self, niche_id: str):
        if niche_id not in self.state:
            self.state[niche_id] = self._create_default_niche(niche_id)
            self._save_db()

    def track_view(self, niche_id: str, viewer_avatar: str = None) -> Dict[str, Any]:
        niche = self.get_niche(niche_id)
        
        niche["view_count"] += 1
        
        if viewer_avatar:
            if viewer_avatar in niche["recent_viewers"]:
                niche["recent_viewers"].remove(viewer_avatar)
            niche["recent_viewers"].insert(0, viewer_avatar)
            niche["recent_viewers"] = niche["recent_viewers"][:3]
            
        self.state[niche_id] = niche
        self._save_db()
        return niche

    def update_analysis(self, niche_id: str, analysis_data: Dict[str, Any]):
        niche = self.get_niche(niche_id)
        niche["analysis_status"] = "completed"
        niche["analysis_data"] = analysis_data
        self.state[niche_id] = niche
        self._save_db()

    def get_pending_niches(self) -> List[str]:
        return [
            n_id for n_id, data in self.state.items() 
            if data.get("analysis_status") == "pending"
        ]

blue_ocean_db = BlueOceanDB()
