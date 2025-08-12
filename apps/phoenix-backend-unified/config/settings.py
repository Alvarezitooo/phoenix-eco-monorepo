"""
Configuration centralisée Phoenix Backend
"""

import os
from typing import List, Union
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Environnement
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # JWT & Security
    jwt_secret: str = os.getenv("JWT_SECRET", "your-super-secret-jwt-key")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    
    # CORS
    allowed_origins: Union[str, List[str]] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:3001"
    ).split(",")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # Redis (optionnel)
    redis_url: str = os.getenv("REDIS_URL", "")
    
    # External APIs
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # App-specific settings
    app_name: str = "Phoenix Backend Unifié"
    app_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instance globale
settings = Settings()