"""
Response Formatter

Formats RAG responses with citations and metadata.
"""

from typing import List, Dict, Optional, Any
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FormattedResponse:
    """Formatted response with citations"""
    answer: str
    sources: List[Dict]
    citations: List[Dict]
    confidence: float


class ResponseFormatter:
    """Formats responses from the RAG pipeline"""
    
    @staticmethod
    def format_response(
        answer: str,
        sources: List[Dict],
        confidence: float
    ) -> FormattedResponse:
        """
        Format the final response with citations
        
        Args:
            answer: Generated answer
            sources: Source documents
            confidence: Confidence score
            
        Returns:
            FormattedResponse with citations
        """
        # Clean answer text
        clean_answer = ResponseFormatter._clean_answer(answer)
        
        # Extract citations from answer
        citations = ResponseFormatter._extract_citations(answer, sources)
        
        # Build source list
        source_list = ResponseFormatter._build_source_list(sources)
        
        return FormattedResponse(
            answer=clean_answer,
            sources=source_list,
            citations=citations,
            confidence=confidence
        )
    
    @staticmethod
    def format_citation_response(
        answer: str,
        context_chunks: List[Dict],
        confidence: float
    ) -> Dict[str, Any]:
        """
        Format response from citation-enabled generation
        
        Args:
            answer: Generated answer
            context_chunks: Retrieved chunks
            confidence: Confidence score
            
        Returns:
            Formatted response dictionary
        """
        # Clean the answer
        clean_answer = ResponseFormatter._clean_answer(answer)
        
        # Build sources from chunks
        sources = []
        for idx, chunk in enumerate(context_chunks):
            metadata = chunk.get("metadata", {})
            source = {
                "id": f"source_{idx + 1}",
                "manual_name": metadata.get("manual_name", "Unknown"),
                "manual_file": metadata.get("manual_file", ""),
                "page_number": metadata.get("page_number", 0),
                "section": metadata.get("section"),
                "bbox": metadata.get("bbox"),
                "similarity": chunk.get("similarity", 0)
            }
            sources.append(source)
        
        return {
            "answer": clean_answer,
            "sources": sources,
            "confidence": confidence
        }
    
    @staticmethod
    def _extract_citations(
        answer: str,
        sources: List[Dict]
    ) -> List[Dict]:
        """Extract citation references from the answer"""
        import re
        
        # Pattern to match citation markers like [1], [2], etc.
        citation_pattern = r'\[(\d+)\]'
        cited_numbers = set(re.findall(citation_pattern, answer))
        
        citations = []
        for num in cited_numbers:
            idx = int(num) - 1  # Convert to 0-based index
            if 0 <= idx < len(sources):
                source = sources[idx]
                metadata = source.get("metadata", {})
                
                citation = {
                    "id": f"cite_{num}",
                    "number": num,
                    "manual_name": metadata.get("manual_name", "Unknown"),
                    "page_number": metadata.get("page_number", 0),
                    "section": metadata.get("section"),
                    "bbox": metadata.get("bbox"),
                    "quoted_text": source.get("text", "")[:200]
                }
                citations.append(citation)
        
        return citations
    
    @staticmethod
    def _build_source_list(sources: List[Dict]) -> List[Dict]:
        """Build a clean list of sources"""
        source_list = []
        
        for idx, source in enumerate(sources):
            metadata = source.get("metadata", {})
            
            source_item = {
                "id": source.get("id", f"source_{idx + 1}"),
                "manual_name": metadata.get("manual_name", "Unknown"),
                "manual_file": metadata.get("manual_file", ""),
                "page_number": metadata.get("page_number", 0),
                "section": metadata.get("section"),
                "bbox": metadata.get("bbox"),
                "similarity": source.get("similarity", 0),
                "chunk_type": metadata.get("chunk_type", "text")
            }
            source_list.append(source_item)
        
        return source_list
    
    @staticmethod
    def _clean_answer(answer: str) -> str:
        """Clean and format the answer text"""
        # Remove excessive newlines
        clean = re.sub(r'\n{3,}', '\n\n', answer)
        
        # Fix spacing around punctuation
        clean = re.sub(r'\s+([.,;:!?])', r'\1', clean)
        
        # Remove leading/trailing whitespace
        clean = clean.strip()
        
        # Fix common formatting issues
        clean = re.sub(r'\*\*\s+', '**', clean)  # Remove space after bold markers
        clean = re.sub(r'\s+\*\*', '**', clean)  # Remove space before bold markers
        
        return clean
    
    @staticmethod
    def calculate_confidence(
        sources: List[Dict],
        rerank_scores: Optional[List[float]] = None
    ) -> float:
        """
        Calculate confidence score based on source quality
        
        Args:
            sources: Retrieved sources
            rerank_scores: Optional reranking scores
            
        Returns:
            Confidence score (0-1)
        """
        if not sources:
            return 0.0
        
        # Average similarity of top sources
        similarities = [s.get("similarity", 0) for s in sources[:3]]
        avg_similarity = sum(similarities) / len(similarities)
        
        # Boost if multiple sources agree
        agreement_bonus = 0.1 if len(sources) >= 3 else 0
        
        # Use rerank scores if available
        if rerank_scores:
            avg_rerank = sum(rerank_scores[:3]) / len(rerank_scores[:3])
            confidence = (avg_similarity * 0.6 + avg_rerank * 0.3 + agreement_bonus)
        else:
            confidence = avg_similarity + agreement_bonus
        
        # Cap at 0.95
        return min(0.95, confidence)
    
    @staticmethod
    def format_answer_with_highlights(
        answer: str,
        sources: List[Dict]
    ) -> str:
        """
        Format answer with highlighted key terms
        
        Args:
            answer: Generated answer
            sources: Source documents
            
        Returns:
            Formatted answer with highlights
        """
        # This is a placeholder for more advanced formatting
        # Could add bolding of key terms, etc.
        
        formatted = ResponseFormatter._clean_answer(answer)
        
        # Add source footer
        if sources:
            formatted += "\n\n**Sources:**\n"
            for idx, source in enumerate(sources[:3], 1):
                metadata = source.get("metadata", {})
                manual_name = metadata.get("manual_name", "Unknown")
                page = metadata.get("page_number", "N/A")
                formatted += f"[{idx}] {manual_name} (Page {page})\n"
        
        return formatted
    
    @staticmethod
    def create_error_response(
        error_message: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Create a standardized error response
        
        Args:
            error_message: Error description
            query: User query
            
        Returns:
            Error response dictionary
        """
        return {
            "answer": f"Sorry, I encountered an error while processing your request: {error_message}",
            "sources": [],
            "citations": [],
            "confidence": 0.0,
            "error": error_message,
            "query": query
        }
    
    @staticmethod
    def create_no_results_response(query: str) -> Dict[str, Any]:
        """
        Create response when no results are found
        
        Args:
            query: User query
            
        Returns:
            No results response dictionary
        """
        return {
            "answer": "I couldn't find any relevant information in the documentation for your query. Try rephrasing your question or uploading additional documents.",
            "sources": [],
            "citations": [],
            "confidence": 0.0,
            "query": query,
            "tip": "Try using different keywords or more specific terms"
        }


def format_rag_response(
    answer: str,
    sources: List[Dict],
    confidence: float
) -> FormattedResponse:
    """Convenience function to format RAG response"""
    return ResponseFormatter.format_response(
        answer=answer,
        sources=sources,
        confidence=confidence
    )
