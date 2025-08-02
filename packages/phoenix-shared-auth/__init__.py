"""
🚀 Phoenix Shared Auth - Module d'Authentification Unifié
Architecture centralisée pour tout l'écosystème Phoenix (Letters, CV, Rise)

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Unified Supabase Authentication
"""

from .config.phoenix_settings import PhoenixSettings, get_phoenix_settings
from .database.phoenix_db_connection import (
    PhoenixDatabaseConnection,
    get_phoenix_db_connection,
)
from .entities.phoenix_user import PhoenixApp, PhoenixUser, UserTier
from .middleware.phoenix_streamlit_auth import PhoenixStreamlitAuth
from .services.jwt_manager import JWTManager
from .services.phoenix_auth_service import PhoenixAuthService

__version__ = "1.0.0"
__author__ = "Claude Phoenix DevSecOps Guardian"

__all__ = [
    "get_phoenix_settings",
    "PhoenixSettings",
    "get_phoenix_db_connection",
    "PhoenixDatabaseConnection",
    "PhoenixUser",
    "PhoenixApp",
    "UserTier",
    "PhoenixAuthService",
    "JWTManager",
    "PhoenixStreamlitAuth",
]
