"""
Dépendances FastAPI pour injection et sécurité
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from ..services.ia_validator import IAFutureValidator
from ..utils.mock_providers import MockEventStore, MockResearchProvider

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Global instances (à améliorer avec DI container)
_ia_validator_instance = None

def get_ia_validator() -> IAFutureValidator:
    """
    Dependency injection pour IAFutureValidator
    """
    global _ia_validator_instance
    
    if _ia_validator_instance is None:
        # Initialize avec mock providers pour MVP
        event_store = MockEventStore()
        research_provider = MockResearchProvider()
        _ia_validator_instance = IAFutureValidator(event_store, research_provider)
        logger.info("IAFutureValidator instance créée")
    
    return _ia_validator_instance

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Authentification utilisateur (mock pour MVP)
    TODO: Implémenter vraie authentification
    """
    try:
        # Mock authentication - à remplacer par JWT/OAuth
        if not credentials.credentials or credentials.credentials == "invalid":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Mock user data
        mock_user = {
            "user_id": "user_" + credentials.credentials[:8],
            "email": f"user@phoenix-aube.com",
            "subscription": "premium",  # "free", "premium"
            "permissions": ["read", "analyze", "explore"]
        }
        
        return mock_user
        
    except Exception as e:
        logger.error(f"Erreur authentification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Vérification droits administrateur
    """
    if "admin" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

async def get_premium_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Vérification abonnement premium
    """
    if current_user.get("subscription") != "premium":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Premium subscription required for this feature"
        )
    
    return current_user

def validate_job_title(job_title: str) -> str:
    """
    Validation et normalisation du titre de métier
    """
    if not job_title or len(job_title.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job title must be at least 2 characters long"
        )
    
    # Normalisation basique
    normalized = job_title.strip().title()
    
    # Validation longueur
    if len(normalized) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job title too long (max 100 characters)"
        )
    
    return normalized

def validate_sector_name(sector: str) -> str:
    """
    Validation nom de secteur
    """
    valid_sectors = [
        "Tech", "Finance", "Santé", "Éducation", "Marketing",
        "RH", "Industrie", "Services", "Commerce", "Immobilier",
        "Consulting", "Créatif", "Communication"
    ]
    
    if sector not in valid_sectors:
        # Mode permissif pour MVP - log warning mais accepte
        logger.warning(f"Secteur non validé: {sector}")
    
    return sector