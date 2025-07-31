import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from utils.exceptions import SecurityException

class SecurityConfig:
    """Configuration sécurisée centralisée"""
    
    ENCRYPTION_KEY_LENGTH = 32
    SALT_LENGTH = 16
    PBKDF2_ITERATIONS = 100000
    
    MAX_INPUT_LENGTH = 10000
    MAX_FILENAME_LENGTH = 255
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    API_CALLS_PER_MINUTE = 10
    FILE_UPLOADS_PER_HOUR = 5
    CV_GENERATION_PER_DAY = 20
    
    SESSION_TIMEOUT_MINUTES = 30
    MAX_SESSIONS_PER_USER = 3
    
    LOG_RETENTION_DAYS = 90
    MAX_LOG_FILE_SIZE = 50 * 1024 * 1024
    
    ALLOWED_HTML_TAGS = ['b', 'i', 'u', 'br', 'p', 'div', 'span']
    ALLOWED_HTML_ATTRIBUTES = {'class': [], 'id': []}
    
    @staticmethod
    def get_encryption_key() -> bytes:
        key_material = os.environ.get('PHOENIX_MASTER_KEY')
        if not key_material:
            raise SecurityException("Master key not configured")
        
        salt = b'phoenix_cv_salt_2025'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=SecurityConfig.ENCRYPTION_KEY_LENGTH,
            salt=salt,
            iterations=SecurityConfig.PBKDF2_ITERATIONS,
        )
        return base64.urlsafe_b64encode(kdf.derive(key_material.encode()))
