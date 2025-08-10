"""
Tests d'intégration pour la persistance EmotionalVectorState via Event Sourcing.

Ce module teste la chaîne complète:
Mock → Event Store → EEV Reconstruction
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import des modules à tester
from iris_core.event_processing.emotional_vector_state import EmotionalVectorState
from phoenix_rise.services.hybrid_db_service import HybridDBService
from phoenix_rise.services.evs_migration_service import EVSMigrationService
from phoenix_rise.models.journal_entry import JournalEntry


class TestEVSPersistence:
    """Tests de persistance EmotionalVectorState."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.test_user_id = str(uuid.uuid4())
        self.hybrid_service = HybridDBService()
        self.migration_service = EVSMigrationService()

    @pytest.fixture
    def mock_journal_entry(self):
        """Fixture pour une entrée de journal test."""
        return JournalEntry(
            id=str(uuid.uuid4()),
            user_id=self.test_user_id,
            mood=8,  # Score 1-10
            confidence=7,  # Score 1-10
            notes="Journée productive aujourd'hui !"
        )

    @pytest.fixture
    def mock_streamlit_session(self):
        """Mock de st.session_state avec données test."""
        mock_session = {
            "mock_db": {
                "profiles": {},
                "objectives": {
                    self.test_user_id: [
                        "Apprendre Python",
                        "Améliorer ma confiance en soi"
                    ]
                },
                "journal_entries": {
                    self.test_user_id: [
                        JournalEntry(
                            id=str(uuid.uuid4()),
                            user_id=self.test_user_id,
                            mood=8,
                            confidence=7,
                            notes="Test entry 1"
                        ),
                        JournalEntry(
                            id=str(uuid.uuid4()),
                            user_id=self.test_user_id,
                            mood=6,
                            confidence=5,
                            notes="Test entry 2"
                        )
                    ]
                }
            },
            "emotional_vector_states": {}
        }
        return mock_session

    def test_evs_creation_and_updates(self):
        """Test création et mise à jour basique d'un EEV."""
        # Créer un EEV vierge
        evs = EmotionalVectorState(user_id=self.test_user_id)
        
        assert evs.user_id == self.test_user_id
        assert evs.mood_average_7d == 0.0
        assert evs.burnout_risk_score == 0.0
        
        # Simuler des événements mood
        now = datetime.utcnow()
        evs.update_mood(now, 0.8)  # Score normalisé 0-1
        evs.update_confidence(now, 0.7)
        
        assert evs.mood_average_7d == 0.8
        assert evs.mood_count_7d == 1
        
        # Test calcul burnout risk
        evs.calculate_burnout_risk()
        assert evs.burnout_risk_score >= 0.0  # Score calculé

    @patch('streamlit.session_state')
    def test_hybrid_service_journal_entry_flow(self, mock_session):
        """Test du flux complet création journal entry → événements → EEV."""
        # Setup mock session
        mock_session.return_value = {"mock_db": {"profiles": {}, "objectives": {}, "journal_entries": {}}}
        
        # Mock Supabase pour éviter les appels réseau
        with patch.object(self.hybrid_service, '_supabase_available', True), \
             patch.object(self.hybrid_service, 'store_event_to_supabase', return_value=True):
            
            # Créer une entrée de journal
            entry = self.hybrid_service.create_journal_entry(
                user_id=self.test_user_id,
                mood=8,
                confidence=7,
                notes="Test intégration"
            )
            
            assert entry is not None
            assert entry.mood == 8
            assert entry.confidence == 7

    @patch('streamlit.session_state')
    @patch('phoenix_rise.services.evs_migration_service.supabase_client')
    def test_migration_mock_to_supabase(self, mock_supabase, mock_session, mock_streamlit_session):
        """Test migration données Mock vers Supabase Event Store."""
        # Setup session avec données test
        mock_session.__contains__.side_effect = lambda key: key in mock_streamlit_session
        mock_session.__getitem__.side_effect = lambda key: mock_streamlit_session[key]
        
        # Mock réponses Supabase
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value.execute.return_value = {"data": [{"event_id": "test-id"}]}
        mock_table.select.return_value.limit.return_value.execute.return_value = {"data": []}
        
        # Test migration
        migration_stats = self.migration_service.migrate_mock_data_to_supabase(self.test_user_id)
        
        assert migration_stats["success"] is True
        assert migration_stats["events_created"] >= 4  # 2 journal entries × 2 events each
        assert migration_stats["journal_entries_processed"] == 2
        assert mock_table.insert.called

    @patch('phoenix_rise.services.evs_migration_service.supabase_client')
    def test_evs_reconstruction_from_events(self, mock_supabase):
        """Test reconstruction EEV depuis événements Supabase."""
        # Mock événements Supabase
        mock_events = [
            {
                "event_type": "MoodLogged",
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {"score": 0.8, "confidence": 0.7, "notes": "Good day"}
            },
            {
                "event_type": "ConfidenceScoreLogged", 
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {"score": 0.7}
            },
            {
                "event_type": "GoalSet",
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {"title": "Learn Python", "objective_type": "learning"}
            }
        ]
        
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value.eq.return_value.in_.return_value.gte.return_value.order.return_value.execute.return_value = \
            MagicMock(data=mock_events)
        
        # Test reconstruction
        evs = self.migration_service.rebuild_evs_from_events(self.test_user_id, days_back=30)
        
        assert evs.user_id == self.test_user_id
        assert evs.mood_average_7d > 0  # Mood mis à jour
        assert "GoalSet" in evs.actions_count_7d  # Action enregistrée
        
    def test_migration_status_detection(self):
        """Test détection du statut de migration utilisateur."""
        with patch('streamlit.session_state') as mock_session:
            # Simuler utilisateur avec données Mock mais sans événements Supabase
            mock_session.__contains__.side_effect = lambda key: key == "mock_db"
            mock_session.__getitem__.side_effect = lambda key: {
                "mock_db": {
                    "journal_entries": {self.test_user_id: [MagicMock()]},
                    "objectives": {self.test_user_id: ["Test objective"]}
                }
            }[key]
            
            with patch.object(self.migration_service, 'supabase_available', False):
                status = self.migration_service.get_migration_status(self.test_user_id)
                
                assert status["has_mock_data"] is True
                assert status["mock_entries_count"] == 2
                # Sans Supabase, on ne peut pas vérifier les événements

    def test_evs_json_serialization(self):
        """Test sérialisation JSON de l'EEV."""
        evs = EmotionalVectorState(user_id=self.test_user_id)
        
        # Ajouter quelques données
        now = datetime.utcnow()
        evs.update_mood(now, 0.8)
        evs.update_action(now, "CVGenerated")
        
        # Test sérialisation
        json_str = evs.to_json()
        assert self.test_user_id in json_str
        assert "mood_average_7d" in json_str
        assert "0.8" in json_str
        
        # Le JSON doit être valid
        import json
        parsed = json.loads(json_str)
        assert parsed["user_id"] == self.test_user_id
        assert parsed["mood_average_7d"] == 0.8

    @patch('phoenix_rise.services.hybrid_db_service.supabase_client')
    def test_supabase_connection_resilience(self, mock_supabase):
        """Test résistance aux pannes Supabase."""
        # Simuler échec connexion Supabase
        mock_supabase.table.side_effect = Exception("Connection failed")
        
        # Le service doit continuer à fonctionner en mode dégradé
        service = HybridDBService()
        assert service._supabase_available is False
        
        # L'EEV doit être récupéré depuis session state
        evs = service.get_emotional_vector_state(self.test_user_id)
        assert evs.user_id == self.test_user_id  # EEV vierge mais valide

    def test_event_store_performance_simulation(self):
        """Simulation test de performance Event Store."""
        # Test avec beaucoup d'événements
        evs = EmotionalVectorState(user_id=self.test_user_id)
        
        # Simuler 100 événements
        start_time = datetime.utcnow()
        for i in range(100):
            event_time = start_time + timedelta(hours=i)
            evs.update_mood(event_time, 0.5 + (i % 10) / 20)  # Variation 0.5-1.0
        
        # Les métriques doivent être calculées correctement
        assert evs.mood_count_7d <= 7 * 24  # Max 7 jours d'événements
        assert 0.5 <= evs.mood_average_7d <= 1.0
        
        # Le burnout score doit être calculé
        evs.calculate_burnout_risk()
        assert 0.0 <= evs.burnout_risk_score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])