import re
import html
from pathlib import Path
from typing import Dict, Any
import bleach
from marshmallow import Schema, fields, validate, ValidationError

from utils.exceptions import ValidationException, SecurityException
from utils.secure_logging import secure_logger
from config.security_config import SecurityConfig

class SecureValidator:
    """Validateur sécurisé pour tous les inputs"""
    
    SAFE_EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]{1,64}@[a-zA-Z0-9.-]{1,255}\.[a-zA-Z]{2,}$')
    SAFE_PHONE_PATTERN = re.compile(r'^[\d\s\-\+\(\)]{8,20}$')
    SAFE_NAME_PATTERN = re.compile(r'^[a-zA-ZÀ-ÿ\s\-\'\.]{1,100}$')
    SAFE_TEXT_PATTERN = re.compile(r'^[^<>{}|\\^`\[\]]{1,10000}$')
    
    FORBIDDEN_KEYWORDS = {
        'script', 'javascript', 'onload', 'onerror', 'eval', 'function',
        'ignore', 'previous', 'instructions', 'system', 'admin', 'root',
        'drop', 'delete', 'truncate', 'union', 'select', 'insert'
    }
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validation sécurisée email"""
        if not email or len(email) > 254:
            raise ValidationException("Email invalide")
        
        email = email.strip().lower()
        
        if not SecureValidator.SAFE_EMAIL_PATTERN.match(email):
            raise ValidationException("Format email invalide")
        
        return email
    
    @staticmethod
    def validate_text_input(text: str, max_length: int = 10000, field_name: str = "input") -> str:
        """Validation sécurisée texte"""
        if not isinstance(text, str):
            raise ValidationException(f"{field_name} doit être une chaîne")
        
        if len(text) > max_length:
            raise ValidationException(f"{field_name} trop long (max {max_length})")
        
        text_lower = text.lower()
        for forbidden in SecureValidator.FORBIDDEN_KEYWORDS:
            if forbidden in text_lower:
                secure_logger.log_security_event(
                    "FORBIDDEN_KEYWORD_DETECTED",
                    {"field": field_name, "keyword": forbidden},
                    "WARNING"
                )
                raise ValidationException("Contenu non autorisé détecté")
        
        cleaned_text = html.escape(text.strip())
        
        return cleaned_text
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validation sécurisée nom de fichier"""
        if not filename or len(filename) > SecurityConfig.MAX_FILENAME_LENGTH:
            raise ValidationException("Nom de fichier invalide")
        
        safe_filename = re.sub(r'[\w\-_\.]', '_', filename)
        
        file_ext = Path(safe_filename).suffix.lower()
        if file_ext not in SecurityConfig.ALLOWED_EXTENSIONS:
            raise ValidationException(f"Extension non autorisée: {file_ext}")
        
        if '..' in safe_filename or '/' in safe_filename or '\\' in safe_filename:
            raise ValidationException("Chemin de fichier non autorisé")
        
        return safe_filename
    
    @staticmethod
    def sanitize_html_output(html_content: str) -> str:
        """Sanitisation HTML pour output sécurisé"""
        cleaned = bleach.clean(
            html_content,
            tags=SecurityConfig.ALLOWED_HTML_TAGS,
            attributes=SecurityConfig.ALLOWED_HTML_ATTRIBUTES,
            strip=True
        )
        
        return cleaned
    
    @staticmethod
    def validate_json_schema(data: Dict, schema: Schema) -> Dict:
        """Validation sécurisée JSON avec schéma"""
        try:
            validated_data = schema.load(data)
            return validated_data
        except ValidationError as e:
            secure_logger.log_security_event(
                "SCHEMA_VALIDATION_FAILED",
                {"errors": str(e.messages)},
                "WARNING"
            )
            raise ValidationException("Données invalides")

