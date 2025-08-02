"""
🚀 Phoenix Database Connection - Connexion Supabase Unifiée
Gestion centralisée de la base de données pour tout l'écosystème Phoenix
"""

import logging
import os
from typing import Optional

from supabase import Client, ClientOptions, create_client

logger = logging.getLogger(__name__)


class PhoenixDatabaseConnection:
    """
    Connexion centralisée à Supabase pour l'écosystème Phoenix
    Gère la connexion, le schéma et les configurations communes
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        schema: str = "api",
    ):
        """
        Initialise la connexion Supabase Phoenix

        Args:
            supabase_url: URL Supabase (env SUPABASE_URL si None)
            supabase_key: Clé Supabase (env SUPABASE_KEY si None)
            schema: Schéma à utiliser (défaut: api)
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.schema = schema
        self.client: Optional[Client] = None

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL et SUPABASE_KEY doivent être définis")

    def initialize(self) -> None:
        """
        Initialise la connexion Supabase avec le schéma spécifié
        """
        try:
            # Options client avec schéma personnalisé
            options = ClientOptions(
                schema=self.schema,
                auto_refresh_token=True,
                persist_session=True,
                headers={"x-application-name": "phoenix-ecosystem"},
            )

            # Création du client Supabase
            self.client = create_client(
                supabase_url=self.supabase_url,
                supabase_key=self.supabase_key,
                options=options,
            )

            logger.info(
                f"✅ Connexion Supabase Phoenix initialisée (schéma: {self.schema})"
            )

        except Exception as e:
            logger.error(f"❌ Erreur initialisation Supabase Phoenix: {e}")
            raise ConnectionError(f"Impossible de se connecter à Supabase: {e}")

    def get_client(self) -> Client:
        """
        Retourne le client Supabase initialisé

        Returns:
            Client: Client Supabase prêt à utiliser
        """
        if self.client is None:
            self.initialize()

        return self.client

    def test_connection(self) -> bool:
        """
        Teste la connexion à la base de données

        Returns:
            bool: True si la connexion fonctionne
        """
        try:
            client = self.get_client()

            # Test simple de connexion
            response = client.from_("users").select("id").limit(1).execute()

            logger.info("✅ Test connexion Supabase Phoenix réussi")
            return True

        except Exception as e:
            logger.error(f"❌ Test connexion Supabase Phoenix échoué: {e}")
            return False

    def close(self) -> None:
        """
        Ferme la connexion (cleanup si nécessaire)
        """
        if self.client:
            # Supabase client n'a pas de méthode close explicit
            # Mais on peut nettoyer les références
            self.client = None
            logger.info("🔒 Connexion Supabase Phoenix fermée")


# Instance globale pour faciliter l'import
_phoenix_db_instance: Optional[PhoenixDatabaseConnection] = None


def get_phoenix_db_connection(
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    schema: str = "api",
) -> PhoenixDatabaseConnection:
    """
    Récupère ou crée l'instance globale de connexion Phoenix
    Pattern Singleton pour éviter les connexions multiples

    Args:
        supabase_url: URL Supabase (optionnel)
        supabase_key: Clé Supabase (optionnel)
        schema: Schéma à utiliser

    Returns:
        PhoenixDatabaseConnection: Instance de connexion
    """
    global _phoenix_db_instance

    if _phoenix_db_instance is None:
        _phoenix_db_instance = PhoenixDatabaseConnection(
            supabase_url=supabase_url, supabase_key=supabase_key, schema=schema
        )
        _phoenix_db_instance.initialize()

    return _phoenix_db_instance


def reset_phoenix_db_connection() -> None:
    """
    Réinitialise l'instance globale (utile pour les tests)
    """
    global _phoenix_db_instance
    if _phoenix_db_instance:
        _phoenix_db_instance.close()
    _phoenix_db_instance = None
