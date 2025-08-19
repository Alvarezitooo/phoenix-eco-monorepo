# packages/phoenix_shared_ui/__init__.py
# 🎨 Phoenix Shared UI Components
# Interface utilisateur unifiée pour l'écosystème Phoenix

__version__ = "1.0.0"
__description__ = "Composants UI partagés Phoenix"

# Exports principaux
from .components.common import PhoenixProgressBar
from .components.header import render_header
from .components.consent_banner import render_consent_banner

__all__ = [
    "PhoenixProgressBar",
    "render_header", 
    "render_consent_banner"
]