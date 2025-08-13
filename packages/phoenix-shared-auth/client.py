"""
🔐 Phoenix AuthManager Unifié - Vision Stratégique Implémentée
Authentification centralisée pour tout l'écosystème Phoenix
avec user_id comme stream_id pour Event-Sourcing

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Strategic Vision Implementation
"""

import os
import logging
from typing import Optional, Dict, Any, Tuple
from supabase import create_client, Client
from .entities.phoenix_user import PhoenixUser
from .entities.phoenix_subscription import PhoenixSubscription

logger = logging.getLogger(__name__)

class AuthManager:
    """
    Gestionnaire d'authentification unifié pour l'écosystème Phoenix
    
    Point d'entrée unique pour :
    - Authentification Supabase
    - Gestion utilisateurs et profils  
    - Synchronisation cross-app
    - user_id devient stream_id pour Event Store
    """
    
    def __init__(self):
        """Initialise la connexion Supabase"""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        
        self.client: Client = create_client(url, key)
        logger.info("✅ AuthManager initialized with Supabase")
    
    def sign_up(self, email: str, password: str, metadata: Optional[Dict] = None) -> Tuple[bool, Optional[PhoenixUser], str]:
        """
        Inscription utilisateur avec création profil
        
        Returns:
            Tuple[success: bool, user: Optional[PhoenixUser], message: str]
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            
            if response.user:
                user_id = response.user.id
                
                # Créer profil Phoenix
                profile_data = {
                    "id": user_id,
                    "email": email,
                    "subscription_tier": "free",
                    "created_at": "now()",
                    **{k: v for k, v in (metadata or {}).items() if k in ['full_name', 'phone']}
                }
                
                self.client.table('profiles').insert(profile_data).execute()
                
                phoenix_user = PhoenixUser(
                    user_id=user_id,
                    email=email,
                    subscription_tier="free",
                    metadata=metadata
                )
                
                logger.info(f"✅ User signed up: {email} -> {user_id}")
                return True, phoenix_user, "Account created successfully"
            
            return False, None, "Registration failed"
            
        except Exception as e:
            logger.error(f"❌ Sign up error for {email}: {e}")
            return False, None, f"Registration error: {str(e)}"
    
    def sign_in(self, email: str, password: str) -> Tuple[bool, Optional[PhoenixUser], str]:
        """
        Connexion utilisateur avec récupération profil
        
        Returns:
            Tuple[success: bool, user: Optional[PhoenixUser], message: str]
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                user_id = response.user.id
                
                # Récupérer profil complet
                profile_response = self.client.table('profiles').select('*').eq('id', user_id).single().execute()
                
                if profile_response.data:
                    profile = profile_response.data
                    
                    phoenix_user = PhoenixUser(
                        user_id=user_id,
                        email=profile['email'],
                        subscription_tier=profile.get('subscription_tier', 'free'),
                        full_name=profile.get('full_name'),
                        phone=profile.get('phone'),
                        metadata=profile
                    )
                    
                    logger.info(f"✅ User signed in: {email} -> {user_id}")
                    return True, phoenix_user, "Successfully signed in"
                
                return False, None, "Profile not found"
            
            return False, None, "Invalid credentials"
            
        except Exception as e:
            logger.error(f"❌ Sign in error for {email}: {e}")
            return False, None, f"Sign in error: {str(e)}"
    
    def get_user(self) -> Optional[Dict[str, Any]]:
        """
        Récupère l'utilisateur actuel avec son profil
        CRITIF: Retourne user_id comme stream_id pour Event Store
        
        Returns:
            Dict avec user_id, email, subscription_tier, etc.
            user_id sert de stream_id pour l'Event-Sourcing
        """
        try:
            user = self.client.auth.get_user()
            
            if user and user.user:
                user_id = user.user.id
                
                # Récupérer profil complet
                profile_response = self.client.table('profiles').select('*').eq('id', user_id).single().execute()
                
                if profile_response.data:
                    profile_data = profile_response.data
                    
                    return {
                        'user_id': user_id,  # 🎯 DEVIENT stream_id pour Event Store
                        'stream_id': user_id,  # Alias explicite pour Event-Sourcing
                        'email': profile_data['email'],
                        'subscription_tier': profile_data.get('subscription_tier', 'free'),
                        'full_name': profile_data.get('full_name'),
                        'phone': profile_data.get('phone'),
                        'created_at': profile_data.get('created_at'),
                        'is_premium': profile_data.get('subscription_tier') != 'free',
                        'profile': profile_data
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Get user error: {e}")
            return None
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le profil d'un utilisateur par ID"""
        try:
            response = self.client.table('profiles').select('*').eq('id', user_id).single().execute()
            return response.data if response.data else None
            
        except Exception as e:
            logger.error(f"❌ Get profile error for {user_id}: {e}")
            return None
    
    def update_user_tier(self, user_id: str, subscription_tier: str) -> bool:
        """Met à jour le tier d'abonnement utilisateur"""
        try:
            response = self.client.table('profiles').update({
                'subscription_tier': subscription_tier
            }).eq('id', user_id).execute()
            
            if response.data:
                logger.info(f"✅ User tier updated: {user_id} -> {subscription_tier}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Update tier error for {user_id}: {e}")
            return False
    
    def sign_out(self) -> bool:
        """Déconnexion utilisateur"""
        try:
            self.client.auth.sign_out()
            logger.info("✅ User signed out")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sign out error: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Vérifie si utilisateur est connecté"""
        try:
            user = self.client.auth.get_user()
            return bool(user and user.user)
        except:
            return False
    
    def has_premium_access(self, feature_app: Optional[str] = None) -> bool:
        """
        Vérifie l'accès Premium selon l'app
        
        Args:
            feature_app: 'cv', 'letters', ou None pour bundle
        """
        user_data = self.get_user()
        if not user_data:
            return False
        
        tier = user_data.get('subscription_tier', 'free')
        
        # Bundle donne accès à tout
        if tier == 'pack_premium':
            return True
        
        # Accès spécifique par app
        if feature_app == 'cv' and tier == 'cv_premium':
            return True
        if feature_app == 'letters' and tier == 'letters_premium':
            return True
        
        return False
    
    def get_subscription_info(self) -> Optional[PhoenixSubscription]:
        """Récupère les informations d'abonnement"""
        user_data = self.get_user()
        if not user_data:
            return None
        
        try:
            response = self.client.table('user_subscriptions').select('*').eq('user_id', user_data['user_id']).single().execute()
            
            if response.data:
                sub_data = response.data
                return PhoenixSubscription(
                    user_id=user_data['user_id'],
                    subscription_tier=sub_data.get('subscription_tier', 'free'),
                    status=sub_data.get('status', 'active'),
                    stripe_customer_id=sub_data.get('stripe_customer_id'),
                    stripe_subscription_id=sub_data.get('stripe_subscription_id')
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Get subscription error: {e}")
            return None


# Instance globale singleton
_auth_manager = None

def get_auth_manager() -> AuthManager:
    """Factory function pour obtenir l'instance AuthManager"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


# Export des classes principales
__all__ = ['AuthManager', 'get_auth_manager', 'PhoenixUser', 'PhoenixSubscription']