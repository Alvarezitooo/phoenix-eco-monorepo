"""
🧪 Tests pour Phoenix Event Bridge
Tests unitaires pour valider l'architecture Event-Sourcing

Author: Claude Phoenix DevSecOps Guardian
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from packages.phoenix_event_bridge.event_bridge import PhoenixEventBridge, PhoenixCVEventHelper
from packages.phoenix_event_bridge.phoenix_event_types import PhoenixEventData, PhoenixEventType, PhoenixEventStream


class TestPhoenixEventData:
    """Tests pour la classe PhoenixEventData"""
    
    def test_event_data_creation(self):
        """Test création d'un événement"""
        # Arrange & Act
        event = PhoenixEventData(
            event_id="test-event-123",
            event_type=PhoenixEventType.USER_REGISTERED,
            stream_id="user-456",
            timestamp=datetime.now(),
            app_source="cv",
            payload={"email": "test@example.com"}
        )
        
        # Assert
        assert event.event_id == "test-event-123"
        assert event.event_type == PhoenixEventType.USER_REGISTERED
        assert event.stream_id == "user-456"
        assert event.app_source == "cv"
        assert event.payload["email"] == "test@example.com"
        assert event.version == "1.0"
    
    def test_event_data_auto_generation(self):
        """Test génération automatique des IDs"""
        # Arrange & Act
        event = PhoenixEventData(
            event_id="",  # Vide, doit être auto-généré
            event_type=PhoenixEventType.CV_GENERATED,
            stream_id="user-789",
            timestamp=None,  # Doit être auto-généré
            app_source="cv"
        )
        
        # Assert
        assert event.event_id != ""
        assert len(event.event_id) > 10  # UUID généré
        assert event.timestamp is not None
        assert event.payload == {}  # Dict vide par défaut
    
    def test_event_data_to_dict(self):
        """Test sérialisation en dictionnaire"""
        # Arrange
        timestamp = datetime.now()
        event = PhoenixEventData(
            event_id="test-123",
            event_type=PhoenixEventType.LETTER_GENERATED,
            stream_id="user-456",
            timestamp=timestamp,
            app_source="letters",
            payload={"job_title": "Developer"}
        )
        
        # Act
        event_dict = event.to_dict()
        
        # Assert
        assert event_dict["event_id"] == "test-123"
        assert event_dict["event_type"] == "letter.generated"
        assert event_dict["stream_id"] == "user-456"
        assert event_dict["timestamp"] == timestamp.isoformat()
        assert event_dict["app_source"] == "letters"
        assert event_dict["payload"]["job_title"] == "Developer"
    
    def test_event_data_from_dict(self):
        """Test désérialisation depuis dictionnaire"""
        # Arrange
        timestamp = datetime.now()
        event_dict = {
            "event_id": "test-456",
            "event_type": "user.signed_in",
            "stream_id": "user-789",
            "timestamp": timestamp.isoformat(),
            "app_source": "website",
            "payload": {"method": "email"},
            "version": "1.0"
        }
        
        # Act
        event = PhoenixEventData.from_dict(event_dict)
        
        # Assert
        assert event.event_id == "test-456"
        assert event.event_type == PhoenixEventType.USER_SIGNED_IN
        assert event.stream_id == "user-789"
        assert event.app_source == "website"
        assert event.payload["method"] == "email"


