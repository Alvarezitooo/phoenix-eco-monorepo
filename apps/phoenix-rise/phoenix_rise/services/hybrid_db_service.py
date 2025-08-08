"""
Service de base de données hybride pour Phoenix Rise.

Combine MockDBService (pour le stockage local) avec Phoenix Event Helper (pour la data pipeline).
Assure la compatibilité et la transition progressive vers l'Event Sourcing.
"""

import uuid
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from models.journal_entry import JournalEntry
from .mock_db_service import MockDBService
from .phoenix_rise_event_helper import phoenix_rise_event_helper
from core.supabase_client import supabase_client
from iris_core.event_processing.emotional_vector_state import EmotionalVectorState
from phoenix_shared_db.services.supabase_batch_service import get_batch_service

# ✅ CORRECTION ARCHITECTURE: Import adaptateur session découplé
try:
    from phoenix_shared_ui.adapters import session_manager
except ImportError:
    # Fallback pour développement local
    class DummySessionManager:
        def __init__(self): self._data = {}
        def get(self, key, default=None): return self._data.get(key, default)
        def set(self, key, value): self._data[key] = value
        def contains(self, key): return key in self._data
    session_manager = DummySessionManager()

logger = logging.getLogger(__name__)


class HybridDBService:
    """
    Service de base de données hybride.
    Utilise MockDBService pour le stockage local ET publie les événements vers la data pipeline.
    Supporte la persistance EmotionalVectorState via Event Sourcing.
    """

    def __init__(self):
        self.mock_service = MockDBService()
        self.event_helper = phoenix_rise_event_helper
        self._supabase_available = self._check_supabase_connection()
        self._batch_service = get_batch_service()
        logger.info(f"✅ HybridDBService initialisé (Mock + Event Sourcing + Batch) - Supabase: {'✅' if self._supabase_available else '⚠️'}")
    
    def _check_supabase_connection(self) -> bool:
        """Vérifie si Supabase est disponible."""
        try:
            # Test simple de connexion
            result = supabase_client.table('events').select('event_id').limit(1).execute()
            return True
        except Exception as e:
            logger.warning(f"⚠️ Supabase indisponible: {e}")
            return False

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
        
        # 2. Publier événement (Event Bridge)
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
        
        # 3. Stocker événement pour EEV
        self.store_event_to_supabase(
            user_id=user_id,
            event_type="GoalSet",
            payload={
                "objective_id": objective["id"],
                "title": title,
                "objective_type": objective_type,
                "target_date": target_date
            }
        )
        
        # 4. Mettre à jour l'EEV
        evs = self.get_emotional_vector_state(user_id)
        evs.update_action(datetime.utcnow(), "GoalSet")
        self.save_emotional_vector_state(evs)
        
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
        
        # 2. Publier événement MoodLogged (Event Bridge)
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
        
        # 3. Stocker événement dans Supabase pour EEV
        self.store_event_to_supabase(
            user_id=user_id,
            event_type="MoodLogged",
            payload={
                "score": mood / 10.0,  # Normaliser 1-10 vers 0.1-1.0
                "confidence": confidence,
                "notes": notes,
                "journal_entry_id": entry.id
            }
        )
        
        # 4. Mettre à jour l'EEV en temps réel
        evs = self.get_emotional_vector_state(user_id)
        evs.update_mood(datetime.utcnow(), mood / 10.0)
        evs.update_confidence(datetime.utcnow(), confidence / 10.0)
        self.save_emotional_vector_state(evs)
        
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
        
        # Stocker événement pour EEV
        self.store_event_to_supabase(
            user_id=user_id,
            event_type="CoachingSessionStarted",
            payload={
                "session_id": session_id,
                "session_type": session_type,
                "user_tier": user_tier
            }
        )
        
        return session_id

    def get_event_status(self) -> Dict[str, Any]:
        """Retourne le statut du système d'événements."""
        return {
            "event_bridge_available": self.event_helper.is_available,
            "supabase_available": self._supabase_available,
            "mock_service_active": True,
            "hybrid_mode": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ===== EMOTIONAL VECTOR STATE - EVENT SOURCING =====
    
    def get_emotional_vector_state(self, user_id: str) -> EmotionalVectorState:
        """Récupère l'EmotionalVectorState d'un utilisateur via Event Sourcing."""
        if self._supabase_available:
            return self._rebuild_evs_from_events(user_id)
        else:
            # Fallback vers session state pour développement
            return self._get_evs_from_session(user_id)
    
    def _rebuild_evs_from_events(self, user_id: str) -> EmotionalVectorState:
        """Reconstruit l'EEV depuis les événements stockés dans Supabase."""
        try:
            # Récupérer tous les événements pertinents pour ce user
            result = supabase_client.table('events') \
                .select('*') \
                .eq('stream_id', user_id) \
                .in_('event_type', ['MoodLogged', 'ConfidenceScoreLogged', 'CVGenerated', 'SkillSuggested', 'TrajectoryBuilt', 'GoalSet']) \
                .order('timestamp', desc=False) \
                .execute()
            
            events = result.data
            evs = EmotionalVectorState(user_id=user_id)
            
            # Rejouer tous les événements pour reconstruire l'état
            for event in events:
                event_formatted = {
                    'type': event['event_type'],
                    'timestamp': event['timestamp'],
                    'payload': event['payload']
                }
                evs.update_from_event(event_formatted)
            
            logger.info(f"✅ EEV reconstruit pour {user_id} depuis {len(events)} événements")
            return evs
            
        except Exception as e:
            logger.error(f"❌ Erreur reconstruction EEV pour {user_id}: {e}")
            return EmotionalVectorState(user_id=user_id)  # EEV vierge
    
    def _get_evs_from_session(self, user_id: str) -> EmotionalVectorState:
        """✅ DÉCOUPLÉ: Récupère l'EEV depuis session adaptée."""
        if not session_manager.contains("emotional_vector_states"):
            session_manager.set("emotional_vector_states", {})
        
        evs_data = session_manager.get("emotional_vector_states", {})
        if user_id not in evs_data:
            evs_data[user_id] = EmotionalVectorState(user_id=user_id)
            session_manager.set("emotional_vector_states", evs_data)
        
        return evs_data[user_id]
    
    def save_emotional_vector_state(self, evs: EmotionalVectorState) -> bool:
        """✅ DÉCOUPLÉ: Sauvegarde l'EEV via session adaptée."""
        if not session_manager.contains("emotional_vector_states"):
            session_manager.set("emotional_vector_states", {})
        
        evs_data = session_manager.get("emotional_vector_states", {})
        evs_data[evs.user_id] = evs
        session_manager.set("emotional_vector_states", evs_data)
        
        logger.info(f"✅ EEV sauvegardé pour {evs.user_id}")
        return True
    
    def store_event_to_supabase(self, user_id: str, event_type: str, payload: Dict[str, Any], app_source: str = "rise") -> bool:
        """Stocke un événement directement dans Supabase Event Store."""
        if not self._supabase_available:
            logger.warning(f"⚠️ Supabase indisponible, événement {event_type} non persisté")
            return False
        
        try:
            event_data = {
                "stream_id": user_id,
                "event_type": event_type,
                "payload": payload,
                "app_source": app_source,
                "metadata": {
                    "source": "phoenix_rise_hybrid_service",
                    "version": "1.0.0"
                }
            }
            
            result = supabase_client.table('events').insert(event_data).execute()
            logger.info(f"✅ Événement {event_type} stocké dans Supabase pour {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage événement {event_type}: {e}")
            return False