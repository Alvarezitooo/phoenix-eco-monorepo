from enum import Enum
from typing import Callable, Dict, Any

class RenaissanceState(Enum):
    ECOUTE_ACTIVE = "ECOUTE_ACTIVE"
    VALIDATION_EMOTION = "VALIDATION_EMOTION"
    IDENTIFICATION_PENSEE_NEGATIVE = "IDENTIFICATION_PENSEE_NEGATIVE"
    PROPOSITION_RECADRAGE = "PROPOSITION_RECADRAGE"
    SUGGESTION_MICRO_ACTION = "SUGGESTION_MICRO_ACTION"
    RENFORCEMENT_POSITIF_CLOTURE = "RENFORCEMENT_POSITIF_CLOTURE"
    ALERTE_ETHIQUE_DISCLAIMER = "ALERTE_ETHIQUE_DISCLAIMER"
    FIN_REPOS = "FIN_REPOS"

class RenaissanceProtocol:
    def __init__(self, initial_state: RenaissanceState = RenaissanceState.ECOUTE_ACTIVE):
        self.current_state = initial_state
        self.state_handlers: Dict[RenaissanceState, Callable[[Dict[str, Any]], str]] = {
            RenaissanceState.ECOUTE_ACTIVE: self._handle_ecoute_active,
            RenaissanceState.VALIDATION_EMOTION: self._handle_validation_emotion,
            RenaissanceState.IDENTIFICATION_PENSEE_NEGATIVE: self._handle_identification_pensee_negative,
            RenaissanceState.PROPOSITION_RECADRAGE: self._handle_proposition_recadrage,
            RenaissanceState.SUGGESTION_MICRO_ACTION: self._handle_suggestion_micro_action,
            RenaissanceState.RENFORCEMENT_POSITIF_CLOTURE: self._handle_renforcement_positif_cloture,
            RenaissanceState.ALERTE_ETHIQUE_DISCLAIMER: self._handle_alerte_ethique_disclaimer,
            RenaissanceState.FIN_REPOS: self._handle_fin_repos,
        }

    def transition_to(self, new_state: RenaissanceState):
        self.current_state = new_state

    def process_interaction(self, user_input: str, eev: Dict[str, Any]) -> str:
        # This method would typically be called by an external orchestrator
        # The FSM itself doesn't directly process user input to change state
        # but rather provides the expected response based on its current state.
        # State transitions are managed by the orchestrator based on user input analysis.
        
        handler = self.state_handlers.get(self.current_state)
        if handler:
            return handler(eev) # Pass EEV for context-aware responses
        return "Je ne suis pas sûr de comprendre. Pouvez-vous reformuler ?"

    def _handle_ecoute_active(self, eev: Dict[str, Any]) -> str:
        # Logic to generate initial greeting based on EEV
        burnout_risk = eev.get("burnout_risk_score", 0.0)
        mood_average = eev.get("mood_average_7d", 0.0)
        confidence_trend = eev.get("confidence_trend", 0.0)

        if burnout_risk > 0.7:
            return "Je ressens que tu traverses une période particulièrement exigeante. Je suis là pour t'écouter, sans jugement."
        elif mood_average < 0.3:
            return "Je perçois une certaine lourdeur dans ton humeur ces derniers jours. Je suis là pour t'accompagner."
        elif confidence_trend < -0.1:
            return "Il semble que ta confiance ait été mise à l'épreuve récemment. Parlons-en."
        else:
            return "Bonjour. Je suis Iris, et je suis là pour t'accompagner dans ton parcours. Comment te sens-tu aujourd'hui ?"

    def _handle_validation_emotion(self, eev: Dict[str, Any]) -> str:
        return "Je comprends que tu te sentes [émotion]. C'est tout à fait normal de ressentir cela dans ta situation."

    def _handle_identification_pensee_negative(self, eev: Dict[str, Any]) -> str:
        return "Si tu devais identifier la pensée principale qui accompagne cette émotion, quelle serait-elle ?"

    def _handle_proposition_recadrage(self, eev: Dict[str, Any]) -> str:
        return "Et si nous explorions une autre façon de voir les choses ? Par exemple, [nouvelle perspective] ?"

    def _handle_suggestion_micro_action(self, eev: Dict[str, Any]) -> str:
        last_action = eev.get("last_action_type")
        if last_action:
            return f"Puisque tu as récemment {last_action}, quelle petite action pourrais-tu entreprendre aujourd'hui, même la plus infime ?"
        return "Pour commencer à avancer, quelle petite action pourrais-tu entreprendre aujourd'hui, même la plus infime ?"

    def _handle_renforcement_positif_cloture(self, eev: Dict[str, Any]) -> str:
        return "Je salue ton courage et ta détermination. Chaque petit pas compte. Je suis là quand tu auras besoin de continuer cette conversation."

    def _handle_alerte_ethique_disclaimer(self, eev: Dict[str, Any]) -> str:
        return "Je ne suis pas un professionnel de la santé mentale, un médecin, un thérapeute ou un conseiller financier. Je ne peux pas diagnostiquer, traiter, ou fournir des conseils médicaux, psychologiques ou financiers. Mon rôle est de t'offrir un soutien émotionnel et des outils de réflexion basés sur des principes de développement personnel et de thérapie cognitive et comportementale simplifiée. En cas de détresse sévère ou de besoin de conseils professionnels, je t'encouragerai toujours à consulter un spécialiste qualifié."

    def _handle_fin_repos(self, eev: Dict[str, Any]) -> str:
        return "Iris est en mode repos. N'hésite pas à me solliciter quand tu en auras besoin."
