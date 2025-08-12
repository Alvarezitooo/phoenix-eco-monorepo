"""
Router Authentication - Phoenix Backend Unifié
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

from services.auth_service import AuthService
from services.supabase_client import SupabaseClient

router = APIRouter()
security = HTTPBearer()

# Schemas Pydantic
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    isPremium: bool
    subscription_tier: str

# Dépendances
async def get_auth_service() -> AuthService:
    """Dependency pour récupérer le service d'auth"""
    from main import auth_service
    if not auth_service:
        raise HTTPException(
            status_code=500,
            detail="Auth service not initialized"
        )
    return auth_service

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Dependency pour récupérer l'utilisateur actuel"""
    token = credentials.credentials
    user = await auth_service.get_current_user_from_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Routes
@router.post("/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Connexion utilisateur avec email/password"""
    user = await auth_service.authenticate_user(
        login_data.email, 
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # Créer le token JWT
    access_token = auth_service.create_access_token(
        data={"sub": user["id"], "email": user["email"]}
    )
    
    return LoginResponse(
        access_token=access_token,
        user=user
    )

@router.get("/auth/verify", response_model=UserResponse)
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Vérification du token et récupération des infos utilisateur"""
    return UserResponse(**current_user)

@router.post("/auth/logout")
async def logout():
    """Déconnexion (côté client principalement)"""
    return {"message": "Déconnexion réussie"}

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Informations sur l'utilisateur connecté"""
    return UserResponse(**current_user)