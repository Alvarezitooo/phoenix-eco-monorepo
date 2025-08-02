"""
🌉 Phoenix Event Bridge - Package partagé de l'écosystème Phoenix
Bus d'événements unifié pour l'Event-Sourcing avec Supabase

Expose les classes principales pour import dans les applications
"""

from .phoenix_event_bridge import (
    PhoenixEventType,
    PhoenixEventFactory,
    EventBridge,
    DataFlywheel,
    PhoenixEventData,
    SupabaseEventStore
)

__version__ = "1.0.0"
__all__ = [
    "PhoenixEventType",
    "PhoenixEventFactory", 
    "EventBridge",
    "DataFlywheel",
    "PhoenixEventData",
    "SupabaseEventStore"
]