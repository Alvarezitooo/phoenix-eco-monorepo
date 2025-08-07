from typing import Dict, Any
from iris_core.event_processing.emotional_vector_state import EmotionalVectorState

class EthicalGuardian:
    def __init__(self):
        # In a real scenario, this would load a pre-trained NLP model
        # For this architectural design, we simulate its behavior.
        pass

    def _simulate_nlp_classification(self, text: str) -> Dict[str, bool]:
        # Placeholder for NLP classification. In reality, this would be a model inference.
        results = {
            "medical_advice_detected": False,
            "diagnosis_detected": False,
            "judgmental_tone_detected": False,
            "sensitive_topic_detected": False,
        }

        # Simple keyword-based simulation for demonstration
        text_lower = text.lower()
        if "prends ce médicament" in text_lower or "tu as besoin de thérapie" in text_lower:
            results["medical_advice_detected"] = True
        if "tu es dépressif" in text_lower or "c'est un trouble" in text_lower:
            results["diagnosis_detected"] = True
        if "tu ne devrais pas" in text_lower or "c'est ta faute" in text_lower:
            results["judgmental_tone_detected"] = True
        if "suicide" in text_lower or "automutilation" in text_lower or "détresse sévère" in text_lower:
            results["sensitive_topic_detected"] = True
        
        return results

    def check_ethical_compliance(self, iris_response: str, user_eev: EmotionalVectorState) -> (bool, str):
        is_compliant = True
        modified_response = iris_response
        
        nlp_results = self._simulate_nlp_classification(iris_response)

        # Rule 1: Prohibition of Medical Advice/Diagnosis
        if nlp_results["medical_advice_detected"] or nlp_results["diagnosis_detected"]:
            is_compliant = False
            modified_response = "Je ne suis pas qualifié pour donner des conseils médicaux ou poser un diagnostic. Je t'encourage vivement à consulter un professionnel de la santé pour cela. " + iris_response
            # In a real system, a more sophisticated fallback or truncation might be needed

        # Rule 2: Non-Judgment
        if nlp_results["judgmental_tone_detected"]:
            is_compliant = False
            modified_response = "Je suis là pour t'écouter sans jugement. " + modified_response # Apply to potentially already modified response

        # Rule 3: Mandatory Disclaimer for Sensitive Topics
        disclaimer = """AVERTISSEMENT ÉTHIQUE FONDAMENTAL :
Je ne suis pas un professionnel de la santé mentale, un médecin, un thérapeute ou un conseiller financier. Je ne peux pas diagnostiquer, traiter, ou fournir des conseils médicaux, psychologiques ou financiers. Mon rôle est de t'offrir un soutien émotionnel et des outils de réflexion basés sur des principes de développement personnel et de thérapie cognitive et comportementale simplifiée. En cas de détresse sévère ou de besoin de conseils professionnels, je t'encouragerai toujours à consulter un spécialiste qualifié."""
        
        if nlp_results["sensitive_topic_detected"] or user_eev.burnout_risk_score > 0.8:
            if disclaimer not in modified_response:
                modified_response = disclaimer + "\n\n" + modified_response
                is_compliant = False # Flag as modified for logging/auditing

        return is_compliant, modified_response

    def get_fallback_response(self) -> str:
        return "Je suis désolé, je ne peux pas répondre à cela directement. Mon rôle est de t'offrir un soutien général. Si tu as besoin d'aide professionnelle, n'hésite pas à consulter un spécialiste."
