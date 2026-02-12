"""
Query Processor

Processes user queries through the RAG pipeline.
"""

from typing import List, Dict, Optional, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of query processing"""
    query: str
    enriched_query: str
    context_chunks: List[Dict]
    total_results: int
    processing_time_seconds: float


class QueryProcessor:
    """Processes user queries for RAG retrieval"""
    
    def __init__(
        self,
        vector_service,
        embedding_service,
        top_k_chunks: int = 10,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize the query processor
        
        Args:
            vector_service: Vector database service
            embedding_service: Embedding service
            top_k_chunks: Number of chunks to retrieve
            similarity_threshold: Minimum similarity score
        """
        self.vector_service = vector_service
        self.embedding_service = embedding_service
        self.top_k_chunks = top_k_chunks
        self.similarity_threshold = similarity_threshold
    
    def process_query(
        self,
        query: str,
        category: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        memory_enabled: bool = True
    ) -> QueryResult:
        """
        Process a user query through the RAG pipeline
        
        Args:
            query: User query
            category: Optional category filter
            conversation_history: Previous messages
            memory_enabled: Whether to include conversation context
            
        Returns:
            QueryResult with context chunks
        """
        import time
        start_time = time.time()
        
        # Step 1: Preprocess query
        clean_query = self._preprocess_query(query)
        
        # Step 2: Enrich query with conversation context
        enriched_query = self._enrich_with_context(
            clean_query, 
            conversation_history, 
            memory_enabled
        )
        
        # Step 3: Generate query embedding
        query_embedding = self.embedding_service.embed_query(enriched_query)
        
        # Step 4: Search vector database
        all_results = self._search_vector_store(
            query_embedding, 
            category
        )
        
        # Step 5: Rerank results
        reranked_results = self._rerank_results(
            query=enriched_query,
            results=all_results
        )
        
        # Step 6: Prepare context for LLM
        context_chunks = self._prepare_context(reranked_results)
        
        processing_time = time.time() - start_time
        
        return QueryResult(
            query=clean_query,
            enriched_query=enriched_query,
            context_chunks=context_chunks,
            total_results=len(all_results),
            processing_time_seconds=processing_time
        )
    
    def _preprocess_query(self, query: str) -> str:
        """Clean and normalize the query"""
        # Remove extra whitespace
        clean = " ".join(query.split())
        
        # Preserve technical terms (don't lowercase everything)
        # Just clean up formatting
        clean = clean.strip()
        
        return clean
    
    def _enrich_with_context(
        self,
        query: str,
        history: Optional[List[Dict]] = None,
        memory_enabled: bool = True
    ) -> str:
        """Enrich query with conversation context"""
        if not history or not memory_enabled:
            return query
        
        # Get last 3 exchanges for context (6 messages)
        recent_history = history[-6:] if len(history) >= 6 else history
        
        context_parts = [query]
        
        for msg in recent_history:
            if msg.get("role") == "user":
                context_parts.append(f"Previous: {msg['content']}")
            elif msg.get("role") == "assistant":
                # Include summary of previous answer
                content = msg.get("content", "")
                if len(content) > 100:
                    content = content[:100] + "..."
                context_parts.append(f"Response: {content}")
        
        return " | ".join(context_parts)
    
    def _search_vector_store(
        self,
        query_embedding: List[float],
        category: Optional[str] = None
    ) -> List[Dict]:
        """Search the vector database"""
        if category:
            # Search specific category
            results = self.vector_service.search(
                query_embedding=query_embedding,
                category=category,
                n_results=self.top_k_chunks,
                similarity_threshold=self.similarity_threshold
            )
            return results
        else:
            # Search all categories
            all_results = {}
            categories = self.vector_service.list_categories()
            
            for cat in categories:
                results = self.vector_service.search(
                    query_embedding=query_embedding,
                    category=cat,
                    n_results=self.top_k_chunks // len(categories) + 1,
                    similarity_threshold=self.similarity_threshold
                )
                all_results[cat] = results
            
            # Flatten and deduplicate
            flattened = []
            seen_ids = set()
            for cat_results in all_results.values():
                for result in cat_results:
                    if result["id"] not in seen_ids:
                        seen_ids.add(result["id"])
                        flattened.append(result)
            
            return flattened
    
    def _rerank_results(
        self,
        query: str,
        results: List[Dict]
    ) -> List[Dict]:
        """Rerank results by multiple factors"""
        query_words = set(query.lower().split())
        
        scored = []
        for idx, result in enumerate(results):
            # Base similarity from vector search
            similarity = result.get("similarity", 0.5)
            
            # Keyword match score
            text = result.get("text", "").lower()
            keyword_score = self._keyword_match_score(query_words, text)
            
            # Position bonus (earlier results get slight boost)
            position_bonus = max(0, 0.1 - idx * 0.01)
            
            # Combined score
            rerank_score = (
                similarity * 0.7 +
                keyword_score * 0.2 +
                position_bonus * 0.1
            )
            
            result["rerank_score"] = rerank_score
            result["keyword_score"] = keyword_score
            scored.append(result)
        
        # Sort by rerank score
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        return scored
    
    def _keyword_match_score(self, query_words: set, text: str) -> float:
        """Calculate keyword match score"""
        if not query_words:
            return 0.0
        
        text_words = set(text.lower().split())
        matches = query_words & text_words
        
        # Count technical terms (longer words)
        tech_term_matches = sum(1 for w in matches if len(w) > 6)
        tech_bonus = tech_term_matches * 0.1
        
        base_score = len(matches) / len(query_words)
        
        return min(1.0, base_score + tech_bonus)
    
    def _prepare_context(self, results: List[Dict]) -> List[Dict]:
        """Prepare top chunks for LLM context"""
        # Return top 3-5 chunks depending on quality
        top_results = []
        
        for result in results[:5]:
            # Only include if score is above threshold
            if result.get("rerank_score", 0) > 0.3:
                top_results.append({
                    "id": result["id"],
                    "text": result["text"],
                    "metadata": result.get("metadata", {}),
                    "similarity": result.get("similarity", 0),
                    "rerank_score": result.get("rerank_score", 0)
                })
        
        return top_results
    
    def get_available_categories(self) -> List[str]:
        """Get list of available categories"""
        return self.vector_service.list_categories()


def create_query_processor(
    vector_service,
    embedding_service,
    top_k_chunks: int = 10,
    similarity_threshold: float = 0.7
) -> QueryProcessor:
    """Factory function to create QueryProcessor"""
    return QueryProcessor(
        vector_service=vector_service,
        embedding_service=embedding_service,
        top_k_chunks=top_k_chunks,
        similarity_threshold=similarity_threshold
    )
