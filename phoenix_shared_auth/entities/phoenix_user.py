"""
🚀 Phoenix User Entity - Entité utilisateur unifiée pour l'écosystème Phoenix
Support multi-applications avec gestion granulaire des permissions
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
    """Permissions par application"""

    READ = "read"
    WRITE = "write"
    PREMIUM_FEATURES = "premium_features"
    ADMIN = "admin"


@dataclass
class AppUsageStats:
    """Statistiques d'utilisation par application"""

    app: PhoenixApp
    letters_generated: int = 0
    cvs_created: int = 0
    coaching_sessions: int = 0
    last_activity: Optional[datetime] = None
    premium_features_used: int = 0


@dataclass
class PhoenixSubscription:
    """Abonnement Phoenix global"""

    current_tier: UserTier = UserTier.FREE
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    auto_renewal: bool = False
    enabled_apps: Set[PhoenixApp] = field(
        default_factory=lambda: {PhoenixApp.LETTERS, PhoenixApp.CV}
    )
    permissions: Dict[PhoenixApp, Set[AppPermission]] = field(default_factory=dict)

    def __post_init__(self):
        """Initialise les permissions par défaut"""
        if not self.permissions:
            for app in self.enabled_apps:
                if self.current_tier == UserTier.FREE:
                    self.permissions[app] = {AppPermission.READ, AppPermission.WRITE}
                else:
                    self.permissions[app] = {
                        AppPermission.READ,
                        AppPermission.WRITE,
                        AppPermission.PREMIUM_FEATURES,
                    }


@dataclass
class PhoenixUser:
    """Utilisateur unifié Phoenix avec support multi-applications"""

    id: uuid.UUID
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    # Statut et vérification
    status: str = "pending"  # pending, active, suspended
    email_verified: bool = False
    newsletter_opt_in: bool = False

    # Dates importantes
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # Abonnement et permissions
    subscription: PhoenixSubscription = field(default_factory=PhoenixSubscription)

    # Statistiques d'utilisation par app
    app_stats: Dict[PhoenixApp, AppUsageStats] = field(default_factory=dict)

    # Préférences utilisateur
    preferences: Dict[str, any] = field(default_factory=dict)

    def has_permission(self, app: PhoenixApp, permission: AppPermission) -> bool:
        """Vérifie si l'utilisateur a une permission spécifique pour une app"""
        return (
            app in self.subscription.permissions
            and permission in self.subscription.permissions[app]
        )

    def can_access_app(self, app: PhoenixApp) -> bool:
        """Vérifie si l'utilisateur peut accéder à une application"""
        return app in self.subscription.enabled_apps

    def get_app_stats(self, app: PhoenixApp) -> AppUsageStats:
        """Récupère les statistiques d'utilisation pour une app"""
        if app not in self.app_stats:
            self.app_stats[app] = AppUsageStats(app=app)
        return self.app_stats[app]

    def update_last_activity(self, app: PhoenixApp):
        """Met à jour la dernière activité pour une app"""
        stats = self.get_app_stats(app)
        stats.last_activity = datetime.utcnow()
        self.last_login = datetime.utcnow()

    @property
    def display_name(self) -> str:
        """Nom d'affichage de l'utilisateur"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.username:
            return self.username
        else:
            return self.email.split("@")[0]

    @property
    def is_premium(self) -> bool:
        """Vérifie si l'utilisateur a un abonnement premium"""
        return self.subscription.current_tier in [
            UserTier.PREMIUM,
            UserTier.PREMIUM_PLUS,
        ]
