import logging
import json
import threading
from datetime import datetime
from typing import Dict, Any, List
import hashlib
import streamlit as st # Temporaire, à revoir si Streamlit est toujours accessible ici

class SecureLogger:
    """Système de logging sécurisé sans PII"""
    
    def __init__(self):
        self.logger = logging.getLogger('phoenix_cv_secure')
        self._setup_secure_logging()
        self._security_events = []
        self._lock = threading.Lock()
    
    def _setup_secure_logging(self):
        """Configure le logging sécurisé"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """Log d'événement sécurisé sans PII"""
        try:
            with self._lock:
                safe_details = self._anonymize_log_data(details)
                
                event = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'event_type': event_type,
                    'details': safe_details,
                    'severity': severity,
                    'session_hash': self._get_session_hash()
                }
                
                self.logger.info(f"SECURITY_EVENT: {json.dumps(event)}")
                
                self._security_events.append(event)
                
                if len(self._security_events) > 1000:
                    self._security_events = self._security_events[-500:]
                    
        except Exception:
            pass
    
    def _anonymize_log_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymise les données de log"""
        safe_data = {}
        
        for key, value in data.items():
            if key.lower() in ['email', 'phone', 'name', 'address']:
                safe_data[key] = '[REDACTED]'
            elif isinstance(value, str) and len(value) > 100:
                safe_data[key] = f'[STRING_LENGTH_{len(value)}]'
            else:
                safe_data[key] = str(value)[:50]
        
        return safe_data
    
    def _get_session_hash(self) -> str:
        """Hash anonyme de session"""
        session_id = st.session_state.get('secure_session_id', 'anonymous')
        return hashlib.sha256(session_id.encode()).hexdigest()[:16]
    
    @property
    def recent_security_events(self) -> List[Dict]:
        """Retourne les événements récents (anonymisés)"""
        with self._lock:
            return self._security_events[-10:].copy()

secure_logger = SecureLogger()
