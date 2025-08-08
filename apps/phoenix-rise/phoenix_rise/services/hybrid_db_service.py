"""
Service de base de données hybride pour Phoenix Rise.

Combine MockDBService (pour le stockage local) avec Phoenix Event Helper (pour la data pipeline).
Assure la compatibilité et la transition progressive vers l'Event Sourcing.
"""

import uuid
import logging
import time
from typing import Any, Dict, List
from datetime import datetime

from ..models.journal_entry import JournalEntry
from .mock_db_service import MockDBService
from .phoenix_rise_event_helper import phoenix_rise_event_helper
from ..core.supabase_client import supabase_client
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
    🚀 Service de base de données hybride optimisé avec batching intelligent.
    Utilise MockDBService pour le stockage local ET publie les événements vers la data pipeline.
    Supporte la persistance EmotionalVectorState via Event Sourcing avec retry/backoff.
    """

    def __init__(self):
        self.mock_service = MockDBService()
        self.event_helper = phoenix_rise_event_helper
        self._supabase_available = self._check_supabase_connection()
        self._batch_service = get_batch_service()
        
        # ✅ Configuration batching optimisé
        self._pending_events = []
        self._batch_size = 10
        self._batch_timeout = 2.0  # 2 secondes
        self._last_batch_time = time.time()
        self._retry_config = {
            'max_attempts': 3,
            'base_delay': 1.0,
            'max_delay': 10.0,
            'exponential_base': 2
        }
        
        logger.info(f"✅ HybridDBService initialisé (Mock + Event Sourcing + Batching Optimisé) - Supabase: {'✅' if self._supabase_available else '⚠️'}")
    
    def __del__(self):
        """🔄 Destructeur - assure le traitement des événements en attente."""
        if hasattr(self, '_pending_events') and self._pending_events:
            logger.info(f"🔄 Traitement final de {len(self._pending_events)} événements en attente...")
            try:
                self.force_flush_pending_events()
            except Exception as e:
                logger.error(f"❌ Erreur lors du flush final: {e}")
    
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
        """🚀 Stocke un événement via batch service optimisé avec retry/backoff."""
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
                    "version": "1.1.0",
                    "batch_enabled": True
                }
            }
            
            # ✅ Ajouter à la file de batch au lieu d'écrire immédiatement
            self._add_to_batch(event_data)
            
            # ✅ Traitement batch si conditions remplies
            if self._should_flush_batch():
                return self._flush_batch()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur préparation batch événement {event_type}: {e}")
            return False
    
    def _add_to_batch(self, event_data: Dict[str, Any]) -> None:
        """Ajoute un événement à la file de batch."""
        self._pending_events.append(event_data)
        logger.debug(f"📦 Événement ajouté au batch ({len(self._pending_events)}/{self._batch_size})")
    
    def _should_flush_batch(self) -> bool:
        """Détermine si le batch doit être traité maintenant."""
        # Batch par taille
        if len(self._pending_events) >= self._batch_size:
            return True
        
        # Batch par timeout
        if (time.time() - self._last_batch_time) >= self._batch_timeout and self._pending_events:
            return True
        
        return False
    
    def _flush_batch(self) -> bool:
        """🚀 Traite le batch d'événements avec retry/backoff exponential."""
        if not self._pending_events:
            return True
        
        batch_to_process = self._pending_events.copy()
        self._pending_events.clear()
        self._last_batch_time = time.time()
        
        return self._execute_batch_with_retry(batch_to_process)
    
    def _execute_batch_with_retry(self, events: List[Dict[str, Any]]) -> bool:
        """Exécute le batch avec retry/backoff intelligent."""
        last_error = None
        
        for attempt in range(1, self._retry_config['max_attempts'] + 1):
            try:
                # ✅ Utiliser le batch service pour insertion optimisée
                if hasattr(self._batch_service, 'batch_insert'):
                    success = self._batch_service.batch_insert('events', events)
                else:
                    # Fallback vers insertion multiple classique
                    result = supabase_client.table('events').insert(events).execute()
                    success = len(result.data) == len(events)
                
                if success:
                    logger.info(f"✅ Batch de {len(events)} événements traité avec succès (tentative {attempt})")
                    return True
                else:
                    raise Exception("Batch insertion failed - partial success")
                    
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ Échec batch tentative {attempt}/{self._retry_config['max_attempts']}: {e}")
                
                if attempt < self._retry_config['max_attempts']:
                    delay = min(
                        self._retry_config['base_delay'] * (self._retry_config['exponential_base'] ** (attempt - 1)),
                        self._retry_config['max_delay']
                    )
                    logger.info(f"⏳ Retry dans {delay}s...")
                    time.sleep(delay)
        
        # ✅ Échec définitif - remettre en file pour retry ultérieur
        logger.error(f"❌ Échec définitif batch {len(events)} événements après {self._retry_config['max_attempts']} tentatives: {last_error}")
        self._pending_events.extend(events)  # Remettre en file
        return False
    
    def force_flush_pending_events(self) -> bool:
        """🔄 Force le traitement immédiat de tous les événements en attente."""
        if not self._pending_events:
            logger.info("📦 Aucun événement en attente à traiter")
            return True
        
        logger.info(f"🔄 Forçage traitement {len(self._pending_events)} événements en attente...")
        return self._flush_batch()
    
    def get_batch_stats(self) -> Dict[str, Any]:
        """📊 Retourne les statistiques du système de batching."""
        return {
            "pending_events": len(self._pending_events),
            "batch_size": self._batch_size,
            "batch_timeout_seconds": self._batch_timeout,
            "last_batch_time": datetime.fromtimestamp(self._last_batch_time).isoformat(),
            "time_since_last_batch": time.time() - self._last_batch_time,
            "retry_config": self._retry_config,
            "supabase_available": self._supabase_available
        }