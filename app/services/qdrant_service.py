"""
qdrant_service.py — Reemplaza chroma_service.py
Usa Qdrant como base de datos vectorial: más rápida, menos RAM, persistencia en disco.
"""
import logging
import uuid
from pathlib import Path
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
    FilterSelector,
)

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "integrator_projects"
_VECTOR_SIZE     = 384   # paraphrase-multilingual-MiniLM-L12-v2
_QDRANT_PATH     = Path(__file__).resolve().parent.parent.parent / "qdrant_data"


class QdrantService:
    """
    Servicio de base de datos vectorial con Qdrant.
    - Desarrollo: almacenamiento persistente en disco (sin Docker).
    - Producción: apuntar a un servidor Qdrant externo cambiando QdrantClient(url=...).
    """

    def __init__(self, path: Optional[str] = None):
        storage_path = path or str(_QDRANT_PATH)
        _QDRANT_PATH.mkdir(parents=True, exist_ok=True)

        self.client = QdrantClient(path=storage_path)
        logger.info(f"[QdrantService] Almacenamiento en: {storage_path}")

        # Crear la colección si no existe
        existing = [c.name for c in self.client.get_collections().collections]
        if _COLLECTION_NAME not in existing:
            self.client.create_collection(
                collection_name=_COLLECTION_NAME,
                vectors_config=VectorParams(size=_VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info(f"[QdrantService] Colección '{_COLLECTION_NAME}' creada.")
        else:
            logger.info(f"[QdrantService] Colección '{_COLLECTION_NAME}' cargada.")

    # ── Escritura ─────────────────────────────────────────────────────────────

    def add_embeddings(
        self,
        vectors: list,
        payloads: list,
        ids: Optional[list] = None,
    ) -> bool:
        """
        Agrega embeddings a la colección.
        - vectors : lista de vectores (384-dim).
        - payloads: lista de dicts con metadatos (project_id, filename, text, etc.).
        - ids     : IDs únicos; se generan automáticamente si no se pasan.
        """
        if not vectors or len(vectors) != len(payloads):
            logger.error("[QdrantService] vectors y payloads deben tener la misma longitud.")
            return False

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in vectors]

        points = [
            PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, str(id_))),
                vector=list(vec),
                payload=payload,
            )
            for id_, vec, payload in zip(ids, vectors, payloads)
        ]

        self.client.upsert(collection_name=_COLLECTION_NAME, points=points)
        logger.info(f"[QdrantService] {len(points)} vectores guardados.")
        return True

    # ── Búsqueda ──────────────────────────────────────────────────────────────

    def search_similar(
        self,
        query_vector: list,
        n_results: int = 5,
        filter_project_id: Optional[str] = None,
        filter_university_id: Optional[str] = None,
        filter_career_id: Optional[str] = None,
    ) -> list:
        """
        Busca los n vectores más similares.
        Retorna: [{project_id, score, payload}, ...]
        """
        must_conditions = []
        if filter_project_id:
            must_conditions.append(FieldCondition(key="project_id", match=MatchValue(value=filter_project_id)))
        if filter_university_id:
            must_conditions.append(FieldCondition(key="university_id", match=MatchValue(value=filter_university_id)))
        if filter_career_id:
            must_conditions.append(FieldCondition(key="career_id", match=MatchValue(value=filter_career_id)))
            
        query_filter = None
        if must_conditions:
            query_filter = Filter(must=must_conditions)

        results = self.client.query_points(
            collection_name=_COLLECTION_NAME,
            query=query_vector,
            limit=n_results,
            query_filter=query_filter,
            with_payload=True,
        )

        return [
            {
                "project_id": hit.payload.get("project_id", "Desconocido"),
                "score": round(float(hit.score), 4),
                "payload": hit.payload,
            }
            for hit in results.points
        ]

    def search_similar_multi(
        self,
        query_embeddings: list,
        n_results: int = 3,
        filter_university_id: Optional[str] = None,
        filter_career_id: Optional[str] = None,
    ) -> dict:
        """
        Búsqueda múltiple: agrega resultados de varios vectores query.
        Retorna formato compatible con routes.py (mismo que chroma_service).
        """
        all_docs, all_metas, all_distances = [], [], []

        for qvec in query_embeddings:
            hits = self.search_similar(
                qvec, 
                n_results=n_results, 
                filter_university_id=filter_university_id,
                filter_career_id=filter_career_id
            )
            docs, metas, dists = [], [], []
            for h in hits:
                docs.append(h["payload"].get("text", ""))
                metas.append(h["payload"])
                # Qdrant retorna similitud coseno [0,1]; convertir a distancia
                dists.append(round(1.0 - h["score"], 4))
            all_docs.append(docs)
            all_metas.append(metas)
            all_distances.append(dists)

        return {
            "documents": all_docs,
            "metadatas": all_metas,
            "distances": all_distances,
        }

    # ── Utilidades ────────────────────────────────────────────────────────────

    def count(self) -> int:
        """Total de vectores en la colección."""
        info = self.client.get_collection(collection_name=_COLLECTION_NAME)
        # La API de Qdrant usa points_count en versiones recientes
        return getattr(info, "points_count", None) or getattr(info, "vectors_count", None) or 0

    def get_all_embeddings(self) -> tuple:
        """
        Extrae todos los vectores y metadatos de la colección.
        Útil para recalcular el K-Means cuando llegan proyectos nuevos.
        """
        points, offset = [], None
        while True:
            batch, next_offset = self.client.scroll(
                collection_name=_COLLECTION_NAME,
                limit=256,
                offset=offset,
                with_vectors=True,
                with_payload=True,
            )
            points.extend(batch)
            if next_offset is None:
                break
            offset = next_offset

        vectors  = [p.vector for p in points]
        payloads = [p.payload for p in points]
        return vectors, payloads

    def delete_by_project_id(self, project_id: str) -> bool:
        """Elimina todos los vectores de un proyecto por su ID."""
        self.client.delete(
            collection_name=_COLLECTION_NAME,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[FieldCondition(
                        key="project_id",
                        match=MatchValue(value=project_id)
                    )]
                )
            ),
        )
        logger.info(f"[QdrantService] Proyecto '{project_id}' eliminado.")
        return True

    def update_project_payload(self, project_id: str, payload_data: dict) -> bool:
        """Actualiza el payload de todos los vectores (chunks) que pertenezcan a este proyecto."""
        from qdrant_client.http.models import FilterSelector, Filter, FieldCondition, MatchValue
        self.client.set_payload(
            collection_name=_COLLECTION_NAME,
            payload=payload_data,
            points=FilterSelector(
                filter=Filter(
                    must=[FieldCondition(
                        key="project_id",
                        match=MatchValue(value=project_id)
                    )]
                )
            ),
        )
        return True


# Instancia global — mismo patrón que chroma_service.py
qdrant_service = QdrantService()
