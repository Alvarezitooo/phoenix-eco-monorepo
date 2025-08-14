"""
🔐 Phoenix Shared Auth - Package d'authentification unifié
Version: 1.0.0 - Contrat d'Exécution V5
"""

from .client import AuthManager, get_auth_manager

__version__ = "1.0.0"
__all__ = ["AuthManager", "get_auth_manager"]