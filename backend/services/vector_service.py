import chromadb
from chromadb.config import Settings as ChromaSettings
from ..config import settings

class VectorService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection_name = "biesse_manuals"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def get_collection(self):
        return self.collection

vector_service = VectorService()
