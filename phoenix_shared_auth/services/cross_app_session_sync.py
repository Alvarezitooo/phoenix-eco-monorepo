"""
🔄 Phoenix Cross-App Session Synchronization
Service de synchronisation des sessions entre toutes les applications Phoenix

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

# Configuration du logger
logger = logging.getLogger(__name__)

# Configuration pour chaque application Phoenix
class PhoenixApp(Enum):
    LETTERS = "phoenix_letters"
    CV = "phoenix_cv"
    RISE = "phoenix_rise"
    WEBSITE = "phoenix_website"


class SessionSyncService:
    """
    Service de synchronisation des sessions entre applications Phoenix
    Gère l'authentification unifiée et la persistance cross-app
    """
    
    def __init__(self):
        self.session_store = {}  # En prod: Redis ou base centralisée
        self.session_ttl = timedelta(hours=24)  # TTL des sessions
        
        # Configuration des applications
        self.app_config = {
            PhoenixApp.LETTERS: {
                "url_base": "https://phoenix-letters.streamlit.app",
                "session_param": "phoenix_session_id",
                "auth_endpoint": "/auth/verify"
            },
            PhoenixApp.CV: {
                "url_base": "https://phoenix-cv.streamlit.app", 
                "session_param": "phoenix_session_id",
                "auth_endpoint": "/auth/verify"
            },
            PhoenixApp.WEBSITE: {
                "url_base": "https://phoenixcreator.netlify.app",
                "session_param": "phoenix_session_id",
                "auth_endpoint": "/api/auth/verify"
            }
        }
        
        logger.info("✅ SessionSyncService initialisé")
    
    def create_unified_session(
        self, 
        user_data: Dict[str, Any], 
        source_app: PhoenixApp
    ) -> str:
        """
        Crée une session unifiée valide pour toutes les applications
        
        Args:
            user_data: Données utilisateur complètes
            source_app: Application source de la création
            
        Returns:
            str: ID de session unifiée
        """
        session_id = f"phoenix_session_{uuid.uuid4().hex}"
        
        session_data = {
            "session_id": session_id,
            "user_id": user_data.get("id"),
            "email": user_data.get("email"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "tier": user_data.get("tier", "free"),
            "is_guest": user_data.get("is_guest", False),
            "phoenix_ecosystem": user_data.get("phoenix_ecosystem", True),
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + self.session_ttl).isoformat(),
            "source_app": source_app.value,
            "active_apps": [source_app.value],
            "last_activity": datetime.now().isoformat(),
            "cross_app_data": {
                "cv_count": user_data.get("cv_count", 0),
                "letters_count": user_data.get("letters_count", 0),
                "premium_features_used": user_data.get("premium_features_used", []),
                "preferences": user_data.get("preferences", {})
            }
        }
        
        # Sauvegarde de la session (en prod: base centralisée)
        self.session_store[session_id] = session_data
        
        logger.info(f"✅ Session unifiée créée: {session_id} pour {user_data.get('email')}")
        return session_id
    
    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Vérifie et récupère une session unifiée
        
        Args:
            session_id: ID de session à vérifier
            
        Returns:
            Optional[Dict]: Données de session si valide, None sinon
        """
        if not session_id or session_id not in self.session_store:
            return None
        
        session_data = self.session_store[session_id]
        
        # Vérification expiration
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        if datetime.now() > expires_at:
            self.invalidate_session(session_id)
            return None
        
        # Mise à jour dernière activité
        session_data["last_activity"] = datetime.now().isoformat()
        self.session_store[session_id] = session_data
        
        return session_data
    
    def sync_session_to_app(
        self, 
        session_id: str, 
        target_app: PhoenixApp,
        additional_data: Dict[str, Any] = None
    ) -> bool:
        """
        Synchronise une session vers une application cible
        
        Args:
            session_id: ID de session à synchroniser
            target_app: Application cible
            additional_data: Données supplémentaires spécifiques à l'app
            
        Returns:
            bool: True si synchronisation réussie
        """
        session_data = self.verify_session(session_id)
        if not session_data:
            return False
        
        try:
            # Ajout de l'app aux apps actives
            if target_app.value not in session_data["active_apps"]:
                session_data["active_apps"].append(target_app.value)
            
            # Ajout des données supplémentaires
            if additional_data:
                session_data["cross_app_data"].update(additional_data)
            
            # Sauvegarde mise à jour
            self.session_store[session_id] = session_data
            
            logger.info(f"✅ Session {session_id} synchronisée vers {target_app.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sync session vers {target_app.value}: {e}")
            return False
    
    def generate_cross_app_url(
        self, 
        session_id: str, 
        target_app: PhoenixApp,
        target_path: str = "",
        params: Dict[str, str] = None
    ) -> str:
        """
        Génère une URL avec session pour navigation cross-app
        
        Args:
            session_id: ID de session active
            target_app: Application cible
            target_path: Chemin cible dans l'app
            params: Paramètres supplémentaires
            
        Returns:
            str: URL complète avec session
        """
        app_config = self.app_config.get(target_app)
        if not app_config:
            return ""
        
        base_url = app_config["url_base"]
        session_param = app_config["session_param"]
        
        # Construction URL
        url = f"{base_url}{target_path}"
        
        # Ajout paramètres de session
        params = params or {}
        params[session_param] = session_id
        
        # Construction query string
        query_params = "&".join([f"{k}={v}" for k, v in params.items()])
        
        if query_params:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{query_params}"
        
        return url
    
    def get_user_apps_activity(self, session_id: str) -> Dict[str, Any]:
        """
        Récupère l'activité utilisateur sur toutes les apps
        
        Args:
            session_id: ID de session
            
        Returns:
            Dict: Activité cross-app
        """
        session_data = self.verify_session(session_id)
        if not session_data:
            return {}
        
        return {
            "active_apps": session_data.get("active_apps", []),
            "last_activity": session_data.get("last_activity"),
            "cross_app_data": session_data.get("cross_app_data", {}),
            "session_duration": self._calculate_session_duration(session_data),
            "recommendations": self._get_app_recommendations(session_data)
        }
    
    def update_session_data(
        self, 
        session_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        Met à jour les données d'une session
        
        Args:
            session_id: ID de session
            updates: Données à mettre à jour
            
        Returns:
            bool: True si mise à jour réussie
        """
        session_data = self.verify_session(session_id)
        if not session_data:
            return False
        
        try:
            # Mise à jour sécurisée (certains champs protégés)
            protected_fields = ["session_id", "created_at", "user_id"]
            
            for key, value in updates.items():
                if key not in protected_fields:
                    if key == "cross_app_data":
                        session_data["cross_app_data"].update(value)
                    else:
                        session_data[key] = value
            
            session_data["last_activity"] = datetime.now().isoformat()
            self.session_store[session_id] = session_data
            
            logger.info(f"✅ Session {session_id} mise à jour")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour session {session_id}: {e}")
            return False
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalide une session sur toutes les applications
        
        Args:
            session_id: ID de session à invalider
            
        Returns:
            bool: True si invalidation réussie
        """
        try:
            if session_id in self.session_store:
                del self.session_store[session_id]
            
            logger.info(f"✅ Session {session_id} invalidée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur invalidation session {session_id}: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Nettoie les sessions expirées
        
        Returns:
            int: Nombre de sessions nettoyées
        """
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.session_store.items():
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            if now > expires_at:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.session_store[session_id]
        
        if expired_sessions:
            logger.info(f"🧹 {len(expired_sessions)} sessions expirées nettoyées")
        
        return len(expired_sessions)
    
    def _calculate_session_duration(self, session_data: Dict[str, Any]) -> str:
        """
        Calcule la durée d'une session
        """
        created_at = datetime.fromisoformat(session_data["created_at"])
        now = datetime.now()
        duration = now - created_at
        
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    
    def _get_app_recommendations(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Génère des recommandations d'applications basées sur l'activité
        """
        recommendations = []
        active_apps = session_data.get("active_apps", [])
        cross_data = session_data.get("cross_app_data", {})
        
        # Recommandation Phoenix Letters si CV créé
        if PhoenixApp.CV.value in active_apps and cross_data.get("cv_count", 0) > 0:
            if PhoenixApp.LETTERS.value not in active_apps:
                recommendations.append({
                    "app": PhoenixApp.LETTERS.value,
                    "title": "Créez votre lettre de motivation",
                    "reason": "Vous avez créé un CV, complétez avec une lettre personnalisée",
                    "priority": "high"
                })
        
        # Recommandation Phoenix CV si lettres créées
        if PhoenixApp.LETTERS.value in active_apps and cross_data.get("letters_count", 0) > 0:
            if PhoenixApp.CV.value not in active_apps:
                recommendations.append({
                    "app": PhoenixApp.CV.value,
                    "title": "Optimisez votre CV",
                    "reason": "Harmonisez votre CV avec vos lettres de motivation",
                    "priority": "medium"
                })
        
        return recommendations


# Instance globale
session_sync_service = SessionSyncService()

logger = logging.getLogger(__name__)