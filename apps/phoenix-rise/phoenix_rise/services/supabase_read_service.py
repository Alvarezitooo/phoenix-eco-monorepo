"""
Supabase Read Service pour Phoenix Rise
Service de lecture des données depuis les vues matérialisées Supabase
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Any
from supabase import create_client, Client
from models.journal_entry import JournalEntry

logger = logging.getLogger(__name__)


class SupabaseReadService:
    """
    Service de lecture des données Phoenix Rise depuis Supabase.
    Utilise les vues matérialisées pour des performances optimales.
    """
    
    def __init__(self):
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not supabase_url or not supabase_key:
                raise ValueError("Variables SUPABASE_URL et SUPABASE_ANON_KEY requises")
            
            self.client: Client = create_client(supabase_url, supabase_key)
            self.is_available = True
            logger.info("✅ SupabaseReadService initialisé avec succès")
            
        except Exception as e:
            logger.warning(f"⚠️ Supabase non disponible: {e}")
            self.client = None
            self.is_available = False

    def get_journal_entries(self, user_id: str, limit: int = 50) -> List[JournalEntry]:
        """
        Récupère les entrées de journal d'un utilisateur depuis Supabase.
        
        Args:
            user_id: ID utilisateur
            limit: Nombre maximum d'entrées à récupérer
            
        Returns:
            Liste des entrées de journal
        """
        if not self.is_available:
            logger.debug("Supabase non disponible - retour liste vide")
            return []
            
        try:
            response = self.client.table("journal_entries_view") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            if response.data:
                entries = []
                for row in response.data:
                    entry = JournalEntry(
                        id=row["journal_entry_id"],
                        user_id=row["user_id"],
                        created_at=datetime.fromisoformat(row["created_at"].replace('Z', '+00:00')),
                        mood=row["mood"],
                        confidence=row["confidence"],
                        notes=row["notes"]
                    )
                    entries.append(entry)
                
                logger.info(f"✅ {len(entries)} entrées journal récupérées pour user {user_id}")
                return entries
            else:
                logger.info(f"Aucune entrée journal trouvée pour user {user_id}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération entrées journal: {e}")
            return []

    def get_journal_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère les statistiques du journal d'un utilisateur.
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            Dictionnaire avec les statistiques
        """
        if not self.is_available:
            return {"total_entries": 0, "avg_mood": 0, "avg_confidence": 0}
            
        try:
            response = self.client.table("user_journal_stats") \
                .select("*") \
                .eq("user_id", user_id) \
                .execute()
            
            if response.data and len(response.data) > 0:
                stats = response.data[0]
                
                result = {
                    "total_entries": stats.get("total_entries", 0),
                    "avg_mood": round(float(stats.get("avg_mood", 0)), 1),
                    "avg_confidence": round(float(stats.get("avg_confidence", 0)), 1),
                    "last_entry_date": stats.get("last_entry_date"),
                    "first_entry_date": stats.get("first_entry_date"),
                    "mood_7d_avg": round(float(stats.get("mood_7d_avg", 0)), 1) if stats.get("mood_7d_avg") else 0,
                    "confidence_7d_avg": round(float(stats.get("confidence_7d_avg", 0)), 1) if stats.get("confidence_7d_avg") else 0,
                    "mood_30d_avg": round(float(stats.get("mood_30d_avg", 0)), 1) if stats.get("mood_30d_avg") else 0,
                    "confidence_30d_avg": round(float(stats.get("confidence_30d_avg", 0)), 1) if stats.get("confidence_30d_avg") else 0
                }
                
                logger.info(f"✅ Statistiques journal récupérées pour user {user_id}")
                return result
            else:
                logger.info(f"Aucune statistique trouvée pour user {user_id}")
                return {"total_entries": 0, "avg_mood": 0, "avg_confidence": 0}
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération statistiques: {e}")
            return {"total_entries": 0, "avg_mood": 0, "avg_confidence": 0}

    def get_objectives(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Récupère les objectifs d'un utilisateur.
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            Liste des objectifs
        """
        if not self.is_available:
            return []
            
        try:
            response = self.client.table("user_objectives_view") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .execute()
            
            if response.data:
                objectives = []
                for row in response.data:
                    objective = {
                        "id": row["objective_id"],
                        "title": row["title"],
                        "description": row["description"],
                        "type": row["objective_type"],
                        "status": row["status"],
                        "created_at": row["created_at"],
                        "target_date": row["target_date"],
                        "completed_at": row["completed_at"]
                    }
                    objectives.append(objective)
                
                logger.info(f"✅ {len(objectives)} objectifs récupérés pour user {user_id}")
                return objectives
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération objectifs: {e}")
            return []

    def get_coaching_sessions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Récupère les sessions de coaching d'un utilisateur.
        
        Args:
            user_id: ID utilisateur
            limit: Nombre maximum de sessions
            
        Returns:
            Liste des sessions de coaching
        """
        if not self.is_available:
            return []
            
        try:
            response = self.client.table("coaching_sessions_view") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("started_at", desc=True) \
                .limit(limit) \
                .execute()
            
            if response.data:
                sessions = []
                for row in response.data:
                    session = {
                        "session_id": row["session_id"],
                        "session_type": row["session_type"],
                        "user_tier": row["user_tier"],
                        "started_at": row["started_at"],
                        "ended_at": row["ended_at"],
                        "duration_minutes": row["duration_minutes"],
                        "ai_prompts_used": row["ai_prompts_used"],
                        "user_satisfaction": row["user_satisfaction"]
                    }
                    sessions.append(session)
                
                logger.info(f"✅ {len(sessions)} sessions coaching récupérées pour user {user_id}")
                return sessions
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération sessions coaching: {e}")
            return []

    def get_dashboard_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère toutes les métriques pour le dashboard utilisateur.
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            Dictionnaire complet des métriques
        """
        if not self.is_available:
            return self._get_default_metrics()
            
        try:
            response = self.client.table("user_dashboard_metrics") \
                .select("*") \
                .eq("user_id", user_id) \
                .execute()
            
            if response.data and len(response.data) > 0:
                metrics = response.data[0]
                
                result = {
                    "user_id": metrics["user_id"],
                    "email": metrics["email"],
                    "full_name": metrics["full_name"],
                    
                    # Stats journal
                    "journal_entries_count": metrics.get("journal_entries_count", 0),
                    "avg_mood": round(float(metrics.get("avg_mood", 0)), 1),
                    "avg_confidence": round(float(metrics.get("avg_confidence", 0)), 1),
                    "last_entry_date": metrics.get("last_entry_date"),
                    
                    # Stats objectifs
                    "total_objectives": metrics.get("total_objectives", 0),
                    "active_objectives": metrics.get("active_objectives", 0),
                    "completed_objectives": metrics.get("completed_objectives", 0),
                    
                    # Stats coaching
                    "total_coaching_sessions": metrics.get("total_coaching_sessions", 0),
                    "recent_coaching_sessions": metrics.get("recent_coaching_sessions", 0),
                    "last_session_date": metrics.get("last_session_date")
                }
                
                logger.info(f"✅ Métriques dashboard récupérées pour user {user_id}")
                return result
            else:
                logger.info(f"Aucune métrique trouvée pour user {user_id}")
                return self._get_default_metrics()
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération métriques dashboard: {e}")
            return self._get_default_metrics()

    def _get_default_metrics(self) -> Dict[str, Any]:
        """Retourne des métriques par défaut."""
        return {
            "journal_entries_count": 0,
            "avg_mood": 0,
            "avg_confidence": 0,
            "total_objectives": 0,
            "active_objectives": 0,
            "completed_objectives": 0,
            "total_coaching_sessions": 0,
            "recent_coaching_sessions": 0
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie la santé de la connexion Supabase.
        
        Returns:
            Status de santé du service
        """
        return {
            "service": "SupabaseReadService",
            "available": self.is_available,
            "timestamp": datetime.utcnow().isoformat(),
            "client_initialized": self.client is not None
        }