from pathlib import Path
import io
from typing import Tuple

import PyPDF2
import docx

from utils.secure_validator import SecureValidator
from utils.secure_logging import secure_logger
from config.security_config import SecurityConfig

class SecureFileHandler:
    """Gestionnaire de fichiers ultra-sécurisé"""
    
    MAGIC_NUMBERS = {
        'pdf': b'%PDF',
        'docx': b'PK\x03\x04',
        'txt': None
    }
    
    @staticmethod
    def validate_file_secure(file_content: bytes, filename: str) -> Tuple[bool, str]:
        """Validation sécurisée complète du fichier"""
        try:
            safe_filename = SecureValidator.validate_filename(filename)
            
            if len(file_content) > SecurityConfig.MAX_FILE_SIZE:
                secure_logger.log_security_event(
                    "FILE_SIZE_EXCEEDED",
                    {"filename": safe_filename[:50], "size": len(file_content)},
                    "WARNING"
                )
                return False, f"Fichier trop volumineux (max {SecurityConfig.MAX_FILE_SIZE // (1024*1024)}MB)"
            
            file_ext = Path(safe_filename).suffix.lower()[1:]
            if file_ext in SecureFileHandler.MAGIC_NUMBERS:
                expected_magic = SecureFileHandler.MAGIC_NUMBERS[file_ext]
                if expected_magic and not file_content.startswith(expected_magic):
                    secure_logger.log_security_event(
                        "FILE_TYPE_MISMATCH",
                        {"filename": safe_filename[:50], "extension": file_ext},
                        "WARNING"
                    )
                    return False, "Type de fichier non conforme à l'extension"
            
            malware_patterns = [
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'data:text/html',
                b'<?php',
                b'<%',
                b'eval(',
                b'exec(',
                b'system(',
                b'shell_exec'
            ]
            
            file_lower = file_content.lower()
            for pattern in malware_patterns:
                if pattern in file_lower:
                    secure_logger.log_security_event(
                        "MALICIOUS_PATTERN_DETECTED",
                        {"filename": safe_filename[:50], "pattern": pattern.decode('utf-8', errors='ignore')},
                        "CRITICAL"
                    )
                    return False, "Contenu de fichier non autorisé détecté"
            
            if file_ext == 'pdf':
                if not SecureFileHandler._validate_pdf_structure(file_content):
                    return False, "Structure PDF invalide ou corrompue"
            
            elif file_ext == 'docx':
                if not SecureFileHandler._validate_docx_structure(file_content):
                    return False, "Structure DOCX invalide ou corrompue"
            
            secure_logger.log_security_event(
                "FILE_VALIDATED_SUCCESSFULLY", 
                {"filename": safe_filename[:50], "size": len(file_content)}
            )
            
            return True, "Fichier valide et sécurisé"
            
        except Exception as e:
            secure_logger.log_security_event(
                "FILE_VALIDATION_ERROR",
                {"filename": filename[:50], "error": str(e)[:100]},
                "ERROR"
            )
            return False, "Erreur lors de la validation du fichier"
    
    @staticmethod
    def _validate_pdf_structure(content: bytes) -> bool:
        """Validation structure PDF sécurisée"""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            
            if len(reader.pages) > 50:
                return False
            
            if len(reader.pages) > 0:
                first_page = reader.pages[0]
                text = first_page.extract_text()
                if len(text) > 100000:
                    return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def _validate_docx_structure(content: bytes) -> bool:
        """Validation structure DOCX sécurisée"""
        try:
            doc = docx.Document(io.BytesIO(content))
            
            total_text = ""
            for paragraph in doc.paragraphs:
                total_text += paragraph.text
                if len(total_text) > 200000:
                    return False
            
            return True
            
        except Exception:
            return False
