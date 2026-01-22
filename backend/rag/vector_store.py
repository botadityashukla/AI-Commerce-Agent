import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
from backend.config import get_settings
from backend.core.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)

class VectorStore:
    def __init__(self):
        self.embeddings = SentenceTransformerEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.index_path = settings.VECTOR_DB_PATH
        self.vector_db = None

    def initialize_db(self, documents: List[Document], force_rebuild: bool = False):
        """Initializes the FAISS index. Loads from disk if exists, else builds from docs."""
        if os.path.exists(self.index_path) and not force_rebuild:
             try:
                self.vector_db = FAISS.load_local(
                    self.index_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True # Local file, safe
                )
                logger.info("Loaded existing FAISS index.")
             except Exception as e:
                 logger.warning(f"Failed to load index, rebuilding: {e}")
                 self._build_index(documents)
        else:
            self._build_index(documents)

    def _build_index(self, documents: List[Document]):
        """Builds a new FAISS index from documents."""
        if not documents:
            logger.warning("No documents provided to build index.")
            return

        logger.info("Building new FAISS index...")
        self.vector_db = FAISS.from_documents(documents, self.embeddings)
        self.vector_db.save_local(self.index_path)
        logger.info(f"FAISS index saved to {self.index_path}")

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """Performs a similarity search."""
        if not self.vector_db:
             raise ValueError("Vector DB not initialized. Call initialize_db first.")
        
        results = self.vector_db.similarity_search(query, k=k)
        return results

# Singleton instance
vector_store = VectorStore()
