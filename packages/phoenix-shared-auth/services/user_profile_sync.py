"""
🔄 Phoenix User Profile Sync Service
Service de synchronisation bidirectionnelle des profils utilisateur
entre applications Streamlit et le website Next.js

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

try:
    from supabase import Client
    from .phoenix_auth_service import PhoenixAuthService
    from phoenix_shared_auth.entities.phoenix_user import PhoenixUser, UserTier, PhoenixApp
    from phoenix_shared_auth.database.phoenix_db_connection import get_phoenix_db_connection
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None
    PhoenixAuthService = None
    PhoenixUser = None

logger = logging.getLogger(__name__)


class SyncDirection(Enum):
    """Direction de synchronisation"""
    APP_TO_WEBSITE = "app_to_website"
    WEBSITE_TO_APP = "website_to_app"
    BIDIRECTIONAL = "bidirectional"


class SyncEventType(Enum):
    """Type d'événement de synchronisation"""
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    PROFILE_SYNC = "profile_sync"
    SUBSCRIPTION_CHANGED = "subscription_changed"
    PREFERENCE_UPDATED = "preference_updated"


class UserProfileSyncService:
    """
    Service de synchronisation des profils utilisateur Phoenix
    Gère la synchronisation bidirectionnelle entre apps et website
    """
    
    def __init__(self, auth_service: PhoenixAuthService = None):
        self.supabase_available = SUPABASE_AVAILABLE
        self.auth_service = auth_service
        self.db_client: Optional[Client] = None
        
        if self.supabase_available and not auth_service:
            try:
                db_connection = get_phoenix_db_connection()
                self.auth_service = PhoenixAuthService(db_connection)
                self.db_client = db_connection.client
                logger.info("✅ UserProfileSyncService initialisé avec Supabase")
            except Exception as e:
                logger.error(f"❌ Erreur initialisation Supabase: {e}")
                self.supabase_available = False
        elif auth_service:
            self.auth_service = auth_service
            # Récupérer client DB depuis auth_service
            if hasattr(auth_service, 'db_connection') and hasattr(auth_service.db_connection, 'client'):
                self.db_client = auth_service.db_connection.client
        
        if not self.supabase_available:
            logger.warning("⚠️ UserProfileSyncService en mode dégradé - Supabase non disponible")
    
    def sync_user_from_app_to_website(
        self, 
        user_data: Dict[str, Any], 
        source_app: PhoenixApp,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Synchronise un utilisateur créé dans une app Streamlit vers le website
        
        Args:
            user_data: Données utilisateur de l'app
            source_app: Application source
            metadata: Métadonnées additionnelles
            
        Returns:
            bool: Succès de la synchronisation
        """
        if not self.supabase_available or not self.db_client:
            logger.warning("⚠️ Synchronisation impossible - Supabase non disponible")
            return False
        
        try:
            # Vérifier si utilisateur existe déjà dans Phoenix
            existing_user = self.auth_service.get_user_by_email(user_data.get("email"))
            
            sync_data = {
                "email": user_data.get("email"),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "source_app": source_app.value,
                "sync_direction": SyncDirection.APP_TO_WEBSITE.value,
                "sync_timestamp": datetime.now().isoformat(),
                "metadata": json.dumps(metadata or {}),
                "user_tier": user_data.get("tier", "free"),
                "is_active": user_data.get("is_active", True)
            }
            
            if existing_user:
                # Mise à jour utilisateur existant
                result = self._update_user_profile_in_db(str(existing_user.id), sync_data)
                if result:
                    self._log_sync_event(
                        str(existing_user.id), 
                        SyncEventType.PROFILE_SYNC, 
                        source_app,
                        f"Profil synchronisé depuis {source_app.value}"
                    )
                    logger.info(f"✅ Utilisateur {user_data.get('email')} synchronisé depuis {source_app.value}")
                    return True
            else:
                # Créer nouvel utilisateur Phoenix
                phoenix_user = self.auth_service.register_user(
                    email=user_data.get("email"),
                    password="app_managed_auth",  # Password géré par l'app source
                    first_name=user_data.get("first_name", ""),
                    last_name=user_data.get("last_name", ""),
                    tier=UserTier.FREE,
                    metadata={
                        **sync_data,
                        "created_from_app": True,
                        "original_app": source_app.value
                    }
                )
                
                if phoenix_user:
                    self._log_sync_event(
                        str(phoenix_user.id), 
                        SyncEventType.USER_CREATED, 
                        source_app,
                        f"Utilisateur créé depuis {source_app.value}"
                    )
                    logger.info(f"✅ Nouvel utilisateur {user_data.get('email')} créé depuis {source_app.value}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur sync app vers website: {e}")
            return False
    
    def sync_user_from_website_to_apps(
        self, 
        user_id: str, 
        target_apps: List[PhoenixApp] = None
    ) -> Dict[str, bool]:
        """
        Synchronise un utilisateur du website vers les apps spécifiées
        
        Args:
            user_id: ID utilisateur Phoenix
            target_apps: Apps cibles (toutes si None)
            
        Returns:
            Dict[str, bool]: Résultat de sync par app
        """
        if not self.supabase_available:
            logger.warning("⚠️ Synchronisation impossible - Supabase non disponible")
            return {}
        
        results = {}
        
        try:
            # Récupérer utilisateur Phoenix
            phoenix_user = self.auth_service.get_user_by_id(user_id)
            if not phoenix_user:
                logger.error(f"❌ Utilisateur {user_id} non trouvé")
                return results
            
            # Apps cibles par défaut
            if target_apps is None:
                target_apps = [PhoenixApp.CV, PhoenixApp.LETTERS, PhoenixApp.RISE]
            
            # Préparer données de synchronisation
            sync_data = {
                "phoenix_user_id": str(phoenix_user.id),
                "email": phoenix_user.email,
                "first_name": phoenix_user.first_name,
                "last_name": phoenix_user.last_name,
                "tier": phoenix_user.tier.value if phoenix_user.tier else "free",
                "is_active": phoenix_user.is_active,
                "sync_timestamp": datetime.now().isoformat(),
                "sync_direction": SyncDirection.WEBSITE_TO_APP.value
            }
            
            # Synchroniser vers chaque app
            for app in target_apps:
                try:
                    # Enregistrer dans table de synchronisation spécifique à l'app
                    result = self._create_app_sync_record(app, sync_data)
                    results[app.value] = result
                    
                    if result:
                        self._log_sync_event(
                            user_id, 
                            SyncEventType.PROFILE_SYNC, 
                            app,
                            f"Profil synchronisé vers {app.value}"
                        )
                        logger.info(f"✅ Utilisateur {phoenix_user.email} synchronisé vers {app.value}")
                    else:
                        logger.warning(f"⚠️ Échec synchronisation vers {app.value}")
                        
                except Exception as e:
                    logger.error(f"❌ Erreur sync vers {app.value}: {e}")
                    results[app.value] = False
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur sync website vers apps: {e}")
            return results
    
    def get_user_sync_status(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère le statut de synchronisation d'un utilisateur
        
        Args:
            user_id: ID utilisateur Phoenix
            
        Returns:
            Dict contenant le statut de sync
        """
        if not self.supabase_available or not self.db_client:
            return {"error": "Supabase non disponible"}
        
        try:
            # Récupérer événements de sync
            response = self.db_client.table('phoenix_sync_events').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
            
            sync_events = response.data if response.data else []
            
            # Récupérer statut par app
            app_sync_status = {}
            for app in PhoenixApp:
                app_response = self.db_client.table(f'phoenix_{app.value}_sync').select('*').eq('phoenix_user_id', user_id).order('sync_timestamp', desc=True).limit(1).execute()
                
                if app_response.data:
                    last_sync = app_response.data[0]
                    app_sync_status[app.value] = {
                        "last_sync": last_sync.get("sync_timestamp"),
                        "sync_direction": last_sync.get("sync_direction"),
                        "is_synced": True
                    }
                else:
                    app_sync_status[app.value] = {
                        "last_sync": None,
                        "sync_direction": None,
                        "is_synced": False
                    }
            
            return {
                "user_id": user_id,
                "sync_events": sync_events,
                "app_sync_status": app_sync_status,
                "total_sync_events": len(sync_events)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut sync: {e}")
            return {"error": str(e)}
    
    def sync_user_preferences(
        self, 
        user_id: str, 
        preferences: Dict[str, Any], 
        source_app: PhoenixApp = None
    ) -> bool:
        """
        Synchronise les préférences utilisateur entre applications
        
        Args:
            user_id: ID utilisateur Phoenix
            preferences: Préférences à synchroniser
            source_app: App source de la modification
            
        Returns:
            bool: Succès de la synchronisation
        """
        if not self.supabase_available or not self.db_client:
            return False
        
        try:
            # Mettre à jour préférences utilisateur
            response = self.db_client.table('phoenix_users').update({
                'preferences': json.dumps(preferences),
                'preferences_updated_at': datetime.now().isoformat()
            }).eq('id', user_id).execute()
            
            if response.data:
                # Log événement
                self._log_sync_event(
                    user_id, 
                    SyncEventType.PREFERENCE_UPDATED, 
                    source_app,
                    f"Préférences mises à jour depuis {source_app.value if source_app else 'unknown'}"
                )
                
                logger.info(f"✅ Préférences utilisateur {user_id} synchronisées")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur sync préférences: {e}")
            return False
    
    def sync_subscription_status(
        self, 
        user_id: str, 
        new_tier: UserTier, 
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Synchronise le statut d'abonnement entre toutes les applications
        
        Args:
            user_id: ID utilisateur Phoenix
            new_tier: Nouveau tier d'abonnement
            metadata: Métadonnées de l'abonnement
            
        Returns:
            bool: Succès de la synchronisation
        """
        if not self.supabase_available:
            return False
        
        try:
            # Mettre à jour tier utilisateur
            success = self.auth_service.update_user_tier(user_id, new_tier)
            
            if success:
                # Synchroniser vers toutes les apps
                sync_results = self.sync_user_from_website_to_apps(user_id)
                
                # Log événement
                self._log_sync_event(
                    user_id, 
                    SyncEventType.SUBSCRIPTION_CHANGED, 
                    PhoenixApp.WEBSITE,
                    f"Abonnement mis à jour vers {new_tier.value}"
                )
                
                logger.info(f"✅ Abonnement utilisateur {user_id} synchronisé: {new_tier.value}")
                return all(sync_results.values()) if sync_results else True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur sync abonnement: {e}")
            return False
    
    def _update_user_profile_in_db(self, user_id: str, sync_data: Dict[str, Any]) -> bool:
        """Met à jour le profil utilisateur dans la DB"""
        try:
            response = self.db_client.table('phoenix_users').update({
                'first_name': sync_data.get('first_name'),
                'last_name': sync_data.get('last_name'),
                'tier': sync_data.get('user_tier'),
                'is_active': sync_data.get('is_active'),
                'last_sync_timestamp': sync_data.get('sync_timestamp'),
                'metadata': sync_data.get('metadata')
            }).eq('id', user_id).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour profil DB: {e}")
            return False
    
    def _create_app_sync_record(self, app: PhoenixApp, sync_data: Dict[str, Any]) -> bool:
        """Crée un enregistrement de synchronisation pour une app spécifique"""
        try:
            table_name = f'phoenix_{app.value}_sync'
            
            response = self.db_client.table(table_name).insert({
                'phoenix_user_id': sync_data.get('phoenix_user_id'),
                'email': sync_data.get('email'),
                'user_data': json.dumps(sync_data),
                'sync_timestamp': sync_data.get('sync_timestamp'),
                'sync_direction': sync_data.get('sync_direction')
            }).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"❌ Erreur création record sync {app.value}: {e}")
            return False
    
    def _log_sync_event(
        self, 
        user_id: str, 
        event_type: SyncEventType, 
        source_app: PhoenixApp,
        description: str
    ):
        """Enregistre un événement de synchronisation"""
        try:
            if not self.db_client:
                return
            
            self.db_client.table('phoenix_sync_events').insert({
                'user_id': user_id,
                'event_type': event_type.value,
                'source_app': source_app.value if source_app else None,
                'description': description,
                'created_at': datetime.now().isoformat()
            }).execute()
            
        except Exception as e:
            logger.error(f"❌ Erreur log sync event: {e}")
    
    def get_sync_metrics(self) -> Dict[str, Any]:
        """
        Récupère les métriques de synchronisation
        
        Returns:
            Dict contenant les métriques
        """
        if not self.supabase_available or not self.db_client:
            return {"error": "Supabase non disponible"}
        
        try:
            # Compter événements de sync par type
            events_response = self.db_client.table('phoenix_sync_events').select('event_type, source_app').execute()
            
            metrics = {
                "total_sync_events": len(events_response.data) if events_response.data else 0,
                "events_by_type": {},
                "events_by_app": {},
                "sync_health": "healthy"
            }
            
            # Analyser événements
            for event in events_response.data or []:
                event_type = event.get('event_type', 'unknown')
                source_app = event.get('source_app', 'unknown')
                
                metrics["events_by_type"][event_type] = metrics["events_by_type"].get(event_type, 0) + 1
                metrics["events_by_app"][source_app] = metrics["events_by_app"].get(source_app, 0) + 1
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur métriques sync: {e}")
            return {"error": str(e)}


# Instance singleton pour import facile
profile_sync_service = None

def get_user_profile_sync_service(auth_service: PhoenixAuthService = None) -> UserProfileSyncService:
    """Factory function pour service de synchronisation des profils"""
    global profile_sync_service
    if profile_sync_service is None:
        profile_sync_service = UserProfileSyncService(auth_service)
    return profile_sync_service