import os
from dataclasses import dataclass, field
from typing import Optional, Tuple
from dotenv import load_dotenv

class ConfigurationError(Exception):
    """Exception levée quand une variable d'environnement requise est manquante."""
    pass

@dataclass(frozen=True)
class Settings:
    """
    Configuration unifiée pour tout l'écosystème Phoenix.
    Charge les variables depuis l'environnement ou un fichier .env à la racine.
    """
    # API Configuration
    google_api_key: Optional[str] = None
    france_travail_client_id: Optional[str] = None
    france_travail_client_secret: Optional[str] = None

    # Supabase (Base de données et Auth)
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # JWT (Authentification)
    jwt_secret_key: str = "a_default_dev_secret_key_that_is_not_secure"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    # Stripe (Paiement)
    stripe_publishable_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_price_id_premium: Optional[str] = None

    # Application & Security
    dev_mode: bool = False
    auth_enabled: bool = True
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    allowed_file_types: Tuple[str, ...] = (".pdf", ".txt")
    session_timeout: int = 3600  # 1 hour

    # Feature Flags
    enable_mirror_match: bool = True
    enable_smart_coach: bool = True
    enable_trajectory_builder: bool = True

    def __post_init__(self):
        # Charger les variables d'environnement depuis un fichier .env à la racine
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path, override=True)

        # Utiliser object.__setattr__ car la classe est frozen
        def set_attr(name, value):
            object.__setattr__(self, name, value)

        # Assignations depuis l'environnement
        set_attr("google_api_key", self._get_required_env("GEMINI_API_KEY")) # Note: Renaming for consistency
        set_attr("france_travail_client_id", os.getenv("FRANCETRAVAIL_CLIENT_ID"))
        set_attr("france_travail_client_secret", os.getenv("FRANCETRAVAIL_CLIENT_SECRET"))
        set_attr("supabase_url", self._get_required_env("SUPABASE_URL"))
        set_attr("supabase_key", self._get_required_env("SUPABASE_KEY"))
        set_attr("jwt_secret_key", os.getenv("JWT_SECRET_KEY", self.jwt_secret_key))
        set_attr("stripe_secret_key", os.getenv("STRIPE_SECRET_KEY"))
        set_attr("stripe_webhook_secret", os.getenv("STRIPE_WEBHOOK_SECRET"))
        set_attr("stripe_publishable_key", os.getenv("STRIPE_PUBLISHABLE_KEY"))
        set_attr("stripe_price_id_premium", os.getenv("STRIPE_PRICE_ID_PREMIUM"))
        set_attr("dev_mode", os.getenv("DEV_MODE", "false").lower() == "true")

    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ConfigurationError(f"Variable d'environnement requise '{key}' est manquante.")
        return value

    def is_valid_for_db(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    def is_valid_for_stripe(self) -> bool:
        return bool(self.stripe_secret_key and self.stripe_webhook_secret)