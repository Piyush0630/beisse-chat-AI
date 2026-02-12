"""
Biesse Technical Documentation Chat Assistant - Main Entry Point

FastAPI application for the RAG-based chat assistant.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create data directories
os.makedirs("./data/manuals", exist_ok=True)
os.makedirs("./data/chromadb", exist_ok=True)
os.makedirs("./data/uploads", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    from config import settings
    
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Chromadb path: {settings.chromadb_path}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    from config import settings
    
    app = FastAPI(
        title=settings.app_name,
        description="Technical Documentation Chat Assistant for Biesse CNC Machines. "
                   "Upload PDF manuals and ask questions about machine operation, "
                   "maintenance, safety, and troubleshooting.",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    from api.health import router as health_router
    from api.chat import router as chat_router
    from api.documents import router as documents_router
    
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(documents_router)
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": "Technical Documentation Chat Assistant for Biesse CNC Machines",
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "chat": "/api/v1/chat",
                "documents": "/api/v1/documents"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Error handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return {
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
