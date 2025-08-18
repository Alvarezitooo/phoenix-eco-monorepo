"""
🛡️ IRIS SECURITY MODULE - Protection contre attaques et vulnérabilités
Module dédié à la sécurisation de l'agent Iris contre les attaques communes.
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Configuration logging sécurisé
logger = logging.getLogger(__name__)

class PromptInjectionGuard:
    """
    Protection avancée contre les attaques de prompt injection.
    Basé sur les patterns OWASP et recherches sécurité IA.
    """
    
    # Patterns dangereux détectés par analyse comportementale
    DANGEROUS_PATTERNS = [
        # Instructions de contournement système
        r'ignore\s+(previous|all|above|system)',
        r'disregard\s+(previous|instructions|context)',
        r'forget\s+(everything|all|previous)',
        
        # Tentatives de role hijacking
        r'(you\s+are\s+now|act\s+as|pretend\s+to\s+be)',
        r'(assistant|system|human|claude):\s*',
        r'###\s*(system|user|assistant)',
        
        # Extraction d'informations sensibles
        r'(show|reveal|display)\s+(prompt|instructions|system)',
        r'what\s+(are\s+your|is\s+your)\s+(instructions|prompt)',
        
        # Injections de code
        r'<(script|iframe|object|embed)',
        r'javascript\s*:',
        r'(eval|exec|import)\s*\(',
        
        # Manipulation du contexte
        r'end\s+of\s+(conversation|chat|session)',
        r'new\s+(conversation|session|user)',
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS]
    
    def is_potentially_malicious(self, text: str) -> tuple[bool, List[str]]:
        """
        Analyse le texte pour détecter des patterns malveillants.
        
        Returns:
            tuple: (is_malicious, list_of_detected_patterns)
        """
        detected_patterns = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text):
                detected_patterns.append(self.DANGEROUS_PATTERNS[i])
        
        return len(detected_patterns) > 0, detected_patterns
    
    def sanitize_input(self, text: str) -> str:
        """
        Nettoie et sécurise l'input utilisateur.
        """
        # Limite longueur pour éviter attaques volumétriques
        if len(text) > 500:
            text = text[:500] + "..."
        
        # Supprime caractères de contrôle dangereux
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        # Échappage des balises markdown/HTML potentiellement dangereuses
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        # Neutralise les tentatives de formatage malveillant
        text = re.sub(r'`{3,}', '```', text)  # Limite les blocs de code
        text = re.sub(r'#{4,}', '###', text)  # Limite les headers
        
        return text.strip()

class RateLimiter:
    """
    Rate limiting simple en mémoire pour l'agent Alessio.
    En production, utiliser Redis ou autre solution distribuée.
    """
    
    def __init__(self, max_requests: int = 10, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests: Dict[str, List[datetime]] = {}
    
    def is_rate_limited(self, user_id: str) -> bool:
        """
        Vérifie si l'utilisateur a dépassé la limite de requêtes.
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        # Initialise ou nettoie l'historique utilisateur
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Supprime les requêtes anciennes
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id] 
            if req_time > window_start
        ]
        
        # Vérifie la limite
        if len(self.requests[user_id]) >= self.max_requests:
            return True
        
        # Enregistre la nouvelle requête
        self.requests[user_id].append(now)
        return False

def validate_user_id(user_id: str) -> bool:
    """
    Validation basique du format user_id.
    """
    if not user_id or len(user_id) < 3 or len(user_id) > 50:
        return False
    
    # Format UUID ou identifiant alphanumérique
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, user_id))

def secure_error_message(error: Exception, include_details: bool = False) -> str:
    """
    Génère un message d'erreur sécurisé sans exposer d'informations sensibles.
    """
    if include_details:
        # Mode développement uniquement
        return f"Erreur technique: {str(error)}"
    
    # Messages génériques pour production
    error_mapping = {
        "HTTPException": "Service temporairement indisponible",
        "ValidationError": "Format de données invalide",
        "TimeoutError": "Délai d'attente dépassé",
        "ConnectionError": "Problème de connexion au service"
    }
    
    error_type = type(error).__name__
    return error_mapping.get(error_type, "Une erreur inattendue s'est produite")