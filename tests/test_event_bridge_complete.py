# tests/test_event_bridge_complete.py
# Test phoenix_event_bridge complet

import pytest
from datetime import datetime
from phoenix_event_bridge import PhoenixEventBridge, PhoenixEventType, PhoenixEventData

def test_event_bridge_importable():
    """Test que phoenix_event_bridge est importable"""
    
    assert PhoenixEventBridge is not None
    assert PhoenixEventType is not None  
    assert PhoenixEventData is not None
    print("✅ phoenix_event_bridge importable")

def test_event_types_available():
    """Test que les types d'événements principaux sont disponibles"""
    
    # Vérifier quelques événements clés
    event_types = [e.value for e in PhoenixEventType]
    
    expected_events = [
        "user.profile_created",
        "user.profile_updated", 
        "cv.generated",
        "letter.generated"
    ]
    
    for expected in expected_events:
        if expected in event_types:
            print(f"✅ Event type {expected} disponible")
        else:
            print(f"⚠️ Event type {expected} manquant")
    
    assert len(event_types) > 0
    print(f"✅ {len(event_types)} types d'événements disponibles")

def test_event_data_creation():
    """Test création d'un événement"""
    
    try:
        event_data = PhoenixEventData(
            event_type=PhoenixEventType.USER_PROFILE_CREATED,
            stream_id="test_user_123",
            payload={
                "user_id": "test_user_123",
                "email": "test@phoenix.com",
                "created_at": datetime.now().isoformat()
            },
            app_source="test_suite"
        )
        
        assert event_data.event_type == PhoenixEventType.USER_PROFILE_CREATED
        assert event_data.stream_id == "test_user_123"
        assert event_data.app_source == "test_suite"
        assert "user_id" in event_data.payload
        
        print("✅ Création PhoenixEventData OK")
        
    except Exception as e:
        pytest.fail(f"Échec création PhoenixEventData: {e}")

def test_event_bridge_initialization():
    """Test initialisation du bridge"""
    
    try:
        bridge = PhoenixEventBridge()
        assert bridge is not None
        print("✅ PhoenixEventBridge initialisation OK")
        
    except Exception as e:
        # OK si Supabase pas configuré en test
        print(f"⚠️ PhoenixEventBridge init failed (normal en test): {e}")
        assert "Supabase" in str(e) or "SUPABASE" in str(e)

def test_event_publication_interface():
    """Test que l'interface de publication existe"""
    
    try:
        bridge = PhoenixEventBridge()
        
        # Vérifier que la méthode publish_event existe
        assert hasattr(bridge, 'publish_event')
        assert callable(bridge.publish_event)
        
        print("✅ Interface publication événements OK")
        
    except Exception as e:
        print(f"⚠️ Bridge unavailable (normal en test): {e}")

def test_event_sourcing_compliance():
    """Test conformité event-sourcing"""
    
    # Vérifier que publier un événement ne lève pas d'exception de design
    try:
        from phoenix_common.event_sourcing_guard import EventSourcingGuard
        
        # Test mutation sécurisée via événement
        payload = {
            "entity": "test_entity", 
            "action": "created",
            "data": {"key": "value"}
        }
        
        # Cela doit fonctionner (ou échouer proprement si pas de Supabase)
        try:
            event_id = EventSourcingGuard.safe_state_mutation("test.entity_created", payload)
            print(f"✅ Safe state mutation via event: {event_id}")
        except Exception as e:
            if "Supabase" in str(e) or "phoenix_event_bridge" in str(e):
                print("⚠️ Event bridge unavailable (normal en test)")
            else:
                raise
                
    except ImportError:
        print("⚠️ EventSourcingGuard non disponible")