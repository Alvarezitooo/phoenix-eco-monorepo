"""
🌉 Phoenix Event Bridge - Package partagé de l'écosystème Phoenix
Bus d'événements unifié pour l'Event-Sourcing avec Supabase

Expose les classes principales pour import dans les applications
"""

# Importe les classes et types nécessaires depuis les modules internes
from .phoenix_event_bridge import (
    PhoenixEventBridge,
    PhoenixEventData,
    PhoenixEventType,
    PhoenixEventFactory
)

# Définit explicitement ce qui est exporté lorsque 'from phoenix_event_bridge import *' est utilisé
# ou ce que les outils d'introspection doivent considérer comme l'API publique.
__version__ = "1.0.0"
__all__ = [
    "PhoenixEventBridge",      # ✅ Le nom de classe original est maintenant exposé
    "PhoenixEventType",
    "PhoenixEventFactory",
    "PhoenixEventData",
]