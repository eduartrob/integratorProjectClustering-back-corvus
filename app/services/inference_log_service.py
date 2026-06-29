
import sqlite3
import os
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "models" / "inference_log.db"

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def _init_db():
    
    with _get_conn() as conn:
        conn.execute()
        conn.commit()

def log_inference(
    user_id: str,
    filename: str,
    score_colision: float,
    nivel_riesgo: str,
    academic_alignment: int,
    veredicto: str = None,
    secciones_faltantes: list = None,
    secciones_opcionales: list = None,
) -> int:
    
    _init_db()
    with _get_conn() as conn:
        cursor = conn.execute(
            ,
            (
                user_id,
                time.time(),
                filename or "desconocido",
                round(score_colision, 2),
                nivel_riesgo,
                academic_alignment,
                veredicto,
                ", ".join(secciones_faltantes) if secciones_faltantes else "",
                ", ".join(secciones_opcionales) if secciones_opcionales else "",
            ),
        )
        conn.commit()
        return cursor.lastrowid

def get_history(limit: int = 50, offset: int = 0) -> dict:
    
    _init_db()
    with _get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM inference_log").fetchone()[0]
        rows = conn.execute(
            ,
            (limit, offset),
        ).fetchall()

    items = []
    for row in rows:
        items.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "timestamp": row["timestamp"],
            "filename": row["filename"],
            "score_colision": row["score_colision"],
            "nivel_riesgo": row["nivel_riesgo"],
            "academic_alignment": row["academic_alignment"],
            "veredicto": row["veredicto"],
            "secciones_faltantes": row["secciones_faltantes"],
            "secciones_opcionales": row["secciones_opcionales"],
        })

    return {"total": total, "limit": limit, "offset": offset, "items": items}
