"""
🔐 PHOENIX AUTH STANDALONE - Authentification sécurisée pour Iris API
Module d'authentification indépendant utilisant JWT + Supabase

Author: Claude Phoenix DevSecOps Guardian  
Version: 2.0.0 - Production Security Ready
"""

import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import httpx

logger = logging.getLogger(__name__)

class UserTier(Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM" 
    ENTERPRISE = "ENTERPRISE"

@dataclass
class IrisUser:
    """Utilisateur Phoenix pour Iris API"""
    id: str
    email: str
    tier: UserTier
    email_verified: bool
    status: str
    daily_usage: int = 0
    last_usage_date: str = ""

class PhoenixAuthStandalone:
    """
    Gestionnaire d'authentification standalone pour Iris API
    Compatible avec l'écosystème Phoenix sans dépendances complexes
    """
    
    def __init__(self):
        self.jwt_secret = self._get_jwt_secret()
        self.supabase = self._init_supabase()
        self.rate_limits = {
            UserTier.FREE: {"daily_messages": 5, "context_retention_days": 1},
            UserTier.PREMIUM: {"daily_messages": 50, "context_retention_days": 7},
            UserTier.ENTERPRISE: {"daily_messages": -1, "context_retention_days": 30}
        }
        
    def _get_jwt_secret(self) -> str:
        """Récupère la clé JWT sécurisée"""
        secret = os.getenv("JWT_SECRET_KEY")
        if not secret:
            raise ValueError("JWT_SECRET_KEY environment variable required")
        return secret
        
    def _init_supabase(self) -> Client:
        """Initialise le client Supabase"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
            
        return create_client(url, key)
    
    async def verify_token(self, token: str) -> Optional[IrisUser]:
        """
        Vérifie et décode un token JWT Phoenix
        
        Returns:
            IrisUser si token valide, None sinon
        """
        try:
            # 1. Décoder le JWT
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # 2. Vérifications de base
            if not payload.get('sub'):
                logger.warning("Token sans user ID")
                return None
                
            # 3. Vérification expiration
            exp = payload.get('exp')
            if exp and datetime.utcnow().timestamp() > exp:
                logger.info("Token expiré")
                return None
                
            # 4. Récupérer les données utilisateur depuis Supabase
            user_data = await self._get_user_data(payload['sub'])
            if not user_data:
                logger.warning(f"Utilisateur non trouvé: {payload['sub']}")
                return None
                
            # 5. Construire l'objet utilisateur
            return IrisUser(
                id=user_data['id'],
                email=user_data['email'],
                tier=self._determine_user_tier(user_data),
                email_verified=user_data.get('email_confirmed_at') is not None,
                status=user_data.get('status', 'active'),
                daily_usage=await self._get_daily_usage(user_data['id']),
                last_usage_date=datetime.now().strftime('%Y-%m-%d')
            )
            
        except jwt.ExpiredSignatureError:
            logger.info("Token JWT expiré")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token JWT invalide: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur vérification token: {e}")
            return None
    
    async def _get_user_data(self, user_id: str) -> Optional[Dict]:
        """Récupère les données utilisateur depuis Supabase"""
        try:
            # Essai direct sur auth.users
            response = self.supabase.auth.admin.get_user_by_id(user_id)
            if response.user:
                return {
                    'id': response.user.id,
                    'email': response.user.email,
                    'email_confirmed_at': response.user.email_confirmed_at,
                    'status': 'active'  # Supabase users are active by default
                }
        except Exception as e:
            logger.warning(f"Auth admin API failed: {e}")
            
        # Fallback: tentative sur une table users personnalisée
        try:
            result = self.supabase.table('users').select('*').eq('id', user_id).single().execute()
            if result.data:
                return result.data
        except Exception as e:
            logger.warning(f"Users table fallback failed: {e}")
            
        return None
    
    def _determine_user_tier(self, user_data: Dict) -> UserTier:
        """Détermine le tier de l'utilisateur"""
        # Logique de détermination du tier
        # Peut être basée sur subscription, metadata, etc.
        
        # Vérifier s'il y a des métadonnées de subscription
        metadata = user_data.get('user_metadata', {}) or user_data.get('raw_user_meta_data', {})
        
        if metadata.get('tier') == 'ENTERPRISE':
            return UserTier.ENTERPRISE
        elif metadata.get('tier') == 'PREMIUM' or metadata.get('subscription') == 'premium':
            return UserTier.PREMIUM
        
        # Fallback sur table subscriptions si elle existe
        try:
            sub_result = self.supabase.table('user_subscriptions').select('current_tier').eq('user_id', user_data['id']).single().execute()
            if sub_result.data:
                tier_value = sub_result.data.get('current_tier', 'FREE')
                return UserTier(tier_value)
        except:
            pass
            
        return UserTier.FREE
    
    async def _get_daily_usage(self, user_id: str) -> int:
        """Récupère l'usage quotidien de l'utilisateur"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Tenter de récupérer depuis une table d'usage
            result = self.supabase.table('iris_usage').select('message_count').eq('user_id', user_id).eq('date', today).single().execute()
            
            if result.data:
                return result.data.get('message_count', 0)
        except:
            pass
            
        return 0
    
    async def increment_usage(self, user_id: str) -> bool:
        """Incrémente l'usage quotidien de l'utilisateur"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Upsert dans la table d'usage
            self.supabase.table('iris_usage').upsert({
                'user_id': user_id,
                'date': today,
                'message_count': 1
            }, on_conflict='user_id,date').execute()
            
            return True
        except Exception as e:
            logger.error(f"Erreur incrémentation usage: {e}")
            return False
    
    def check_rate_limit(self, user: IrisUser) -> bool:
        """Vérifie si l'utilisateur peut faire une requête"""
        limits = self.rate_limits[user.tier]
        daily_limit = limits["daily_messages"]
        
        # -1 = illimité
        if daily_limit == -1:
            return True
            
        return user.daily_usage < daily_limit
    
    def check_access_permissions(self, user: IrisUser) -> bool:
        """Vérifie les permissions d'accès à Iris"""
        
        # 1. Email doit être vérifié
        if not user.email_verified:
            logger.info(f"Accès refusé - email non vérifié: {user.email}")
            return False
            
        # 2. Compte doit être actif
        if user.status != 'active':
            logger.info(f"Accès refusé - compte inactif: {user.email}")
            return False
            
        # 3. Vérifier les limites de taux
        if not self.check_rate_limit(user):
            logger.info(f"Accès refusé - limite quotidienne atteinte: {user.email}")
            return False
            
        return True

# Instance globale
auth_service = PhoenixAuthStandalone()

# Security scheme pour FastAPI
security = HTTPBearer()

async def get_authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> IrisUser:
    """
    Dependency FastAPI pour récupérer l'utilisateur authentifié
    
    Usage:
        @app.post("/protected")
        async def protected_route(user: IrisUser = Depends(get_authenticated_user)):
            return {"user_id": user.id}
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Token d'authentification requis")
    
    user = await auth_service.verify_token(credentials.credentials)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    
    # Vérification des permissions d'accès
    if not auth_service.check_access_permissions(user):
        raise HTTPException(
            status_code=403,
            detail="Accès refusé. Vérifiez votre email, le statut de votre compte ou vos limites d'usage."
        )
    
    return user

async def get_optional_authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[IrisUser]:
    """
    Dependency FastAPI pour récupérer l'utilisateur de façon optionnelle
    """
    if not credentials:
        return None
        
    try:
        return await get_authenticated_user(credentials)
    except HTTPException:
        return None

def require_tier(required_tier: UserTier):
    """
    Décorateur pour restreindre l'accès selon le tier utilisateur
    
    Usage:
        @app.post("/enterprise-feature")
        async def enterprise_only(user: IrisUser = Depends(require_tier(UserTier.ENTERPRISE))):
            return {"feature": "advanced"}
    """
    async def check_tier(user: IrisUser = Depends(get_authenticated_user)) -> IrisUser:
        tier_hierarchy = {UserTier.FREE: 0, UserTier.PREMIUM: 1, UserTier.ENTERPRISE: 2}
        
        if tier_hierarchy[user.tier] < tier_hierarchy[required_tier]:
            raise HTTPException(
                status_code=403,
                detail=f"Cette fonctionnalité nécessite un abonnement {required_tier.value}"
            )
        
        return user
    
    return check_tier