"""
Configuration de sécurité pour Phoenix CV
"""

import os
from dataclasses import dataclass
from typing import List

@dataclass
class SecurityConfig:
    """Configuration de sécurité centralisée"""
    
    # Limites de sécurité
    max_file_size_mb: int = 10
    max_sessions_per_user: int = 5
    session_timeout_minutes: int = 30
    
    # Rate limiting
    max_requests_per_minute: int = 60
    max_cv_generations_per_hour: int = 10
    
    # Chiffrement
    encryption_key: str = os.getenv('PHOENIX_CV_ENCRYPTION_KEY', 'default-dev-key-change-in-prod')
    
    # Validation des fichiers
    allowed_file_types: List[str] = None
    max_text_length: int = 100000
    
    # API Keys
    gemini_api_key: str = os.getenv('GEMINI_API_KEY', '')
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['pdf', 'docx', 'txt']
    
    @classmethod
    def get_production_config(cls):
        """Configuration sécurisée pour la production"""
        return cls(
            max_file_size_mb=5,  # Plus restrictif en production
            max_sessions_per_user=3,
            session_timeout_minutes=15,
            max_requests_per_minute=30,
            max_cv_generations_per_hour=5
        )