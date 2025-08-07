"""
Phoenix User Entity - Copie locale pour éviter les problèmes d'import
Entité utilisateur unifiée pour Phoenix CV
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set


class PhoenixApp(Enum):
    """Applications de l'écosystème Phoenix"""
    LETTERS = "letters"
    CV = "cv"
    RISE = "rise"
    SITE = "site"


class UserTier(Enum):
    """Niveaux d'abonnement utilisateur"""
    FREE = "free"
    PREMIUM = "premium"
    PREMIUM_PLUS = "premium_plus"


class AppPermission(Enum):
    """Permissions spécifiques par application"""
    # Phoenix Letters
    GENERATE_LETTER = "generate_letter"
    PREMIUM_TEMPLATES = "premium_templates"
    UNLIMITED_GENERATIONS = "unlimited_generations"
    
    # Phoenix CV
    GENERATE_CV = "generate_cv"
    ATS_OPTIMIZATION = "ats_optimization"
    PREMIUM_CV_TEMPLATES = "premium_cv_templates"
    
    # Phoenix Rise
    COACHING_ACCESS = "coaching_access"
    PREMIUM_COACHING = "premium_coaching"
    MOOD_TRACKING = "mood_tracking"
    
    # Cross-app
    CROSS_APP_DATA = "cross_app_data"
    IRIS_INTEGRATION = "iris_integration"


@dataclass
class PhoenixUser:
    """Utilisateur unifié Phoenix avec support multi-applications"""
    
    # Identification
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    email: str = ""
    username: Optional[str] = None
    
    # Profil
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    # Abonnement et permissions
    tier: UserTier = UserTier.FREE
    app_permissions: Dict[PhoenixApp, Set[AppPermission]] = field(default_factory=dict)
    
    # Données par application
    app_data: Dict[PhoenixApp, Dict] = field(default_factory=dict)
    
    # Métadonnées
    is_active: bool = True
    email_verified: bool = False
    
    # 🔬 RECHERCHE-ACTION PHOENIX - Consentement Éthique
    research_consent: bool = False  # Opt-in explicite pour contribution anonymisée à la recherche
    
    def has_permission(self, app: PhoenixApp, permission: AppPermission) -> bool:
        """Vérifie si l'utilisateur a une permission spécifique"""
        return permission in self.app_permissions.get(app, set())
    
    def is_premium(self) -> bool:
        """Vérifie si l'utilisateur a un abonnement premium"""
        return self.tier in [UserTier.PREMIUM, UserTier.PREMIUM_PLUS]