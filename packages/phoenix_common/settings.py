# packages/phoenix_common/settings.py
# Unifie le chargement des variables (ENV > st.secrets > défaut)
# Conforme Directive V3 (sécurité, pas de secrets en clair)

from dataclasses import dataclass
import os

# Streamlit peut ne pas être dispo (tests, workers)
try:
    import streamlit as st  # type: ignore
    _SECRETS = dict(st.secrets) if hasattr(st, "secrets") else {}
except Exception:
    _SECRETS = {}

def _get(key: str, default: str = "") -> str:
    """Retourne la valeur depuis ENV, puis st.secrets, sinon défaut."""
    return os.getenv(key) or _SECRETS.get(key, default)

@dataclass(frozen=True)
class Settings:
    # Core services
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    STRIPE_PK: str = ""
    STRIPE_SK: str = ""          # ⚠️ idéalement côté backend seulement
    GEMINI_API_KEY: str = ""

    # Runtime
    ENV: str = "dev"             # dev|staging|prod
    PHOENIX_SAFE_MODE: bool = False

    # Observabilité (optionnels)
    SENTRY_DSN: str = ""
    POSTHOG_KEY: str = ""
    POSTHOG_HOST: str = "https://app.posthog.com"

def get_settings() -> Settings:
    """Construit l'objet Settings à partir de l'environnement."""
    return Settings(
        SUPABASE_URL=_get("SUPABASE_URL"),
        SUPABASE_ANON_KEY=_get("SUPABASE_ANON_KEY"),
        STRIPE_PK=_get("STRIPE_PK"),
        STRIPE_SK=_get("STRIPE_SK"),
        GEMINI_API_KEY=_get("GEMINI_API_KEY"),
        ENV=_get("ENV", "dev"),
        PHOENIX_SAFE_MODE=_get("PHOENIX_SAFE_MODE", "0") == "1",
        SENTRY_DSN=_get("SENTRY_DSN"),
        POSTHOG_KEY=_get("POSTHOG_KEY"),
        POSTHOG_HOST=_get("POSTHOG_HOST", "https://app.posthog.com"),
    )

def validate_env(S: Settings) -> list[str]:
    """
    Valide la config minimale requise pour démarrer l'app.
    Ajoute/retire des checks selon l'app (CV/Letters) et l'ENV.
    """
    errs: list[str] = []
    if not S.SUPABASE_URL:
        errs.append("SUPABASE_URL manquante")
    if not S.SUPABASE_ANON_KEY:
        errs.append("SUPABASE_ANON_KEY manquante")
    # Active ce check si l'app dépend de Gemini pour fonctionner:
    # if not S.GEMINI_API_KEY and S.ENV == "prod":
    #     errs.append("GEMINI_API_KEY manquante (prod)")
    return errs