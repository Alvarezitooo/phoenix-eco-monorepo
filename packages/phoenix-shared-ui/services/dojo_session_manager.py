"""
Gestionnaire de session persistante pour Dojo Mental.
Maintient l'état entre les sessions et synchronise l'interface.

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Session Management Pattern
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class DojoSessionState:
    """État de session persistant pour Dojo Mental."""
    user_id: str
    current_dialogue: str = "Bienvenue dans le Dojo. Tu n'es pas ici pour tout résoudre, juste pour faire un pas. Lequel ?"
    kaizen_input: str = ""
    last_activity: float = field(default_factory=time.time)
    session_stats: Dict[str, Any] = field(default_factory=dict)
    zazen_state: Dict[str, Any] = field(default_factory=dict)
    ui_preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialise l'état en dictionnaire."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DojoSessionState':
        """Désérialise depuis un dictionnaire."""
        return cls(**data)
    
    def update_activity(self):
        """Met à jour le timestamp de dernière activité."""
        self.last_activity = time.time()
    
    def is_expired(self, ttl_hours: int = 24) -> bool:
        """Vérifie si la session est expirée."""
        return time.time() - self.last_activity > (ttl_hours * 3600)

class SessionStorageInterface(ABC):
    """Interface abstraite pour le stockage de session."""
    
    @abstractmethod
    def save_session(self, user_id: str, state: DojoSessionState) -> bool:
        """Sauvegarde l'état de session."""
        pass
    
    @abstractmethod
    def load_session(self, user_id: str) -> Optional[DojoSessionState]:
        """Charge l'état de session."""
        pass
    
    @abstractmethod  
    def delete_session(self, user_id: str) -> bool:
        """Supprime la session."""
        pass

class LocalStorageAdapter(SessionStorageInterface):
    """Adaptateur pour localStorage (frontend)."""
    
    def __init__(self, storage_key_prefix: str = "dojo_session"):
        self.prefix = storage_key_prefix
    
    def _get_key(self, user_id: str) -> str:
        return f"{self.prefix}_{user_id}"
    
    def save_session(self, user_id: str, state: DojoSessionState) -> bool:
        """Sauvegarde en localStorage."""
        try:
            # Note: Cette implémentation serait utilisée côté client
            # Ici on simule avec un dictionnaire en mémoire
            if not hasattr(self, '_memory_storage'):
                self._memory_storage = {}
            
            key = self._get_key(user_id)
            self._memory_storage[key] = json.dumps(state.to_dict())
            logger.debug(f"✅ Session saved for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save session for {user_id}: {e}")
            return False
    
    def load_session(self, user_id: str) -> Optional[DojoSessionState]:
        """Charge depuis localStorage."""
        try:
            if not hasattr(self, '_memory_storage'):
                return None
                
            key = self._get_key(user_id)
            if key not in self._memory_storage:
                return None
            
            data = json.loads(self._memory_storage[key])
            state = DojoSessionState.from_dict(data)
            
            # Vérifier expiration
            if state.is_expired():
                self.delete_session(user_id)
                return None
            
            logger.debug(f"✅ Session loaded for user {user_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Failed to load session for {user_id}: {e}")
            return None
    
    def delete_session(self, user_id: str) -> bool:
        """Supprime de localStorage."""
        try:
            if hasattr(self, '_memory_storage'):
                key = self._get_key(user_id)
                self._memory_storage.pop(key, None)
            logger.debug(f"✅ Session deleted for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete session for {user_id}: {e}")
            return False

