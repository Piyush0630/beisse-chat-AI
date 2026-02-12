"""
Embedding Service using Google Text Embedding API

Generates text embeddings for document chunks and queries.
"""

from typing import List, Optional
import google.generativeai as genai
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates text embeddings using Google Embedding API"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-004",
        dimensions: int = 768
    ):
        """
        Initialize the embedding service
        
        Args:
            api_key: Google API key
            model: Embedding model name
            dimensions: Embedding dimensions
        """
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        logger.info(f"EmbeddingService initialized with model: {model}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document",
                output_dimensionality=self.dimensions
            )
            
            embedding = result.get("embedding", [])
            
            if not embedding:
                logger.warning("Empty embedding returned")
                return []
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query
        
        Args:
            query: Search query
            
        Returns:
            Query embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=query,
                task_type="retrieval_query",
                output_dimensionality=self.dimensions
            )
            
            embedding = result.get("embedding", [])
            
            if not embedding:
                logger.warning("Empty query embedding returned")
                return []
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batched)
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = []
        batch_size = 50  # Process in batches to avoid rate limits
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self._embed_batch(batch)
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of texts
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for text in texts:
            try:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error embedding text: {e}")
                # Return zero embedding as fallback
                embeddings.append([0.0] * self.dimensions)
        
        return embeddings
    
    def embed_documents(self, documents: List[Dict]) -> List[List[float]]:
        """
        Embed document chunks with their metadata
        
        Args:
            documents: List of document dictionaries with 'text' key
            
        Returns:
            List of embedding vectors
        """
        texts = [doc.get("text", doc.get("content", "")) for doc in documents]
        return self.embed_texts(texts)
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def truncate_for_embedding(self, text: str, max_tokens: int = 1000) -> str:
        """
        Truncate text to fit within embedding limits
        
        Args:
            text: Input text
            max_tokens: Maximum tokens
            
        Returns:
            Truncated text
        """
        # Rough estimate: 4 characters per token
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        return text[:max_chars]
    
    def embed_long_text(self, text: str, chunk_chars: int = 5000) -> List[float]:
        """
        Embed a long text by chunking
        
        Args:
            text: Long input text
            chunk_chars: Characters per chunk
            
        Returns:
            Aggregated embedding (average of chunk embeddings)
        """
        # Split into chunks
        chunks = []
        for i in range(0, len(text), chunk_chars):
            chunk = text[i:i + chunk_chars]
            chunks.append(chunk)
        
        # Get embeddings for each chunk
        chunk_embeddings = self.embed_texts(chunks)
        
        # Average the embeddings
        if not chunk_embeddings:
            return [0.0] * self.dimensions
        
        avg_embedding = [
            sum(chunk_emb[idx] for chunk_emb in chunk_embeddings) / len(chunk_embeddings)
            for idx in range(self.dimensions)
        ]
        
        return avg_embedding


@lru_cache(maxsize=1000)
def cached_embed_text(api_key: str, text: str) -> List[float]:
    """
    Cached embedding function for repeated texts
    
    Args:
        api_key: API key
        text: Text to embed
        
    Returns:
        Cached embedding vector
    """
    service = EmbeddingService(api_key)
    return service.embed_text(text)


def create_embedding_service(api_key: str) -> EmbeddingService:
    """Factory function to create EmbeddingService"""
    return EmbeddingService(api_key=api_key)
