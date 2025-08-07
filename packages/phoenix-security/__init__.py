"""
Phoenix Security Package
Centralise les services de sécurité et protection des données pour l'écosystème Phoenix
"""

__version__ = "1.0.0"
__author__ = "Claude Phoenix DevSecOps Guardian"

from .services.data_anonymizer import DataAnonymizer, AnonymizationResult
from .services.data_anonymizer import anonymize_text, anonymize_email, anonymize_user_id

__all__ = [
    "DataAnonymizer",
    "AnonymizationResult", 
    "anonymize_text",
    "anonymize_email",
    "anonymize_user_id"
]