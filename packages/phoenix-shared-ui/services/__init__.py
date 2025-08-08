"""
Services partagés Phoenix UI
"""

# ✅ CORRECTION CRITIQUE: Import DataAnonymizer depuis phoenix-security (Clean Architecture)
try:
    from phoenix_security.services import DataAnonymizer
except ImportError:
    # Stub minimal pour éviter le couplage apps ← packages
    class DataAnonymizer:
        """Stub DataAnonymizer pour éviter couplage architectural."""
        def __init__(self): 
            self._available = False
        
        def anonymize_text(self, text: str):
            """Stub method - utiliser phoenix_security.services.DataAnonymizer pour fonctionnalité complète."""
            return type('Result', (), {'success': False, 'error': 'DataAnonymizer non disponible'})()
        
        @property
        def is_available(self) -> bool:
            return self._available

# ✅ Import du gestionnaire de session Dojo
from .dojo_session_manager import (
    DojoSessionManager,
    DojoSessionState,
    SessionStorageInterface,
    LocalStorageAdapter,
    SupabaseStorageAdapter,
    create_local_session_manager,
    create_supabase_session_manager
)

__all__ = [
    "DataAnonymizer",
    "DojoSessionManager",
    "DojoSessionState", 
    "SessionStorageInterface",
    "LocalStorageAdapter",
    "SupabaseStorageAdapter",
    "create_local_session_manager",
    "create_supabase_session_manager"
]