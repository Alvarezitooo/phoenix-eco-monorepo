"""
Client Supabase centralisé pour Phoenix Backend
"""

import logging
from typing import Optional, Dict, Any
from supabase import create_client, Client
from config.settings import settings

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Client Supabase avec gestion d'erreurs et logging"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise la connexion Supabase"""
        try:
            if not settings.supabase_url or not settings.supabase_key:
                raise ValueError("SUPABASE_URL et SUPABASE_ANON_KEY sont requis")
            
            self.client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            logger.info("✅ Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par email"""
        try:
            response = self.client.table('profiles').select('*').eq('email', email).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            return None
    
    async def get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère l'abonnement d'un utilisateur"""
        try:
            response = self.client.table('user_subscriptions').select('*').eq('user_id', user_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching subscription for user {user_id}: {e}")
            return None
    
    async def create_kaizen_entry(self, user_id: str, action: str, completed: bool = False) -> Dict[str, Any]:
        """Crée une entrée Kaizen"""
        try:
            data = {
                'user_id': user_id,
                'action': action,
                'date': 'now()',
                'completed': completed
            }
            response = self.client.table('kaizen').insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error creating Kaizen entry: {e}")
            raise
    
    async def get_user_kaizen_history(self, user_id: str, limit: int = 50) -> list:
        """Récupère l'historique Kaizen d'un utilisateur"""
        try:
            response = self.client.table('kaizen').select('*').eq('user_id', user_id).limit(limit).order('date', desc=True).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching Kaizen history for user {user_id}: {e}")
            return []
    
    async def create_zazen_session(self, user_id: str, duration: int, triggered_by: str = None) -> Dict[str, Any]:
        """Crée une session Zazen"""
        try:
            data = {
                'user_id': user_id,
                'timestamp': 'now()',
                'duration': duration,
                'triggered_by': triggered_by
            }
            response = self.client.table('zazen_sessions').insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error creating Zazen session: {e}")
            raise
    
    async def save_career_exploration(self, user_id: str, exploration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sauvegarde une exploration de carrière"""
        try:
            data = {
                'user_id': user_id,
                'exploration_data': exploration_data,
                'completion_status': 'completed'
            }
            response = self.client.table('career_explorations').insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error saving career exploration: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Vérifie si la connexion Supabase est active"""
        return self.client is not None