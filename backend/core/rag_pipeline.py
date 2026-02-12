"""
RAG Pipeline Orchestrator

Main entry point for chat message processing.
"""

from typing import Dict, Optional, List, Any
from datetime import datetime
import uuid
import logging

from services.vector_service import VectorService
from services.embedding_service import EmbeddingService
from services.llm_service import LLMService
from core.query_processor import QueryProcessor
from core.response_formatter import ResponseFormatter
from models.chat import ChatResponse, SourceMetadata, ChatMessage

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Main RAG pipeline orchestrator
    
    Coordinates query processing, retrieval, and response generation.
    """
    
    def __init__(
        self,
        vector_service: VectorService,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
        query_processor: QueryProcessor
    ):
        """
        Initialize the RAG pipeline
        
        Args:
            vector_service: Vector database service
            embedding_service: Embedding service
            llm_service: LLM service
            query_processor: Query processor
        """
        self.vector_service = vector_service
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.query_processor = query_processor
        
        logger.info("RAGPipeline initialized")
    
    def process_chat_message(
        self,
        message: str,
        category: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        memory_enabled: bool = True
    ) -> ChatResponse:
        """
        Main entry point for chat message processing
        
        Args:
            message: User message
            category: Optional category filter
            conversation_history: Previous messages
            memory_enabled: Whether to use conversation context
            
        Returns:
            ChatResponse with answer and sources
        """
        try:
            # Step 1: Process query through RAG pipeline
            query_result = self.query_processor.process_query(
                query=message,
                category=category,
                conversation_history=conversation_history,
                memory_enabled=memory_enabled
            )
            
            # Step 2: Generate response with LLM
            llm_result = self._generate_response(
                query=query_result.enriched_query,
                context_chunks=query_result.context_chunks,
                category=category
            )
            
            # Step 3: Format response
            formatted = ResponseFormatter.format_citation_response(
                answer=llm_result["answer"],
                context_chunks=query_result.context_chunks,
                confidence=llm_result["confidence"]
            )
            
            # Step 4: Build response
            sources_metadata = [
                SourceMetadata(
                    manual_name=s.get("manual_name", "Unknown"),
                    manual_file=s.get("manual_file", ""),
                    page_number=s.get("page_number", 0),
                    section=s.get("section"),
                    bbox=s.get("bbox"),
                    similarity_score=s.get("similarity", 0)
                )
                for s in formatted["sources"]
            ]
            
            return ChatResponse(
                answer=formatted["answer"],
                sources=sources_metadata,
                citations=[],  # Will be populated if needed
                confidence=formatted["confidence"],
                message_id=f"msg_{uuid.uuid4().hex[:12]}"
            )
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            raise
    
    def _generate_response(
        self,
        query: str,
        context_chunks: List[Dict],
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response using LLM"""
        
        if not context_chunks:
            # No results found
            return {
                "answer": "I couldn't find any relevant information in the documentation for your query. Try rephrasing your question or check if documents have been uploaded.",
                "confidence": 0.0,
                "sources": []
            }
        
        # Generate response with citations
        llm_result = self.llm_service.generate_with_citations(
            query=query,
            context_chunks=context_chunks,
            system_instruction=self._get_system_instruction(category)
        )
        
        # Calculate confidence
        rerank_scores = [c.get("rerank_score", c.get("similarity", 0)) for c in context_chunks]
        confidence = ResponseFormatter.calculate_confidence(
            sources=context_chunks,
            rerank_scores=rerank_scores
        )
        
        return {
            "answer": llm_result["answer"],
            "confidence": confidence,
            "sources": llm_result["sources"]
        }
    
    def _get_system_instruction(self, category: Optional[str] = None) -> str:
        """Get system instruction based on category"""
        base_instruction = """You are a helpful technical documentation assistant for Biesse CNC machines.
Your role is to:
1. Provide accurate, factual answers based on the documentation
2. Include specific page numbers and citations
3. Be clear and concise
4. If information is not available, clearly state this"""
        
        if category:
            category_instructions = {
                "machine_operation": " Focus on operational procedures, controls, and workflows.",
                "maintenance": " Focus on maintenance schedules, procedures, and troubleshooting.",
                "safety": " Emphasize safety precautions, warning labels, and operational safety.",
                "troubleshooting": " Focus on error codes, diagnostic procedures, and solutions.",
                "programming": " Focus on G-code, machine programming, and code examples."
            }
            base_instruction += category_instructions.get(category, "")
        
        return base_instruction
    
    def search_documents(
        self,
        query: str,
        category: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Search documents without generating a response
        
        Args:
            query: Search query
            category: Optional category filter
            n_results: Number of results
            
        Returns:
            List of matching documents
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)
        
        # Search vector store
        if category:
            results = self.vector_service.search(
                query_embedding=query_embedding,
                category=category,
                n_results=n_results
            )
        else:
            all_results = self.vector_service.search_all_categories(
                query_embedding=query_embedding,
                n_results_per_category=n_results
            )
            results = []
            for cat_results in all_results.values():
                results.extend(cat_results)
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get available document categories"""
        return self.vector_service.list_categories()
    
    def health_check(self) -> Dict[str, Any]:
        """Check pipeline health"""
        try:
            # Check vector service
            categories = self.vector_service.list_categories()
            
            return {
                "status": "healthy",
                "categories_count": len(categories),
                "categories": categories,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class RAGPipelineBuilder:
    """Builder for creating RAGPipeline instances"""
    
    def __init__(self):
        self._vector_service = None
        self._embedding_service = None
        self._llm_service = None
        self._query_processor = None
    
    def with_vector_service(self, vector_service: VectorService) -> 'RAGPipelineBuilder':
        self._vector_service = vector_service
        return self
    
    def with_embedding_service(self, embedding_service: EmbeddingService) -> 'RAGPipelineBuilder':
        self._embedding_service = embedding_service
        return self
    
    def with_llm_service(self, llm_service: LLMService) -> 'RAGPipelineBuilder':
        self._llm_service = llm_service
        return self
    
    def with_query_processor(self, query_processor: QueryProcessor) -> 'RAGPipelineBuilder':
        self._query_processor = query_processor
        return self
    
    def build(self) -> RAGPipeline:
        """Build the RAG pipeline"""
        if not all([self._vector_service, self._embedding_service, 
                    self._llm_service, self._query_processor]):
            raise ValueError("All services must be configured before building")
        
        return RAGPipeline(
            vector_service=self._vector_service,
            embedding_service=self._embedding_service,
            llm_service=self._llm_service,
            query_processor=self._query_processor
        )


def create_rag_pipeline(
    vector_service: VectorService,
    embedding_service: EmbeddingService,
    llm_service: LLMService,
    top_k_chunks: int = 10,
    similarity_threshold: float = 0.7
) -> RAGPipeline:
    """
    Factory function to create RAGPipeline
    
    Args:
        vector_service: Vector database service
        embedding_service: Embedding service
        llm_service: LLM service
        top_k_chunks: Number of chunks to retrieve
        similarity_threshold: Minimum similarity score
        
    Returns:
        Configured RAGPipeline instance
    """
    # Create query processor
    query_processor = QueryProcessor(
        vector_service=vector_service,
        embedding_service=embedding_service,
        top_k_chunks=top_k_chunks,
        similarity_threshold=similarity_threshold
    )
    
    return RAGPipeline(
        vector_service=vector_service,
        embedding_service=embedding_service,
        llm_service=llm_service,
        query_processor=query_processor
    )
