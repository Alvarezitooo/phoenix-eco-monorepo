"""
💰 Phoenix Subscription System - Gestion Abonnements Granulaires
Système d'abonnements différenciés par application Phoenix

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import json


class SubscriptionTier(Enum):
    """Tiers d'abonnement disponibles"""
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"


class PhoenixApp(Enum):
    """Applications Phoenix disponibles"""
    CV = "cv"
    LETTERS = "letters" 
    RISE = "rise"
    WEBSITE = "website"


class SubscriptionStatus(Enum):
    """Statut d'abonnement"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


@dataclass
class AppSubscriptionDetails:
    """Détails d'abonnement pour une application spécifique"""
    app: PhoenixApp
    tier: SubscriptionTier
    status: SubscriptionStatus
    stripe_subscription_id: Optional[str] = None
    stripe_price_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    trial_end: Optional[datetime] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def is_active(self) -> bool:
        """Vérifie si l'abonnement est actif"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
    
    def is_premium(self) -> bool:
        """Vérifie si l'abonnement est Premium ou Pro"""
        return self.tier in [SubscriptionTier.PREMIUM, SubscriptionTier.PRO] and self.is_active()
    
    def days_until_renewal(self) -> Optional[int]:
        """Calcule les jours jusqu'au renouvellement"""
        if self.current_period_end:
            delta = self.current_period_end - datetime.now()
            return max(0, delta.days)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "app": self.app.value,
            "tier": self.tier.value,
            "status": self.status.value,
            "stripe_subscription_id": self.stripe_subscription_id,
            "stripe_price_id": self.stripe_price_id,
            "current_period_start": self.current_period_start.isoformat() if self.current_period_start else None,
            "current_period_end": self.current_period_end.isoformat() if self.current_period_end else None,
            "cancel_at_period_end": self.cancel_at_period_end,
            "trial_end": self.trial_end.isoformat() if self.trial_end else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active(),
            "is_premium": self.is_premium(),
            "days_until_renewal": self.days_until_renewal()
        }


