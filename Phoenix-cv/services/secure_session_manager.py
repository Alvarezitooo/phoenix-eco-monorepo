import streamlit as st
import threading
from datetime import datetime, timedelta
import hashlib
import hmac # Added import
from typing import Tuple, Any

from models.cv_data import CVTier
from utils.secure_crypto import secure_crypto
from utils.secure_logging import secure_logger
from config.security_config import SecurityConfig

class SecureSessionManager:
    """Gestionnaire de sessions sécurisé"""
    
    def __init__(self):
        self._active_sessions = {}
        self._lock = threading.Lock()
    
    def init_secure_session(self):
        """Initialise une session sécurisée"""
        if 'secure_session_id' not in st.session_state:
            st.session_state.secure_session_id = secure_crypto.generate_secure_token()
            st.session_state.session_created = datetime.utcnow()
            st.session_state.last_activity = datetime.utcnow()
        
        self._check_session_timeout()
        
        if 'user_tier' not in st.session_state:
            st.session_state.user_tier = CVTier.FREE
        
        if 'cv_count_monthly' not in st.session_state:
            st.session_state.cv_count_monthly = 0
        
        if 'current_cv_profile' not in st.session_state:
            st.session_state.current_cv_profile = None
        
        if 'csrf_token' not in st.session_state:
            st.session_state.csrf_token = secure_crypto.generate_secure_token(16)
        
        st.session_state.last_activity = datetime.utcnow()
    
    def _check_session_timeout(self):
        """Vérifie et gère le timeout de session"""
        if 'last_activity' in st.session_state:
            last_activity = st.session_state.last_activity
            if datetime.utcnow() - last_activity > timedelta(minutes=SecurityConfig.SESSION_TIMEOUT_MINUTES):
                secure_logger.log_security_event(
                    "SESSION_TIMEOUT",
                    {"session_age_minutes": (datetime.utcnow() - last_activity).total_seconds() / 60}
                )
                self.invalidate_session()
                st.error("🔒 Session expirée. Veuillez recharger la page.")
                st.stop()
    
    def invalidate_session(self):
        """Invalide la session courante"""
        secure_logger.log_security_event("SESSION_INVALIDATED", {})
        
        for key in list(st.session_state.keys()):
            if key not in ['page_config']:
                del st.session_state[key]
    
    def validate_csrf_token(self, provided_token: str) -> bool:
        """Valide le token CSRF"""
        expected_token = st.session_state.get('csrf_token')
        if not expected_token or not provided_token:
            return False
        
        return hmac.compare_digest(expected_token, provided_token)
    
    def check_limits(self, tier: CVTier) -> Tuple[bool, str]:
        """Vérifie les limites sécurisées selon le tier"""
        if tier == CVTier.FREE:
            if st.session_state.cv_count_monthly >= 1:
                secure_logger.log_security_event(
                    "USAGE_LIMIT_REACHED",
                    {"tier": tier.value, "count": st.session_state.cv_count_monthly}
                )
                return False, "Limite gratuite atteinte (1 CV/mois). Passez Pro pour CV illimités!"
        
        return True, ""
    
    def increment_usage(self):
        """Incrémente l'utilisation de façon thread-safe"""
        with self._lock:
            st.session_state.cv_count_monthly += 1
            secure_logger.log_security_event(
                "CV_GENERATION_COUNT",
                {"new_count": st.session_state.cv_count_monthly}
            )

secure_session = SecureSessionManager()
