"""
🏛️ PHOENIX COMMON - Settings Unifié
Configuration centralisée pour tout l'écosystème Phoenix
Conforme au Contrat d'Exécution V5

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Settings Unifié
"""

from dataclasses import dataclass
import os
from typing import Optional

# 🛡️ SÉCURITÉ: Import Streamlit sécurisé
try:
    import streamlit as st  # type: ignore
    _S = dict(st.secrets) if hasattr(st, "secrets") else {}
except Exception:
    _S = {}

def _get(k: str, default: str = "") -> str:
    """
    Récupération sécurisée des variables d'environnement
    Priorité: os.environ > st.secrets > default
    
    Args:
        k: Clé de configuration
        default: Valeur par défaut
        
    Returns:
        Valeur de configuration
    """
    return os.getenv(k) or _S.get(k, default)

@dataclass(frozen=True)
class Settings:
    """
    Configuration unifiée Phoenix Ecosystem
    Respecte le Contrat d'Exécution V5:
    - Gestion des secrets via variables d'environnement
    - Fallback Streamlit secrets
    - Immutable (frozen=True)
    """
    
    # 🗄️ Supabase (Services partagés obligatoires V5)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    # 💳 Stripe (Cycle de vie client V5)
    STRIPE_PK: str = ""
    STRIPE_SK: str = ""
    
    # 🤖 IA Services
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # 🌍 Environment
    ENV: str = "dev"
    DEBUG: bool = False
    
    # 🛡️ Security & Safety
    PHOENIX_SAFE_MODE: bool = False
    RATE_LIMIT_ENABLED: bool = True
    
    # 📊 Monitoring
    POSTHOG_API_KEY: str = ""
    SENTRY_DSN: str = ""
    
    # 🔗 URLs & Endpoints
    PHOENIX_BACKEND_URL: str = ""
    ALESSIO_API_URL: str = ""
    
    def is_production(self) -> bool:
        """Vérifie si on est en production"""
        return self.ENV.lower() in ["prod", "production"]
    
    def is_development(self) -> bool:
        """Vérifie si on est en développement"""
        return self.ENV.lower() in ["dev", "development", "local"]
    
    def has_supabase(self) -> bool:
        """Vérifie si Supabase est configuré"""
        return bool(self.SUPABASE_URL and self.SUPABASE_ANON_KEY)
    
    def has_stripe(self) -> bool:
        """Vérifie si Stripe est configuré"""
        return bool(self.STRIPE_PK and self.STRIPE_SK)
    
    def has_gemini(self) -> bool:
        """Vérifie si Gemini est configuré"""
        return bool(self.GEMINI_API_KEY)

def get_settings() -> Settings:
    """
    Factory pour obtenir la configuration Phoenix unifiée
    
    Returns:
        Instance Settings avec toutes les configurations
    """
    return Settings(
        # Supabase
        SUPABASE_URL=_get("SUPABASE_URL"),
        SUPABASE_ANON_KEY=_get("SUPABASE_ANON_KEY"),
        
        # Stripe
        STRIPE_PK=_get("STRIPE_PK"),
        STRIPE_SK=_get("STRIPE_SK"),
        
        # IA
        GEMINI_API_KEY=_get("GEMINI_API_KEY"),
        OPENAI_API_KEY=_get("OPENAI_API_KEY"),
        
        # Environment
        ENV=_get("ENV", "dev"),
        DEBUG=_get("DEBUG", "0") == "1",
        
        # Security
        PHOENIX_SAFE_MODE=_get("PHOENIX_SAFE_MODE", "0") == "1",
        RATE_LIMIT_ENABLED=_get("RATE_LIMIT_ENABLED", "1") == "1",
        
        # Monitoring
        POSTHOG_API_KEY=_get("POSTHOG_API_KEY"),
        SENTRY_DSN=_get("SENTRY_DSN"),
        
        # URLs
        PHOENIX_BACKEND_URL=_get("PHOENIX_BACKEND_URL", "http://localhost:8000"),
        ALESSIO_API_URL=_get("ALESSIO_API_URL", "http://localhost:8003"),
    )

# Instance globale pour compatibilité
settings = get_settings()