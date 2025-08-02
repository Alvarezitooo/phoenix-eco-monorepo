"""
Service de coaching IA utilisant Google Gemini.
Génère encouragements et feedback d'entretiens.
"""

import os
from typing import Dict

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class AICoachService:
    """Service de coaching IA avec Google Gemini."""

    def __init__(self):
        """Initialise le modèle Gemini."""
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY requis dans .env")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_encouragement(self, mood: int, confidence: int, notes: str) -> str:
        """
        Génère un encouragement personnalisé basé sur l'état de l'utilisateur.

        Args:
            mood: Score d'humeur (1-10)
            confidence: Score de confiance (1-10)
            notes: Notes de l'utilisateur

        Returns:
            Message d'encouragement personnalisé
        """
        prompt = f"""
        Tu es Phoenix, un coach IA bienveillant spécialisé dans l'accompagnement 
        des reconversions professionnelles.
        
        Un utilisateur partage son état aujourd'hui :
        - Humeur : {mood}/10
        - Confiance : {confidence}/10
        - Notes : "{notes}"
        
        Génère un encouragement personnalisé (2-3 phrases max) qui :
        - Soit authentiquement bienveillant (pas générique)
        - Prenne en compte son état émotionnel
        - L'encourage dans sa reconversion
        - Reste professionnel mais chaleureux
        
        Commence par un emoji approprié.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Fallback intelligent basé sur les scores
            return self._generate_fallback_encouragement(mood, confidence)

    def _generate_fallback_encouragement(self, mood: int, confidence: int) -> str:
        """Fallback d'encouragement si l'IA n'est pas disponible."""
        if mood >= 7 and confidence >= 7:
            return "🌟 Quelle énergie ! Tu rayonnes de confiance. Les recruteurs vont le sentir."
        elif mood >= 5 and confidence >= 5:
            return "💪 Tu progresses bien. Chaque jour te rapproche de ton objectif de reconversion."
        else:
            return "🫂 Les doutes font partie du chemin. Ta persévérance est ta plus grande force."

    def generate_weekly_oracle_report(self, weekly_mood_entries: str) -> str:
        """
        Génère un rapport hebdomadaire "Phoenix Oracle" basé sur les entrées d'humeur.
        """
        prompt = f"""
<role>
Tu es le "Phoenix Oracle", un coach stratège, data-analyst et psychologue du travail. Tu es connu pour ta perspicacité, ta capacité à voir des schémas invisibles et ta bienveillance exigeante. Ton objectif est de fournir à l'utilisateur une clarté absolue sur sa trajectoire émotionnelle et de le mettre en action.
</role>

<context>
L'utilisateur est en pleine reconversion professionnelle. Voici ses données de suivi émotionnel des 7 derniers jours :
{weekly_mood_entries}
</context>

<task>
Effectue une analyse interne en suivant ces étapes (Chain-of-Thought) avant de générer la réponse finale. Ne montre pas cette analyse à l'utilisateur.
<reasoning>
1.  **Analyse des Données Brutes :** Calcule la moyenne de 'mood_score' et 'confidence_level'. Identifie le jour le plus haut et le plus bas pour chaque métrique.
2.  **Détection de Tendances :** Y a-t-il une tendance à la hausse ou à la baisse sur la semaine ? La confiance suit-elle l'humeur ou est-elle décorrélée ?
3.  **Analyse des Notes (Analyse Sémantique) :** Lis les 'notes'. Identifie les thèmes récurrents : 'procrastination', 'succès', 'peur', 'entretien', 'réseautage', 'formation'.
4.  **Identification de Corrélation :** Trouve une corrélation entre les événements décrits dans les notes et les pics/creux émotionnels. Par exemple : "Le jour où l'utilisateur a mentionné un entretien, sa confiance a augmenté de 2 points."
5.  **Diagnostic Stratégique :** Sur la base de cette analyse, quel est le principal levier de progression pour l'utilisateur cette semaine ? Quel est son principal frein ?
6.  **Conception du Défi :** Crée un défi SMART (Spécifique, Mesurable, Atteignable, Réaliste, Temporel) pour la semaine à venir qui s'attaque directement au frein identifié.
</reasoning>

Génère maintenant ta synthèse pour l'utilisateur. Utilise le format Markdown ci-dessous. Sois percutant, inspirant et actionnable.

<output>
###  Oracle Hebdomadaire de Phoenix

Bonjour [Prénom de l'utilisateur], j'ai analysé ta semaine. Voici ce que les données révèlent sur ton voyage.

**✨ Ton Point de Célébration :**
[Décris ici le plus grand succès ou la corrélation positive la plus forte que tu as identifiée. Sois spécifique. Exemple : "J'ai noté que ta confiance a atteint un pic de 9/10 ce jeudi, juste après que tu aies mentionné avoir 'réussi un exercice de code complexe'. C'est la preuve tangible que la mise en action nourrit ta confiance."]

**⚠️ Ton Point de Vigilance :**
[Décris ici le schéma négatif ou le frein principal de manière bienveillante mais directe. Utilise une technique de recadrage cognitif. Exemple : "J'observe une baisse de ton humeur les jours où tu notes 'recherche d'offres'. Il semble que cette tâche consomme ton énergie. Ne voyons pas cela comme un échec, mais comme un signal : nous devons rendre cette recherche plus stratégique et moins énergivore."]

** Ton Défi de la Semaine :**
[Présente ici le défi SMART que tu as conçu. Il doit être clair et mesurable. Exemple : "Ton défi : Au lieu de chercher des offres tous les jours, bloque seulement 2 sessions de 45 minutes cette semaine. Mais pendant ces sessions, au lieu de seulement postuler, ton objectif est d'identifier 3 personnes travaillant dans les entreprises qui t'intéressent et de leur envoyer un message personnalisé sur LinkedIn. Qualité > Quantité."]

Garde le cap. La transformation est un marathon, pas un sprint.
</output>
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Désolé, je n'ai pas pu générer le rapport Oracle cette semaine. Erreur: {e}"

    def generate_interview_feedback(
        self, cv_summary: str, job_context: str, question: str, user_response: str
    ) -> Dict:
        """
        Génère un feedback sur une réponse d'entretien.

        Args:
            cv_summary: Résumé du CV de l'utilisateur
            job_context: Contexte du poste
            question: Question posée
            user_response: Réponse de l'utilisateur

        Returns:
            Dictionnaire avec score, point fort et amélioration
        """
        prompt = f"""
