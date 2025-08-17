import pytest
from unittest.mock import Mock
from apps.phoenix-iris-api.ai.alessio_prompt_orchestrator import AlessioPromptOrchestrator
from apps.phoenix-iris-api.event_processing.emotional_vector_state import EmotionalVectorState
from apps.phoenix-iris-api.interaction.renaissance_protocol import RenaissanceState

@pytest.fixture
def mock_eev():
    eev = Mock(spec=EmotionalVectorState)
    eev.burnout_risk_score = 0.1
    eev.mood_average_7d = 0.8
    eev.confidence_trend = 0.05
    eev.actions_count_7d = {"CVGenerated": 2}
    eev.to_json.return_value = '{"mock_eev_data": true}'
    return eev

@pytest.fixture
def orchestrator():
    return AlessioPromptOrchestrator()

def test_generate_prompt_basic(orchestrator, mock_eev):
    state = RenaissanceState.ECOUTE_ACTIVE
    prompt = orchestrator.generate_prompt(mock_eev, state)

    assert "DECRET D'INCARNATION D'ALESSIO" in prompt
    assert "Vous êtes Alessio" in prompt
    assert "CONTEXTE UTILISATEUR" in prompt
    assert '{"mock_eev_data": true}' in prompt
    assert "Accueille l'utilisateur et invite-le à partager son état ou son intention du jour." in prompt
    assert "Écoute Active" in prompt # Check for user state strategy text

def test_generate_prompt_with_previous_conversation(orchestrator, mock_eev):
    state = RenaissanceState.PROPOSITION_RECADRAGE
    previous_conv = "User: Je me sens bloqué.\nAlessio: Pourquoi te sens-tu bloqué?"
    prompt = orchestrator.generate_prompt(mock_eev, state, previous_conversation=previous_conv)

    assert "CONVERSATION PRÉCÉDENTE" in prompt
    assert previous_conv in prompt
    assert "Propose des perspectives alternatives ou des questions pour aider l'utilisateur à recadrer sa pensée négative." in prompt

def test_determine_user_state(orchestrator, mock_eev):
    # Test fatigued state
    mock_eev.burnout_risk_score = 0.8
    assert orchestrator._determine_user_state(mock_eev) == "fatigué"

    # Test discouraged state
    mock_eev.burnout_risk_score = 0.1
    mock_eev.mood_average_7d = 0.2
    assert orchestrator._determine_user_state(mock_eev) == "découragé"

    # Test stressed state
    mock_eev.mood_average_7d = 0.8
    mock_eev.confidence_trend = -0.2
    assert orchestrator._determine_user_state(mock_eev) == "stressé"

    # Test confident state
    mock_eev.confidence_trend = 0.05
    mock_eev.actions_count_7d = {"CVGenerated": 6}
    assert orchestrator._determine_user_state(mock_eev) == "confiant"

    # Test neutral state
    mock_eev.actions_count_7d = {}
    assert orchestrator._determine_user_state(mock_eev) == "neutre"