class TestPhoenixEventStream:
    """Tests pour la classe PhoenixEventStream"""
    
    def test_event_stream_creation(self):
        """Test création d'un stream d'événements"""
        # Arrange
        created_at = datetime.now()
        
        # Act
        stream = PhoenixEventStream(
            stream_id="user-123",
            events=[],
            created_at=created_at,
            updated_at=created_at
        )
        
        # Assert
        assert stream.stream_id == "user-123"
        assert stream.events == []
        assert stream.version == 1
    
    def test_add_event_to_stream(self):
        """Test ajout d'événement au stream"""
        # Arrange
        stream = PhoenixEventStream(
            stream_id="user-123",
            events=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        event = PhoenixEventData(
            event_id="event-1",
            event_type=PhoenixEventType.CV_UPLOADED,
            stream_id="user-123",
            timestamp=datetime.now(),
            app_source="cv"
        )
        
        # Act
        initial_version = stream.version
        stream.add_event(event)
        
        # Assert
        assert len(stream.events) == 1
        assert stream.events[0] == event
        assert stream.version == initial_version + 1
    
    def test_add_event_wrong_stream_id(self):
        """Test erreur si stream_id ne correspond pas"""
        # Arrange
        stream = PhoenixEventStream(
            stream_id="user-123",
            events=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        event = PhoenixEventData(
            event_id="event-1",
            event_type=PhoenixEventType.CV_UPLOADED,
            stream_id="user-456",  # Différent du stream
            timestamp=datetime.now(),
            app_source="cv"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Event stream_id user-456 doesn't match stream user-123"):
            stream.add_event(event)
    
    def test_get_events_by_type(self):
        """Test filtrage des événements par type"""
        # Arrange
        stream = PhoenixEventStream(
            stream_id="user-123",
            events=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Ajouter plusieurs événements
        events = [
            PhoenixEventData("", PhoenixEventType.CV_UPLOADED, "user-123", datetime.now(), "cv"),
            PhoenixEventData("", PhoenixEventType.LETTER_GENERATED, "user-123", datetime.now(), "letters"),
            PhoenixEventData("", PhoenixEventType.CV_GENERATED, "user-123", datetime.now(), "cv")
        ]
        
        for event in events:
            stream.add_event(event)
        
        # Act
        cv_events = stream.get_events_by_type(PhoenixEventType.CV_UPLOADED)
        
        # Assert
        assert len(cv_events) == 1
        assert cv_events[0].event_type == PhoenixEventType.CV_UPLOADED


class TestPhoenixEventBridge:
    """Tests pour la classe PhoenixEventBridge"""
    
    def test_event_bridge_initialization(self):
        """Test initialisation du bridge"""
        # Act
        bridge = PhoenixEventBridge()
        
        # Assert
        assert bridge.supabase_client is None
        assert bridge.event_handlers == {}
        assert bridge.streams == {}
        assert bridge.enable_persistence is True
        assert bridge.enable_logging is True
    
    @pytest.mark.asyncio
    async def test_publish_event_success(self):
        """Test publication d'événement réussie"""
        # Arrange
        bridge = PhoenixEventBridge()
        
        event = PhoenixEventData(
            event_id="test-123",
            event_type=PhoenixEventType.USER_REGISTERED,
            stream_id="user-456",
            timestamp=datetime.now(),
            app_source="website"
        )
        
        # Act
        result = await bridge.publish_event(event)
        
        # Assert
        assert result is True
        assert "user-456" in bridge.streams
        assert len(bridge.streams["user-456"].events) == 1
    
    @pytest.mark.asyncio
    async def test_publish_event_with_supabase(self):
        """Test publication avec persistance Supabase"""
        # Arrange
        mock_supabase = Mock()
        mock_table = Mock()
        mock_response = Mock()
        mock_response.data = [{"id": 1}]
        
        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = mock_response
        
        bridge = PhoenixEventBridge(supabase_client=mock_supabase)
        
        event = PhoenixEventData(
            event_id="test-456",
            event_type=PhoenixEventType.CV_GENERATED,
            stream_id="user-789",
            timestamp=datetime.now(),
            app_source="cv"
        )
        
        # Act
        result = await bridge.publish_event(event)
        
        # Assert
        assert result is True
        mock_supabase.table.assert_called_with('phoenix_events')
        mock_table.insert.assert_called_once()
        mock_table.execute.assert_called_once()
    
    def test_subscribe_to_event(self):
        """Test abonnement à un type d'événement"""
        # Arrange
        bridge = PhoenixEventBridge()
        handler_called = []
        
        def test_handler(event):
            handler_called.append(event)
        
        # Act
        bridge.subscribe(PhoenixEventType.USER_SIGNED_IN, test_handler)
        
        # Assert
        assert PhoenixEventType.USER_SIGNED_IN in bridge.event_handlers
        assert len(bridge.event_handlers[PhoenixEventType.USER_SIGNED_IN]) == 1
    
    @pytest.mark.asyncio
    async def test_notify_handlers(self):
        """Test notification des handlers d'événements"""
        # Arrange
        bridge = PhoenixEventBridge()
        handler_calls = []
        
        def sync_handler(event):
            handler_calls.append(f"sync_{event.event_id}")
        
        async def async_handler(event):
            handler_calls.append(f"async_{event.event_id}")
        
        bridge.subscribe(PhoenixEventType.PAYMENT_SUCCEEDED, sync_handler)
        bridge.subscribe(PhoenixEventType.PAYMENT_SUCCEEDED, async_handler)
        
        event = PhoenixEventData(
            event_id="payment-123",
            event_type=PhoenixEventType.PAYMENT_SUCCEEDED,
            stream_id="user-456",
            timestamp=datetime.now(),
            app_source="billing"
        )
        
        # Act
        await bridge.publish_event(event)
        
        # Assert
        assert len(handler_calls) == 2
        assert "sync_payment-123" in handler_calls
        assert "async_payment-123" in handler_calls
    
    def test_get_user_journey(self):
        """Test récupération du parcours utilisateur"""
        # Arrange
        bridge = PhoenixEventBridge()
        user_id = "user-123"
        
        # Créer un stream avec des événements
        stream = PhoenixEventStream(
            stream_id=user_id,
            events=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        events = [
            PhoenixEventData("", PhoenixEventType.USER_REGISTERED, user_id, datetime.now(), "website"),
            PhoenixEventData("", PhoenixEventType.CV_UPLOADED, user_id, datetime.now(), "cv"),
            PhoenixEventData("", PhoenixEventType.LETTER_GENERATED, user_id, datetime.now(), "letters")
        ]
        
        for event in events:
            stream.add_event(event)
        
        bridge.streams[user_id] = stream
        
        # Act
        journey = bridge.get_user_journey(user_id)
        
        # Assert
        assert len(journey) == 3
        assert journey[0].event_type == PhoenixEventType.USER_REGISTERED
        assert journey[1].event_type == PhoenixEventType.CV_UPLOADED
        assert journey[2].event_type == PhoenixEventType.LETTER_GENERATED


class TestPhoenixCVEventHelper:
    """Tests pour le helper spécialisé Phoenix CV"""
    
    @pytest.mark.asyncio
    async def test_track_cv_uploaded(self):
        """Test tracking d'upload CV"""
        # Arrange
        bridge = PhoenixEventBridge()
        helper = PhoenixCVEventHelper(bridge)
        
        # Act
        event_id = await helper.track_cv_uploaded(
            user_id="user-123",
            cv_filename="mon_cv.pdf",
            cv_size=1024000
        )
        
        # Assert
        assert event_id is not None
        user_stream = bridge.get_stream("user-123")
        assert user_stream is not None
        assert len(user_stream.events) == 1
        
        event = user_stream.events[0]
        assert event.event_type == PhoenixEventType.CV_UPLOADED
        assert event.payload["filename"] == "mon_cv.pdf"
        assert event.payload["file_size"] == 1024000
    
    @pytest.mark.asyncio
    async def test_track_cv_generated(self):
        """Test tracking de génération CV"""
        # Arrange
        bridge = PhoenixEventBridge()
        helper = PhoenixCVEventHelper(bridge)
        
        # Act
        event_id = await helper.track_cv_generated(
            user_id="user-456",
            template_name="Modern Professional",
            ats_score=85.5,
            skills_count=12,
            experience_count=3
        )
        
        # Assert
        assert event_id is not None
        user_stream = bridge.get_stream("user-456")
        assert user_stream is not None
        
        event = user_stream.events[0]
        assert event.event_type == PhoenixEventType.CV_GENERATED
        assert event.payload["template_name"] == "Modern Professional"
        assert event.payload["ats_score"] == 85.5
        assert event.payload["skills_count"] == 12
        assert event.payload["experience_count"] == 3


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])