"""
Services partagés Phoenix UI
"""

# Import du service d'anonymisation
try:
    from .data_anonymizer import DataAnonymizer
except ImportError:
    # Mode dégradé - utilisation du DataAnonymizer de Phoenix Rise
    try:
        from apps.phoenix_rise.phoenix_rise.utils.security import DataAnonymizer
    except ImportError:
        pass

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