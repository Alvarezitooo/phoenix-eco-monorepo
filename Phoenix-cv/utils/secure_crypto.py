import os
import secrets
import hmac
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.security_config import SecurityConfig
from utils.exceptions import SecurityException
from utils.secure_logging import secure_logger

class SecureCrypto:
    """Services cryptographiques sécurisés"""
    
    def __init__(self):
        self._encryption_key = SecurityConfig.get_encryption_key()
        self._fernet = Fernet(self._encryption_key)
    
    def encrypt_data(self, data: str) -> str:
        """Chiffrement sécurisé AES-256"""
        try:
            encrypted = self._fernet.encrypt(data.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')
        except Exception:
            raise SecurityException("Erreur de chiffrement")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Déchiffrement sécurisé"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception:
            raise SecurityException("Erreur de déchiffrement")
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Génération token cryptographiquement sécurisé"""
        return secrets.token_urlsafe(length)
    
    def generate_hmac(self, data: str, key: str) -> str:
        """Génération HMAC sécurisé"""
        return hmac.new(
            key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def verify_hmac(self, data: str, signature: str, key: str) -> bool:
        """Vérification HMAC sécurisé"""
        expected = self.generate_hmac(data, key)
        return hmac.compare_digest(expected, signature)

secure_crypto = SecureCrypto()
