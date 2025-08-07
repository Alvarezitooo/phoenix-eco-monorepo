"""
Tests unitaires pour le Renaissance Protocol Analyzer
Validation de la logique de déclenchement et des analyses
"""

import pytest
from datetime import datetime, timedelta
from packages.phoenix_shared_ai.services.renaissance_protocol_analyzer import (
    RenaissanceProtocolAnalyzer,
    UserEvent,
    EventFactory,
    should_trigger_renaissance_protocol
)


class TestUserEvent:
    """Tests pour la classe UserEvent"""
    
    def test_user_event_creation(self):
        """Test création d'un UserEvent"""
        event = UserEvent(
            event_type="MoodLogged",
            user_id="test_user",
            timestamp=datetime.now(),
            payload={"mood": 5, "confidence": 6, "notes": "Test note"}
        )
        
        assert event.mood_score == 5
        assert event.confidence_score == 6
        assert event.notes == "Test note"
    
    def test_user_event_alternative_keys(self):
        """Test avec des clés alternatives dans payload"""
        event = UserEvent(
            event_type="CoachingSessionCompleted",
            user_id="test_user",
            timestamp=datetime.now(),
            payload={"mood_score": 7, "confidence_score": 8, "content": "Session content"}
        )
        
        assert event.mood_score == 7
        assert event.confidence_score == 8
        assert event.notes == "Session content"


class TestRenaissanceProtocolAnalyzer:
    """Tests pour l'analyseur Renaissance Protocol"""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture pour créer un analyseur"""
        return RenaissanceProtocolAnalyzer(debug=True)
    
    def test_should_trigger_with_low_scores(self, analyzer):
        """Test déclenchement avec scores faibles"""
        events = [
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=1),
                     {"mood": 2, "confidence": 3, "notes": "Je me sens inutile et bloqué"}),
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=2),
                     {"mood": 3, "confidence": 2, "notes": "Encore un échec"}),
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=3),
                     {"mood": 1, "confidence": 1, "notes": "Désespoir total"}),
        ]
        
        result = analyzer.should_trigger_renaissance_protocol(events)
        
        assert result.should_trigger == True
        assert result.confidence_level >= 0.6
        assert "mood_analysis" in result.analysis_details
        assert "confidence_analysis" in result.analysis_details
        assert "keyword_analysis" in result.analysis_details
    
    def test_should_not_trigger_with_high_scores(self, analyzer):
        """Test non-déclenchement avec scores élevés"""
        events = [
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=1),
                     {"mood": 8, "confidence": 9, "notes": "Excellente journée aujourd'hui"}),
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=2),
                     {"mood": 7, "confidence": 8, "notes": "Progrès encourageants"}),
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=3),
                     {"mood": 9, "confidence": 7, "notes": "Motivation au top"}),
        ]
        
        result = analyzer.should_trigger_renaissance_protocol(events)
        
        assert result.should_trigger == False
        assert result.confidence_level < 0.7
    
    def test_insufficient_events(self, analyzer):
        """Test avec nombre insuffisant d'événements"""
        events = [
            UserEvent("MoodLogged", "user1", datetime.now(),
                     {"mood": 1, "confidence": 1, "notes": "Test"})
        ]
        
        result = analyzer.should_trigger_renaissance_protocol(events)
        
        assert result.should_trigger == False
        assert "error" in result.analysis_details
    
    def test_mood_analysis(self, analyzer):
        """Test analyse des tendances d'humeur"""
        events = [
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=1),
                     {"mood": 2}),
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=2),
                     {"mood": 3}),
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=3),
                     {"mood": 4}),
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=4),
                     {"mood": 6}),
        ]
        
        mood_analysis = analyzer._analyze_mood_trends(events)
        
        assert mood_analysis["below_threshold"] == True
        assert mood_analysis["trend"] == "declining"
        assert mood_analysis["average"] < 4.0
    
    def test_negative_keywords_detection(self, analyzer):
        """Test détection des mots-clés négatifs"""
        events = [
            UserEvent("MoodLogged", "user1", datetime.now(),
                     {"notes": "Je me sens bloqué et inutile dans cette situation d'échec"}),
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=1),
                     {"notes": "Désespoir total, rien ne marche jamais"}),
        ]
        
        keyword_analysis = analyzer._analyze_negative_keywords(events)
        
        assert keyword_analysis["above_threshold"] == True
        assert len(keyword_analysis["detected_keywords"]) >= 2
        assert "bloqué" in keyword_analysis["detected_keywords"]
        assert "échec" in keyword_analysis["detected_keywords"]
    
    def test_temporal_patterns(self, analyzer):
        """Test analyse des patterns temporels"""
        now = datetime.now()
        events = [
            UserEvent("MoodLogged", "user1", now - timedelta(days=1), {"mood": 5}),
            UserEvent("MoodLogged", "user1", now - timedelta(days=3), {"mood": 4}),
            UserEvent("MoodLogged", "user1", now - timedelta(days=10), {"mood": 6}),
        ]
        
        temporal_analysis = analyzer._analyze_temporal_patterns(events)
        
        assert "days_since_last_event" in temporal_analysis
        assert "engagement_pattern" in temporal_analysis
        assert temporal_analysis["total_events"] == 3
    
    def test_trigger_score_calculation(self, analyzer):
        """Test calcul du score de déclenchement"""
        mood_analysis = {"average": 2.0, "below_threshold": True, "trend": "declining"}
        confidence_analysis = {"average": 3.0, "below_threshold": True, "trend": "declining"}
        keyword_analysis = {"above_threshold": True, "total_frequency": 5}
        temporal_analysis = {"engagement_pattern": "declining", "days_since_last_event": 5}
        
        score = analyzer._calculate_trigger_score(
            mood_analysis, confidence_analysis, keyword_analysis, temporal_analysis
        )
        
        assert 0.0 <= score <= 1.0
        assert score >= 0.6  # Should be high given the negative inputs
    
    def test_recommendations_generation(self, analyzer):
        """Test génération des recommandations"""
        analysis = {
            "mood_analysis": {"below_threshold": True},
            "confidence_analysis": {"below_threshold": True},
            "keyword_analysis": {"above_threshold": True},
            "temporal_analysis": {"engagement_pattern": "declining"}
        }
        
        recommendations = analyzer._generate_recommendations(analysis, should_trigger=True)
        
        assert len(recommendations) >= 4
        assert any("Renaissance" in rec for rec in recommendations)
        assert any("humeur" in rec for rec in recommendations)
        assert any("confiance" in rec for rec in recommendations)


