"""
Phoenix Rise Event Helper
Service pour publier les événements Phoenix Rise vers la data pipeline Event Sourcing
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from phoenix_event_bridge import PhoenixEventBridge

logger = logging.getLogger(__name__)


class PhoenixRiseEventHelper:
    """
    Helper pour publier les événements Phoenix Rise vers le système Event Sourcing.
    """
    
    def __init__(self):
        try:
            self.event_bridge = PhoenixEventBridge()
            self.is_available = True
            logger.info("✅ Phoenix Rise Event Helper initialisé avec succès")
        except Exception as e:
            logger.warning(f"⚠️ Event Bridge non disponible: {e}")
            self.event_bridge = None
            self.is_available = False

    def publish_mood_logged(
        self, 
        user_id: str, 
        mood: int, 
        confidence: int, 
        notes: Optional[str] = None,
        journal_entry_id: str = None
    ) -> bool:
        """
        Publie un événement MoodLogged.
        
        Args:
            user_id: ID utilisateur
            mood: Niveau d'humeur (1-10)
            confidence: Niveau de confiance (1-10)
            notes: Notes optionnelles
            journal_entry_id: ID de l'entrée journal
            
        Returns:
            bool: True si publié avec succès
        """
        if not self.is_available:
            logger.debug("Event Bridge non disponible - événement ignoré")
            return False
            
        try:
            event_data = {
                "event_type": "MoodLogged",
                "user_id": user_id,
                "journal_entry_id": journal_entry_id,
                "mood": mood,
                "confidence": confidence,
                "notes": notes,
                "timestamp": datetime.utcnow().isoformat(),
                "source_app": "phoenix_rise",
                "version": "1.0"
            }
            
            success = self.event_bridge.publish_event(
                event_type="MoodLogged",
                data=event_data,
                source="phoenix_rise"
            )
            
            if success:
                logger.info(f"✅ Événement MoodLogged publié pour user {user_id}")
            else:
                logger.error(f"❌ Échec publication MoodLogged pour user {user_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur publication MoodLogged: {e}")
            return False

    def publish_objective_created(
        self, 
        user_id: str, 
        objective_id: str,
        objective_title: str,
        objective_type: str,
        target_date: Optional[str] = None
    ) -> bool:
        """
        Publie un événement ObjectiveCreated.
        
        Args:
            user_id: ID utilisateur
            objective_id: ID objectif
            objective_title: Titre de l'objectif
            objective_type: Type d'objectif
            target_date: Date cible optionnelle
            
        Returns:
            bool: True si publié avec succès
        """
        if not self.is_available:
            logger.debug("Event Bridge non disponible - événement ignoré")
            return False
            
        try:
            event_data = {
                "event_type": "ObjectiveCreated",
                "user_id": user_id,
                "objective_id": objective_id,
                "objective_title": objective_title,
                "objective_type": objective_type,
                "target_date": target_date,
                "timestamp": datetime.utcnow().isoformat(),
                "source_app": "phoenix_rise",
                "version": "1.0"
            }
            
            success = self.event_bridge.publish_event(
                event_type="ObjectiveCreated",
                data=event_data,
                source="phoenix_rise"
            )
            
            if success:
                logger.info(f"✅ Événement ObjectiveCreated publié pour user {user_id}")
            else:
                logger.error(f"❌ Échec publication ObjectiveCreated pour user {user_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur publication ObjectiveCreated: {e}")
            return False

    def publish_coaching_session_started(
        self,
        user_id: str,
        session_id: str,
        session_type: str,
        user_tier: str = "free"
    ) -> bool:
        """
        Publie un événement CoachingSessionStarted.
        
        Args:
            user_id: ID utilisateur
            session_id: ID session coaching
            session_type: Type de session (gratuit/premium)
            user_tier: Tier utilisateur
            
        Returns:
            bool: True si publié avec succès
        """
        if not self.is_available:
            logger.debug("Event Bridge non disponible - événement ignoré")
            return False
            
        try:
            event_data = {
                "event_type": "CoachingSessionStarted",
                "user_id": user_id,
                "session_id": session_id,
                "session_type": session_type,
                "user_tier": user_tier,
                "timestamp": datetime.utcnow().isoformat(),
                "source_app": "phoenix_rise",
                "version": "1.0"
            }
            
            success = self.event_bridge.publish_event(
                event_type="CoachingSessionStarted", 
                data=event_data,
                source="phoenix_rise"
            )
            
            if success:
                logger.info(f"✅ Événement CoachingSessionStarted publié pour user {user_id}")
            else:
                logger.error(f"❌ Échec publication CoachingSessionStarted pour user {user_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur publication CoachingSessionStarted: {e}")
            return False

    def publish_profile_created(
        self,
        user_id: str,
        email: str,
        full_name: Optional[str] = None
    ) -> bool:
        """
        Publie un événement ProfileCreated.
        
        Args:
            user_id: ID utilisateur
            email: Email utilisateur
            full_name: Nom complet optionnel
            
        Returns:
            bool: True si publié avec succès
        """
        if not self.is_available:
            logger.debug("Event Bridge non disponible - événement ignoré")
            return False
            
        try:
            event_data = {
                "event_type": "ProfileCreated",
                "user_id": user_id,
                "email": email,
                "full_name": full_name,
                "timestamp": datetime.utcnow().isoformat(),
                "source_app": "phoenix_rise",
                "version": "1.0"
            }
            
            success = self.event_bridge.publish_event(
                event_type="ProfileCreated",
                data=event_data,
                source="phoenix_rise"
            )
            
            if success:
                logger.info(f"✅ Événement ProfileCreated publié pour user {user_id}")
            else:
                logger.error(f"❌ Échec publication ProfileCreated pour user {user_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur publication ProfileCreated: {e}")
            return False


# Instance globale
phoenix_rise_event_helper = PhoenixRiseEventHelper()