import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    """Application settings"""
    
    # Basic settings
    PROJECT_NAME: str = "Phoenix Rise & Dojo Mental"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    SECRET_KEY: str
    ENCRYPTION_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Email (development)
    MAILHOG_HOST: str = "localhost"
    MAILHOG_PORT: int = 1025
    
    # AI Providers (future use)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    @validator("ENCRYPTION_KEY", pre=True, always=True)
    def set_encryption_key(cls, v, values):
        if v:
            return v
        # Generate a new key if none provided
        return Fernet.generate_key().decode()
    
    @validator("DEBUG", pre=True)
    def set_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Load settings
settings = Settings()

# Create Fernet cipher for encryption
fernet = Fernet(settings.ENCRYPTION_KEY.encode())