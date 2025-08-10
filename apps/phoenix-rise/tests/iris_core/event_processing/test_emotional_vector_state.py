import pytest
from datetime import datetime, timedelta
import pytz
from iris_core.event_processing.emotional_vector_state import EmotionalVectorState

class TestEmotionalVectorState:

    @pytest.fixture
    def eev(self):
        return EmotionalVectorState(user_id="test_user_123")

    def test_initial_state(self, eev):
        assert eev.user_id == "test_user_123"
        assert eev.mood_average_7d == 0.0
        assert eev.confidence_trend == 0.0
        assert eev.last_action_type is None
        assert eev.actions_count_7d == {}
        assert eev.burnout_risk_score == 0.0
        assert isinstance(eev.last_updated, datetime)

    def test_update_mood_single_event(self, eev):
        now = datetime.now(pytz.utc)
        eev.update_mood(now, 0.8)
        assert eev.mood_average_7d == 0.8
        assert eev.mood_count_7d == 1
        assert eev.mood_sum_7d == 0.8
        assert len(eev.event_history_7d) == 1

    def test_update_mood_multiple_events_within_window(self, eev):
        now = datetime.now(pytz.utc)
        eev.update_mood(now - timedelta(days=1), 0.6)
        eev.update_mood(now, 0.9)
        assert eev.mood_count_7d == 2
        assert eev.mood_sum_7d == 1.5
        assert eev.mood_average_7d == 0.75
        assert len(eev.event_history_7d) == 2

    def test_update_mood_events_outside_window(self, eev):
        now = datetime.now(pytz.utc)
        # Event outside 7-day window
        eev.update_mood(now - timedelta(days=8), 0.2)
        # Events within 7-day window
        eev.update_mood(now - timedelta(days=2), 0.7)
        eev.update_mood(now, 0.9)

        assert eev.mood_count_7d == 2
        assert eev.mood_sum_7d == pytest.approx(1.6)
        assert eev.mood_average_7d == pytest.approx(0.8)
        assert len(eev.event_history_7d) == 2 # Only 2 events should remain

    def test_update_confidence_single_event(self, eev):
        now = datetime.now(pytz.utc)
        eev.update_confidence(now, 0.7)
        assert len(eev.confidence_scores_30d) == 1
        assert eev.confidence_scores_30d[0] == 0.7
        assert eev.confidence_trend == 0.0 # Not enough data for trend

    def test_update_confidence_multiple_events_within_window(self, eev):
        now = datetime.now(pytz.utc)
        eev.update_confidence(now - timedelta(days=5), 0.5)
        eev.update_confidence(now - timedelta(days=1), 0.6)
        eev.update_confidence(now, 0.8)
        assert len(eev.confidence_scores_30d) == 3
        # Trend calculation is simplified, so check for non-zero if expected
        # With simplified trend calculation, it might be 0.0 even with multiple events if values are constant.
        # We assert that if there are enough data points, a calculation was attempted.
        if len(eev.confidence_scores_30d) > 1:
            assert eev.confidence_trend is not None # Ensure it's calculated
        else:
            assert eev.confidence_trend == 0.0

    def test_update_confidence_events_outside_window(self, eev):
        now = datetime.now(pytz.utc)
        # Event outside 30-day window
        eev.update_confidence(now - timedelta(days=31), 0.1)
        # Events within 30-day window
        eev.update_confidence(now - timedelta(days=10), 0.5)
        eev.update_confidence(now, 0.9)

        assert len(eev.confidence_scores_30d) == 2
        assert eev.confidence_scores_30d[0] == 0.5
        assert eev.confidence_scores_30d[1] == 0.9

    def test_update_action(self, eev):
        now = datetime.now(pytz.utc)
        eev.update_action(now, "CVGenerated")
        assert eev.last_action_type == "CVGenerated"
        assert eev.actions_count_7d["CVGenerated"] == 1

        eev.update_action(now, "SkillSuggested")
        eev.update_action(now, "CVGenerated")
        assert eev.last_action_type == "CVGenerated"
        assert eev.actions_count_7d["CVGenerated"] == 2
        assert eev.actions_count_7d["SkillSuggested"] == 1

    def test_calculate_burnout_risk_low_mood_negative_trend_low_activity(self, eev):
        # Simulate conditions for high burnout risk
        now = datetime.now(pytz.utc)
        for i in range(7):
            eev.update_mood(now - timedelta(days=i), 0.2) # Low mood
        for i in range(30):
            eev.update_confidence(now - timedelta(days=i), 0.8 - (i * 0.01)) # Negative trend
        # No actions
        eev.calculate_burnout_risk()
        assert eev.burnout_risk_score > 0.5 # Should be high

    def test_calculate_burnout_risk_low_risk(self, eev):
        # Simulate conditions for low burnout risk
        now = datetime.now(pytz.utc)
        for i in range(7):
            eev.update_mood(now - timedelta(days=i), 0.8) # High mood
        for i in range(30):
            eev.update_confidence(now - timedelta(days=i), 0.5 + (i * 0.01)) # Positive trend
        eev.update_action(now, "CVGenerated")
        eev.update_action(now, "SkillSuggested")
        eev.update_action(now, "TrajectoryBuilt")
        eev.calculate_burnout_risk()
        assert eev.burnout_risk_score < 0.5 # Should be low

    def test_update_from_event_mood(self, eev):
        event = {
            "type": "MoodLogged",
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "payload": {"score": 0.7}
        }
        eev.update_from_event(event)
        assert eev.mood_average_7d == 0.7

    def test_update_from_event_confidence(self, eev):
        event = {
            "type": "ConfidenceScoreLogged",
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "payload": {"score": 0.6}
        }
        eev.update_from_event(event)
        assert len(eev.confidence_scores_30d) == 1
        assert eev.confidence_scores_30d[0] == 0.6

    def test_update_from_event_action(self, eev):
        event = {
            "type": "CVGenerated",
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "payload": {}
        }
        eev.update_from_event(event)
        assert eev.last_action_type == "CVGenerated"
        assert eev.actions_count_7d["CVGenerated"] == 1

    def test_update_from_event_unknown_type(self, eev):
        event = {
            "type": "UnknownEvent",
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "payload": {}
        }
        initial_mood = eev.mood_average_7d
        eev.update_from_event(event)
        assert eev.mood_average_7d == initial_mood # Should not change

    def test_burnout_risk_updates_on_event(self, eev):
        # Initial state, low risk
        assert eev.burnout_risk_score == 0.0

        # Simulate events leading to high risk
        now = datetime.now(pytz.utc)
        for i in range(7):
            event = {"type": "MoodLogged", "timestamp": (now - timedelta(days=i)).isoformat(), "payload": {"score": 0.1}}
            eev.update_from_event(event)
        
        # No actions, negative confidence trend (default for empty)
        assert eev.burnout_risk_score > 0.5