class SupabaseStorageAdapter(SessionStorageInterface):
    """Adaptateur pour stockage Supabase."""
    
    def __init__(self, supabase_client, table_name: str = "dojo_sessions"):
        self.client = supabase_client
        self.table = table_name
    
    def save_session(self, user_id: str, state: DojoSessionState) -> bool:
        """Sauvegarde en Supabase."""
        try:
            session_data = {
                "user_id": user_id,
                "session_state": state.to_dict(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Upsert (insert or update)
            result = self.client.table(self.table).upsert(
                session_data, 
                on_conflict="user_id"
            ).execute()
            
            logger.debug(f"✅ Session saved to Supabase for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save session to Supabase for {user_id}: {e}")
            return False
    
    def load_session(self, user_id: str) -> Optional[DojoSessionState]:
        """Charge depuis Supabase."""
        try:
            result = self.client.table(self.table).select("*").eq("user_id", user_id).single().execute()
            
            if not result.data:
                return None
            
            session_data = result.data["session_state"]
            state = DojoSessionState.from_dict(session_data)
            
            # Vérifier expiration
            if state.is_expired():
                self.delete_session(user_id)
                return None
            
            logger.debug(f"✅ Session loaded from Supabase for user {user_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Failed to load session from Supabase for {user_id}: {e}")
            return None
    
    def delete_session(self, user_id: str) -> bool:
        """Supprime de Supabase."""
        try:
            self.client.table(self.table).delete().eq("user_id", user_id).execute()
            logger.debug(f"✅ Session deleted from Supabase for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete session from Supabase for {user_id}: {e}")
            return False

class DojoSessionManager:
    """✅ Gestionnaire principal de session persistante pour Dojo Mental."""
    
    def __init__(self, storage: SessionStorageInterface, auto_save_interval: int = 30):
        """
        Initialise le gestionnaire de session.
        
        Args:
            storage: Adaptateur de stockage
            auto_save_interval: Intervalle de sauvegarde auto (secondes)
        """
        self.storage = storage
        self.auto_save_interval = auto_save_interval
        self._sessions: Dict[str, DojoSessionState] = {}
        self._last_save: Dict[str, float] = {}
    
    def get_session(self, user_id: str) -> DojoSessionState:
        """
        Récupère ou crée une session utilisateur.
        
        Args:
            user_id: Identifiant utilisateur
            
        Returns:
            État de session (chargé ou nouveau)
        """
        # Vérifier cache mémoire
        if user_id in self._sessions:
            session = self._sessions[user_id]
            if not session.is_expired():
                session.update_activity()
                self._maybe_auto_save(user_id)
                return session
            else:
                # Session expirée, nettoyer
                del self._sessions[user_id]
        
        # Charger depuis stockage persistant
        session = self.storage.load_session(user_id)
        if session is None:
            # Créer nouvelle session
            session = DojoSessionState(user_id=user_id)
            logger.info(f"🆕 New Dojo session created for user {user_id}")
        else:
            logger.info(f"📂 Dojo session restored for user {user_id}")
        
        # Mettre en cache
        self._sessions[user_id] = session
        session.update_activity()
        
        return session
    
    def update_dialogue(self, user_id: str, dialogue: str):
        """Met à jour le dialogue en cours."""
        session = self.get_session(user_id)
        session.current_dialogue = dialogue
        session.update_activity()
        self._maybe_auto_save(user_id)
    
    def update_kaizen_input(self, user_id: str, input_text: str):
        """Met à jour le champ Kaizen."""
        session = self.get_session(user_id)
        session.kaizen_input = input_text
        session.update_activity()
        self._maybe_auto_save(user_id)
    
    def clear_kaizen_input(self, user_id: str):
        """Vide le champ Kaizen après soumission."""
        session = self.get_session(user_id)
        session.kaizen_input = ""
        session.update_activity()
        self._maybe_auto_save(user_id)
    
    def update_stats(self, user_id: str, stat_key: str, value: Any):
        """Met à jour les statistiques de session."""
        session = self.get_session(user_id)
        session.session_stats[stat_key] = value
        session.update_activity()
        self._maybe_auto_save(user_id)
    
    def set_zazen_state(self, user_id: str, duration: int, status: str = "active"):
        """Met à jour l'état Zazen."""
        session = self.get_session(user_id)
        session.zazen_state = {
            "duration": duration,
            "status": status,
            "started_at": time.time()
        }
        session.update_activity()
        self._maybe_auto_save(user_id)
    
    def save_session(self, user_id: str) -> bool:
        """Force la sauvegarde d'une session."""
        if user_id not in self._sessions:
            return False
        
        session = self._sessions[user_id]
        success = self.storage.save_session(user_id, session)
        
        if success:
            self._last_save[user_id] = time.time()
            logger.debug(f"💾 Session manually saved for user {user_id}")
        
        return success
    
    def save_all_sessions(self) -> Dict[str, bool]:
        """Sauvegarde toutes les sessions actives."""
        results = {}
        for user_id in self._sessions:
            results[user_id] = self.save_session(user_id)
        
        logger.info(f"💾 Bulk save completed: {sum(results.values())}/{len(results)} sessions saved")
        return results
    
    def delete_session(self, user_id: str) -> bool:
        """Supprime une session."""
        # Supprimer du cache
        if user_id in self._sessions:
            del self._sessions[user_id]
        if user_id in self._last_save:
            del self._last_save[user_id]
        
        # Supprimer du stockage
        return self.storage.delete_session(user_id)
    
    def _maybe_auto_save(self, user_id: str):
        """Sauvegarde automatique si intervalle dépassé."""
        current_time = time.time()
        last_save = self._last_save.get(user_id, 0)
        
        if current_time - last_save > self.auto_save_interval:
            self.save_session(user_id)
    
    def get_session_stats(self, user_id: str) -> Dict[str, Any]:
        """Retourne les statistiques de session."""
        session = self.get_session(user_id)
        
        return {
            "user_id": user_id,
            "session_duration": time.time() - session.last_activity,
            "stats": session.session_stats,
            "zazen_state": session.zazen_state,
            "current_dialogue": session.current_dialogue[:50] + "..." if len(session.current_dialogue) > 50 else session.current_dialogue
        }
    
    def cleanup_expired_sessions(self) -> int:
        """Nettoie les sessions expirées."""
        expired_users = []
        
        for user_id, session in self._sessions.items():
            if session.is_expired():
                expired_users.append(user_id)
        
        for user_id in expired_users:
            self.delete_session(user_id)
            logger.info(f"🧹 Expired session cleaned for user {user_id}")
        
        return len(expired_users)


# Factory functions pour création facile
def create_local_session_manager(auto_save_interval: int = 30) -> DojoSessionManager:
    """Crée un gestionnaire avec stockage local."""
    storage = LocalStorageAdapter()
    return DojoSessionManager(storage, auto_save_interval)

def create_supabase_session_manager(supabase_client, auto_save_interval: int = 60) -> DojoSessionManager:
    """Crée un gestionnaire avec stockage Supabase."""
    storage = SupabaseStorageAdapter(supabase_client)
    return DojoSessionManager(storage, auto_save_interval)