import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChromaService:
    def __init__(self):
        logger.info(f"Iniciando ChromaDB en: {settings.CHROMA_DB_PATH}")
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        
        self.collection = self.client.get_or_create_collection(
            name="integrator_projects",
            metadata={"hnsw:space": "cosine"}
        )

    def add_vectors(self, project_id: str, texts: list[str], embeddings: list[list[float]], url_drive: str, semestre: str = "historico"):
        
        if not texts or not embeddings:
            return
            
        ids = [f"{project_id}_chunk_{i}" for i in range(len(texts))]
        
        metadatas = [{"project_id": project_id, "url": url_drive, "chunk_index": i, "semestre": semestre} for i in range(len(texts))]

        logger.info(f"Guardando {len(texts)} vectores para el proyecto {project_id}...")
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def search_similar_multi(self, query_embeddings: list[list[float]], n_results: int = 5):
        
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
        return results
    
    def get_all_embeddings(self):
        
        return self.collection.get(include=["embeddings", "metadatas", "documents"])

chroma_service = ChromaService()
