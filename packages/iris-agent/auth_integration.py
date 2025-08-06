"""
🔐 IRIS AUTH INTEGRATION - Intégration avec le système d'authentification Phoenix Letters
Module responsable de l'authentification et autorisation pour l'agent Iris.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import du système Phoenix Letters (adapter le path selon l'architecture)
# En production, ceci devrait être via un package partagé ou API
sys.path.append('/Users/mattvaness/Desktop/IA/phoenix/phoenix-eco-monorepo/apps/phoenix-letters')

try:
    from infrastructure.auth.jwt_manager import JWTManager
    from infrastructure.auth.user_auth_service import UserAuthService
    from infrastructure.database.db_connection import DatabaseConnection
    from config.settings import Settings
    from core.entities.user import User, UserTier
except ImportError as e:
    logging.error(f"Impossible d'importer les modules Phoenix Letters: {e}")
    # Fallback mode pour développement
    User = None
    UserTier = None

logger = logging.getLogger(__name__)

# Security scheme pour FastAPI
security = HTTPBearer()

class IrisAuthManager:
    """
    Gestionnaire d'authentification pour l'agent Iris.
    Interface avec le système d'auth Phoenix Letters.
    """
    
    def __init__(self):
        self.settings = self._load_settings()
        self.jwt_manager = None
        self.user_service = None
        self._initialize_services()
    
    def _load_settings(self) -> Optional[Any]:
        """Charge les paramètres Phoenix Letters"""
        try:
            settings = Settings()
            return settings
        except Exception as e:
            logger.error(f"Impossible de charger les settings Phoenix: {e}")
            return None
    
    def _initialize_services(self):
        """Initialise les services d'authentification Phoenix"""
        if not self.settings:
            logger.warning("Mode dégradé: services d'auth non disponibles")
            return
        
        try:
            db_connection = DatabaseConnection()
            self.jwt_manager = JWTManager(self.settings)
            self.user_service = UserAuthService(self.jwt_manager, db_connection)
            logger.info("Services d'authentification Phoenix initialisés")
        except Exception as e:
            logger.error(f"Erreur initialisation services auth: {e}")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Vérifie la validité d'un token JWT Phoenix Letters.
        
        Returns:
            Dict contenant les infos utilisateur ou None si invalide
        """
        if not self.jwt_manager:
            logger.warning("JWT Manager non disponible")
            return None
        
        try:
            payload = self.jwt_manager.decode_token(token)
            if not payload:
                return None
            
            # Vérification de l'expiration
            exp = payload.get('exp')
            if exp and datetime.utcnow().timestamp() > exp:
                logger.info("Token expiré")
                return None
            
            # Vérification du type de token
            token_type = payload.get('type')
            if token_type != 'access':
                logger.warning(f"Type de token invalide: {token_type}")
                return None
            
            return payload
        except Exception as e:
            logger.error(f"Erreur vérification token: {e}")
            return None
    
    def get_user_from_token(self, token: str) -> Optional[Any]:
        """
        Récupère l'utilisateur complet à partir d'un token.
        
        Returns:
            Objet User Phoenix Letters ou None
        """
        payload = self.verify_token(token)
        if not payload or not self.user_service:
            return None
        
        user_id = payload.get('sub')
        if not user_id:
            return None
        
        try:
            user = self.user_service.get_user_by_id(user_id)
            return user
        except Exception as e:
            logger.error(f"Erreur récupération utilisateur: {e}")
            return None
    
    def check_iris_access_permission(self, user: Any) -> bool:
        """
        Vérifie si l'utilisateur a accès à l'agent Iris.
        
        Politique d'accès:
        - Utilisateurs FREE: 5 messages/jour
        - Utilisateurs PREMIUM: illimité
        - Utilisateurs ENTERPRISE: illimité + features avancées
        """
        if not user:
            return False
        
        try:
            # Accès basique pour tous les utilisateurs vérifiés
            if not user.email_verified:
                logger.info(f"Accès refusé - email non vérifié: {user.email}")
                return False
            
            # Vérification du statut du compte
            if user.status != 'active':
                logger.info(f"Accès refusé - compte inactif: {user.email}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Erreur vérification permissions: {e}")
            return False
    
    def get_user_tier_limits(self, user: Any) -> Dict[str, int]:
        """
        Retourne les limites d'utilisation selon le tier utilisateur.
        """
        if not user or not hasattr(user, 'subscription'):
            return {"daily_messages": 0, "context_retention_days": 0}
        
        tier_limits = {
            "FREE": {"daily_messages": 5, "context_retention_days": 1},
            "PREMIUM": {"daily_messages": 50, "context_retention_days": 7},
            "ENTERPRISE": {"daily_messages": -1, "context_retention_days": 30}  # -1 = illimité
        }
        
        user_tier = user.subscription.current_tier.value if user.subscription.current_tier else "FREE"
        return tier_limits.get(user_tier, tier_limits["FREE"])

# Instance globale du gestionnaire d'auth
auth_manager = IrisAuthManager()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Any:
    """
    Dependency FastAPI pour récupérer l'utilisateur authentifié.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"user_id": str(user.id)}
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Token d'authentification requis")
    
    token = credentials.credentials
    user = auth_manager.get_user_from_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    
    # Vérification des permissions Iris
    if not auth_manager.check_iris_access_permission(user):
        raise HTTPException(
            status_code=403, 
            detail="Accès à Iris refusé. Vérifiez votre email ou le statut de votre compte."
        )
    
    return user

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Any]:
    """
    Dependency FastAPI pour récupérer l'utilisateur si présent (optionnel).
    Utilisé pour les endpoints qui fonctionnent avec ou sans auth.
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None

def check_daily_limit(user: Any, current_usage: int) -> bool:
    """
    Vérifie si l'utilisateur a atteint sa limite quotidienne.
    """
    limits = auth_manager.get_user_tier_limits(user)
    daily_limit = limits["daily_messages"]
    
    # -1 signifie illimité
    if daily_limit == -1:
        return True
    
    return current_usage < daily_limit