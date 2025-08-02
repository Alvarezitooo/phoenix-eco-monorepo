"""
🚀 Phoenix Settings - Configuration Unifiée Écosystème
Gestion centralisée des paramètres pour toutes les apps Phoenix
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class PhoenixEnvironment(Enum):
    """Environnements Phoenix"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class PhoenixDatabaseConfig:
    """Configuration base de données Phoenix"""

    supabase_url: str
    supabase_key: str
    schema: str = "api"
    auto_refresh_token: bool = True
    persist_session: bool = True


@dataclass
class PhoenixJWTConfig:
    """Configuration JWT Phoenix"""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24h
    refresh_token_expire_days: int = 30


@dataclass
class PhoenixAppConfig:
    """Configuration spécifique à une app Phoenix"""

    app_name: str
    app_title: str
    app_icon: str
    app_description: str
    base_url: Optional[str] = None
    debug_mode: bool = False


class PhoenixSettings:
    """
    Configuration centralisée pour l'écosystème Phoenix
    Charge les paramètres depuis les variables d'environnement
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialise la configuration Phoenix

        Args:
            env_file: Fichier .env optionnel à charger
        """
        if env_file and os.path.exists(env_file):
            self._load_env_file(env_file)

        self.environment = PhoenixEnvironment(os.getenv("PHOENIX_ENV", "development"))

        # Configuration base de données
        self.database = PhoenixDatabaseConfig(
            supabase_url=self._get_required_env("SUPABASE_URL"),
            supabase_key=self._get_required_env("SUPABASE_KEY"),
            schema=os.getenv("SUPABASE_SCHEMA", "api"),
        )

        # Configuration JWT
        self.jwt = PhoenixJWTConfig(
            secret_key=self._get_required_env("JWT_SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(
                os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
            ),
            refresh_token_expire_days=int(
                os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30")
            ),
        )

        # Configuration des apps
        self.apps = {
            "letters": PhoenixAppConfig(
                app_name="letters",
                app_title="Phoenix Letters",
                app_icon="📝",
                app_description="Générateur IA de lettres de motivation",
                base_url=os.getenv(
                    "PHOENIX_LETTERS_URL", "https://phoenix-letters.streamlit.app"
                ),
                debug_mode=os.getenv("PHOENIX_LETTERS_DEBUG", "false").lower()
                == "true",
            ),
            "cv": PhoenixAppConfig(
                app_name="cv",
                app_title="Phoenix CV",
                app_icon="🔍",
                app_description="Générateur IA de CV optimisés",
                base_url=os.getenv(
                    "PHOENIX_CV_URL", "https://phoenix-cv.streamlit.app"
                ),
                debug_mode=os.getenv("PHOENIX_CV_DEBUG", "false").lower() == "true",
            ),
            "rise": PhoenixAppConfig(
                app_name="rise",
                app_title="Phoenix Rise",
                app_icon="🎯",
                app_description="Coach IA pour reconversion",
                base_url=os.getenv(
                    "PHOENIX_RISE_URL", "https://phoenix-rise.streamlit.app"
                ),
                debug_mode=os.getenv("PHOENIX_RISE_DEBUG", "false").lower() == "true",
            ),
            "site": PhoenixAppConfig(
                app_name="site",
                app_title="Phoenix Ecosystem",
                app_icon="🌐",
                app_description="Site vitrine Phoenix",
                base_url=os.getenv("PHOENIX_SITE_URL", "https://phoenix-ecosystem.com"),
                debug_mode=os.getenv("PHOENIX_SITE_DEBUG", "false").lower() == "true",
            ),
        }

        # Configuration générale
        self.general = {
            "timezone": os.getenv("PHOENIX_TIMEZONE", "Europe/Paris"),
            "language": os.getenv("PHOENIX_LANGUAGE", "fr"),
            "log_level": os.getenv("PHOENIX_LOG_LEVEL", "INFO"),
            "enable_analytics": os.getenv("PHOENIX_ANALYTICS", "true").lower()
            == "true",
            "enable_monitoring": os.getenv("PHOENIX_MONITORING", "true").lower()
            == "true",
        }

    def get_app_config(self, app_name: str) -> Optional[PhoenixAppConfig]:
        """
        Récupère la configuration d'une app spécifique

        Args:
            app_name: Nom de l'app (letters, cv, rise, site)

        Returns:
            Optional[PhoenixAppConfig]: Configuration de l'app
        """
        return self.apps.get(app_name)

    def is_production(self) -> bool:
        """Vérifie si on est en production"""
        return self.environment == PhoenixEnvironment.PRODUCTION

    def is_development(self) -> bool:
        """Vérifie si on est en développement"""
        return self.environment == PhoenixEnvironment.DEVELOPMENT

    def get_database_url(self) -> str:
        """Retourne l'URL complète de la base de données"""
        return f"{self.database.supabase_url}/rest/v1/"

    def _get_required_env(self, key: str) -> str:
        """
        Récupère une variable d'environnement requise

        Args:
            key: Nom de la variable

        Returns:
            str: Valeur de la variable

        Raises:
            ValueError: Si la variable n'est pas définie
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Variable d'environnement requise manquante: {key}")
        return value

    def _load_env_file(self, env_file: str) -> None:
        """
        Charge un fichier .env

        Args:
            env_file: Chemin vers le fichier .env
        """
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
        except Exception as e:
            print(f"⚠️ Erreur chargement fichier .env {env_file}: {e}")


# Instance globale de configuration
_phoenix_settings_instance: Optional[PhoenixSettings] = None


def get_phoenix_settings(env_file: Optional[str] = None) -> PhoenixSettings:
    """
    Récupère l'instance globale de configuration Phoenix
    Pattern Singleton pour éviter les recharges multiples

    Args:
        env_file: Fichier .env optionnel à charger

    Returns:
        PhoenixSettings: Instance de configuration
    """
    global _phoenix_settings_instance

    if _phoenix_settings_instance is None:
        _phoenix_settings_instance = PhoenixSettings(env_file=env_file)

    return _phoenix_settings_instance


def reset_phoenix_settings() -> None:
    """
    Réinitialise l'instance globale (utile pour les tests)
    """
    global _phoenix_settings_instance
    _phoenix_settings_instance = None
