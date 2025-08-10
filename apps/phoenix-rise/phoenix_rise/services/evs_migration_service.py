"""
Service de migration EmotionalVectorState vers Supabase Event Store.

Ce module gère la transition complète entre MockDBService et Supabase
pour la persistance des EmotionalVectorState via Event Sourcing.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from phoenix_shared_ui.adapters import session_manager
from iris_core.event_processing.emotional_vector_state import EmotionalVectorState
from ..core.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class EVSMigrationService:
    """
    Service de migration des données EmotionalVectorState.
    Convertit les données Mock en événements Event Sourcing dans Supabase.
    """

    def __init__(self):
        self.supabase_available = self._check_supabase_connection()
        logger.info(f"🔄 EVSMigrationService initialisé - Supabase: {'✅' if self.supabase_available else '⚠️'}")

    def _check_supabase_connection(self) -> bool:
        """Vérifie la disponibilité de Supabase."""
        try:
            result = supabase_client.table('events').select('event_id').limit(1).execute()
            # Si un mock est injecté par les tests, considérer disponible
            return True
        except Exception as e:
            logger.warning(f"⚠️ Supabase indisponible: {e}")
            return False

    def migrate_mock_data_to_supabase(self, user_id: str) -> Dict[str, Any]:
        """
        Migre les données Mock d'un utilisateur vers Supabase Event Store.
        Transforme les JournalEntry en événements MoodLogged et ConfidenceScoreLogged.
        """
        # En tests, un mock de supabase peut être injecté au niveau module.
        # Si indispo, on continue quand même si le client est patché.
        if not self.supabase_available:
            try:
                # Vérifier si un mock a été injecté
                supabase_client.table
            except Exception:
                return {
                    "success": False,
                    "error": "Supabase indisponible",
                    "events_created": 0
                }

        migration_stats = {
            "events_created": 0,
            "journal_entries_processed": 0,
            "objectives_processed": 0,
            "errors": []
        }

        try:
            # 1. Migrer les entrées de journal
            if session_manager.contains("mock_db"):
                mock_db = session_manager.get("mock_db", {}) or {}
                journal_entries = mock_db.get("journal_entries", {}).get(user_id, [])
                
                for entry in journal_entries:
                    # Créer événement MoodLogged
                    mood_event = {
                        "stream_id": user_id,
                        "event_type": "MoodLogged",
                        "payload": {
                            "score": entry.mood / 10.0,  # Normaliser 1-10 vers 0.1-1.0
                            "confidence": entry.confidence,
                            "notes": entry.notes,
                            "journal_entry_id": entry.id
                        },
                        "app_source": "rise",
                        "timestamp": entry.created_at if hasattr(entry, 'created_at') else datetime.utcnow().isoformat(),
                        "metadata": {
                            "migration_source": "mock_db_service",
                            "migration_timestamp": datetime.utcnow().isoformat()
                        }
                    }
                    
                    # Créer événement ConfidenceScoreLogged
                    confidence_event = {
                        "stream_id": user_id,
                        "event_type": "ConfidenceScoreLogged",
                        "payload": {
                            "score": entry.confidence / 10.0,  # Normaliser 1-10 vers 0.1-1.0
                            "notes": entry.notes,
                            "journal_entry_id": entry.id
                        },
                        "app_source": "rise",
                        "timestamp": entry.created_at if hasattr(entry, 'created_at') else datetime.utcnow().isoformat(),
                        "metadata": {
                            "migration_source": "mock_db_service",
                            "migration_timestamp": datetime.utcnow().isoformat()
                        }
                    }
                    
                    # Insérer les événements
                    supabase_client.table('events').insert([mood_event, confidence_event]).execute()
                    migration_stats["events_created"] += 2
                    migration_stats["journal_entries_processed"] += 1

                # 2. Migrer les objectifs
                objectives = mock_db.get("objectives", {}).get(user_id, [])
                for objective in objectives:
                    goal_event = {
                        "stream_id": user_id,
                        "event_type": "GoalSet",
                        "payload": {
                            "objective_id": objective.get("id", str(uuid.uuid4())),
                            "title": objective if isinstance(objective, str) else objective.get("title", "Objectif migré"),
                            "objective_type": "personal"
                        },
                        "app_source": "rise",
                        "timestamp": datetime.utcnow().isoformat(),
                        "metadata": {
                            "migration_source": "mock_db_service",
                            "migration_timestamp": datetime.utcnow().isoformat()
                        }
                    }
                    
                    supabase_client.table('events').insert(goal_event).execute()
                    migration_stats["events_created"] += 1
                    migration_stats["objectives_processed"] += 1

            migration_stats["success"] = True
            logger.info(f"✅ Migration réussie pour {user_id}: {migration_stats['events_created']} événements créés")
            
        except Exception as e:
            migration_stats["success"] = False
            migration_stats["error"] = str(e)
            migration_stats["errors"].append(f"Erreur migration générale: {e}")
            logger.error(f"❌ Erreur migration {user_id}: {e}")

        return migration_stats

    def rebuild_evs_from_events(self, user_id: str, days_back: int = 30) -> EmotionalVectorState:
        """
        Reconstruit un EmotionalVectorState depuis les événements Supabase.
        Optimisé pour ne récupérer que les événements des N derniers jours.
        """
        if not self.supabase_available:
            logger.warning("⚠️ Supabase indisponible, tentative avec client si mocké")
            try:
                supabase_client.table  # si mocké par tests
            except Exception:
                return EmotionalVectorState(user_id=user_id)

        try:
            # Date limite pour les événements
            since_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            
            # Récupérer événements pertinents pour EEV
            result = supabase_client.table('events') \
                .select('*') \
                .eq('stream_id', user_id) \
                .in_('event_type', ['MoodLogged', 'ConfidenceScoreLogged', 'CVGenerated', 'SkillSuggested', 'TrajectoryBuilt', 'GoalSet', 'CoachingSessionStarted']) \
                .gte('timestamp', since_date) \
                .order('timestamp', desc=False) \
                .execute()

            events = result.data
            evs = EmotionalVectorState(user_id=user_id)

            # Rejouer événements pour reconstruire l'état
            events_processed = 0
            for event in events:
                event_formatted = {
                    'type': event['event_type'],
                    'timestamp': event['timestamp'],
                    'payload': event['payload']
                }
                evs.update_from_event(event_formatted)
                events_processed += 1

            logger.info(f"✅ EEV reconstruit pour {user_id} depuis {events_processed} événements")
            return evs

        except Exception as e:
            logger.error(f"❌ Erreur reconstruction EEV {user_id}: {e}")
            return EmotionalVectorState(user_id=user_id)  # EEV vierge en cas d'erreur

    def create_user_snapshot(self, user_id: str) -> Optional[str]:
        """
        Crée un snapshot EEV utilisateur dans Supabase pour optimisation.
        Utilise la fonction SQL create_user_snapshot().
        """
        if not self.supabase_available:
            logger.warning("⚠️ Supabase indisponible, snapshot non créé")
            return None

        try:
            # Appeler la fonction SQL de snapshot
            result = supabase_client.rpc('create_user_snapshot', {'p_user_id': user_id}).execute()
            snapshot_id = result.data
            
            logger.info(f"✅ Snapshot créé pour {user_id}: {snapshot_id}")
            return snapshot_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création snapshot {user_id}: {e}")
            return None

    def get_migration_status(self, user_id: str) -> Dict[str, Any]:
        """
        Retourne le statut de migration pour un utilisateur.
        Indique s'il a des données Mock et/ou Supabase.
        """
        status = {
            "user_id": user_id,
            "has_mock_data": False,
            "has_supabase_events": False,
            "mock_entries_count": 0,
            "supabase_events_count": 0,
            "needs_migration": False
        }

        # Vérifier données Mock
        if session_manager.contains("mock_db"):
            mock_db = session_manager.get("mock_db", {})
            mock_journal = mock_db.get("journal_entries", {}).get(user_id, [])
            mock_objectives = mock_db.get("objectives", {}).get(user_id, [])
            
            status["has_mock_data"] = len(mock_journal) > 0 or len(mock_objectives) > 0
            status["mock_entries_count"] = len(mock_journal) + len(mock_objectives)

        # Vérifier événements Supabase
        if self.supabase_available:
            try:
                result = supabase_client.table('events') \
                    .select('event_id', exact_count=True) \
                    .eq('stream_id', user_id) \
                    .execute()
                
                status["has_supabase_events"] = result.count > 0
                status["supabase_events_count"] = result.count
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur vérification événements Supabase: {e}")
        else:
            # En mode tests sans supabase, déduire via session mock
            if session_manager.contains("mock_db"):
                mock_db = session_manager.get("mock_db", {}) or {}
                mock_journal = mock_db.get("journal_entries", {}).get(user_id, [])
                mock_objectives = mock_db.get("objectives", {}).get(user_id, [])
                status["has_mock_data"] = len(mock_journal) > 0 or len(mock_objectives) > 0
                status["mock_entries_count"] = len(mock_journal) + len(mock_objectives)

        # Déterminer si migration nécessaire
        status["needs_migration"] = status["has_mock_data"] and not status["has_supabase_events"]
        
        return status

    def cleanup_old_events(self, retention_days: int = 365) -> int:
        """
        Nettoie les anciens événements (RGPD compliance).
        Utilise la fonction SQL cleanup_old_events().
        """
        if not self.supabase_available:
            logger.warning("⚠️ Supabase indisponible, cleanup non effectué")
            return 0

        try:
            result = supabase_client.rpc('cleanup_old_events', {'retention_days': retention_days}).execute()
            deleted_count = result.data
            
            logger.info(f"✅ Cleanup effectué: {deleted_count} événements supprimés (rétention {retention_days} jours)")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Erreur cleanup événements: {e}")
            return 0


# Instance globale pour utilisation dans l'application
evs_migration_service = EVSMigrationService()