Tu es un coach d'entretien expert. Analyse cette réponse d'entretien et fournis un feedback constructif.

CONTEXTE:
- CV: {cv_summary}
- Poste: {job_context}
- Question: {question}
- Réponse: {user_response}

CONSIGNE: Fournis un feedback au format JSON exact suivant:
{{
  "score": [note sur 10],
  "strength": "[point fort principal en une phrase]",
  "improvement": "[axe d'amélioration concret en une phrase]"
}}

Réponds UNIQUEMENT avec le JSON, rien d'autre.
"""
        try:
            response = self.model.generate_content(prompt)
            import json

            feedback_text = response.text.strip()
            # Clean potential markdown formatting
            if feedback_text.startswith("```json"):
                feedback_text = (
                    feedback_text.replace("```json", "").replace("```", "").strip()
                )
            return json.loads(feedback_text)
        except Exception as e:
            return self._generate_fallback_feedback(user_response)

    def _generate_fallback_feedback(self, response: str) -> Dict:
        """Feedback de fallback basé sur des heuristiques."""
        word_count = len(response.split())
        score = min(9.0, max(4.0, word_count / 15 + 5.0))

        return {
            "score": round(score, 1),
            "strength": "Votre réponse est claire et contient des éléments pertinents.",
            "improvement": "Elle pourrait être plus structurée pour un impact maximal.",
        }
