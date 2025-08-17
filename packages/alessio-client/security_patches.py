"""
🛡️ SECURITY PATCHES POUR ALESSIO CROSS-APP INTEGRATION
Corrections des vulnérabilités VUL-001 et VUL-002 identifiées dans l'audit.
"""

import logging
import html
import re
import hashlib
from typing import Dict, Any, Optional
from enum import Enum

from .base_client import AlessioAppContext # Import from base_client.py

logger = logging.getLogger(__name__)

class SecureContextBuilder:
    """
    Constructeur de contexte sécurisé pour prévenir les injections cross-app.
    Correction de VUL-001: Context Injection.
    """
    
    # Préfixes validés et sécurisés par contexte
    SECURE_CONTEXT_PREFIXES = {
        AlessioAppContext.LETTERS: "[PHOENIX-LETTERS]",
        AlessioAppContext.CV: "[PHOENIX-CV]",
        AlessioAppContext.RISE: "[PHOENIX-RISE]", 
        AlessioAppContext.WEBSITE: "[PHOENIX-WEB]"
    }
    
    # Patterns dangereux à filtrer
    DANGEROUS_PATTERNS = [
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"data:text/html",
        r"<iframe.*?>",
        r"<object.*?>",
        r"<embed.*?>",
        r"eval\s*\(",
        r"document\.",
        r"window\.",
        r"\[SYSTEM\]",
        r"\[ADMIN\]",
        r"</USER_DATA>",
        r"</SYSTEM_INSTRUCTIONS>"
    ]
    
    @classmethod
    def build_secure_contextual_message(cls, message: str, app_context: AlessioAppContext) -> str:
        """
        Construit un message contextuel sécurisé.
        
        Args:
            message: Message utilisateur à contextualiser
            app_context: Contexte d'application validé
            
        Returns:
            str: Message contextualisé et sécurisé
            
        Raises:
            ValueError: Si le contexte ou le message est invalide
        """
        # Validation du contexte d'application
        if not isinstance(app_context, AlessioAppContext):
            logger.warning(f"Invalid app context provided: {app_context}")
            raise ValueError("Contexte application invalide")
        
        # Validation et sanitisation du message
        if not message or not isinstance(message, str):
            raise ValueError("Message invalide ou vide")
        
        # Détection de patterns malveillants
        sanitized_message = cls._sanitize_message(message)
        
        # Construction sécurisée du contexte
        secure_prefix = cls.SECURE_CONTEXT_PREFIXES[app_context]
        
        # Échappement HTML pour prévenir injections
        escaped_message = html.escape(sanitized_message)
        
        # Construction du message final avec isolation
        contextual_message = f"{secure_prefix} {escaped_message}"
        
        # Validation finale
        cls._validate_final_message(contextual_message)
        
        logger.debug(f"Secure contextual message built for {app_context.value}")
        return contextual_message
    
    @classmethod
    def _sanitize_message(cls, message: str) -> str:
        """Sanitise le message en supprimant les patterns dangereux."""
        sanitized = message
        
        # Suppression des patterns dangereux
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, "[FILTERED_CONTENT]", sanitized, flags=re.IGNORECASE)
        
        # Limitation de taille pour prévenir DoS
        if len(sanitized) > 10000:
            logger.warning("Message too long, truncating")
            sanitized = sanitized[:10000] + "...[TRUNCATED]"
        
        # Suppression caractères de contrôle
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        return sanitized.strip()
    
    @classmethod
    def _validate_final_message(cls, message: str) -> None:
        """Validation finale du message construit."""
        # Vérification de patterns suspects résiduels
        suspicious_patterns = [
            "</USER_DATA>",
            "</SYSTEM_INSTRUCTIONS>",
            "[ADMIN]",
            "[SYSTEM]"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in message:
                logger.error(f"Suspicious pattern detected in final message: {pattern}")
                raise ValueError("Message contient du contenu potentiellement dangereux")

class SecureLogger:
    """
    Logger sécurisé pour prévenir l'exposition d'informations sensibles.
    Correction de VUL-002: Information Exposure in Logs.
    """
    
    @classmethod
    def log_alessio_interaction(cls, app_context: AlessioAppContext, user_id: str, message_preview: str = ""):
        """
        Log sécurisé des interactions Alessio.
        
        Args:
            app_context: Contexte d'application
            user_id: ID utilisateur à anonymiser
            message_preview: Aperçu du message à anonymiser
        """
        # Anonymisation de l'ID utilisateur
        anonymized_user_id = cls._anonymize_user_id(user_id)
        
        # Anonymisation du contexte
        anonymized_context = cls._anonymize_app_context(app_context)
        
        # Anonymisation du message
        safe_message_preview = cls._anonymize_message_preview(message_preview)
        
        # Log sécurisé
        logger.info(
            f"Alessio interaction - App: {anonymized_context}, "
            f"User: {anonymized_user_id}, "
            f"Preview: {safe_message_preview}"
        )
    
    @classmethod
    def log_security_event(cls, event_type: str, app_context: AlessioAppContext, details: Dict[str, Any]):
        """
        Log d'événements de sécurité avec anonymisation.
        
        Args:
            event_type: Type d'événement (injection_detected, validation_failed, etc.)
            app_context: Contexte d'application
            details: Détails à logger (seront anonymisés)
        """
        # Anonymisation des détails sensibles
        safe_details = cls._anonymize_security_details(details)
        
        # Log sécurisé
        logger.warning(
            f"Security event: {event_type} - "
            f"App: {cls._anonymize_app_context(app_context)} - "
            f"Details: {safe_details}"
        )
    
    @classmethod
    def _anonymize_user_id(cls, user_id: str) -> str:
        """Anonymise l'ID utilisateur pour les logs."""
        if not user_id or len(user_id) < 4:
            return "unknown"
        
        # Hash les 4 premiers caractères + masquage
        hash_prefix = hashlib.md5(user_id.encode()).hexdigest()[:4]
        return f"{user_id[:4]}***{hash_prefix}"
    
    @classmethod
    def _anonymize_app_context(cls, app_context: AlessioAppContext) -> str:
        """Anonymise le contexte d'application."""
        context_map = {
            AlessioAppContext.LETTERS: "L***",
            AlessioAppContext.CV: "C***", 
            AlessioAppContext.RISE: "R***",
            AlessioAppContext.WEBSITE: "W***"
        }
        return context_map.get(app_context, "UNK***")
    
    @classmethod
    def _anonymize_message_preview(cls, message: str, max_length: int = 20) -> str:
        """Crée un aperçu anonymisé du message."""
        if not message:
            return "[EMPTY]"
        
        # Suppression des données potentiellement sensibles
        sanitized = re.sub(r'\b\d{4,}\b', '[NUMBERS]', message)  # Numéros longs
        sanitized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', sanitized)  # Emails
        sanitized = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP]', sanitized)  # IPs
        
        # Troncature sécurisée
        preview = sanitized[:max_length]
        if len(sanitized) > max_length:
            preview += "..."
            
        return f"[{len(message)}ch] {preview}"
    
    @classmethod
    def _anonymize_security_details(cls, details: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymise les détails d'événements de sécurité."""
        safe_details = {}
        
        for key, value in details.items():
            if key in ['user_id', 'session_id']:
                safe_details[key] = cls._anonymize_user_id(str(value))
            elif key in ['message', 'content']:
                safe_details[key] = cls._anonymize_message_preview(str(value))
            elif key in ['pattern', 'threat_type']:
                # Ces info sont utiles pour debug sécurité
                safe_details[key] = str(value)[:50]  # Limitation longueur
            else:
                # Autres clés : anonymisation générale
                safe_details[key] = f"[{type(value).__name__}]"
        
        return safe_details

class SecureAlessioClient:
    """
    Client Alessio sécurisé avec les corrections appliquées.
    Intègre les corrections VUL-001 et VUL-002.
    """
    
    def __init__(self, app_context: AlessioAppContext, user_id: str, api_url: str):
        """
        Initialise le client sécurisé.
        
        Args:
            app_context: Contexte d'application validé
            user_id: ID utilisateur
            api_url: URL API Iris
        """
        # Validation du contexte
        if not isinstance(app_context, AlessioAppContext):
            raise ValueError("Contexte application invalide")
        
        # Validation de l'URL en production
        self._validate_api_url(api_url)
        
        self.app_context = app_context
        self.user_id = user_id
        self.api_url = api_url
        
        # Log sécurisé de l'initialisation
        SecureLogger.log_alessio_interaction(
            app_context=app_context,
            user_id=user_id,
            message_preview="[CLIENT_INIT]"
        )
    
    def send_secure_message(self, message: str, additional_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Envoie un message sécurisé à Alessio.
        
        Args:
            message: Message utilisateur
            additional_context: Contexte additionnel sécurisé
            
        Returns:
            str: Réponse d'Alessio
        """
        try:
            # Construction sécurisée du message contextuel
            contextual_message = SecureContextBuilder.build_secure_contextual_message(
                message=message,
                app_context=self.app_context
            )
            
            # Log sécurisé de l'interaction
            SecureLogger.log_alessio_interaction(
                app_context=self.app_context,
                user_id=self.user_id,
                message_preview=message
            )
            
            # TODO: Implémentation de l'envoi HTTP sécurisé
            # (timeout, validation réponse, etc.)
            
            return f"[SECURE] Message processed for {self.app_context.value}"
            
        except Exception as e:
            # Log sécurisé de l'erreur
            SecureLogger.log_security_event(
                event_type="message_processing_error",
                app_context=self.app_context,
                details={
                    "error": str(e),
                    "user_id": self.user_id,
                    "message_length": len(message)
                }
            )
            raise
    
    def _validate_api_url(self, api_url: str) -> None:
        """
        Valide l'URL API en fonction de l'environnement.
        """
        import os
        
        if not api_url:
            raise ValueError("URL API Iris manquante")
        
        # En production, forcer HTTPS
        if os.getenv('IRIS_ENV', 'production') == 'production':
            if not api_url.startswith('https://'):
                raise ValueError("HTTPS requis en production")
        
        # Validation du domaine (whitelist)
        allowed_domains = [
            'localhost',
            '127.0.0.1',
            'iris.phoenix-letters.app',  # Domaine de production
            'staging-iris.phoenix-letters.app'  # Domaine de staging
        ]
        
        from urllib.parse import urlparse
        parsed_url = urlparse(api_url)
        
        if parsed_url.hostname not in allowed_domains:
            logger.warning(f"Suspicious API URL domain: {parsed_url.hostname}")
            # En production, rejeter. En dev, warning seulement.
            if os.getenv('IRIS_ENV', 'production') == 'production':
                raise ValueError("Domaine API non autorisé")

# Fonction utilitaire pour migration
def create_secure_alessio_client(app_context: str, user_id: str, api_url: str) -> SecureAlessioClient:
    """
    Crée un client Alessio sécurisé à partir d'un contexte string.
    Fonction de transition pour compatibilité.
    """
    # Mapping string -> enum pour migration
    context_mapping = {
        "phoenix-letters": AlessioAppContext.LETTERS,
        "phoenix-cv": AlessioAppContext.CV,
        "phoenix-rise": AlessioAppContext.RISE,
        "phoenix-website": AlessioAppContext.WEBSITE
    }
    
    enum_context = context_mapping.get(app_context)
    if not enum_context:
        raise ValueError(f"Contexte application non reconnu: {app_context}")
    
    return SecureAlessioClient(
        app_context=enum_context,
        user_id=user_id,
        api_url=api_url
    )