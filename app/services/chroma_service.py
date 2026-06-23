import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChromaService:
    def __init__(self):
        logger.info(f"Iniciando ChromaDB en: {settings.CHROMA_DB_PATH}")
        # Inicializamos el cliente persistente para guardar en disco local (cero costos de nube)
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        
        # Usaremos la métrica "cosine" (Coseno) que es excelente para medir similitud de textos
        self.collection = self.client.get_or_create_collection(
            name="integrator_projects",
            metadata={"hnsw:space": "cosine"}
        )

    def add_vectors(self, project_id: str, texts: list[str], embeddings: list[list[float]], url_drive: str, semestre: str = "historico"):
        """
        Guarda los vectores en ChromaDB atados a su texto original y su URL.
        """
        if not texts or not embeddings:
            return
            
        # Generamos IDs únicos para cada fragmento del proyecto
        ids = [f"{project_id}_chunk_{i}" for i in range(len(texts))]
        
        # Guardamos metadatos para poder recuperarlos después sin tener el PDF físico
        metadatas = [{"project_id": project_id, "url": url_drive, "chunk_index": i, "semestre": semestre} for i in range(len(texts))]

        logger.info(f"Guardando {len(texts)} vectores para el proyecto {project_id}...")
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def search_similar(self, query_embedding: list[float], n_results: int = 5):
        """
        Busca los proyectos más similares en el espacio vectorial (potencial plagio o afinidad).
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
    
    def get_all_embeddings(self):
        """
        Extrae todos los vectores para poder correr los algoritmos de Scikit-Learn
        y encontrar Océanos Azules.
        """
        return self.collection.get(include=["embeddings", "metadatas", "documents"])

chroma_service = ChromaService()
