"""
LLM Service using Google Gemini

Generates responses for chat queries.
"""

from typing import List, Dict, Optional, Any
import google.generativeai as genai
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Generates responses using Google Gemini"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.3,
        max_tokens: int = 2048,
        system_instruction: str = None
    ):
        """
        Initialize the LLM service
        
        Args:
            api_key: Google API key
            model: Gemini model name
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum output tokens
            system_instruction: System instruction for the model
        """
        self.api_key = api_key
        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_instruction = system_instruction
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(model)
        
        logger.info(f"LLMService initialized with model: {model}")
    
    def generate_response(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate a response for a given prompt
        
        Args:
            prompt: User prompt
            conversation_history: Previous messages
            
        Returns:
            Generated response text
        """
        try:
            # Build the full prompt with conversation context
            full_prompt = self._build_prompt(prompt, conversation_history)
            
            # Generate response
            response = self.model.generate_content(
                contents=full_prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                    "top_p": 0.95,
                    "response_mime_type": "text/plain"
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def generate_with_citations(
        self,
        query: str,
        context_chunks: List[Dict],
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response with citation context
        
        Args:
            query: User question
            context_chunks: Retrieved document chunks
            system_instruction: Optional system instruction
            
        Returns:
            Dictionary with answer and sources
        """
        # Build context from retrieved chunks
        context = self._build_context(context_chunks)
        
        # Build the prompt with citations
        prompt = self._build_citation_prompt(
            query=query,
            context=context,
            context_chunks=context_chunks
        )
        
        # Generate response
        try:
            response = self.model.generate_content(
                contents=prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens
                }
            )
            
            answer = response.text
            
            # Extract cited sources
            sources = self._extract_sources_from_response(
                answer, 
                context_chunks
            )
            
            return {
                "answer": answer,
                "sources": sources,
                "context_chunks": context_chunks
            }
            
        except Exception as e:
            logger.error(f"Error generating response with citations: {e}")
            raise
    
    def _build_prompt(
        self,
        current_query: str,
        history: Optional[List[Dict]] = None
    ) -> str:
        """Build full prompt with conversation history"""
        prompt_parts = []
        
        # Add system instruction if available
        if self.system_instruction:
            prompt_parts.append(f"System: {self.system_instruction}")
        
        # Add conversation history
        if history:
            prompt_parts.append("\n## Conversation History")
            for msg in history:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                prompt_parts.append(f"**{role.upper()}:** {content}")
        
        # Add current query
        prompt_parts.append(f"\n**USER:** {current_query}")
        prompt_parts.append("\n**ASSISTANT:**")
        
        return "\n".join(prompt_parts)
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        
        for idx, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            text = chunk.get("text", "")
            
            source_info = f"[{idx}] "
            source_info += metadata.get("manual_name", "Unknown Manual")
            source_info += f", Page {metadata.get('page_number', 'N/A')}"
            
            if metadata.get("section"):
                source_info += f" - {metadata['section']}"
            
            # Truncate text for context
            text_preview = text[:400] + "..." if len(text) > 400 else text
            
            context_parts.append(f"{source_info}:\n{text_preview}")
        
        return "\n\n".join(context_parts)
    
    def _build_citation_prompt(
        self,
        query: str,
        context: str,
        context_chunks: List[Dict]
    ) -> str:
        """Build prompt for response with citations"""
        system_prompt = self.system_instruction or """You are a helpful technical documentation assistant for Biesse CNC machines.
Your role is to provide accurate, factual answers based on the documentation.
Always cite your sources using the numbered reference format [1], [2], etc.
If the answer is not in the documentation, clearly state this."""
        
        prompt = f"""{system_prompt}

## User Question
{query}

## Relevant Documentation
{context}

## Instructions
1. Provide a clear, accurate answer based on the documentation above
2. Cite your sources using numbered references like [1], [2], etc.
3. Reference specific page numbers when available
4. Be concise but thorough
5. If the documentation doesn't contain the answer, say "This information is not available in the current documentation."

## Answer:"""
        
        return prompt
    
    def _extract_sources_from_response(
        self,
        answer: str,
        context_chunks: List[Dict]
    ) -> List[Dict]:
        """Extract cited sources from the response"""
        import re
        
        sources = []
        
        # Find citation markers like [1], [2], etc.
        citation_pattern = r'\[(\d+)\]'
        cited_numbers = set(re.findall(citation_pattern, answer))
        
        for num in cited_numbers:
            idx = int(num) - 1  # Convert to 0-based index
            if 0 <= idx < len(context_chunks):
                chunk = context_chunks[idx]
                metadata = chunk.get("metadata", {})
                
                sources.append({
                    "citation_number": num,
                    "manual_name": metadata.get("manual_name", "Unknown"),
                    "manual_file": metadata.get("manual_file", ""),
                    "page_number": metadata.get("page_number", 0),
                    "section": metadata.get("section"),
                    "bbox": metadata.get("bbox"),
                    "text": chunk.get("text", "")[:200]
                })
        
        return sources
    
    def generate_streaming_response(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict]] = None
    ):
        """
        Generate a streaming response
        
        Args:
            prompt: User prompt
            conversation_history: Previous messages
            
        Yields:
            Response text chunks
        """
        full_prompt = self._build_prompt(prompt, conversation_history)
        
        response = self.model.generate_content(
            contents=full_prompt,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens
            },
            stream=True
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 4 characters per token
        return len(text) // 4
    
    def truncate_for_context(
        self,
        text: str,
        max_tokens: int = 15000
    ) -> str:
        """
        Truncate text to fit within context limits
        
        Args:
            text: Input text
            max_tokens: Maximum tokens
            
        Returns:
            Truncated text
        """
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        return text[:max_chars]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "system_instruction": self.system_instruction[:100] + "..." if self.system_instruction else None
        }


def create_llm_service(
    api_key: str,
    model: str = "gemini-2.0-flash-exp",
    temperature: float = 0.3,
    system_instruction: str = None
) -> LLMService:
    """Factory function to create LLMService"""
    return LLMService(
        api_key=api_key,
        model=model,
        temperature=temperature,
        system_instruction=system_instruction
    )
