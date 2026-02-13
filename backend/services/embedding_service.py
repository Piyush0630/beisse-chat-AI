import google.generativeai as genai
from typing import List
from backend.config import settings

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

class EmbeddingService:
    def __init__(self, model_name: str = "models/embedding-001"):
        self.model_name = model_name

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding for a single text.
        """
        result = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a batch of texts.
        """
        # Batch size for Gemini embeddings is typically 100
        result = genai.embed_content(
            model=self.model_name,
            content=texts,
            task_type="retrieval_document"
        )
        return result['embedding']

embedding_service = EmbeddingService()
