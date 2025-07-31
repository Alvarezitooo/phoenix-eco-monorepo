import time
import threading
from functools import wraps
import streamlit as st

from utils.secure_logging import secure_logger

class RateLimiter:
    """Rate limiter thread-safe"""
    
    def __init__(self):
        self._limits = {}
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Vérifie si la requête est autorisée"""
        now = time.time()
        
        with self._lock:
            if key not in self._limits:
                self._limits[key] = []
            
            self._limits[key] = [
                timestamp for timestamp in self._limits[key]
                if now - timestamp < window_seconds
            ]
            
            if len(self._limits[key]) >= max_requests:
                secure_logger.log_security_event(
                    "RATE_LIMIT_EXCEEDED",
                    {"key": key[:10], "requests": len(self._limits[key])},
                    "WARNING"
                )
                return False
            
            self._limits[key].append(now)
            return True
    
    def get_remaining_requests(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Retourne le nombre de requêtes restantes"""
        now = time.time()
        
        with self._lock:
            if key not in self._limits:
                return max_requests
            
            recent_requests = [
                timestamp for timestamp in self._limits[key]
                if now - timestamp < window_seconds
            ]
            
            return max(0, max_requests - len(recent_requests))

rate_limiter = RateLimiter()

def rate_limit(max_requests: int, window_seconds: int):
    """Décorateur de rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_key = st.session_state.get('secure_session_id', 'anonymous')
            
            if not rate_limiter.is_allowed(client_key, max_requests, window_seconds):
                st.error("🚫 Trop de requêtes. Veuillez patienter avant de réessayer.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
