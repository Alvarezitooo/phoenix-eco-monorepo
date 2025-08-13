"""
🔐 Phoenix Shared Auth - AuthManager Unifié
Implémentation de la vision stratégique d'authentification unique
pour tout l'écosystème Phoenix avec user_id comme stream_id

Author: Claude Phoenix DevSecOps Guardian  
Version: 1.0.0 - Strategic Vision Implementation
"""

import os
import logging
from typing import Optional, Dict, Any, Tuple
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class AuthManager:
    """
    Gestionnaire d'authentification unifié pour l'écosystème Phoenix
    
    Le user_id retourné par cette classe devient le stream_id pour tous
    les événements Phoenix (CVGenerated, LetterGenerated, etc.)
    """
    
    def __init__(self):
        """Initialise le client Supabase Auth"""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")  # Clé publique pour auth
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")
        
        try:
            self.client: Client = create_client(url, key)
            logger.info("✅ AuthManager initialized with Supabase")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    def sign_up(self, email: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Inscription utilisateur
        
        Args:
            email: Email utilisateur
            password: Mot de passe
            metadata: Métadonnées additionnelles (nom, etc.)
            
        Returns:
            Tuple[success: bool, message: str, user_id: Optional[str]]
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": metadata or {}}
            })
            
            if response.user:
                logger.info(f"✅ User registered: {email}")
                return True, "Registration successful", str(response.user.id)
            else:
                return False, "Registration failed", None
                
        except Exception as e:
            logger.error(f"❌ Registration error for {email}: {e}")
            return False, f"Registration error: {str(e)}", None
    
    def sign_in(self, email: str, password: str) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Connexion utilisateur
        
        Args:
            email: Email utilisateur
            password: Mot de passe
            
        Returns:
            Tuple[success: bool, message: str, user_id: Optional[str], access_token: Optional[str]]
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                logger.info(f"✅ User authenticated: {email}")
                return True, "Login successful", str(response.user.id), response.session.access_token
            else:
                return False, "Invalid credentials", None, None
                
        except Exception as e:
            logger.error(f"❌ Login error for {email}: {e}")
            return False, f"Login error: {str(e)}", None, None
    
    def get_user(self, access_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations utilisateur courant
        
        Args:
            access_token: Token d'accès (optionnel si session active)
            
        Returns:
            Dict avec user_id, email, metadata ou None si non connecté
        """
        try:
            if access_token:
                # Définir le token pour cette requête
                self.client.auth.set_session(access_token, "")
            
            response = self.client.auth.get_user()
            
            if response.user:
                user_data = {
                    "user_id": str(response.user.id),  # ⭐ STREAM_ID pour Event Store
                    "email": response.user.email,
                    "metadata": response.user.user_metadata or {},
                    "created_at": response.user.created_at,
                    "last_sign_in": response.user.last_sign_in_at
                }
                
                logger.debug(f"✅ User data retrieved: {user_data['user_id']}")
                return user_data
            else:
                logger.debug("⚠️ No authenticated user found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Get user error: {e}")
            return None
    
    def sign_out(self) -> Tuple[bool, str]:
        """
        Déconnexion utilisateur
        
        Returns:
            Tuple[success: bool, message: str]
        """
        try:
            response = self.client.auth.sign_out()
            logger.info("✅ User signed out")
            return True, "Logout successful"
            
        except Exception as e:
            logger.error(f"❌ Logout error: {e}")
            return False, f"Logout error: {str(e)}"
    
    def validate_token(self, access_token: str) -> Optional[str]:
        """
        Valide un token d'accès et retourne le user_id
        
        Args:
            access_token: Token à valider
            
        Returns:
            user_id si token valide, None sinon
        """
        try:
            # Temporary set session with token
            self.client.auth.set_session(access_token, "")
            user = self.client.auth.get_user()
            
            if user.user:
                return str(user.user.id)
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Token validation error: {e}")
            return None
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le profil utilisateur depuis la table profiles
        
        Args:
            user_id: ID utilisateur (stream_id)
            
        Returns:
            Profil utilisateur ou None
        """
        try:
            response = self.client.table('profiles').select('*').eq('id', user_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Get profile error for {user_id}: {e}")
            return None
    
    def create_or_update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Crée ou met à jour le profil utilisateur
        
        Args:
            user_id: ID utilisateur (stream_id)
            profile_data: Données du profil
            
        Returns:
            Success boolean
        """
        try:
            # Essayer de mettre à jour
            update_response = self.client.table('profiles').update(profile_data).eq('id', user_id).execute()
            
            if update_response.data:
                logger.info(f"✅ Profile updated for {user_id}")
                return True
            else:
                # Si pas de mise à jour, créer le profil
                profile_data['id'] = user_id
                create_response = self.client.table('profiles').insert(profile_data).execute()
                
                if create_response.data:
                    logger.info(f"✅ Profile created for {user_id}")
                    return True
                else:
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Profile upsert error for {user_id}: {e}")
            return False
    
    def get_user_subscription_status(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère le statut d'abonnement utilisateur
        
        Args:
            user_id: ID utilisateur (stream_id)
            
        Returns:
            Dict avec subscription_tier, status, features, etc.
        """
        try:
            # Récupérer depuis table user_subscriptions
            response = self.client.table('user_subscriptions').select('*').eq('user_id', user_id).execute()
            
            if response.data:
                subscription = response.data[0]
                return {
                    "subscription_tier": subscription.get("subscription_tier", "free"),
                    "status": subscription.get("status", "inactive"),
                    "stripe_customer_id": subscription.get("stripe_customer_id"),
                    "stripe_subscription_id": subscription.get("stripe_subscription_id"),
                    "current_period_end": subscription.get("current_period_end"),
                    "features": self._get_features_for_tier(subscription.get("subscription_tier", "free"))
                }
            else:
                # Utilisateur gratuit par défaut
                return {
                    "subscription_tier": "free",
                    "status": "active",
                    "stripe_customer_id": None,
                    "stripe_subscription_id": None,
                    "current_period_end": None,
                    "features": self._get_features_for_tier("free")
                }
                
        except Exception as e:
            logger.error(f"❌ Subscription status error for {user_id}: {e}")
            return {"subscription_tier": "free", "status": "error", "features": {}}
    
    def _get_features_for_tier(self, tier: str) -> Dict[str, Any]:
        """Retourne les fonctionnalités selon le tier d'abonnement"""
        features_map = {
            "free": {
                "cv_monthly_limit": 3,
                "letters_monthly_limit": 5,
                "premium_templates": False,
                "ats_optimization": False,
                "mirror_match": False,
                "advanced_ai": False
            },
            "cv_premium": {
                "cv_monthly_limit": -1,  # illimité
                "letters_monthly_limit": 5,  # reste limité
                "premium_templates": True,
                "ats_optimization": True,
                "mirror_match": True,
                "advanced_ai": False
            },
            "letters_premium": {
                "cv_monthly_limit": 3,  # reste limité
                "letters_monthly_limit": -1,  # illimité
                "premium_templates": False,
                "ats_optimization": False,
                "mirror_match": False,
                "advanced_ai": True
            },
            "pack_premium": {
                "cv_monthly_limit": -1,  # illimité
                "letters_monthly_limit": -1,  # illimité
                "premium_templates": True,
                "ats_optimization": True,
                "mirror_match": True,
                "advanced_ai": True
            }
        }
        
        return features_map.get(tier, features_map["free"])


# Instance globale pour faciliter l'import
auth_manager = None

def get_auth_manager() -> AuthManager:
    """Factory function pour obtenir l'instance AuthManager"""
    global auth_manager
    if auth_manager is None:
        auth_manager = AuthManager()
    return auth_manager