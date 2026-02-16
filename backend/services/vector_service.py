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

    def delete_by_filename(self, filename: str):
        """
        Deletes all vectors associated with a specific filename.
        """
        self.collection.delete(where={"filename": filename})

vector_service = VectorService()
