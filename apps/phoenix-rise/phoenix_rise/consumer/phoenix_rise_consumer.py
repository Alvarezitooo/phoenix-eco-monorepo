"""
Phoenix Rise Event Consumer
Consumer pour écouter les événements Phoenix Rise et mettre à jour les vues matérialisées
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class PhoenixRiseConsumer:
    """
    Consumer Phoenix Rise pour traiter les événements et mettre à jour les vues matérialisées.
    """
    
    def __init__(self):
        # Configuration Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Clé service pour écriture
        
        if not supabase_url or not supabase_service_key:
            raise ValueError("SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY requis")
        
        self.client: Client = create_client(supabase_url, supabase_service_key)
        self.is_running = False
        
        logger.info("✅ Phoenix Rise Consumer initialisé")

    async def start_consuming(self):
        """Démarre l'écoute des événements (simulation pour MVP)."""
        self.is_running = True
        logger.info("🎧 Phoenix Rise Consumer démarré")
        
        # En mode MVP, on peut simuler la réception d'événements
        # Dans une version complète, ceci connecterait à RabbitMQ ou Kafka
        
        while self.is_running:
            try:
                # Simulation d'attente d'événements
                await asyncio.sleep(5)
                
                # Dans la vraie implémentation:
                # - Connexion à message broker
                # - Écoute des événements Phoenix Rise
                # - Traitement des événements reçus
                
            except Exception as e:
                logger.error(f"❌ Erreur dans le consumer: {e}")
                await asyncio.sleep(10)

    def stop_consuming(self):
        """Arrête l'écoute des événements."""
        self.is_running = False
        logger.info("🛑 Phoenix Rise Consumer arrêté")

    def process_mood_logged_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Traite un événement MoodLogged et met à jour journal_entries_view.
        
        Args:
            event_data: Données de l'événement
            
        Returns:
            True si traité avec succès
        """
        try:
            # Extraction des données
            user_id = event_data.get("user_id")
            journal_entry_id = event_data.get("journal_entry_id")
            mood = event_data.get("mood")
            confidence = event_data.get("confidence")
            notes = event_data.get("notes")
            timestamp = event_data.get("timestamp")
            
            if not all([user_id, journal_entry_id, mood, confidence]):
                logger.error("❌ Données d'événement MoodLogged incomplètes")
                return False
            
            # Insertion dans journal_entries_view
            entry_data = {
                "user_id": user_id,
                "journal_entry_id": journal_entry_id,
                "mood": mood,
                "confidence": confidence,
                "notes": notes,
                "created_at": timestamp,
                "date_logged": datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date().isoformat()
            }
            
            # Calcul des tendances (simplifié pour MVP)
            mood_trend = self._calculate_mood_trend(user_id, mood)
            confidence_trend = self._calculate_confidence_trend(user_id, confidence)
            
            entry_data.update({
                "mood_trend": mood_trend,
                "confidence_trend": confidence_trend
            })
            
            result = self.client.table("journal_entries_view").insert(entry_data).execute()
            
            if result.data:
                logger.info(f"✅ Événement MoodLogged traité pour user {user_id}")
                return True
            else:
                logger.error(f"❌ Échec insertion journal_entries_view pour user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement MoodLogged: {e}")
            return False

    def process_objective_created_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Traite un événement ObjectiveCreated et met à jour user_objectives_view.
        
        Args:
            event_data: Données de l'événement
            
        Returns:
            True si traité avec succès
        """
        try:
            # Extraction des données
            user_id = event_data.get("user_id")
            objective_id = event_data.get("objective_id")
            objective_title = event_data.get("objective_title")
            objective_type = event_data.get("objective_type")
            target_date = event_data.get("target_date")
            timestamp = event_data.get("timestamp")
            
            if not all([user_id, objective_id, objective_title]):
                logger.error("❌ Données d'événement ObjectiveCreated incomplètes")
                return False
            
            # Insertion dans user_objectives_view
            objective_data = {
                "user_id": user_id,
                "objective_id": objective_id,
                "title": objective_title,
                "objective_type": objective_type or "personal",
                "target_date": target_date,
                "created_at": timestamp,
                "status": "active"
            }
            
            result = self.client.table("user_objectives_view").insert(objective_data).execute()
            
            if result.data:
                logger.info(f"✅ Événement ObjectiveCreated traité pour user {user_id}")
                return True
            else:
                logger.error(f"❌ Échec insertion user_objectives_view pour user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement ObjectiveCreated: {e}")
            return False

    def process_coaching_session_started_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Traite un événement CoachingSessionStarted et met à jour coaching_sessions_view.
        
        Args:
            event_data: Données de l'événement
            
        Returns:
            True si traité avec succès
        """
        try:
            # Extraction des données
            user_id = event_data.get("user_id")
            session_id = event_data.get("session_id")
            session_type = event_data.get("session_type")
            user_tier = event_data.get("user_tier")
            timestamp = event_data.get("timestamp")
            
            if not all([user_id, session_id, session_type]):
                logger.error("❌ Données d'événement CoachingSessionStarted incomplètes")
                return False
            
            # Insertion dans coaching_sessions_view
            session_data = {
                "user_id": user_id,
                "session_id": session_id,
                "session_type": session_type,
                "user_tier": user_tier or "free",
                "started_at": timestamp,
                "ai_prompts_used": 1  # Session démarrée = au moins 1 prompt
            }
            
            result = self.client.table("coaching_sessions_view").insert(session_data).execute()
            
            if result.data:
                logger.info(f"✅ Événement CoachingSessionStarted traité pour user {user_id}")
                return True
            else:
                logger.error(f"❌ Échec insertion coaching_sessions_view pour user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement CoachingSessionStarted: {e}")
            return False

    def process_profile_created_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Traite un événement ProfileCreated et s'assure que le profil existe.
        
        Args:
            event_data: Données de l'événement
            
        Returns:
            True si traité avec succès
        """
        try:
            user_id = event_data.get("user_id")
            email = event_data.get("email")
            full_name = event_data.get("full_name")
            timestamp = event_data.get("timestamp")
            
            if not all([user_id, email]):
                logger.error("❌ Données d'événement ProfileCreated incomplètes")
                return False
            
            # Vérifier si le profil existe déjà
            existing = self.client.table("profiles").select("id").eq("id", user_id).execute()
            
            if not existing.data:
                # Créer le profil
                profile_data = {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "created_at": timestamp
                }
                
                result = self.client.table("profiles").insert(profile_data).execute()
                
                if result.data:
                    logger.info(f"✅ Profil créé pour user {user_id}")
                else:
                    logger.error(f"❌ Échec création profil pour user {user_id}")
                    return False
            else:
                logger.info(f"ℹ️ Profil {user_id} existe déjà")
            
            return True
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement ProfileCreated: {e}")
            return False

    def _calculate_mood_trend(self, user_id: str, current_mood: int) -> str:
        """Calcule la tendance d'humeur (simplifié)."""
        try:
            # Récupération de la dernière entrée
            last_entry = self.client.table("journal_entries_view") \
                .select("mood") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()
            
            if last_entry.data and len(last_entry.data) > 0:
                last_mood = last_entry.data[0]["mood"]
                
                if current_mood > last_mood:
                    return "up"
                elif current_mood < last_mood:
                    return "down"
                else:
                    return "stable"
            else:
                return "stable"  # Première entrée
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur calcul tendance humeur: {e}")
            return "stable"

    def _calculate_confidence_trend(self, user_id: str, current_confidence: int) -> str:
        """Calcule la tendance de confiance (simplifié)."""
        try:
            # Récupération de la dernière entrée
            last_entry = self.client.table("journal_entries_view") \
                .select("confidence") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()
            
            if last_entry.data and len(last_entry.data) > 0:
                last_confidence = last_entry.data[0]["confidence"]
                
                if current_confidence > last_confidence:
                    return "up"
                elif current_confidence < last_confidence:
                    return "down"
                else:
                    return "stable"
            else:
                return "stable"  # Première entrée
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur calcul tendance confiance: {e}")
            return "stable"

    def process_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Traite un événement selon son type.
        
        Args:
            event_type: Type d'événement
            event_data: Données de l'événement
            
        Returns:
            True si traité avec succès
        """
        try:
            if event_type == "MoodLogged":
                return self.process_mood_logged_event(event_data)
            elif event_type == "ObjectiveCreated":
                return self.process_objective_created_event(event_data)
            elif event_type == "CoachingSessionStarted":
                return self.process_coaching_session_started_event(event_data)
            elif event_type == "ProfileCreated":
                return self.process_profile_created_event(event_data)
            else:
                logger.warning(f"⚠️ Type d'événement non supporté: {event_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement événement {event_type}: {e}")
            return False


# Script standalone pour tester le consumer
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test des événements
    consumer = PhoenixRiseConsumer()
    
    # Test MoodLogged
    test_mood_event = {
        "user_id": "test_user_123",
        "journal_entry_id": "entry_456",
        "mood": 8,
        "confidence": 7,
        "notes": "Bonne journée aujourd'hui",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print("🧪 Test événement MoodLogged...")
    success = consumer.process_event("MoodLogged", test_mood_event)
    print(f"Résultat: {'✅ Success' if success else '❌ Échec'}")
    
    # Test ObjectiveCreated
    test_objective_event = {
        "user_id": "test_user_123",
        "objective_id": "obj_789",
        "objective_title": "Apprendre Python",
        "objective_type": "skill",
        "target_date": "2025-12-31",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print("🧪 Test événement ObjectiveCreated...")
    success = consumer.process_event("ObjectiveCreated", test_objective_event)
    print(f"Résultat: {'✅ Success' if success else '❌ Échec'}")
    
    print("✅ Tests du consumer terminés")