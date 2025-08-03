"""
Service de base de données hybride pour Phoenix Rise.

Combine MockDBService (pour le stockage local) avec Phoenix Event Helper (pour la data pipeline).
Assure la compatibilité et la transition progressive vers l'Event Sourcing.
"""

import uuid
import logging
from typing import Any, Dict, List
from datetime import datetime

import streamlit as st
from models.journal_entry import JournalEntry
from .mock_db_service import MockDBService
from .phoenix_rise_event_helper import phoenix_rise_event_helper

logger = logging.getLogger(__name__)


class HybridDBService:
    """
    Service de base de données hybride.
    Utilise MockDBService pour le stockage local ET publie les événements vers la data pipeline.
    """

    def __init__(self):
        self.mock_service = MockDBService()
        self.event_helper = phoenix_rise_event_helper
        logger.info("✅ HybridDBService initialisé (Mock + Event Sourcing)")

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Récupère un profil utilisateur."""
        return self.mock_service.get_profile(user_id)

    def create_profile(
        self, user_id: str, email: str, full_name: str = None
    ) -> Dict[str, Any]:
        """Crée un profil utilisateur."""
        # 1. Créer via Mock (pour compatibilité locale)
        profile = self.mock_service.create_profile(user_id, email, full_name)
        
        # 2. Publier événement (pour data pipeline)
        try:
            self.event_helper.publish_profile_created(
                user_id=user_id,
                email=email,
                full_name=full_name
            )
        except Exception as e:
            logger.warning(f"⚠️ Échec publication ProfileCreated: {e}")
        
        return profile

    def get_objectives(self, user_id: str) -> list:
        """Récupère la liste des objectifs d'un utilisateur."""
        return self.mock_service.get_objectives(user_id)

    def create_objective(
        self,
        user_id: str,
        title: str,
        description: str = None,
        objective_type: str = "personal",
        target_date: str = None,
    ) -> Dict[str, Any]:
        """Crée un nouvel objectif."""
        # 1. Créer via Mock
        objective = self.mock_service.create_objective(
            user_id, title, description, objective_type, target_date
        )
        
        # 2. Publier événement
        try:
            self.event_helper.publish_objective_created(
                user_id=user_id,
                objective_id=objective["id"],
                objective_title=title,
                objective_type=objective_type,
                target_date=target_date
            )
        except Exception as e:
            logger.warning(f"⚠️ Échec publication ObjectiveCreated: {e}")
        
        return objective

    def update_objective(
        self, user_id: str, objective_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Met à jour un objectif."""
        return self.mock_service.update_objective(user_id, objective_id, updates)

    def delete_objective(self, user_id: str, objective_id: str) -> bool:
        """Supprime un objectif."""
        return self.mock_service.delete_objective(user_id, objective_id)

    def get_journal_entries(self, user_id: str, limit: int = 50) -> List[JournalEntry]:
        """Récupère les entrées de journal d'un utilisateur."""
        return self.mock_service.get_journal_entries(user_id, limit)

    def create_journal_entry(
        self, user_id: str, mood: int, confidence: int, notes: str = None
    ) -> JournalEntry:
        """Crée une nouvelle entrée de journal."""
        # 1. Créer via Mock
        entry = self.mock_service.create_journal_entry(user_id, mood, confidence, notes)
        
        # 2. Publier événement MoodLogged
        try:
            self.event_helper.publish_mood_logged(
                user_id=user_id,
                mood=mood,
                confidence=confidence,
                notes=notes,
                journal_entry_id=entry.id
            )
            logger.info(f"✅ Événement MoodLogged publié pour entrée {entry.id}")
        except Exception as e:
            logger.warning(f"⚠️ Échec publication MoodLogged: {e}")
        
        return entry

    def get_journal_stats(self, user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques du journal d'un utilisateur."""
        return self.mock_service.get_journal_stats(user_id)

    def start_coaching_session(
        self, 
        user_id: str, 
        session_type: str = "free",
        user_tier: str = "free"
    ) -> str:
        """Démarre une session de coaching et publie l'événement."""
        session_id = str(uuid.uuid4())
        
        # Publier événement CoachingSessionStarted
        try:
            self.event_helper.publish_coaching_session_started(
                user_id=user_id,
                session_id=session_id,
                session_type=session_type,
                user_tier=user_tier
            )
            logger.info(f"✅ Session coaching {session_id} démarrée pour user {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Échec publication CoachingSessionStarted: {e}")
        
        return session_id

    def get_event_status(self) -> Dict[str, Any]:
        """Retourne le statut du système d'événements."""
        return {
            "event_bridge_available": self.event_helper.is_available,
            "mock_service_active": True,
            "hybrid_mode": True,
            "timestamp": datetime.utcnow().isoformat()
        }