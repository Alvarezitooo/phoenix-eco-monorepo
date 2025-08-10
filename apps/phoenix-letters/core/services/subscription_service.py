"""
🔥 Phoenix Letters - Subscription Management Service
Gestion complète des abonnements avec synchronisation Stripe/Supabase

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from config.settings import Settings
from core.entities.user import UserTier
from infrastructure.payment.stripe_service import StripeService, PaymentSession
from infrastructure.database.db_connection import DatabaseConnection
from shared.exceptions.specific_exceptions import SubscriptionError, DatabaseError
from infrastructure.security.input_validator import InputValidator

logger = logging.getLogger(__name__)


class SubscriptionStatus(Enum):
    """Statuts d'abonnement Phoenix."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    EXPIRED = "expired"


@dataclass
class UserSubscription:
    """Modèle d'abonnement utilisateur."""
    user_id: str
    current_tier: UserTier
    subscription_id: Optional[str] = None
    customer_id: Optional[str] = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    auto_renewal: bool = False
    payment_method: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SubscriptionService:
    """
    Service de gestion des abonnements Phoenix Letters.
    Orchestre Stripe et Supabase pour une expérience utilisateur fluide.
    """
    
    def __init__(
        self, 
        settings: Settings, 
        stripe_service: StripeService,
        db_connection: DatabaseConnection,
        input_validator: InputValidator
    ):
        self.settings = settings
        self.stripe_service = stripe_service
        self.db = db_connection
        self.validator = input_validator
        
        # Limites par tier
        self.tier_limits = {
            UserTier.FREE: {
                "letters_per_month": 3,
                "features": ["basic_generation", "simple_templates"]
            },
            UserTier.PREMIUM: {
                "letters_per_month": 50,
                "features": [
                    "advanced_generation", "ats_analysis", "mirror_match", 
                    "smart_coach", "premium_templates", "pdf_export"
                ]
            },
        }
        
        logger.info("Service d'abonnement initialisé")

    async def create_subscription_checkout(
        self, 
        user_id: str, 
        plan_id: str,
        success_url: str,
        cancel_url: str,
        user_email: Optional[str] = None
    ) -> PaymentSession:
        """
        Crée une session de checkout pour un nouvel abonnement.
        
        Args:
            user_id: ID utilisateur Phoenix
            plan_id: ID du plan (premium, premium_plus)
            success_url: URL de redirection succès
            cancel_url: URL d'annulation
            user_email: Email utilisateur
            
        Returns:
            PaymentSession avec URL de checkout
        """
        try:
            # Validation utilisateur
            if not self.validator.validate_uuid(user_id):
                raise SubscriptionError("ID utilisateur invalide")
                
            # Vérification qu'il n'a pas déjà un abonnement actif
            current_subscription = await self.get_user_subscription(user_id)
            if current_subscription and current_subscription.current_tier != UserTier.FREE:
                raise SubscriptionError("Utilisateur possède déjà un abonnement actif")
                
            # Création de la session Stripe
            payment_session = self.stripe_service.create_checkout_session(
                user_id=user_id,
                plan_id=plan_id,
                success_url=success_url,
                cancel_url=cancel_url,
                user_email=user_email
            )
            
            # Enregistrement de la session en attente
            await self._record_pending_subscription(user_id, plan_id, payment_session)
            
            logger.info(f"Session checkout créée pour user {user_id}, plan {plan_id}")
            return payment_session
            
        except Exception as e:
            logger.error(f"Erreur création checkout: {e}")
            raise SubscriptionError(f"Impossible de créer la session: {e}")

    async def handle_subscription_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Traite les webhooks Stripe pour synchroniser les abonnements.
        
        Args:
            webhook_data: Données du webhook Stripe
            
        Returns:
            True si traitement réussi
        """
        try:
            status = webhook_data.get("status")
            phoenix_user_id = webhook_data.get("phoenix_user_id")
            
            if not phoenix_user_id:
                logger.warning("Webhook sans phoenix_user_id, ignoré")
                return False
                
            if status == "checkout_completed":
                await self._handle_checkout_completed(webhook_data)
            elif status == "subscription_created":
                await self._handle_subscription_created(webhook_data)
            elif status == "subscription_updated":
                await self._handle_subscription_updated(webhook_data)
            elif status == "subscription_deleted":
                await self._handle_subscription_deleted(webhook_data)
            elif status == "payment_succeeded":
                await self._handle_payment_succeeded(webhook_data)
            elif status == "payment_failed":
                await self._handle_payment_failed(webhook_data)
            else:
                logger.info(f"Webhook status non traité: {status}")
                
            return True
            
        except Exception as e:
            logger.error(f"Erreur traitement webhook: {e}")
            raise SubscriptionError(f"Erreur webhook: {e}")

    async def get_user_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """
        Récupère l'abonnement actuel d'un utilisateur.
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            UserSubscription ou None
        """
        try:
            client = self.db.get_client()
            
            response = client.table("user_subscriptions").select("*").eq("user_id", user_id).execute()
            
            if not response.data:
                return None
                
            data = response.data[0]
            
            return UserSubscription(
                user_id=data["user_id"],
                current_tier=UserTier(data["current_tier"]),
                subscription_id=data.get("subscription_id"),
                customer_id=data.get("stripe_customer_id"),
                status=SubscriptionStatus(data.get("status", "active")),
                subscription_start=self._parse_datetime(data.get("subscription_start")),
                subscription_end=self._parse_datetime(data.get("subscription_end")),
                auto_renewal=data.get("auto_renewal", False),
                payment_method=data.get("payment_method"),
                last_payment_date=self._parse_datetime(data.get("last_payment_date")),
                created_at=self._parse_datetime(data.get("created_at")),
                updated_at=self._parse_datetime(data.get("updated_at"))
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération abonnement user {user_id}: {e}")
            raise DatabaseError(f"Impossible de récupérer l'abonnement: {e}")

    async def upgrade_user_tier(
        self, 
        user_id: str, 
        new_tier: UserTier,
        subscription_id: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> bool:
        """
        Met à niveau le tier d'un utilisateur.
        
        Args:
            user_id: ID utilisateur
            new_tier: Nouveau tier
            subscription_id: ID abonnement Stripe (optionnel)
            customer_id: ID customer Stripe (optionnel)
            
        Returns:
            True si succès
        """
        try:
            client = self.db.get_client()
            
            subscription_data = {
                "current_tier": new_tier.value,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if new_tier != UserTier.FREE:
                subscription_data["subscription_start"] = datetime.now(timezone.utc).isoformat()
                subscription_data["subscription_end"] = (
                    datetime.now(timezone.utc) + timedelta(days=30)
                ).isoformat()
                subscription_data["auto_renewal"] = True
                
            if subscription_id:
                subscription_data["subscription_id"] = subscription_id
                
            if customer_id:
                subscription_data["stripe_customer_id"] = customer_id
                
            # Upsert dans user_subscriptions
            response = client.table("user_subscriptions").upsert(
                {**subscription_data, "user_id": user_id}
            ).execute()
            
            # Mise à jour des stats utilisateur
            await self._update_user_stats_on_tier_change(user_id, new_tier)
            
            logger.info(f"Tier utilisateur {user_id} mis à jour vers {new_tier.value}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur upgrade tier user {user_id}: {e}")
            raise DatabaseError(f"Impossible de mettre à jour le tier: {e}")

    async def cancel_subscription(self, user_id: str) -> bool:
        """
        Annule l'abonnement d'un utilisateur.
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            True si annulation réussie
        """
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription or subscription.current_tier == UserTier.FREE:
                raise SubscriptionError("Aucun abonnement actif à annuler")
                
            # Annulation côté Stripe
            if subscription.subscription_id:
                self.stripe_service.cancel_subscription(subscription.subscription_id)
                
            # Mise à jour en base
            client = self.db.get_client()
            client.table("user_subscriptions").update({
                "auto_renewal": False,
                "status": SubscriptionStatus.CANCELLED.value,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("user_id", user_id).execute()
            
            logger.info(f"Abonnement utilisateur {user_id} annulé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur annulation abonnement user {user_id}: {e}")
            raise SubscriptionError(f"Impossible d'annuler l'abonnement: {e}")

    async def check_usage_limits(self, user_id: str, action: str) -> bool:
        """
        Vérifie si l'utilisateur peut effectuer une action selon ses limites.
        
        Args:
            user_id: ID utilisateur
            action: Action à vérifier (letters_generation, etc.)
            
        Returns:
            True si action autorisée
        """
        try:
            subscription = await self.get_user_subscription(user_id)
            tier = subscription.current_tier if subscription else UserTier.FREE
            
            if action == "letters_generation":
                return await self._check_letters_limit(user_id, tier)
            elif action in self.tier_limits[tier]["features"]:
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Erreur vérification limites user {user_id}: {e}")
            return False

    async def get_user_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère les statistiques d'usage d'un utilisateur.
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            Dict avec statistiques d'usage
        """
        try:
            client = self.db.get_client()
            
            response = client.table("user_usage_stats").select("*").eq("user_id", user_id).execute()
            
            if not response.data:
                return {
                    "letters_generated": 0,
                    "letters_generated_this_month": 0,
                    "total_sessions": 0,
                    "premium_features_used": 0
                }
                
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Erreur récupération stats user {user_id}: {e}")
            return {}

    # Méthodes privées

    async def _record_pending_subscription(
        self, 
        user_id: str, 
        plan_id: str, 
        payment_session: PaymentSession
    ):
        """Enregistre une session de paiement en attente."""
        # Implementation pour tracker les sessions en cours
        pass

    async def _handle_checkout_completed(self, webhook_data: Dict[str, Any]):
        """Traite la completion d'un checkout."""
        user_id = webhook_data.get("phoenix_user_id")
        plan_id = webhook_data.get("plan_id")
        customer_id = webhook_data.get("customer_id")
        subscription_id = webhook_data.get("subscription_id")
        
        # Mapping plan_id vers UserTier
        tier_mapping = {
            "premium": UserTier.PREMIUM
        }
        
        new_tier = tier_mapping.get(plan_id, UserTier.FREE)
        
        await self.upgrade_user_tier(
            user_id=user_id,
            new_tier=new_tier,
            subscription_id=subscription_id,
            customer_id=customer_id
        )

    async def _handle_subscription_created(self, webhook_data: Dict[str, Any]):
        """Traite la création d'un abonnement."""
        # Déjà géré dans checkout_completed
        pass

    async def _handle_subscription_updated(self, webhook_data: Dict[str, Any]):
        """Traite la mise à jour d'un abonnement."""
        subscription_id = webhook_data.get("subscription_id")
        status_stripe = webhook_data.get("status_stripe")
        
        # Mise à jour du statut en base
        client = self.db.get_client()
        client.table("user_subscriptions").update({
            "status": status_stripe,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("subscription_id", subscription_id).execute()

    async def _handle_subscription_deleted(self, webhook_data: Dict[str, Any]):
        """Traite la suppression d'un abonnement."""
        subscription_id = webhook_data.get("subscription_id")
        
        # Downgrade vers FREE
        client = self.db.get_client()
        response = client.table("user_subscriptions").select("user_id").eq(
            "subscription_id", subscription_id
        ).execute()
        
        if response.data:
            user_id = response.data[0]["user_id"]
            await self.upgrade_user_tier(user_id, UserTier.FREE)

    async def _handle_payment_succeeded(self, webhook_data: Dict[str, Any]):
        """Traite un paiement réussi."""
        subscription_id = webhook_data.get("subscription_id")
        
        client = self.db.get_client()
        client.table("user_subscriptions").update({
            "last_payment_date": datetime.now(timezone.utc).isoformat(),
            "status": SubscriptionStatus.ACTIVE.value
        }).eq("subscription_id", subscription_id).execute()

    async def _handle_payment_failed(self, webhook_data: Dict[str, Any]):
        """Traite un paiement échoué."""
        subscription_id = webhook_data.get("subscription_id")
        
        client = self.db.get_client()
        client.table("user_subscriptions").update({
            "status": SubscriptionStatus.PAST_DUE.value
        }).eq("subscription_id", subscription_id).execute()

    async def _check_letters_limit(self, user_id: str, tier: UserTier) -> bool:
        """Vérifie la limite de lettres pour un utilisateur."""
        tier_limit = self.tier_limits[tier]["letters_per_month"]
        
        if tier_limit == -1:  # Illimité
            return True
            
        stats = await self.get_user_usage_stats(user_id)
        current_usage = stats.get("letters_generated_this_month", 0)
        
        return current_usage < tier_limit

    async def _update_user_stats_on_tier_change(self, user_id: str, new_tier: UserTier):
        """Met à jour les stats utilisateur lors d'un changement de tier."""
        client = self.db.get_client()
        
        client.table("user_usage_stats").upsert({
            "user_id": user_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).execute()

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse une string datetime ISO vers datetime object."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return None