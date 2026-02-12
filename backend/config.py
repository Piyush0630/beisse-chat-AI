"""
Configuration Management for Biesse Technical Documentation Chat Assistant

Centralized configuration using Pydantic Settings with environment variable support.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Biesse Technical Documentation Chat Assistant"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # API Keys - Required
    google_api_key: str = ""  # Set via GOOGLE_API_KEY environment variable
    
    # Database
    database_url: str = "sqlite:///./data/conversations.db"
    
    # Vector Database
    chromadb_path: str = "./data/chromadb"
    collection_name_prefix: str = "biesse_"
    
    # PDF Processing
    max_file_size_mb: int = 50
    chunk_size: int = 500  # tokens
    chunk_overlap: int = 50  # tokens
    top_k_chunks: int = 10  # Number of chunks to retrieve per query
    
    # LLM Settings
    embedding_model: str = "text-embedding-004"
    embedding_dimensions: int = 768
    llm_model: str = "gemini-2.0-flash-exp"
    llm_temperature: float = 0.3
    max_tokens: int = 2048
    similarity_threshold: float = 0.7
    
    # Categories
    document_categories: List[str] = [
        "machine_operation",
        "maintenance", 
        "safety",
        "troubleshooting",
        "programming"
    ]
    
    # File Paths
    data_dir: str = "./data"
    manuals_dir: str = "./data/manuals"
    uploads_dir: str = "./data/uploads"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_settings):
            # Priority: init > env > .env file
            return init_settings, env_settings, file_settings


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Convenience function for accessing settings
settings = get_settings()