class TestEventFactory:
    """Tests pour EventFactory"""
    
    def test_from_journal_entry(self):
        """Test création depuis JournalEntry"""
        journal_data = {
            "user_id": "test_user",
            "created_at": datetime.now().isoformat(),
            "mood": 5,
            "confidence": 6,
            "notes": "Test journal entry"
        }
        
        event = EventFactory.from_journal_entry(journal_data)
        
        assert event.event_type == "MoodLogged"
        assert event.user_id == "test_user"
        assert event.mood_score == 5
        assert event.confidence_score == 6
        assert event.notes == "Test journal entry"
    
    def test_from_phoenix_event(self):
        """Test création depuis Phoenix Event"""
        event_data = {
            "event_type": "CoachingSessionCompleted",
            "user_id": "test_user",
            "timestamp": datetime.now().isoformat(),
            "payload": {"mood": 7, "confidence": 8, "notes": "Great session"}
        }
        
        event = EventFactory.from_phoenix_event(event_data)
        
        assert event.event_type == "CoachingSessionCompleted"
        assert event.user_id == "test_user"
        assert event.mood_score == 7
        assert event.confidence_score == 8


class TestIntegrationScenarios:
    """Tests de scénarios d'intégration réalistes"""
    
    def test_gradual_decline_scenario(self):
        """Test scénario de déclin graduel"""
        events = []
        base_time = datetime.now()
        
        # Simulation d'un déclin progressif sur 10 jours
        for i in range(10):
            mood = max(1, 8 - i)  # Déclin de 8 à 1
            confidence = max(1, 7 - i)  # Déclin de 7 à 1
            notes = f"Jour {i+1}: " + ["Tout va bien", "Quelques difficultés", "Ça se complique", 
                                       "Situation difficile", "Je commence à douter",
                                       "C'est dur", "Je me sens bloqué", "Échec répété",
                                       "Désespoir", "Inutile de continuer"][i]
            
            event = UserEvent(
                "MoodLogged", "user1", 
                base_time - timedelta(days=9-i),
                {"mood": mood, "confidence": confidence, "notes": notes}
            )
            events.append(event)
        
        analyzer = RenaissanceProtocolAnalyzer()
        result = analyzer.should_trigger_renaissance_protocol(events)
        
        assert result.should_trigger == True
        assert result.confidence_level >= 0.7
    
    def test_mixed_signals_scenario(self):
        """Test scénario avec signaux mixtes"""
        events = [
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=1),
                     {"mood": 2, "confidence": 8, "notes": "Moral bas mais confiant"}),
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=2),
                     {"mood": 8, "confidence": 2, "notes": "Bonne humeur mais pas confiant"}),
            UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=3),
                     {"mood": 5, "confidence": 5, "notes": "Journée moyenne, rien d'exceptionnel"}),
        ]
        
        analyzer = RenaissanceProtocolAnalyzer()
        result = analyzer.should_trigger_renaissance_protocol(events)
        
        # Avec des signaux mixtes, le déclenchement devrait être incertain
        assert 0.3 <= result.confidence_level <= 0.7


def test_simple_function_interface():
    """Test de l'interface fonction simple"""
    events = [
        UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=1),
                 {"mood": 1, "confidence": 2, "notes": "Échec total, je suis bloqué"}),
        UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=2),
                 {"mood": 2, "confidence": 1, "notes": "Inutile de continuer"}),
        UserEvent("MoodLogged", "user1", datetime.now() - timedelta(days=3),
                 {"mood": 3, "confidence": 3, "notes": "Désespoir complet"}),
    ]
    
    result = should_trigger_renaissance_protocol(events)
    
    assert isinstance(result, bool)
    assert result == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])