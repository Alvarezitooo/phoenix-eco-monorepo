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
    max_filename_length: int = 255
    
    # Extensions autorisées
    allowed_extensions: List[str] = None
    
    # HTML sécurisé
    allowed_html_tags: List[str] = None
    allowed_html_attributes: dict = None
    
    # API Keys
    gemini_api_key: str = os.getenv('GOOGLE_API_KEY', '')
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['pdf', 'docx', 'txt']
        
        if self.allowed_extensions is None:
            self.allowed_extensions = ['.pdf', '.docx', '.txt', '.doc']
            
        if self.allowed_html_tags is None:
            self.allowed_html_tags = [
                'p', 'br', 'strong', 'em', 'b', 'i', 'u', 
                'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'div', 'span', 'a'
            ]
            
        if self.allowed_html_attributes is None:
            self.allowed_html_attributes = {
                '*': ['class', 'style'],
                'a': ['href', 'title', 'target'],
                'div': ['class', 'style', 'id'],
                'span': ['class', 'style']
            }
    
    @classmethod
    def get_encryption_key(cls) -> bytes:
        """Génère ou récupère la clé de chiffrement sécurisée"""
        from cryptography.fernet import Fernet
        import base64

        key_env = os.getenv('PHOENIX_CV_ENCRYPTION_KEY')
        
        if key_env:
            # SECURITY FIX: The environment variable MUST hold a valid, URL-safe, base64-encoded 32-byte key.
            # The KDF (key derivation function) was removed as it's inappropriate to derive a key from another key.
            # A static salt was a critical vulnerability.
            try:
                # Validate that the key is correctly formatted and has the right length.
                key_bytes = base64.urlsafe_b64decode(key_env.encode())
                if len(key_bytes) != 32:
                    raise ValueError("Invalid key length. PHOENIX_CV_ENCRYPTION_KEY must be 32 bytes.")
                return key_env.encode()
            except (ValueError, TypeError) as e:
                raise ValueError(f"CRITICAL: PHOENIX_CV_ENCRYPTION_KEY is not a valid Fernet key. {e}")
        else:
            # For development only, generate a key. This should not be used in production.
            print("WARNING: PHOENIX_CV_ENCRYPTION_KEY not set. Generating a temporary development key.")
            return Fernet.generate_key()
    
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