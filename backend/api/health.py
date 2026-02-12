"""
Health Check Endpoints

Monitors service health and readiness.
"""

from fastapi import APIRouter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check():
    """
    Basic health check
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "biesse-chat-assistant"
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check including dependencies
    
    Returns:
        Detailed status of all dependencies
    """
    from config import settings
    
    checks = {
        "database": "unknown",
        "vector_store": "unknown",
        "llm": "unknown",
        "embedding": "unknown"
    }
    
    # Check database
    try:
        import sqlite3
        conn = sqlite3.connect("./data/conversations.db")
        conn.close()
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Check vector store
    try:
        from services.vector_service import create_vector_service
        vs = create_vector_service(
            persist_directory=settings.chromadb_path,
            collection_name_prefix=settings.collection_name_prefix
        )
        categories = vs.list_categories()
        checks["vector_store"] = f"healthy ({len(categories)} categories)"
    except Exception as e:
        checks["vector_store"] = f"unhealthy: {str(e)}"
    
    # Check LLM
    try:
        from services.llm_service import LLMService
        import google.generativeai as genai
        genai.configure(api_key=settings.google_api_key)
        model = genai.GenerativeModel(settings.llm_model)
        # Simple API test - just check if we can initialize
        checks["llm"] = "healthy"
    except Exception as e:
        checks["llm"] = f"unhealthy: {str(e)}"
    
    # Check Embedding API
    try:
        from services.embedding_service import EmbeddingService
        es = EmbeddingService(
            api_key=settings.google_api_key,
            model=settings.embedding_model,
            dimensions=settings.embedding_dimensions
        )
        # Simple API test - just check if we can initialize
        checks["embedding"] = "healthy"
    except Exception as e:
        checks["embedding"] = f"unhealthy: {str(e)}"
    
    # Determine overall status
    all_healthy = all("unhealthy" not in v for v in checks.values())
    
    return {
        "status": "ready" if all_healthy else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
        "configuration": {
            "llm_model": settings.llm_model,
            "embedding_model": settings.embedding_model,
            "categories": settings.document_categories
        }
    }


@router.get("/live")
async def liveness_check():
    """
    Liveness check (basic response)
    
    Returns:
        Simple liveness status
    """
    return {"status": "alive"}


@router.get("/metrics")
async def metrics():
    """
    Basic metrics endpoint
    
    Returns:
        Application metrics
    """
    import os
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": 0,  # Would need process tracking
        "memory_usage_mb": 0,  # Would need psutil
        "active_conversations": 0,  # Would need DB query
        "total_documents": 0  # Would need catalog count
    }
