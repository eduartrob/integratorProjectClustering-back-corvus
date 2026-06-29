"""
inference_log_service.py
Servicio de auditoría de inferencias usando SQLite.
Registra cada análisis de propuesta con: user_id, timestamp, score, riesgo y veredicto.
"""
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
    """Crea la tabla de auditoría si no existe."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inference_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     TEXT    NOT NULL,
                timestamp   REAL    NOT NULL,
                filename    TEXT,
                score_colision  REAL    DEFAULT 0,
                nivel_riesgo    TEXT    DEFAULT 'Bajo',
                academic_alignment INTEGER DEFAULT 0,
                veredicto   TEXT,
                secciones_faltantes TEXT,
                secciones_opcionales TEXT
            )
        """)
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
    """Inserta un registro de auditoría y devuelve el id generado."""
    _init_db()
    with _get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT INTO inference_log
                (user_id, timestamp, filename, score_colision, nivel_riesgo,
                 academic_alignment, veredicto, secciones_faltantes, secciones_opcionales)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
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
    """Devuelve el historial paginado de inferencias."""
    _init_db()
    with _get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM inference_log").fetchone()[0]
        rows = conn.execute(
            """
            SELECT id, user_id, timestamp, filename, score_colision,
                   nivel_riesgo, academic_alignment, veredicto,
                   secciones_faltantes, secciones_opcionales
            FROM inference_log
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
            """,
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
