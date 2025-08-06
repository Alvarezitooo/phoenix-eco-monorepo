"""
🔥 Phoenix Letters - Stripe Payment Service
Service de paiement Stripe professionnel avec sécurité renforcée

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import logging
import stripe
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from config.settings import Settings
from shared.exceptions.specific_exceptions import PaymentError, ValidationError
from infrastructure.security.input_validator import InputValidator

logger = logging.getLogger(__name__)


@dataclass
class SubscriptionPlan:
    """Modèle des plans d'abonnement."""
    id: str
    name: str
    price_id: str
    price_amount: int  # en centimes
    currency: str = "eur"
    interval: str = "month"
    features: List[str] = None


@dataclass
class PaymentSession:
    """Session de paiement Stripe."""
    session_id: str
    session_url: str
    customer_id: Optional[str] = None
    subscription_id: Optional[str] = None
    status: str = "pending"


class StripeService:
    """
    Service Stripe professionnel pour Phoenix Letters.
    Gère abonnements, paiements et webhooks avec sécurité maximale.
    """
    
    def __init__(self, settings: Settings, input_validator: InputValidator):
        self.settings = settings
        self.validator = input_validator
        
        if not settings.stripe_secret_key:
            raise PaymentError("Clé secrète Stripe manquante dans la configuration")
            
        stripe.api_key = settings.stripe_secret_key
        
        # Plans d'abonnement Phoenix Letters
        self.subscription_plans = {
            "premium": SubscriptionPlan(
                id="premium",
                name="Phoenix Premium",
                price_id=settings.stripe_price_id_premium or "price_premium_default",
                price_amount=999,  # 9.99€
                features=[
                    "Lettres illimitées",
                    "Analyses ATS avancées",
                    "Mirror Match précis",
                    "Smart Coach personnalisé",
                    "Trajectory Builder",
                    "Templates exclusifs",
                    "Export PDF premium",
                    "Support prioritaire"
                ]
            )
        }
        
        logger.info("Service Stripe initialisé avec succès")

    def create_checkout_session(
        self, 
        user_id: str, 
        plan_id: str, 
        success_url: str, 
        cancel_url: str,
        user_email: Optional[str] = None
    ) -> PaymentSession:
        """
        Crée une session de checkout Stripe sécurisée.
        
        Args:
            user_id: ID utilisateur Phoenix
            plan_id: ID du plan (premium, premium_plus)
            success_url: URL de redirection succès
            cancel_url: URL de redirection annulation
            user_email: Email utilisateur (optionnel)
            
        Returns:
            PaymentSession avec URL de paiement
        """
        try:
            # Validation des entrées
            if not self.validator.validate_uuid(user_id):
                raise ValidationError("ID utilisateur invalide")
                
            if plan_id not in self.subscription_plans:
                raise ValidationError(f"Plan '{plan_id}' non disponible")
                
            plan = self.subscription_plans[plan_id]
            
            # Création du customer Stripe
            customer_data = {
                "metadata": {
                    "phoenix_user_id": user_id,
                    "plan_id": plan_id
                }
            }
            
            if user_email and self.validator.validate_email(user_email):
                customer_data["email"] = user_email
                
            customer = stripe.Customer.create(**customer_data)
            
            # Configuration de la session de checkout
            session_config = {
                "customer": customer.id,
                "payment_method_types": ["card", "sepa_debit"],
                "line_items": [{
                    "price": plan.price_id,
                    "quantity": 1,
                }],
                "mode": "subscription",
                "success_url": f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
                "cancel_url": cancel_url,
                "metadata": {
                    "phoenix_user_id": user_id,
                    "plan_id": plan_id
                },
                "subscription_data": {
                    "metadata": {
                        "phoenix_user_id": user_id,
                        "plan_id": plan_id
                    }
                },
                "automatic_tax": {"enabled": True},
                "billing_address_collection": "required",
                "customer_update": {
                    "address": "auto",
                    "name": "auto"
                }
            }
            
            session = stripe.checkout.Session.create(**session_config)
            
            payment_session = PaymentSession(
                session_id=session.id,
                session_url=session.url,
                customer_id=customer.id,
                status="pending"
            )
            
            logger.info(f"Session checkout créée pour user {user_id}, plan {plan_id}")
            return payment_session
            
        except stripe.StripeError as e:
            logger.error(f"Erreur Stripe lors création session: {e}")
            raise PaymentError(f"Impossible de créer la session de paiement: {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue création session: {e}")
            raise PaymentError(f"Erreur interne: {e}")

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Récupère le statut d'une session de checkout.
        
        Args:
            session_id: ID de la session Stripe
            
        Returns:
            Dict avec informations de session
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            result = {
                "session_id": session.id,
                "payment_status": session.payment_status,
                "customer_id": session.customer,
                "subscription_id": session.subscription,
                "phoenix_user_id": session.metadata.get("phoenix_user_id"),
                "plan_id": session.metadata.get("plan_id")
            }
            
            return result
            
        except stripe.StripeError as e:
            logger.error(f"Erreur récupération session {session_id}: {e}")
            raise PaymentError(f"Session introuvable: {e}")

    def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Annule un abonnement Stripe.
        
        Args:
            subscription_id: ID de l'abonnement Stripe
            
        Returns:
            True si annulation réussie
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            logger.info(f"Abonnement {subscription_id} programmé pour annulation")
            return True
            
        except stripe.StripeError as e:
            logger.error(f"Erreur annulation abonnement {subscription_id}: {e}")
            raise PaymentError(f"Impossible d'annuler l'abonnement: {e}")

    def reactivate_subscription(self, subscription_id: str) -> bool:
        """
        Réactive un abonnement annulé.
        
        Args:
            subscription_id: ID de l'abonnement Stripe
            
        Returns:
            True si réactivation réussie
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False
            )
            
            logger.info(f"Abonnement {subscription_id} réactivé")
            return True
            
        except stripe.StripeError as e:
            logger.error(f"Erreur réactivation abonnement {subscription_id}: {e}")
            raise PaymentError(f"Impossible de réactiver l'abonnement: {e}")

    def get_customer_subscriptions(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Récupère les abonnements d'un customer.
        
        Args:
            customer_id: ID du customer Stripe
            
        Returns:
            Liste des abonnements
        """
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status="all"
            )
            
            result = []
            for sub in subscriptions.data:
                result.append({
                    "subscription_id": sub.id,
                    "status": sub.status,
                    "current_period_start": datetime.fromtimestamp(
                        sub.current_period_start, tz=timezone.utc
                    ),
                    "current_period_end": datetime.fromtimestamp(
                        sub.current_period_end, tz=timezone.utc
                    ),
                    "cancel_at_period_end": sub.cancel_at_period_end,
                    "phoenix_user_id": sub.metadata.get("phoenix_user_id"),
                    "plan_id": sub.metadata.get("plan_id")
                })
                
            return result
            
        except stripe.StripeError as e:
            logger.error(f"Erreur récupération abonnements customer {customer_id}: {e}")
            raise PaymentError(f"Impossible de récupérer les abonnements: {e}")

    def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Traite un webhook Stripe de manière sécurisée.
        
        Args:
            payload: Corps de la requête webhook
            signature: Signature Stripe
            
        Returns:
            Données de l'événement traité
        """
        if not self.settings.stripe_webhook_secret:
            raise PaymentError("Secret webhook Stripe non configuré")
            
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.settings.stripe_webhook_secret
            )
            
            logger.info(f"Webhook Stripe reçu: {event['type']}")
            
            # Traitement selon le type d'événement
            if event['type'] == 'checkout.session.completed':
                return self._handle_checkout_completed(event['data']['object'])
            elif event['type'] == 'customer.subscription.created':
                return self._handle_subscription_created(event['data']['object'])
            elif event['type'] == 'customer.subscription.updated':
                return self._handle_subscription_updated(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event['data']['object'])
            elif event['type'] == 'invoice.payment_succeeded':
                return self._handle_payment_succeeded(event['data']['object'])
            elif event['type'] == 'invoice.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            else:
                logger.info(f"Événement webhook non traité: {event['type']}")
                return {"status": "ignored", "type": event['type']}
                
        except stripe.SignatureVerificationError as e:
            logger.error(f"Erreur signature webhook: {e}")
            raise PaymentError("Signature webhook invalide")
        except Exception as e:
            logger.error(f"Erreur traitement webhook: {e}")
            raise PaymentError(f"Erreur interne webhook: {e}")

    def _handle_checkout_completed(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Traite la completion d'un checkout."""
        phoenix_user_id = session.get('metadata', {}).get('phoenix_user_id')
        plan_id = session.get('metadata', {}).get('plan_id')
        
        return {
            "status": "checkout_completed",
            "phoenix_user_id": phoenix_user_id,
            "plan_id": plan_id,
            "customer_id": session.get('customer'),
            "subscription_id": session.get('subscription')
        }

    def _handle_subscription_created(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Traite la création d'un abonnement."""
        phoenix_user_id = subscription.get('metadata', {}).get('phoenix_user_id')
        plan_id = subscription.get('metadata', {}).get('plan_id')
        
        return {
            "status": "subscription_created",
            "phoenix_user_id": phoenix_user_id,
            "plan_id": plan_id,
            "subscription_id": subscription.get('id'),
            "customer_id": subscription.get('customer')
        }

    def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Traite la mise à jour d'un abonnement."""
        return {
            "status": "subscription_updated",
            "subscription_id": subscription.get('id'),
            "status_stripe": subscription.get('status')
        }

    def _handle_subscription_deleted(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Traite la suppression d'un abonnement."""
        return {
            "status": "subscription_deleted",
            "subscription_id": subscription.get('id')
        }

    def _handle_payment_succeeded(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Traite un paiement réussi."""
        return {
            "status": "payment_succeeded",
            "subscription_id": invoice.get('subscription'),
            "customer_id": invoice.get('customer')
        }

    def _handle_payment_failed(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Traite un paiement échoué."""
        return {
            "status": "payment_failed",
            "subscription_id": invoice.get('subscription'),
            "customer_id": invoice.get('customer')
        }

    def get_available_plans(self) -> Dict[str, SubscriptionPlan]:
        """Retourne les plans d'abonnement disponibles."""
        return self.subscription_plans.copy()