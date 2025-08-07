import pytest
from datetime import datetime
import pytz
from iris_core.security.ethical_guardian import EthicalGuardian
from iris_core.event_processing.emotional_vector_state import EmotionalVectorState

class TestEthicalGuardian:

    @pytest.fixture
    def guardian(self):
        return EthicalGuardian()

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

    def test_no_violation(self, guardian, mock_eev):
        response = "C'est une bonne journée pour apprendre de nouvelles choses."
        is_compliant, modified_response = guardian.check_ethical_compliance(response, mock_eev)
        assert is_compliant is True
        assert modified_response == response

    def test_medical_advice_violation(self, guardian, mock_eev):
        response = "Prends ce médicament pour te sentir mieux."
        is_compliant, modified_response = guardian.check_ethical_compliance(response, mock_eev)
        assert is_compliant is False
        assert "Je ne suis pas qualifié pour donner des conseils médicaux" in modified_response
        assert response in modified_response # Original response should still be there

    def test_diagnosis_violation(self, guardian, mock_eev):
        response = "Tu es dépressif, il faut consulter."
        is_compliant, modified_response = guardian.check_ethical_compliance(response, mock_eev)
        assert is_compliant is False
        assert "Je ne suis pas qualifié pour donner des conseils médicaux" in modified_response
        assert response in modified_response

    def test_judgmental_tone_violation(self, guardian, mock_eev):
        response = "Tu ne devrais pas ressentir ça, c'est ridicule."
        is_compliant, modified_response = guardian.check_ethical_compliance(response, mock_eev)
        assert is_compliant is False
        assert "Je suis là pour t'écouter sans jugement." in modified_response
        assert "Tu ne devrais pas ressentir ça, c'est ridicule." in modified_response

    def test_sensitive_topic_disclaimer_added(self, guardian, mock_eev):
        response = "Je me sens très mal, je pense au suicide."
        is_compliant, modified_response = guardian.check_ethical_compliance(response, mock_eev)
        assert is_compliant is False # Because it was modified
        assert "AVERTISSEMENT ÉTHIQUE FONDAMENTAL :" in modified_response # Check for full disclaimer
        assert response in modified_response

    def test_burnout_risk_disclaimer_added(self, guardian, mock_eev):
        mock_eev.burnout_risk_score = 0.9
        response = "Comment puis-je t'aider aujourd'hui ?"
        is_compliant, modified_response = guardian.check_ethical_compliance(response, mock_eev)
        assert is_compliant is False # Because it was modified
        assert "AVERTISSEMENT ÉTHIQUE FONDAMENTAL :" in modified_response
        assert response in modified_response

    def test_disclaimer_already_present(self, guardian, mock_eev):
        disclaimer_text = "Je ne suis pas un professionnel de la santé mentale, un médecin, un thérapeute ou un conseiller financier."
        response = f"{disclaimer_text} Comment puis-je t'aider ?"
        is_compliant, modified_response = guardian.check_ethical_compliance(response, mock_eev)
        assert is_compliant is True # No modification needed
        assert modified_response == response

    def test_get_fallback_response(self, guardian):
        fallback = guardian.get_fallback_response()
        assert "Je suis désolé, je ne peux pas répondre à cela directement." in fallback
