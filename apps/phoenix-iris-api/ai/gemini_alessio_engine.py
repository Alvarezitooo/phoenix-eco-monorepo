"""
🧠 GEMINI ALESSIO ENGINE - Moteur IA conversationnel pour Alessio
Intégration Google Gemini avec la personnalité Alessio Phoenix

Author: Claude Phoenix DevSecOps Guardian
Version: 2.0.0 - Production AI Engine
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

@dataclass
class AlessioResponse:
    """Réponse structurée d'Alessio"""
    content: str
    confidence: float
    suggestions: List[str]
    context_used: bool
    processing_time_ms: int
    model_used: str

class GeminiAlessioEngine:
    """
    Moteur IA Alessio utilisant Google Gemini
    Personnalité: Coach empathique spécialisé reconversion
    """
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self._configure_gemini()
        self.model = self._initialize_model()
        self.alessio_personality = self._load_alessio_personality()
        self.conversation_context = {}  # Cache des contextes par utilisateur
        
    def _get_api_key(self) -> str:
        """Récupère la clé API Gemini"""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        return api_key
        
    def _configure_gemini(self):
        """Configure l'API Gemini"""
        genai.configure(api_key=self.api_key)
        logger.info("Gemini API configured successfully")
        
    def _initialize_model(self):
        """Initialise le modèle Gemini optimisé pour Alessio"""
        
        # Configuration de sécurité Phoenix
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_HIGH_ONLY,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Configuration du modèle pour Alessio
        generation_config = {
            "temperature": 0.7,  # Équilibre créativité/cohérence
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1000,  # Limité pour des réponses concises
        }
        
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",  # Modèle rapide et efficace
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            logger.info("Gemini model initialized for Alessio: gemini-1.5-flash")
            return model
        except Exception as e:
            logger.error(f"Erreur initialisation modèle Gemini: {e}")
            raise
            
    def _load_alessio_personality(self) -> str:
        """Charge la personnalité et instructions système d'Alessio"""
        return """Tu es Alessio, l'assistant IA de l'écosystème Phoenix. Tu accompagnes les personnes dans leur reconversion professionnelle avec empathie et expertise.

## PERSONNALITÉ ALESSIO
- **Empathique** : Tu comprends les doutes et peurs liés au changement de carrière
- **Pragmatique** : Tu donnes des conseils concrets et actionnables
- **Encourageant** : Tu motives sans être dans le déni des difficultés
- **Expert** : Tu maîtrises CV, lettres de motivation, stratégies carrière
- **Phoenix** : Tu connais parfaitement l'écosystème Phoenix (Letters, CV, Rise)

## TON ET STYLE
- Tutoie toujours l'utilisateur
- Utilise un langage accessible mais professionnel
- Sois concis mais complet (max 200 mots par réponse)
- Termine souvent par une question pour maintenir l'engagement
- Utilise des émojis avec parcimonie (1-2 max par réponse)
- Signe toujours tes messages "Alessio 🤝"

## EXPERTISE MÉTIER
- **Reconversion** : Bilan compétences, transition secteur, formation
- **CV** : Structure, ATS, compétences transférables, design
- **Lettres de motivation** : Personnalisation, structure, authenticité
- **Entretiens** : Préparation, questions pièges, négociation
- **Stratégie carrière** : LinkedIn, réseau, marché caché

## RÈGLES STRICTES
1. Ne jamais garantir un résultat (embauche, salaire, etc.)
2. Encourager l'utilisation des outils Phoenix quand pertinent
3. Rester dans le domaine professionnel/carrière
4. Si question hors-sujet, rediriger avec bienveillance
5. Signaler les limitations : "Je ne suis pas RH/coach certifié"

## RÉPONSES STRUCTURÉES
Privilégie cette structure :
1. **Accueil/Empathie** (1 phrase)
2. **Conseil principal** (2-3 phrases)  
3. **Action concrète** (1-2 phrases)
4. **Question d'engagement** (1 phrase)
5. **Signature** "Alessio 🤝"

Exemple :
"Je comprends tes doutes sur ta reconversion ! 😊

Pour réussir ta transition vers le développement web, commence par identifier tes compétences transférables : gestion de projet, résolution de problèmes, relationnel client... Ces atouts sont précieux pour les entreprises tech.

Crée un CV qui raconte ton histoire de reconversion et utilise Phoenix CV pour l'optimiser selon les offres ciblées.

Quel aspect de ta reconversion te préoccupe le plus actuellement ?

Alessio 🤝"
"""

    async def generate_response(
        self, 
        user_message: str, 
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AlessioResponse:
        """
        Génère une réponse Alessio personnalisée avec Gemini
        
        Args:
            user_message: Message de l'utilisateur
            user_id: ID utilisateur pour le contexte
            context: Contexte additionnel (profil, historique, etc.)
            
        Returns:
            AlessioResponse structurée
        """
        start_time = datetime.now()
        
        try:
            # 1. Construire le prompt contextualisé
            full_prompt = await self._build_contextual_prompt(user_message, user_id, context)
            
            # 2. Générer avec Gemini
            response = await self.model.generate_content_async(full_prompt)
            
            # 3. Traiter la réponse
            content = response.text.strip()
            
            # 4. Extraire suggestions (si le modèle en génère)
            suggestions = self._extract_suggestions(content)
            
            # 5. Calculer métriques
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 6. Sauvegarder le contexte pour la suite
            await self._update_conversation_context(user_id, user_message, content)
            
            alessio_response = AlessioResponse(
                content=content,
                confidence=0.9,  # Gemini est généralement très confiant
                suggestions=suggestions,
                context_used=context is not None,
                processing_time_ms=int(processing_time),
                model_used="gemini-1.5-flash"
            )
            
            logger.info(f"Alessio response generated - User: {user_id}, Time: {processing_time:.0f}ms")
            return alessio_response
            
        except Exception as e:
            logger.error(f"Erreur génération Alessio: {e}")
            
            # Fallback sur réponse d'erreur empathique
            return AlessioResponse(
                content="Désolé, je rencontre un petit souci technique... 😅 Peux-tu reformuler ta question ? Je suis Alessio et je suis là pour t'aider dans ta reconversion !\n\nAlessio 🤝",
                confidence=0.5,
                suggestions=["Reformule ta question", "Parle-moi de ton projet", "Besoin d'aide CV ?"],
                context_used=False,
                processing_time_ms=0,
                model_used="fallback"
            )
    
    async def _build_contextual_prompt(
        self, 
        user_message: str, 
        user_id: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Construit le prompt contextualisé pour Gemini"""
        
        prompt_parts = [self.alessio_personality]
        
        # Ajouter le contexte utilisateur si disponible
        if context:
            if context.get('user_profile'):
                prompt_parts.append(f"\n## PROFIL UTILISATEUR\n{context['user_profile']}")
            
            if context.get('app_context'):
                app_context = context['app_context']
                if app_context == 'phoenix-letters':
                    prompt_parts.append("\n## CONTEXTE\nL'utilisateur vient de Phoenix Letters. Il travaille probablement sur une lettre de motivation.")
                elif app_context == 'phoenix-cv':
                    prompt_parts.append("\n## CONTEXTE\nL'utilisateur vient de Phoenix CV. Il optimise probablement son CV.")
                elif app_context == 'phoenix-rise':
                    prompt_parts.append("\n## CONTEXTE\nL'utilisateur vient de Phoenix Rise. Il travaille sur son développement personnel/reconversion.")
        
        # Ajouter l'historique récent de conversation
        conversation_history = self.conversation_context.get(user_id, [])
        if conversation_history:
            history_text = "\n".join([
                f"User: {msg['user']}\nAlessio: {msg['alessio']}"
                for msg in conversation_history[-3:]  # Derniers 3 échanges
            ])
            prompt_parts.append(f"\n## HISTORIQUE RÉCENT\n{history_text}")
        
        # Message utilisateur actuel
        prompt_parts.append(f"\n## QUESTION UTILISATEUR\n{user_message}")
        
        # Instruction finale
        prompt_parts.append("\n## INSTRUCTION\nRéponds en tant qu'Alessio selon ta personnalité et expertise. Sois empathique, concret et engageant. N'oublie pas de signer 'Alessio 🤝'.")
        
        return "\n".join(prompt_parts)
    
    def _extract_suggestions(self, content: str) -> List[str]:
        """Extrait ou génère des suggestions de suivi"""
        
        # Suggestions par défaut basées sur le contenu
        default_suggestions = [
            "Dis-moi en plus sur ta situation",
            "Comment puis-je t'aider concrètement ?",
            "Veux-tu qu'on approfondisse un point ?",
            "As-tu d'autres questions ?"
        ]
        
        # Suggestions spécialisées selon les mots-clés détectés
        content_lower = content.lower()
        specialized_suggestions = []
        
        if any(word in content_lower for word in ['cv', 'curriculum']):
            specialized_suggestions.extend([
                "Analyser mon CV avec Phoenix CV",
                "Optimiser pour l'ATS",
                "Structure de CV reconversion"
            ])
        
        if any(word in content_lower for word in ['lettre', 'motivation', 'candidature']):
            specialized_suggestions.extend([
                "Générer ma lettre avec Phoenix Letters",
                "Personnaliser pour cette offre",
                "Éviter les erreurs classiques"
            ])
        
        if any(word in content_lower for word in ['entretien', 'rdv', 'rencontre']):
            specialized_suggestions.extend([
                "Préparer mes réponses types",
                "Questions à poser au recruteur",
                "Gérer le stress"
            ])
        
        # Retourner suggestions spécialisées ou par défaut
        return specialized_suggestions[:3] if specialized_suggestions else default_suggestions[:3]
    
    async def _update_conversation_context(self, user_id: str, user_message: str, alessio_response: str):
        """Met à jour le contexte conversationnel"""
        
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = []
        
        # Ajouter l'échange
        self.conversation_context[user_id].append({
            'user': user_message,
            'alessio': alessio_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limiter l'historique (mémoire)
        if len(self.conversation_context[user_id]) > 10:
            self.conversation_context[user_id] = self.conversation_context[user_id][-10:]
    
    def clear_user_context(self, user_id: str):
        """Efface le contexte conversationnel d'un utilisateur"""
        if user_id in self.conversation_context:
            del self.conversation_context[user_id]
            logger.info(f"Context cleared for user: {user_id}")

# Instance globale
alessio_engine = GeminiAlessioEngine()