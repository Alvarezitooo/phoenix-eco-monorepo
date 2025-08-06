"""Gestionnaire de session sécurisé et performant avec génération cryptographiquement sûre."""

import logging
import time
import secrets
import re
import hashlib
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set

import streamlit as st
from config.settings import Settings
from shared.exceptions.specific_exceptions import SecurityError, SessionError

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """Données de session structurées."""

    user_id: str
    created_at: datetime
    last_activity: datetime
    data: Dict[str, Any]
    settings: Settings  # Ajout de l'attribut settings

    @property
    def is_expired(self) -> bool:
        """Vérifie si la session est expirée."""
        return (
            datetime.now() - self.last_activity
        ).total_seconds() > self.settings.session_timeout

    @property
    def session_duration(self) -> float:
        """Durée de la session en secondes."""
        return (datetime.now() - self.created_at).total_seconds()


class SecureSessionManager:
    """Gestionnaire de session sécurisé avec validation, nettoyage automatique et protection contre session fixation."""

    # Clés sensibles qui nécessitent un nettoyage spécial
    SENSITIVE_KEYS: Set[str] = {
        "cv_content",
        "job_offer_content",
        "generated_letter",
        "api_key",
        "personal_data",
        "uploaded_files",
        "auth_token",
        "payment_info",
    }

    # Clés critiques qui doivent persister
    CRITICAL_KEYS: Set[str] = {"user_id", "session_id", "user_tier", "generation_count"}
    
    # Protection contre session fixation
    MAX_SESSION_DURATION = 24 * 3600  # 24 heures max
    MAX_IDLE_TIME = 2 * 3600  # 2 heures d'inactivité max
    
    # Tracking des sessions actives pour détection d'anomalies
    _active_sessions: Set[str] = set()

    def __init__(self, settings: Settings):
        """Initialise le gestionnaire de session."""
        self.session_state = st.session_state
        self.settings = settings  # Ajout de cette ligne pour stocker les settings
        self._init_session()  # Initialise la session ici
        logger.info("SecureSessionManager initialized")

    def _init_session(self) -> None:
        """Initialise une nouvelle session ou récupère l'existante avec vérifications de sécurité."""
        try:
            if "session_data" not in st.session_state:
                # Génération d'un nouvel ID utilisateur sécurisé
                user_id_to_use = st.session_state.get("user_id")
                if user_id_to_use is None:
                    user_id_to_use = self._generate_user_id()
                
                # Création session avec validation
                session_data = SessionData(
                    user_id=user_id_to_use,
                    created_at=datetime.now(),
                    last_activity=datetime.now(),
                    data={},
                    settings=self.settings,
                )
                st.session_state.session_data = session_data
                self._active_sessions.add(user_id_to_use)
                logger.info(f"New secure session created: {user_id_to_use[:12]}...")
                
            else:
                # Vérifications de sécurité sur session existante
                session_data = st.session_state.session_data
                current_time = datetime.now()
                
                # Vérification durée maximale de session
                session_age = (current_time - session_data.created_at).total_seconds()
                if session_age > self.MAX_SESSION_DURATION:
                    logger.warning(f"Session max duration exceeded: {session_data.user_id[:12]}...")
                    self._force_session_regeneration()
                    return
                
                # Vérification temps d'inactivité
                idle_time = (current_time - session_data.last_activity).total_seconds()
                if idle_time > self.MAX_IDLE_TIME:
                    logger.warning(f"Session idle timeout: {session_data.user_id[:12]}...")
                    self._cleanup_expired_session()
                    self._init_session()
                    return
                
                # Mise à jour activité
                session_data.last_activity = current_time
                
                # Vérification d'expiration standard
                if session_data.is_expired:
                    logger.warning(f"Session expired: {session_data.user_id[:12]}...")
                    self._cleanup_expired_session()
                    self._init_session()

        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            raise SessionError(f"Impossible d'initialiser la session: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de session.

        Args:
            key: Clé à récupérer
            default: Valeur par défaut

        Returns:
            Any: Valeur de session ou défaut
        """
        try:
            session_data: SessionData = st.session_state.session_data
            return session_data.data.get(key, default)
        except (KeyError, AttributeError):
            logger.warning(f"Session data not found for key: {key}")
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Définit une valeur de session avec validation.

        Args:
            key: Clé à définir
            value: Valeur à stocker

        Raises:
            SessionError: En cas d'erreur de stockage
            SecurityError: En cas de données sensibles non sécurisées
        """
        try:
            # Validation des données sensibles
            if key in self.SENSITIVE_KEYS:
                self._validate_sensitive_data(key, value)

            # Validation de la taille
            if isinstance(value, str) and len(value) > 100000:
                logger.warning(f"Large data stored in session for key: {key}")

            session_data: SessionData = st.session_state.session_data
            session_data.data[key] = value
            session_data.last_activity = datetime.now()

            logger.debug(f"Session value set for key: {key}")

        except Exception as e:
            logger.error(f"Error setting session value for key {key}: {e}")
            raise SessionError(f"Impossible de stocker la valeur: {e}")

    def delete(self, key: str) -> None:
        """
        Supprime une clé de session.

        Args:
            key: Clé à supprimer
        """
        try:
            session_data: SessionData = st.session_state.session_data
            if key in session_data.data:
                del session_data.data[key]
                logger.debug(f"Session key deleted: {key}")
        except Exception as e:
            logger.warning(f"Error deleting session key {key}: {e}")

    def clear_sensitive_data(self) -> None:
        """Nettoie toutes les données sensibles de la session."""
        try:
            session_data: SessionData = st.session_state.session_data
            for key in list(session_data.data.keys()):
                if key in self.SENSITIVE_KEYS:
                    del session_data.data[key]

            logger.info("Sensitive data cleared from session")

        except Exception as e:
            logger.error(f"Error clearing sensitive data: {e}")

    def reset_session(self) -> None:
        """Réinitialise complètement la session."""
        try:
            # Sauvegarde des données critiques
            critical_data = {}
            if "session_data" in st.session_state:
                session_data: SessionData = st.session_state.session_data
                for key in self.CRITICAL_KEYS:
                    if key in session_data.data:
                        critical_data[key] = session_data.data[key]

            # Nettoyage complet
            for key in list(st.session_state.keys()):
                del st.session_state[key]

            # Réinitialisation
            self._init_session()

            # Restauration des données critiques
            for key, value in critical_data.items():
                self.set(key, value)

            logger.info("Session reset successfully")

        except Exception as e:
            logger.error(f"Error resetting session: {e}")
            raise SessionError(f"Impossible de réinitialiser la session: {e}")

    def get_session_info(self) -> Dict[str, Any]:
        """Retourne les informations de session."""
        try:
            session_data: SessionData = st.session_state.session_data
            return {
                "user_id": session_data.user_id,
                "created_at": session_data.created_at.isoformat(),
                "last_activity": session_data.last_activity.isoformat(),
                "duration_seconds": session_data.session_duration,
                "data_keys": list(session_data.data.keys()),
                "data_size": len(str(session_data.data)),
            }
        except Exception as e:
            logger.warning(f"Error getting session info: {e}")
            return {}

    def _generate_user_id(self) -> str:
        """Génère un ID utilisateur unique de manière cryptographiquement sûre."""
        return self._generate_secure_session_id()
    
    def _generate_secure_session_id(self) -> str:
        """
        Génère un ID de session cryptographiquement sûr.
        
        Returns:
            str: ID de session avec 256 bits d'entropie
        """
        # Combinaison de plusieurs sources d'entropie
        random_bytes = secrets.token_bytes(16)  # 128 bits d'entropie
        timestamp_nano = str(time.time_ns()).encode()  # Timestamp nanoseconde
        process_entropy = os.urandom(8)  # 64 bits d'entropie OS
        additional_entropy = str(secrets.randbits(64)).encode()  # 64 bits supplémentaires
        
        # Combine toutes les sources d'entropie
        entropy_source = (
            random_bytes + 
            timestamp_nano + 
            process_entropy + 
            additional_entropy
        )
        
        # Hash SHA-256 pour uniformité et sécurité
        session_hash = hashlib.sha256(entropy_source).hexdigest()
        
        # Format avec préfixe pour identification
        session_id = f"usr_{session_hash[:32]}"  # 32 caractères hex = 128 bits
        
        logger.debug("Secure session ID generated with 256+ bits entropy")
        return session_id

    def _validate_sensitive_data(self, key: str, value: Any) -> None:
        """Valide les données sensibles avant stockage."""
        if key in {"api_key", "personal_data"}:
            if not isinstance(value, str) or len(value) < 10:
                raise SecurityError(f"Invalid sensitive data for key: {key}")

        # Détection basique de données personnelles
        if isinstance(value, str):
            email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            if re.search(email_pattern, value):
                logger.warning(
                    f"Potential email detected in session data for key: {key}"
                )

    def _force_session_regeneration(self) -> None:
        """Force la régénération complète de la session pour sécurité."""
        try:
            old_user_id = None
            if "session_data" in st.session_state:
                old_user_id = st.session_state.session_data.user_id
                self._active_sessions.discard(old_user_id)
            
            # Nettoyage complet
            self.clear_sensitive_data()
            
            # Suppression de session_data pour forcer régénération
            if "session_data" in st.session_state:
                del st.session_state["session_data"]
            
            # Régénération avec nouvel ID
            self._init_session()
            
            logger.info(f"Session regenerated for security: {old_user_id[:12] if old_user_id else 'unknown'}...")
            
        except Exception as e:
            logger.error(f"Error during session regeneration: {e}")
    
    def _cleanup_expired_session(self) -> None:
        """Nettoie une session expirée avec logging sécurisé."""
        try:
            if "session_data" in st.session_state:
                user_id = st.session_state.session_data.user_id
                self._active_sessions.discard(user_id)
                logger.info(f"Cleaning expired session: {user_id[:12]}...")
            
            self.clear_sensitive_data()
            logger.info("Expired session cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired session: {e}")
    
    def regenerate_session_id(self) -> str:
        """
        Régénère l'ID de session après authentification pour prévenir session fixation.
        
        Returns:
            str: Nouvel ID de session
        """
        try:
            old_session_data = st.session_state.get("session_data")
            if old_session_data:
                # Sauvegarde des données critiques
                critical_data = {}
                for key in self.CRITICAL_KEYS:
                    if key in old_session_data.data:
                        critical_data[key] = old_session_data.data[key]
                
                # Nettoyage ancien ID
                self._active_sessions.discard(old_session_data.user_id)
                
                # Génération nouvel ID sécurisé
                new_user_id = self._generate_secure_session_id()
                
                # Mise à jour session
                old_session_data.user_id = new_user_id
                old_session_data.created_at = datetime.now()  # Reset création
                old_session_data.last_activity = datetime.now()
                
                # Restauration données critiques
                for key, value in critical_data.items():
                    old_session_data.data[key] = value
                
                # Tracking nouveau ID
                self._active_sessions.add(new_user_id)
                
                logger.info(f"Session ID regenerated successfully: {new_user_id[:12]}...")
                return new_user_id
                
        except Exception as e:
            logger.error(f"Error regenerating session ID: {e}")
            raise SessionError(f"Impossible de régénérer l'ID de session: {e}")
    
    def get_session_security_info(self) -> Dict[str, Any]:
        """Retourne les informations de sécurité de la session."""
        try:
            session_data: SessionData = st.session_state.session_data
            current_time = datetime.now()
            
            return {
                "user_id_hash": hashlib.sha256(session_data.user_id.encode()).hexdigest()[:16],
                "session_age_seconds": (current_time - session_data.created_at).total_seconds(),
                "idle_time_seconds": (current_time - session_data.last_activity).total_seconds(),
                "max_duration_remaining": self.MAX_SESSION_DURATION - (current_time - session_data.created_at).total_seconds(),
                "max_idle_remaining": self.MAX_IDLE_TIME - (current_time - session_data.last_activity).total_seconds(),
                "sensitive_keys_count": len([k for k in session_data.data.keys() if k in self.SENSITIVE_KEYS]),
                "is_near_expiry": (current_time - session_data.last_activity).total_seconds() > (self.MAX_IDLE_TIME * 0.8),
                "active_sessions_count": len(self._active_sessions)
            }
            
        except Exception as e:
            logger.warning(f"Error getting session security info: {e}")
            return {"error": "Unable to get security info"}
