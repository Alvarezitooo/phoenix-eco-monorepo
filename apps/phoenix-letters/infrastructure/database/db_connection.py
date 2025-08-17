"""
🏛️ CONSOLIDATION: Gestionnaire de connexion Supabase unifié pour Phoenix Letters
Utilise le client centralisé phoenix_common au lieu de duplications locales

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Consolidation Supabase
"""

import logging
from typing import Optional
from supabase import Client
from shared.exceptions.specific_exceptions import DatabaseError

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    🏛️ CONSOLIDATION: Délègue au client Supabase centralisé
    """

    _client: Optional[Client] = None

    def __init__(self, settings=None):
        """
        Initialise avec le client centralisé phoenix_common
        
        Args:
            settings: Ignoré, garde compatibilité API
        """
        try:
            # 🏛️ CONSOLIDATION: Utilisation client centralisé
            from phoenix_common.clients import get_supabase_client
            self._client = get_supabase_client()
            logger.info("Client Supabase centralisé initialisé pour Phoenix Letters")
            
        except Exception as e:
            logger.error(f"Erreur client Supabase centralisé: {e}")
            raise DatabaseError(f"Impossible de charger client Supabase centralisé: {e}")

    def get_client(self) -> Client:
        """Retourne le client Supabase centralisé."""
        if not self._client:
            raise DatabaseError("Le client Supabase centralisé n'a pas été initialisé.")
        return self._client

# 🏛️ CONSOLIDATION: Factory function pour compatibilité
def get_database_client() -> Client:
    """
    Factory centralisée pour client Supabase Phoenix Letters
    
    Returns:
        Client Supabase configuré via phoenix_common
    """
    try:
        from phoenix_common.clients import get_supabase_client
        return get_supabase_client()
    except Exception as e:
        logger.error(f"Factory client Supabase échec: {e}")
        raise DatabaseError(f"Factory client Supabase échec: {e}")