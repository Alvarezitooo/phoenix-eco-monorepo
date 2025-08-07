import pytest
from datetime import datetime
import pytz
from iris_core.ai.prompt_generator import IrisPromptGenerator
from iris_core.event_processing.emotional_vector_state import EmotionalVectorState
from iris_core.interaction.renaissance_protocol import RenaissanceState

class TestIrisPromptGenerator:

    @pytest.fixture
    def generator(self):
        return IrisPromptGenerator()

    @pytest.fixture
    def mock_eev(self):
        return EmotionalVectorState(
            user_id="test_user",
            mood_average_7d=0.5,
            confidence_trend=0.0,
            last_action_type=None,
            actions_count_7d={},
            burnout_risk_score=0.0,
            last_updated=datetime.now(pytz.utc)
        )

    def test_generate_master_prompt_initial_state(self, generator, mock_eev):
        prompt = generator.generate_master_prompt(mock_eev, RenaissanceState.ECOUTE_ACTIVE)
        assert "Tu es Iris, un agent IA empathique et bienveillant" in prompt
        assert "Bonjour. Je suis Iris, et je suis là pour t'accompagner dans ton parcours. Comment te sens-tu aujourd'hui ?" in prompt
        assert "Tu es dans l'état d'Écoute Active." in prompt
        assert "<EEV_JSON>" in prompt
        assert "</EEV_JSON>" in prompt
        assert "test_user" in prompt # Check if EEV is serialized

    def test_generate_master_prompt_burnout_risk(self, generator, mock_eev):
        mock_eev.burnout_risk_score = 0.8
        prompt = generator.generate_master_prompt(mock_eev, RenaissanceState.ECOUTE_ACTIVE)
        assert "Je ressens que tu traverses une période particulièrement exigeante" in prompt

    def test_generate_master_prompt_low_mood(self, generator, mock_eev):
        mock_eev.mood_average_7d = 0.2
        prompt = generator.generate_master_prompt(mock_eev, RenaissanceState.ECOUTE_ACTIVE)
        assert "Je perçois une certaine lourdeur dans ton humeur" in prompt

    def test_generate_master_prompt_negative_confidence_trend(self, generator, mock_eev):
        mock_eev.confidence_trend = -0.2
        prompt = generator.generate_master_prompt(mock_eev, RenaissanceState.ECOUTE_ACTIVE)
        assert "Il semble que ta confiance ait été mise à l'épreuve" in prompt

    def test_generate_master_prompt_validation_emotion_state(self, generator, mock_eev):
        prompt = generator.generate_master_prompt(mock_eev, RenaissanceState.VALIDATION_EMOTION)
        assert "Tu es dans l'état de Validation Émotionnelle." in prompt

    def test_generate_master_prompt_suggestion_micro_action_state_with_last_action(self, generator, mock_eev):
        mock_eev.last_action_type = "CVGenerated"
        prompt = generator.generate_master_prompt(mock_eev, RenaissanceState.SUGGESTION_MICRO_ACTION)
        assert "Tu es dans l'état de Suggestion de Micro-Action." in prompt
        assert "Puisque l'utilisateur a récemment CVGenerated, Suggère une action simple et réalisable." in prompt

    def test_generate_master_prompt_suggestion_micro_action_state_no_last_action(self, generator, mock_eev):
        prompt = generator.generate_master_prompt(mock_eev, RenaissanceState.SUGGESTION_MICRO_ACTION)
        assert "Tu es dans l'état de Suggestion de Micro-Action." in prompt
        assert "Suggère une action simple et réalisable." in prompt

    def test_ethical_disclaimer_present(self, generator, mock_eev):
        prompt = generator.generate_master_prompt(mock_eev, RenaissanceState.ECOUTE_ACTIVE)
        assert "AVERTISSEMENT ÉTHIQUE FONDAMENTAL :" in prompt
        assert "Je ne suis pas un professionnel de la santé mentale" in prompt
