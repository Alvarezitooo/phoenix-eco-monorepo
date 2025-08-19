# packages/phoenix_shared_models/__init__.py
# 📊 Phoenix Shared Models
# Modèles de données partagés pour l'écosystème Phoenix

__version__ = "1.0.0"
__description__ = "Modèles de données partagés Phoenix"

# Imports des modèles existants s'ils existent
try:
    from .phoenix_shared_models.events import PhoenixEvent
    from .phoenix_shared_models.user_profile import UserProfile
except ImportError:
    # Fallback pour compatibilité
    pass

__all__ = [
    "PhoenixEvent",
    "UserProfile"
]