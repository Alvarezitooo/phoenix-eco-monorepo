"""
Phoenix Aube - Event Store Models
Architecture Event Sourcing pour intégration écosystème Phoenix
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid

# =============================================
# MODÈLES ÉVÉNEMENTS EVENT STORE  
# =============================================

class ÉvénementPhoenixAube(BaseModel):
    """Événement de base pour l'event store Phoenix Aube"""
    
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="Identifiant utilisateur")
    event_type: str = Field(..., description="Type d'événement")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Données événement
    data: Dict[str, Any] = Field(..., description="Données spécifiques à l'événement")
    
    # Métadonnées
    source_app: str = Field(default="phoenix_aube", description="Application source")
    version: str = Field(default="1.0", description="Version du schema")
    
    # Contexte utilisateur
    session_id: Optional[str] = Field(None, description="ID de session")
    user_agent: Optional[str] = Field(None, description="User agent si applicable")
    
    # Partition key pour scalabilité
    partition_key: str = Field(
        default="", description="Clé partition pour Event Store"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        # Auto-générer partition key si pas fourni
        if not self.partition_key and self.user_id:
            self.partition_key = self.user_id[:8]  # 8 premiers chars UUID

# Types d'événements spécifiques
class ExplorationCommencée(ÉvénementPhoenixAube):
    """Utilisateur commence son exploration métier"""
    event_type: str = Field(default="exploration_commencée", const=True)

class ValeursExplorées(ÉvénementPhoenixAube):
    """Valeurs profondes explorées et identifiées"""
    event_type: str = Field(default="valeurs_explorées", const=True)

class CompétencesRévélées(ÉvénementPhoenixAube):
    """Compétences transférables révélées"""
    event_type: str = Field(default="compétences_révélées", const=True)

class TestsPsychométriquesComplétés(ÉvénementPhoenixAube):
    """Tests Big Five et RIASEC complétés"""
    event_type: str = Field(default="tests_psychométriques_complétés", const=True)

class RecommandationsGénérées(ÉvénementPhoenixAube):
    """Recommandations métiers générées"""
    event_type: str = Field(default="recommandations_générées", const=True)

class ValidationIAEffectuée(ÉvénementPhoenixAube):
    """Validation IA effectuée pour un métier"""
    event_type: str = Field(default="validation_ia_effectuée", const=True)

class MétierChoisi(ÉvénementPhoenixAube):
    """Utilisateur choisit un métier"""
    event_type: str = Field(default="métier_choisi", const=True)

class PlanTransitionCréé(ÉvénementPhoenixAube):
    """Plan de transition créé"""
    event_type: str = Field(default="plan_transition_créé", const=True)

class TransitionÉcosystème(ÉvénementPhoenixAube):
    """Transition vers autre app Phoenix"""
    event_type: str = Field(default="transition_écosystème", const=True)

class ConsentementRecherche3IA(ÉvénementPhoenixAube):
    """Consentement recherche 3IA accordé"""
    event_type: str = Field(default="consentement_recherche_3ia", const=True)

# Événements d'analytics et monitoring
class MétriqueUtilisation(ÉvénementPhoenixAube):
    """Métrique d'utilisation de la plateforme"""
    event_type: str = Field(default="métrique_utilisation", const=True)

class ErreurSystème(ÉvénementPhoenixAube):
    """Erreur système pour monitoring"""
    event_type: str = Field(default="erreur_système", const=True)

class FeedbackUtilisateur(ÉvénementPhoenixAube):
    """Feedback utilisateur sur l'expérience"""
    event_type: str = Field(default="feedback_utilisateur", const=True)


# =============================================
# PHOENIX ECOSYSTEM BRIDGE
# =============================================

class PhoenixEcosystemBridge:
    """Bridge pour intégration cross-apps Phoenix"""
    
    def __init__(self, event_store):
        self.event_store = event_store
    
    async def prepare_cv_transition(
        self, 
        user_id: str, 
        chosen_career: str,
        exploration_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prépare transition vers Phoenix CV"""
        
        transition_event = TransitionÉcosystème(
            user_id=user_id,
            data={
                "target_app": "phoenix_cv",
                "chosen_career": chosen_career,
                "context": {
                    "career_focus": chosen_career,
                    "ia_resistance_score": exploration_context.get("ia_resistance_score"),
                    "skills_to_highlight": exploration_context.get("key_skills", []),
                    "transition_narrative": f"Reconversion vers {chosen_career} validée par Phoenix Aube"
                },
                "transition_url": "https://phoenix-cv.streamlit.app/",
            }
        )
        
        if self.event_store:
            await self.event_store.store_event(transition_event)
        
        return {
            "transition_id": transition_event.event_id,
            "target_url": "https://phoenix-cv.streamlit.app/",
            "context_data": transition_event.data["context"]
        }
    
    async def prepare_letters_transition(
        self, 
        user_id: str, 
        chosen_career: str,
        exploration_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prépare transition vers Phoenix Letters"""
        
        transition_event = TransitionÉcosystème(
            user_id=user_id,
            data={
                "target_app": "phoenix_letters",
                "chosen_career": chosen_career,
                "context": {
                    "reconversion_story": f"Transition validée vers {chosen_career}",
                    "ia_narrative": "Métier choisi résistant aux disruptions IA",
                    "motivation_context": exploration_context.get("motivations", []),
                    "personality_insights": exploration_context.get("psychometric_profile", {})
                },
                "transition_url": "https://phoenix-letters.streamlit.app/",
            }
        )
        
        if self.event_store:
            await self.event_store.store_event(transition_event)
        
        return {
            "transition_id": transition_event.event_id,
            "target_url": "https://phoenix-letters.streamlit.app/",
            "context_data": transition_event.data["context"]
        }
    
    async def prepare_rise_transition(
        self, 
        user_id: str, 
        chosen_career: str,
        exploration_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prépare transition vers Phoenix Rise"""
        
        transition_event = TransitionÉcosystème(
            user_id=user_id,
            data={
                "target_app": "phoenix_rise",
                "chosen_career": chosen_career,
                "context": {
                    "transformation_goal": chosen_career,
                    "confidence_baseline": exploration_context.get("confidence_level", "medium"),
                    "coaching_focus": "IA-proof career transition",
                    "anxiety_level": exploration_context.get("anxiety_score", 0.5),
                    "growth_areas": exploration_context.get("development_needs", [])
                },
                "transition_url": "https://phoenix-rise.streamlit.app/",
            }
        )
        
        if self.event_store:
            await self.event_store.store_event(transition_event)
        
        return {
            "transition_id": transition_event.event_id,
            "target_url": "https://phoenix-rise.streamlit.app/",
            "context_data": transition_event.data["context"]
        }