@dataclass
class PhoenixUserSubscription:
    """Gestion complète des abonnements utilisateur Phoenix"""
    user_id: str
    app_subscriptions: Dict[PhoenixApp, AppSubscriptionDetails] = field(default_factory=dict)
    global_subscription_id: Optional[str] = None  # ID global pour bundles
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialise les abonnements gratuits par défaut"""
        for app in PhoenixApp:
            if app not in self.app_subscriptions:
                self.app_subscriptions[app] = AppSubscriptionDetails(
                    app=app,
                    tier=SubscriptionTier.FREE,
                    status=SubscriptionStatus.ACTIVE
                )
    
    def get_app_subscription(self, app: PhoenixApp) -> AppSubscriptionDetails:
        """Récupère l'abonnement pour une application"""
        return self.app_subscriptions.get(app, AppSubscriptionDetails(
            app=app,
            tier=SubscriptionTier.FREE,
            status=SubscriptionStatus.ACTIVE
        ))
    
    def update_app_subscription(
        self, 
        app: PhoenixApp, 
        tier: SubscriptionTier,
        status: SubscriptionStatus,
        **kwargs
    ) -> bool:
        """Met à jour l'abonnement pour une application"""
        try:
            if app not in self.app_subscriptions:
                self.app_subscriptions[app] = AppSubscriptionDetails(
                    app=app,
                    tier=tier,
                    status=status
                )
            else:
                subscription = self.app_subscriptions[app]
                subscription.tier = tier
                subscription.status = status
                subscription.updated_at = datetime.now()
                
                # Mise à jour des champs additionnels
                for key, value in kwargs.items():
                    if hasattr(subscription, key):
                        setattr(subscription, key, value)
            
            self.updated_at = datetime.now()
            return True
            
        except Exception:
            return False
    
    def is_app_premium(self, app: PhoenixApp) -> bool:
        """Vérifie si l'utilisateur a un abonnement Premium pour une app"""
        subscription = self.get_app_subscription(app)
        return subscription.is_premium()
    
    def get_premium_apps(self) -> List[PhoenixApp]:
        """Retourne la liste des apps avec abonnement Premium"""
        return [
            app for app, subscription in self.app_subscriptions.items()
            if subscription.is_premium()
        ]
    
    def has_pack_cv_letters(self) -> bool:
        """Vérifie si l'utilisateur a le pack CV + Letters"""
        cv_premium = self.is_app_premium(PhoenixApp.CV)
        letters_premium = self.is_app_premium(PhoenixApp.LETTERS)
        
        # Vérifier si les deux abonnements ont le même stripe_subscription_id (indicateur de pack)
        if cv_premium and letters_premium:
            cv_sub = self.get_app_subscription(PhoenixApp.CV)
            letters_sub = self.get_app_subscription(PhoenixApp.LETTERS)
            
            return (cv_sub.stripe_subscription_id == letters_sub.stripe_subscription_id 
                    and cv_sub.stripe_subscription_id is not None)
        
        return False
    
    def get_package_type(self) -> PackageType:
        """Détermine le type de package de l'utilisateur"""
        premium_apps = self.get_premium_apps()
        
        if len(premium_apps) == 0:
            return PackageType.SINGLE_APP  # Gratuit
        elif self.has_pack_cv_letters():
            return PackageType.PACK_CV_LETTERS
        elif len(premium_apps) >= 3:
            return PackageType.ALL_APPS
        else:
            return PackageType.SINGLE_APP
    
    def activate_pack_cv_letters(self, stripe_subscription_id: str, **kwargs) -> bool:
        """Active le pack CV + Letters avec un seul ID Stripe"""
        try:
            # Activer Premium sur CV et Letters avec le même stripe_subscription_id
            cv_success = self.update_app_subscription(
                PhoenixApp.CV,
                SubscriptionTier.PREMIUM,
                SubscriptionStatus.ACTIVE,
                stripe_subscription_id=stripe_subscription_id,
                stripe_price_id=BUNDLE_PRICE_IDS["phoenix_pack_cv_letters"],
                **kwargs
            )
            
            letters_success = self.update_app_subscription(
                PhoenixApp.LETTERS,
                SubscriptionTier.PREMIUM,
                SubscriptionStatus.ACTIVE,
                stripe_subscription_id=stripe_subscription_id,
                stripe_price_id=BUNDLE_PRICE_IDS["phoenix_pack_cv_letters"],
                **kwargs
            )
            
            if cv_success and letters_success:
                # Marquer comme pack dans les métadonnées
                self.global_subscription_id = stripe_subscription_id
                return True
            
            return False
            
        except Exception:
            return False
    
    def get_subscription_summary(self) -> Dict[str, Any]:
        """Résumé des abonnements utilisateur"""
        premium_apps = self.get_premium_apps()
        package_type = self.get_package_type()
        
        return {
            "user_id": self.user_id,
            "total_apps": len(self.app_subscriptions),
            "premium_apps_count": len(premium_apps),
            "premium_apps": [app.value for app in premium_apps],
            "package_type": package_type.value,
            "has_pack_cv_letters": self.has_pack_cv_letters(),
            "subscriptions": {
                app.value: subscription.to_dict() 
                for app, subscription in self.app_subscriptions.items()
            },
            "has_any_premium": len(premium_apps) > 0,
            "is_fully_premium": len(premium_apps) == len([app for app in PhoenixApp if app != PhoenixApp.WEBSITE]),
            "global_subscription_id": self.global_subscription_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "subscription_display": self._get_subscription_display_info()
        }
    
    def _get_subscription_display_info(self) -> Dict[str, Any]:
        """Informations d'affichage pour l'interface utilisateur"""
        package_type = self.get_package_type()
        premium_apps = self.get_premium_apps()
        
        if package_type == PackageType.PACK_CV_LETTERS:
            return {
                "title": "Pack Phoenix CV + Letters",
                "badge": "PACK PREMIUM",
                "description": "Accès complet à Phoenix CV et Phoenix Letters",
                "color": "#f97316",
                "icon": "🔥",
                "apps_included": ["CV", "Letters"]
            }
        elif len(premium_apps) == 1:
            app = premium_apps[0]
            app_names = {"cv": "Phoenix CV", "letters": "Phoenix Letters", "rise": "Phoenix Rise"}
            return {
                "title": f"{app_names.get(app.value, app.value)} Premium",
                "badge": "PREMIUM",
                "description": f"Accès premium à {app_names.get(app.value, app.value)}",
                "color": "#ef4444",
                "icon": "⭐",
                "apps_included": [app.value.upper()]
            }
        elif len(premium_apps) > 2:
            return {
                "title": "Phoenix Écosystème Complet",
                "badge": "PREMIUM MAX",
                "description": "Accès premium à toutes les applications Phoenix",
                "color": "#8b5cf6",
                "icon": "👑",
                "apps_included": [app.value.upper() for app in premium_apps]
            }
        else:
            return {
                "title": "Phoenix Gratuit",
                "badge": "GRATUIT",
                "description": "Accès aux fonctionnalités de base",
                "color": "#6b7280",
                "icon": "🆓",
                "apps_included": []
            }
    
    def get_app_features(self, app: PhoenixApp) -> Dict[str, Any]:
        """Retourne les fonctionnalités disponibles pour une app"""
        subscription = self.get_app_subscription(app)
        
        # Fonctionnalités par app et tier
        app_features = {
            PhoenixApp.CV: {
                SubscriptionTier.FREE: {
                    "cv_count_monthly": 3,
                    "templates_count": 5,
                    "ats_optimization": False,
                    "mirror_match": False,
                    "premium_templates": False,
                    "trajectory_builder": False,
                    "smart_coach_advanced": False,
                    "export_formats": ["PDF"],
                    "support_level": "email"
                },
                SubscriptionTier.PREMIUM: {
                    "cv_count_monthly": -1,  # illimité
                    "templates_count": 20,
                    "ats_optimization": True,
                    "mirror_match": True,
                    "premium_templates": True,
                    "trajectory_builder": True,
                    "smart_coach_advanced": True,
                    "export_formats": ["PDF", "DOCX", "HTML"],
                    "support_level": "priority"
                }
            },
            PhoenixApp.LETTERS: {
                SubscriptionTier.FREE: {
                    "letters_count_monthly": 5,
                    "templates_count": 3,
                    "ai_optimization": "basic",
                    "job_analysis": False,
                    "premium_prompts": False,
                    "batch_generation": False,
                    "export_formats": ["TXT"],
                    "support_level": "email"
                },
                SubscriptionTier.PREMIUM: {
                    "letters_count_monthly": -1,  # illimité
                    "templates_count": 15,
                    "ai_optimization": "advanced",
                    "job_analysis": True,
                    "premium_prompts": True,
                    "batch_generation": True,
                    "export_formats": ["TXT", "PDF", "DOCX"],
                    "support_level": "priority"
                }
            },
            PhoenixApp.RISE: {
                SubscriptionTier.FREE: {
                    "coaching_sessions_monthly": 2,
                    "meditation_count": 10,
                    "premium_content": False,
                    "personalized_roadmap": False,
                    "community_access": "limited",
                    "support_level": "email"
                },
                SubscriptionTier.PREMIUM: {
                    "coaching_sessions_monthly": -1,
                    "meditation_count": -1,
                    "premium_content": True,
                    "personalized_roadmap": True,
                    "community_access": "full",
                    "support_level": "priority"
                }
            }
        }
        
        base_features = app_features.get(app, {}).get(subscription.tier, {})
        
        # Ajouter informations d'abonnement
        return {
            **base_features,
            "subscription_tier": subscription.tier.value,
            "subscription_status": subscription.status.value,
            "is_active": subscription.is_active(),
            "is_premium": subscription.is_premium(),
            "days_until_renewal": subscription.days_until_renewal(),
            "stripe_subscription_id": subscription.stripe_subscription_id
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire complet"""
        return {
            "user_id": self.user_id,
            "app_subscriptions": {
                app.value: subscription.to_dict()
                for app, subscription in self.app_subscriptions.items()
            },
            "global_subscription_id": self.global_subscription_id,
            "summary": self.get_subscription_summary(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhoenixUserSubscription':
        """Créé depuis un dictionnaire"""
        user_subscription = cls(
            user_id=data.get("user_id"),
            global_subscription_id=data.get("global_subscription_id")
        )
        
        # Reconstituer les abonnements par app
        app_subscriptions_data = data.get("app_subscriptions", {})
        for app_name, sub_data in app_subscriptions_data.items():
            try:
                app = PhoenixApp(app_name)
                subscription = AppSubscriptionDetails(
                    app=app,
                    tier=SubscriptionTier(sub_data.get("tier", "free")),
                    status=SubscriptionStatus(sub_data.get("status", "active")),
                    stripe_subscription_id=sub_data.get("stripe_subscription_id"),
                    stripe_price_id=sub_data.get("stripe_price_id"),
                    current_period_start=datetime.fromisoformat(sub_data["current_period_start"]) if sub_data.get("current_period_start") else None,
                    current_period_end=datetime.fromisoformat(sub_data["current_period_end"]) if sub_data.get("current_period_end") else None,
                    cancel_at_period_end=sub_data.get("cancel_at_period_end", False),
                    trial_end=datetime.fromisoformat(sub_data["trial_end"]) if sub_data.get("trial_end") else None
                )
                user_subscription.app_subscriptions[app] = subscription
            except (ValueError, KeyError):
                continue
        
        return user_subscription


# Prix Stripe par application (IDs de production réels)
STRIPE_PRICE_IDS = {
    PhoenixApp.CV: {
        SubscriptionTier.PREMIUM: "price_1RraUoDcM3VIYgvy0NXiKmKV",  # Phoenix CV Premium
        SubscriptionTier.PRO: "price_cv_pro_monthly"
    },
    PhoenixApp.LETTERS: {
        SubscriptionTier.PREMIUM: "price_1RraAcDcM3VIYgvyEBNFXfbR",  # Phoenix Letters Premium
        SubscriptionTier.PRO: "price_letters_pro_monthly"
    },
    PhoenixApp.RISE: {
        SubscriptionTier.PREMIUM: "price_rise_premium_monthly",
        SubscriptionTier.PRO: "price_rise_pro_monthly"
    }
}

# Bundles (abonnements combinés avec réduction)
BUNDLE_PRICE_IDS = {
    "phoenix_pack_cv_letters": "price_1RraWhDcM3VIYgvyGykPghCc",  # Pack CV + Letters Premium
    "phoenix_trio_all_apps": "price_bundle_all_apps_monthly"
}

# Clé publique Stripe (production)
STRIPE_PUBLISHABLE_KEY = "pk_live_51RrZGNDcM3VIYgvyvNDVGUCRzqBv0gn23jVS82xNTnJxwSO2hOVxzWAazgRp6oaGubVcgE0iYlnw4kfMlJYSdwEK00NWdVHGM8"

class PackageType(Enum):
    """Types de packages disponibles"""
    SINGLE_APP = "single_app"           # Abonnement à une seule app
    PACK_CV_LETTERS = "pack_cv_letters" # Pack CV + Letters
    ALL_APPS = "all_apps"               # Toutes les applications