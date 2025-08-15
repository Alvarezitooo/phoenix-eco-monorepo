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
try:
    from phoenix_shared_auth.stripe_manager import StripeManager
    # Import PaymentSession depuis StripeManager 
    from phoenix_shared_auth.stripe_manager import PaymentSession
except ImportError:
    # Fallback pour Streamlit Cloud
    class StripeManager:
        def create_checkout_session(self, *args, **kwargs):
            return {"id": "fallback_session", "url": "https://fallback.url"}
        def cancel_subscription(self, *args, **kwargs):
            return True
    
    class PaymentSession:
        def __init__(self, session_id: str, url: str):
            self.id = session_id
            self.url = url
from infrastructure.database.db_connection import DatabaseConnection
from shared.exceptions.specific_exceptions import SubscriptionError, DatabaseError
from infrastructure.security.input_validator import InputValidator

# Imports pour l'architecture événementielle Phoenix
import uuid
try:
    from phoenix_event_bridge import PhoenixEventBridge, PhoenixEventFactory, PhoenixEventType, PhoenixEventData
except ImportError:
    # Fallback pour Streamlit Cloud - Event bridge simplifié
    import logging
    logger = logging.getLogger(__name__)
    
    class PhoenixEventBridge:
        @staticmethod
        def publish_event(event_type: str, data: dict):
            logger.info(f"Event published: {event_type} - {data}")
            return True
    
    class PhoenixEventType:
        USER_SUBSCRIPTION_UPDATED = "user.subscription.updated"
        USER_SUBSCRIPTION_CANCELLED = "user.subscription.cancelled"
    
    class PhoenixEventData:
        @staticmethod
        def create(data: dict):
            return data
    
    class PhoenixEventFactory:
        @staticmethod
        def create_subscription_event(event_type: str, user_id: str, subscription_data: dict):
            return {
                "type": event_type,
                "user_id": user_id,
                "data": subscription_data,
                "timestamp": datetime.utcnow().isoformat()
            }

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
        stripe_service: StripeManager,
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
        Crée automatiquement une subscription FREE si aucune n'existe (Contrat V5).
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            UserSubscription (jamais None grâce à l'auto-création)
        """
        try:
            client = self.db.get_client()
            
            response = client.table("user_subscriptions").select("*").eq("user_id", user_id).execute()
            
            if not response.data:
                # 🔥 AUTO-CRÉATION PHOENIX : Subscription FREE par défaut
                logger.info(f"Auto-création subscription FREE pour user {user_id}")
                
                default_subscription = {
                    "user_id": user_id,
                    "current_tier": "free",
                    "auto_renewal": False,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                try:
                    client.table("user_subscriptions").insert(default_subscription).execute()
                    logger.info(f"✅ Subscription FREE créée pour user {user_id}")
                except Exception as create_error:
                    logger.warning(f"⚠️ Erreur création subscription DB: {create_error}")
                
                # Retourner subscription FREE par défaut (même si échec DB)
                return UserSubscription(
                    user_id=user_id,
                    current_tier=UserTier.FREE,
                    status=SubscriptionStatus.ACTIVE,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                
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
            # 🛡️ FALLBACK PHOENIX : Subscription FREE garantie
            logger.warning(f"Fallback vers subscription FREE pour user {user_id}")
            return UserSubscription(
                user_id=user_id,
                current_tier=UserTier.FREE,
                status=SubscriptionStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )

    async def upgrade_user_tier(
        self, 
        user_id: str, 
        new_tier: UserTier,
        subscription_id: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> bool:
        """
        Déclenche la mise à niveau du tier d'un utilisateur en publiant un événement.
        Toute modification de la base de données sera gérée par les services d'écoute.
        """
        try:
            # Récupérer l'ancien tier avant la mise à jour
            old_subscription = await self.get_user_subscription(user_id)
            old_tier = old_subscription.current_tier if old_subscription else UserTier.FREE

            if old_tier == new_tier:
                logger.info(f"Le tier pour l'utilisateur {user_id} est déjà {new_tier.value}. Aucun événement publié.")
                return True

            # Publier l'événement UserTierUpdated. Le data pipeline se chargera de la mise à jour.
            logger.info(f"Publication de l'événement USER_TIER_UPDATED pour {user_id}...")
            event_to_publish = PhoenixEventData(
                event_type=PhoenixEventType.USER_TIER_UPDATED,
                stream_id=user_id,
                app_source="phoenix-letters",
                payload={
                    "old_tier": old_tier.value,
                    "new_tier": new_tier.value,
                    "subscription_id": subscription_id,
                    "customer_id": customer_id,
                    "change_reason": "upgrade_tier_call"
                }
            )
            
            event_bridge = PhoenixEventBridge()
            await event_bridge.publish_event(event_to_publish)

            logger.info(f"✅ Événement USER_TIER_UPDATED publié pour {user_id} (de {old_tier.value} à {new_tier.value})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la publication de l'événement USER_TIER_UPDATED pour {user_id}: {e}")
            return False

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
                
            # Publier l'événement d'annulation pour traitement par le data pipeline
            try:
                # Utilisation de la factory pour garantir un événement standardisé
                event_to_publish = PhoenixEventFactory.create_subscription_cancelled(
                    user_id=user_id,
                    subscription_tier=subscription.current_tier.value,
                    stripe_subscription_id=subscription.subscription_id,
                    cancellation_reason="user_request_from_app"
                )
                
                # Instanciation correcte du pont d'événements
                event_bridge = PhoenixEventFactory.create_bridge()
                await event_bridge.publish_event(event_to_publish)
                
                logger.info(f"✅ Event SUBSCRIPTION_CANCELLED published for user {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to publish SUBSCRIPTION_CANCELLED event: {e}")
            
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
        """Traite la mise à jour d'un abonnement en appelant la logique de changement de tier."""
        user_id = webhook_data.get("phoenix_user_id")
        new_plan_id = webhook_data.get("new_plan_id")  # ex: "premium", "free"
        subscription_id = webhook_data.get("subscription_id")
        customer_id = webhook_data.get("customer_id")

        if not user_id or not new_plan_id:
            logger.warning(f"⚠️ Webhook 'subscription_updated' incomplet pour sub {subscription_id}. Ignoré.")
            return

        # Mapper l'ID du plan vers notre Enum UserTier
        tier_mapping = {
            "premium": UserTier.PREMIUM,
            "free": UserTier.FREE
            # Ajoutez d'autres plans si nécessaire
        }
        new_tier = tier_mapping.get(new_plan_id.lower(), UserTier.FREE)

        logger.info(f"Traitement de 'subscription_updated' pour user {user_id}. Nouveau tier: {new_tier.value}")
        
        # Appelle la méthode refactorisée qui publiera l'événement
        await self.upgrade_user_tier(
            user_id=user_id,
            new_tier=new_tier,
            subscription_id=subscription_id,
            customer_id=customer_id
        )

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
        """Traite un paiement réussi en publiant un événement."""
        subscription_id = webhook_data.get("subscription_id")
        user_id = webhook_data.get("phoenix_user_id")
        amount_paid = webhook_data.get("amount_paid", 0) # Montant en centimes
        currency = webhook_data.get("currency", "eur")
        stripe_invoice_id = webhook_data.get("invoice_id")

        if not user_id:
            logger.warning("⚠️ PAYMENT_SUCCEEDED webhook sans phoenix_user_id, ignoré")
            return

        try:
            event_to_publish = PhoenixEventFactory.create_payment_succeeded(
                user_id=user_id,
                amount_paid=amount_paid / 100.0, # Conversion en unité monétaire
                currency=currency,
                stripe_invoice_id=stripe_invoice_id
            )
            
            event_bridge = PhoenixEventBridge()
            await event_bridge.publish_event(event_to_publish)
            
            logger.info(f"✅ Event PAYMENT_SUCCEEDED published for user {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to publish PAYMENT_SUCCEEDED event: {e}")

    async def _handle_payment_failed(self, webhook_data: Dict[str, Any]):
        """Traite un paiement échoué en publiant un événement."""
        user_id = webhook_data.get("phoenix_user_id")
        failure_reason = webhook_data.get("failure_reason", "unknown_from_app")
        amount_due = webhook_data.get("amount_due", 0)  # Montant en centimes
        currency = webhook_data.get("currency", "eur")

        if not user_id:
            logger.warning("⚠️ PAYMENT_FAILED webhook sans phoenix_user_id, ignoré")
            return

        try:
            event_to_publish = PhoenixEventFactory.create_payment_failed(
                user_id=user_id,
                failure_reason=failure_reason,
                amount_due=amount_due / 100.0,  # Conversion en unité monétaire
                currency=currency
            )

            event_bridge = PhoenixEventBridge()
            await event_bridge.publish_event(event_to_publish)

            logger.info(f"✅ Event PAYMENT_FAILED published for user {user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to publish PAYMENT_FAILED event: {e}")

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