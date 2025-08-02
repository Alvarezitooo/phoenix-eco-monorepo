# 🌉 Phoenix Event Bridge

Bus d'événements partagé de l'écosystème Phoenix pour Event-Sourcing avec Supabase.

## Usage

```python
from phoenix_event_bridge import PhoenixEventFactory, EventBridge

# Créer une instance du bridge
bridge = EventBridge()

# Utiliser le factory pour créer des événements
event_factory = PhoenixEventFactory(bridge)
```

## Architecture

Ce package permet aux applications Phoenix Letters, Phoenix CV et Phoenix Website de communiquer via un Event Store Supabase centralisé.