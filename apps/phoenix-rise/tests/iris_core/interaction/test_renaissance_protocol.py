import pytest
from iris_core.interaction.renaissance_protocol import RenaissanceProtocol, RenaissanceState

class TestRenaissanceProtocol:

    @pytest.fixture
    def protocol(self):
        return RenaissanceProtocol()

    @pytest.fixture
    def mock_eev(self):
        return {
            "user_id": "test_user",
            "mood_average_7d": 0.5,
            "confidence_trend": 0.0,
            "last_action_type": None,
            "actions_count_7d": {},
            "burnout_risk_score": 0.0
        }

    def test_initial_state(self, protocol):
        assert protocol.current_state == RenaissanceState.ECOUTE_ACTIVE

    def test_transition_to(self, protocol):
        protocol.transition_to(RenaissanceState.VALIDATION_EMOTION)
        assert protocol.current_state == RenaissanceState.VALIDATION_EMOTION

    def test_ecoute_active_default(self, protocol, mock_eev):
        response = protocol.process_interaction("", mock_eev)
        assert "Bonjour. Je suis Iris" in response
        assert protocol.current_state == RenaissanceState.ECOUTE_ACTIVE # State doesn't change on process_interaction

    def test_ecoute_active_burnout_risk(self, protocol, mock_eev):
        mock_eev["burnout_risk_score"] = 0.8
        response = protocol.process_interaction("", mock_eev)
        assert "Je ressens que tu traverses une période particulièrement exigeante" in response

    def test_ecoute_active_low_mood(self, protocol, mock_eev):
        mock_eev["mood_average_7d"] = 0.2
        response = protocol.process_interaction("", mock_eev)
        assert "Je perçois une certaine lourdeur dans ton humeur" in response

    def test_ecoute_active_negative_confidence_trend(self, protocol, mock_eev):
        mock_eev["confidence_trend"] = -0.2
        response = protocol.process_interaction("", mock_eev)
        assert "Il semble que ta confiance ait été mise à l'épreuve" in response

    def test_validation_emotion(self, protocol, mock_eev):
        protocol.transition_to(RenaissanceState.VALIDATION_EMOTION)
        response = protocol.process_interaction("", mock_eev)
        assert "Je comprends que tu te sentes [émotion]" in response

    def test_identification_pensee_negative(self, protocol, mock_eev):
        protocol.transition_to(RenaissanceState.IDENTIFICATION_PENSEE_NEGATIVE)
        response = protocol.process_interaction("", mock_eev)
        assert "Si tu devais identifier la pensée principale" in response

    def test_proposition_recadrage(self, protocol, mock_eev):
        protocol.transition_to(RenaissanceState.PROPOSITION_RECADRAGE)
        response = protocol.process_interaction("", mock_eev)
        assert "Et si nous explorions une autre façon de voir les choses" in response

    def test_suggestion_micro_action_no_last_action(self, protocol, mock_eev):
        protocol.transition_to(RenaissanceState.SUGGESTION_MICRO_ACTION)
        response = protocol.process_interaction("", mock_eev)
        assert "quelle petite action pourrais-tu entreprendre aujourd'hui" in response

    def test_suggestion_micro_action_with_last_action(self, protocol, mock_eev):
        protocol.transition_to(RenaissanceState.SUGGESTION_MICRO_ACTION)
        mock_eev["last_action_type"] = "CVGenerated"
        response = protocol.process_interaction("", mock_eev)
        assert "Puisque tu as récemment CVGenerated, quelle petite action" in response

    def test_renforcement_positif_cloture(self, protocol, mock_eev):
        protocol.transition_to(RenaissanceState.RENFORCEMENT_POSITIF_CLOTURE)
        response = protocol.process_interaction("", mock_eev)
        assert "Je salue ton courage et ta détermination" in response

    def test_alerte_ethique_disclaimer(self, protocol, mock_eev):
        protocol.transition_to(RenaissanceState.ALERTE_ETHIQUE_DISCLAIMER)
        response = protocol.process_interaction("", mock_eev)
        assert "Je ne suis pas un professionnel de la santé mentale" in response

    def test_fin_repos(self, protocol, mock_eev):
        protocol.transition_to(RenaissanceState.FIN_REPOS)
        response = protocol.process_interaction("", mock_eev)
        assert "Iris est en mode repos" in response

    def test_unknown_state_handler(self, protocol, mock_eev):
        # Temporarily set an invalid state to test fallback
        protocol.current_state = RenaissanceState.ECOUTE_ACTIVE # Set to a valid state first
        protocol.state_handlers[RenaissanceState.ECOUTE_ACTIVE] = None # Invalidate handler
        response = protocol.process_interaction("", mock_eev)
        assert "Je ne suis pas sûr de comprendre" in response
