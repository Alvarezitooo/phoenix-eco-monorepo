"""
Patch temporaire pour ajouter les méthodes batch à HybridDBService.
Ce fichier sera mergé avec hybrid_db_service.py.

Author: Claude Phoenix DevSecOps Guardian  
"""

def add_batch_methods_to_hybrid_db_service():
    """Méthodes batch à ajouter à HybridDBService."""
    
    def _store_event_batch(self, user_id: str, event_type: str, payload: Dict[str, Any], app_source: str = "rise") -> bool:
        """✅ Stocke un événement via le service batch optimisé."""
        if not self._supabase_available or not self._batch_service:
            logger.warning(f"⚠️ Batch service indisponible, fallback vers store_event_to_supabase")
            return self.store_event_to_supabase(user_id, event_type, payload, app_source)
        
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
            
            # ✅ Queue dans le batch service
            self._batch_service.queue_insert(
                table="events",
                data=event_data,
                callback=lambda: logger.debug(f"✅ Event {event_type} batched for {user_id}")
            )
            
            logger.debug(f"✅ Event {event_type} queued for batch processing (user: {user_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur batch queue événement {event_type}: {e}")
            # Fallback vers méthode synchrone
            return self.store_event_to_supabase(user_id, event_type, payload, app_source)
    
    def flush_batch_events(self) -> Dict[str, Any]:
        """✅ Force le flush des événements en batch."""
        if not self._batch_service:
            return {"success": False, "error": "Batch service non disponible"}
        
        try:
            result = self._batch_service.flush_now()
            logger.info(f"✅ Batch flush completed: {result.operation_count} operations")
            return {
                "success": result.success,
                "operation_count": result.operation_count,
                "execution_time": result.execution_time,
                "error": result.error
            }
        except Exception as e:
            logger.error(f"❌ Erreur flush batch: {e}")
            return {"success": False, "error": str(e)}
    
    def get_batch_stats(self) -> Dict[str, Any]:
        """✅ Retourne les statistiques du batch service."""
        if not self._batch_service:
            return {"error": "Batch service non disponible"}
        
        return self._batch_service.get_stats()

    # Remplacement des appels store_event_to_supabase par _store_event_batch
    REPLACEMENTS = [
        # Dans create_objective
        {
            "old": '''        # 3. Stocker événement pour EEV
        self.store_event_to_supabase(
            user_id=user_id,
            event_type="GoalSet",
            payload={
                "objective_id": objective["id"],
                "title": title,
                "objective_type": objective_type,
                "target_date": target_date
            }
        )''',
            "new": '''        # 3. ✅ Stocker événement via batch service
        self._store_event_batch(
            user_id=user_id,
            event_type="GoalSet",
            payload={
                "objective_id": objective["id"],
                "title": title,
                "objective_type": objective_type,
                "target_date": target_date
            }
        )'''
        },
        # Dans create_journal_entry
        {
            "old": '''        # 3. Stocker événement dans Supabase pour EEV
        self.store_event_to_supabase(
            user_id=user_id,
            event_type="MoodLogged",
            payload={
                "score": mood / 10.0,  # Normaliser 1-10 vers 0.1-1.0
                "confidence": confidence,
                "notes": notes,
                "journal_entry_id": entry.id
            }
        )''',
            "new": '''        # 3. ✅ Stocker événement via batch service
        self._store_event_batch(
            user_id=user_id,
            event_type="MoodLogged",
            payload={
                "score": mood / 10.0,  # Normaliser 1-10 vers 0.1-1.0
                "confidence": confidence,
                "notes": notes,
                "journal_entry_id": entry.id
            }
        )'''
        },
        # Dans start_coaching_session
        {
            "old": '''        # Stocker événement pour EEV
        self.store_event_to_supabase(
            user_id=user_id,
            event_type="CoachingSessionStarted",
            payload={
                "session_id": session_id,
                "session_type": session_type,
                "user_tier": user_tier
            }
        )''',
            "new": '''        # ✅ Stocker événement via batch service
        self._store_event_batch(
            user_id=user_id,
            event_type="CoachingSessionStarted",
            payload={
                "session_id": session_id,
                "session_type": session_type,
                "user_tier": user_tier
            }
        )'''
        }
    ]

if __name__ == "__main__":
    print("Patch methods ready for integration into HybridDBService")