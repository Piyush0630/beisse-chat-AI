import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/app.db"
    
    # Vector DB
    CHROMA_DB_PATH: str = "./data/chroma_db"
    
    # Storage
    UPLOAD_DIR: str = "./data/uploads"
    
    # App Settings
    DEBUG: bool = True
    APP_NAME: str = "Biesse Chat Assistant"
    
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

settings = Settings()

# Ensure directories exist
os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///./", "./")), exist_ok=True)
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
