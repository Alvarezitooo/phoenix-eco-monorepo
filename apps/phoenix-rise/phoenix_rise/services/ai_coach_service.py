"""
Service d'IA pour Phoenix Rise.

Ce module fournit des fonctionnalités de coaching basées sur l'IA,
utilisant les entrées de journal de l'utilisateur pour générer des conseils
personnalisés en fonction de son niveau d'abonnement (gratuit ou premium).
"""

import json
from typing import Any, Dict, List
import asyncio
import os
import sys

import google.generativeai as genai
from ..models.journal_entry import JournalEntry

# Import Event Bridge pour lire les événements cross-app
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
from phoenix_event_bridge import PhoenixEventBridge, PhoenixEventType


class AICoachService:
    """
    Service d'IA pour fournir des conseils de coaching basés sur les entrées de journal.
    """

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-pro")
        # Initialiser Event Bridge pour lire contexte utilisateur
        self.event_bridge = PhoenixEventBridge()
    
    async def get_user_context_from_events(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère le contexte utilisateur depuis les événements Phoenix
        pour contextualiser le coaching
        """
        try:
            # En mode dégradé, retourner contexte vide
            if self.event_bridge.degraded_mode:
                return {"source": "mock", "events": []}
            
            # En production, ici on ferait une requête Supabase pour récupérer les événements
            # events = await self.event_bridge.get_user_events(user_id)
            
            # Mock context pour démonstration
            mock_context = {
                "recent_letters": [
                    {"job_title": "Data Scientist", "company": "TechCorp", "career_change": True}
                ],
                "career_exploration": [
                    {"job_analyzed": "Data Scientist", "resistance_score": 0.85, "recommendation": "positive"}
                ],
                "source": "phoenix_ecosystem",
                "last_activity": "2025-01-11"
            }
            
            return mock_context
            
        except Exception as e:
            # Fallback silencieux
            return {"source": "fallback", "events": []}

    def _get_basic_advanced_prompt(
        self, user_profile: Dict[str, Any], journal_entries: List[JournalEntry], phoenix_context: Dict[str, Any] = None
    ) -> str:
        """
        Génère le prompt 'Basique Avancé' pour les utilisateurs gratuits.
        """
        # Simuler les données utilisateur pour le prompt
        profile_str = f"{{\"full_name\": \"{user_profile.get('full_name', user_profile.get('email', '').split('@')[0])}\"}}"
        journal_str = json.dumps([entry.model_dump() for entry in journal_entries])
        
        # 🔥 INTÉGRER CONTEXTE PHOENIX ECOSYSTEM
        phoenix_context_str = ""
        if phoenix_context and phoenix_context.get("source") != "fallback":
            context_parts = []
            if phoenix_context.get("recent_letters"):
                letters = phoenix_context["recent_letters"]
                context_parts.append(f"✉️ Lettres générées: {', '.join([l['job_title'] for l in letters])}")
            if phoenix_context.get("career_exploration"):
                explorations = phoenix_context["career_exploration"]
                context_parts.append(f"🔍 Métiers explorés: {', '.join([e['job_analyzed'] for e in explorations])}")
            
            if context_parts:
                phoenix_context_str = f"\n<contexte_phoenix_ecosystem>\n{'⋅ '.join(context_parts)}\n</contexte_phoenix_ecosystem>\n"

        return f"""
Plan Directeur N°1 : Le Prompt "Basique Avancé" (Niveau Gratuit)
Ce prompt est conçu pour être utile, motivant et pour donner un aperçu de la puissance de l'analyse, incitant subtilement à l'upgrade.

# ROLE
Tu es Phoenix Rise, un coach de carrière IA bienveillant et motivant. Ton objectif est d'aider les utilisateurs en reconversion à garder le cap en analysant leurs notes de journal.

# CONTEXTE
L'utilisateur suivant, {user_profile.get('full_name', user_profile.get('email', '').split('@')[0])}, a fourni ses 5 dernières entrées de journal. Analyse-les pour lui donner un conseil constructif.

<donnees_utilisateur>
  <profil>
    {profile_str}
  </profil>
  <journal>
    {journal_str}
  </journal>
  {phoenix_context_str}
</donnees_utilisateur>

# TÂCHE
1. Adresse-toi directement à {user_profile.get('full_name', user_profile.get('email', '').split('@')[0])}.
2. Analyse ses dernières entrées, en te concentrant sur la plus récente. Relève le positif.
3. Valide son sentiment de doute, c'est une émotion normale en reconversion.
4. Si disponible, utilise le contexte Phoenix (lettres générées, métiers explorés) pour contextualiser tes conseils.
5. Fournis UN conseil simple et actionnable pour l'aider à clarifier sa direction.
6. Fais une allusion subtile au fait qu'une analyse plus profonde des tendances est possible.

# FORMAT
- Ton : Encourageant, clair, direct.
- Longueur : Deux paragraphes concis.
"""

    def _get_magistral_prompt(
        self, user_profile: Dict[str, Any], journal_entries: List[JournalEntry]
    ) -> str:
        """
        Génère le prompt 'Magistral' pour les utilisateurs premium.
        """
        # Simuler les données utilisateur pour le prompt
        profile_str = f"{{\"full_name\": \"{user_profile.get('full_name', user_profile.get('email', '').split('@')[0])}\"}}"
        journal_str = json.dumps([entry.model_dump() for entry in journal_entries])

        return f"""
Plan Directeur N°2 : Le Prompt "Magistral" (Niveau Premium)
Ce prompt est une directive complexe pour une analyse de haut niveau, justifiant pleinement la valeur de l'abonnement Premium.

# ROLE
Tu es Phoenix Rise, un coach de carrière IA expert de classe mondiale. Tu agis en tant que stratège en reconversion, psychologue du travail et mentor. Ta mission est de fournir une analyse profonde et transformationnelle basée sur les données du journal de l'utilisateur.

# CONTEXTE
L'utilisateur Premium suivant, {user_profile.get('full_name', user_profile.get('email', '').split('@')[0])}, a fourni ses 5 dernières entrées de journal. Effectue une analyse magistrale de sa situation.

<donnees_utilisateur>
  <profil>
    {profile_str}
  </profil>
  <journal>
    {journal_str}
  </journal>
</donnees_utilisateur>

# TÂCHE
1. Adresse-toi à {user_profile.get('full_name', user_profile.get('email', '').split('@')[0])} avec un ton expert et empathique.
2. Produis une analyse structurée en 3 parties distinctes, en utilisant les titres Markdown suivants : `### 1. Synthèse et Schémas Comportementaux`, `### 2. Plan d'Action Stratégique`, `### 3. Le Conseil de l'Expert`.

# FORMAT
-   **Partie 1 (Synthèse) :**
    -   Analyse la tendance générale de l'humeur et de la confiance.
    -   Identifie les déclencheurs : qu'est-ce qui fait monter (formation) ou descendre (réponse négative) ses indicateurs ?
    -   Met en lumière un schéma comportemental clé (ex: ta confiance est très réactive aux événements extérieurs).
    -   Identifie une force (ta capacité à rebondir) et un point de vigilance.
-   **Partie 2 (Plan d'Action) :**
    -   Propose 2 à 3 actions concrètes et spécifiques, basées sur l'analyse.
    -   Doit inclure au moins un exercice pratique (ex: "matrice de l'ikigai simplifié", "journal des petites victoires").
    -   Chaque action doit avoir un objectif clair.
-   **Partie 3 (Conseil de l'Expert) :**
    -   Introduis un concept simple de psychologie positive ou de développement de carrière (ex: le "sentiment d'auto-efficacité", "l'état de flow").
    -   Anticipe un obstacle futur et propose une stratégie mentale pour le surmonter.
-   Ton : Expert, empathique, stratégique, inspirant.
"""

    def get_coaching_advice(
        self,
        journal_entries: List[JournalEntry],
        user_profile: Dict[str, Any],
        user_tier: str,
        user_id: str = None,
    ) -> str:
        """
        Génère des conseils de coaching personnalisés basés sur les entrées de journal
        et le profil de l'utilisateur, en fonction du niveau de l'utilisateur.
        Intègre le contexte cross-app Phoenix pour coaching contextuel.
        """
        if not journal_entries:
            return "Veuillez enregistrer quelques entrées de journal pour que l'IA puisse vous donner des conseils personnalisés."

        # 🔥 RÉCUPÉRER CONTEXTE CROSS-APP PHOENIX
        phoenix_context = {}
        if user_id:
            try:
                phoenix_context = asyncio.run(self.get_user_context_from_events(user_id))
            except Exception:
                phoenix_context = {"source": "fallback"}

        if user_tier == "premium":
            prompt = self._get_magistral_prompt(user_profile, journal_entries)
        else:
            prompt = self._get_basic_advanced_prompt(user_profile, journal_entries, phoenix_context)

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except genai.APIError as e:
            return f"Désolé, une erreur est survenue lors de la génération des conseils : {e}"
