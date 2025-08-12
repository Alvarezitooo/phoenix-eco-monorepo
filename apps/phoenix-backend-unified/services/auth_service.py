"""
Service d'authentification centralisé
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from config.settings import settings
from services.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

# Context pour hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service d'authentification avec Supabase"""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase = supabase_client
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hache un mot de passe"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Crée un token JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret, 
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT Error: {e}")
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authentifie un utilisateur via Supabase"""
        try:
            # Récupérer l'utilisateur depuis Supabase Auth
            auth_response = self.supabase.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Récupérer le profil complet
                profile = await self.supabase.get_user_by_email(email)
                subscription = await self.supabase.get_user_subscription(auth_response.user.id)
                
                return {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "full_name": profile.get("full_name") if profile else "",
                    "avatar_url": profile.get("avatar_url") if profile else None,
                    "subscription_tier": profile.get("subscription_tier", "free") if profile else "free",
                    "isPremium": (
                        subscription and subscription.get("subscription_tier") in ["premium", "premium_plus"] 
                        and subscription.get("status") == "active"
                    ) if subscription else False,
                    "created_at": auth_response.user.created_at
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Authentication failed for {email}: {e}")
            return None
    
    async def get_current_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Récupère l'utilisateur actuel depuis un token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        try:
            # Récupérer le profil utilisateur
            response = self.supabase.client.table('profiles').select('*').eq('id', user_id).single().execute()
            if response.data:
                profile = response.data
                subscription = await self.supabase.get_user_subscription(user_id)
                
                return {
                    "id": profile["id"],
                    "email": profile["email"],
                    "full_name": profile.get("full_name", ""),
                    "avatar_url": profile.get("avatar_url"),
                    "subscription_tier": profile.get("subscription_tier", "free"),
                    "isPremium": (
                        subscription and subscription.get("subscription_tier") in ["premium", "premium_plus"] 
                        and subscription.get("status") == "active"
                    ) if subscription else False
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user from token: {e}")
            return None