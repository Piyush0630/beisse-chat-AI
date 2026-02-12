"""
Chat API Endpoints

Handles chat message processing.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
from models.chat import ChatRequest, ChatResponse, ChatMessage
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


def get_rag_pipeline():
    """Get or create RAG pipeline instance"""
    from core.rag_pipeline import create_rag_pipeline
    from services.vector_service import create_vector_service
    from services.embedding_service import EmbeddingService
    from services.llm_service import LLMService
    from config import settings
    
    # Create services (singleton pattern in production)
    vector_service = create_vector_service(
        persist_directory=settings.chromadb_path,
        collection_name_prefix=settings.collection_name_prefix
    )
    
    embedding_service = EmbeddingService(
        api_key=settings.google_api_key,
        model=settings.embedding_model,
        dimensions=settings.embedding_dimensions
    )
    
    llm_service = LLMService(
        api_key=settings.google_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature
    )
    
    rag_pipeline = create_rag_pipeline(
        vector_service=vector_service,
        embedding_service=embedding_service,
        llm_service=llm_service,
        top_k_chunks=settings.top_k_chunks,
        similarity_threshold=settings.similarity_threshold
    )
    
    return rag_pipeline


# In-memory conversation storage (for Phase 1 - replace with database in V2)
conversations: dict = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a chat message and get a response
    
    Args:
        request: ChatRequest with message and optional context
        
    Returns:
        ChatResponse with answer and sources
    """
    try:
        rag = get_rag_pipeline()
        
        # Get conversation history
        conversation_id = request.conversation_id or "default"
        history = conversations.get(conversation_id, [])
        
        # Convert history to dict format
        history_dicts = [
            {"role": msg.role.value if hasattr(msg.role, 'value') else msg.role, 
             "content": msg.content}
            for msg in history
        ]
        
        # Process message
        response = rag.process_chat_message(
            message=request.message,
            category=request.category,
            conversation_history=history_dicts,
            memory_enabled=request.memory_enabled
        )
        
        # Store in conversation (Phase 1 - in-memory)
        user_msg = ChatMessage(
            role="user",
            content=request.message
        )
        
        assistant_msg = ChatMessage(
            role="assistant",
            content=response.answer,
            citations=response.citations
        )
        
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversations[conversation_id].append(user_msg)
        conversations[conversation_id].append(assistant_msg)
        
        # Return response
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        List of messages
    """
    messages = conversations.get(conversation_id, [])
    
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role.value if hasattr(msg.role, 'value') else msg.role,
                "content": msg.content,
                "citations": msg.citations,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ],
        "message_count": len(messages)
    }


@router.post("/conversation")
async def create_conversation():
    """
    Create a new conversation
    
    Returns:
        Conversation ID
    """
    import uuid
    conversation_id = str(uuid.uuid4())
    conversations[conversation_id] = []
    
    return {
        "conversation_id": conversation_id,
        "message": "Conversation created successfully"
    }


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Deletion confirmation
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {
            "success": True,
            "conversation_id": conversation_id,
            "message": "Conversation deleted successfully"
        }
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/categories")
async def get_categories():
    """Get available document categories"""
    try:
        rag = get_rag_pipeline()
        categories = rag.get_categories()
        
        return {
            "categories": categories,
            "available": categories
        }
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return {
            "categories": [],
            "available": []
        }
