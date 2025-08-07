import pytest
from datetime import datetime
import pytz
from iris_core.ai.iris_prompt_orchestrator import IrisPromptOrchestrator
from iris_core.event_processing.emotional_vector_state import EmotionalVectorState
from iris_core.interaction.renaissance_protocol import RenaissanceState

class TestIrisPromptOrchestrator:

    @pytest.fixture
    def orchestrator(self):
        return IrisPromptOrchestrator()

    @pytest.fixture
    def mock_eev_fatigue(self):
        return EmotionalVectorState(
            user_id="test_user_fatigue",
            mood_average_7d=0.2, # Low mood
            confidence_trend=0.0,
            burnout_risk_score=0.8, # High burnout risk
            last_updated=datetime.now(pytz.utc)
        )

    @pytest.fixture
    def mock_eev_stressed(self):
        return EmotionalVectorState(
            user_id="test_user_stressed",
            mood_average_7d=0.6,
            confidence_trend=-0.2, # Negative confidence trend
            burnout_risk_score=0.3,
            last_updated=datetime.now(pytz.utc)
        )

    @pytest.fixture
    def mock_eev_confident(self):
        eev = EmotionalVectorState(
            user_id="test_user_confident",
            mood_average_7d=0.9,
            confidence_trend=0.3,
            burnout_risk_score=0.1,
            last_updated=datetime.now(pytz.utc)
        )
        eev.actions_count_7d = {"CVGenerated": 6} # Active user
        return eev

    @pytest.fixture
    def mock_eev_neutral(self):
        return EmotionalVectorState(
            user_id="test_user_neutral",
            mood_average_7d=0.5,
            confidence_trend=0.0,
            burnout_risk_score=0.0,
            last_updated=datetime.now(pytz.utc)
        )

    def test_determine_user_state_fatigue(self, orchestrator, mock_eev_fatigue):
        state = orchestrator._determine_user_state(mock_eev_fatigue)
        assert state == "fatigué"

    def test_determine_user_state_stressed(self, orchestrator, mock_eev_stressed):
        state = orchestrator._determine_user_state(mock_eev_stressed)
        assert state == "stressé"

    def test_determine_user_state_confident(self, orchestrator, mock_eev_confident):
        state = orchestrator._determine_user_state(mock_eev_confident)
        assert state == "confiant"

    def test_determine_user_state_neutral(self, orchestrator, mock_eev_neutral):
        state = orchestrator._determine_user_state(mock_eev_neutral)
        assert state == "neutre"

    def test_generate_prompt_fatigue_ecoute_active(self, orchestrator, mock_eev_fatigue):
        prompt = orchestrator.generate_prompt(mock_eev_fatigue, RenaissanceState.ECOUTE_ACTIVE)
        assert "État de l'utilisateur: fatigué" in prompt
        assert "Tonalité à adopter: empathique" in prompt
        assert "Stratégie de réponse: Allège les formulations, favorise les invitations à la respiration ou au repos." in prompt
        assert "Accueille l'utilisateur et invite-le à partager son état ou son intention du jour." in prompt
        assert "test_user_fatigue" in prompt # EEV serialized

    def test_generate_prompt_stressed_suggestion_micro_action(self, orchestrator, mock_eev_stressed):
        prompt = orchestrator.generate_prompt(mock_eev_stressed, RenaissanceState.SUGGESTION_MICRO_ACTION)
        assert "État de l'utilisateur: stressé" in prompt
        assert "Tonalité à adopter: stoïque" in prompt
        assert "Stratégie de réponse: Ralentis le rythme, propose un Zazen ou un Kaizen simple." in prompt
        assert "Suggère une petite action concrète et réalisable (Kaizen du jour) pour briser le cycle négatif et renforcer le sentiment d'efficacité personnelle." in prompt

    def test_generate_prompt_confident_renforcement_positif(self, orchestrator, mock_eev_confident):
        prompt = orchestrator.generate_prompt(mock_eev_confident, RenaissanceState.RENFORCEMENT_POSITIF_CLOTURE)
        assert "État de l'utilisateur: confiant" in prompt
        assert "Tonalité à adopter: sobre et soutenante" in prompt
        assert "Stratégie de réponse: Soutiens le rythme, renforce la discipline douce." in prompt
        assert "Renforce positivement les efforts de l'utilisateur et clôture la session de manière bienveillante." in prompt

    def test_generate_prompt_with_previous_conversation(self, orchestrator, mock_eev_neutral):
        previous_conv = "User: Je me sens un peu perdu. Iris: Je comprends. Qu'est-ce qui te pèse le plus ?"
        prompt = orchestrator.generate_prompt(mock_eev_neutral, RenaissanceState.IDENTIFICATION_PENSEE_NEGATIVE, previous_conversation=previous_conv)
        assert previous_conv in prompt
        assert "Aide l'utilisateur à identifier les pensées ou croyances négatives sous-jacentes à son émotion." in prompt
