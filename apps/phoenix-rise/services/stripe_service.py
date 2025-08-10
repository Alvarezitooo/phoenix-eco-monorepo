import os
import stripe
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PaymentError(Exception):
    """Custom exception for Stripe payment errors."""

class StripeService:
    """
    Service Stripe professionnel pour Phoenix Rise.
    Gère la création de sessions de paiement, la gestion des abonnements et le traitement des webhooks.
    """
    def __init__(self):
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self.stripe_price_id_premium = os.getenv("STRIPE_PRICE_ID_PREMIUM")
        self.stripe_price_id_premium_plus = os.getenv("STRIPE_PRICE_ID_PREMIUM_PLUS")

        if not self.stripe_secret_key:
            raise PaymentError("STRIPE_SECRET_KEY non configurée dans les variables d'environnement.")
        stripe.api_key = self.stripe_secret_key
        logger.info("Service Stripe Phoenix Rise initialisé.")

    def create_checkout_session(self, user_email: str, price_id: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
        """
        Crée une session de checkout Stripe sécurisée pour un abonnement.
        """
        try:
            # Create a new customer in Stripe or retrieve existing one
            customers = stripe.Customer.list(email=user_email)
            if customers.data:
                customer = customers.data[0]
            else:
                customer = stripe.Customer.create(email=user_email)

            session = stripe.checkout.Session.create(
                customer=customer.id,
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
            )
            logger.info(f"Session de checkout Stripe créée: {session.id}")
            return {"session_id": session.id, "url": session.url}
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la création de la session: {e}")
            raise PaymentError(f"Erreur lors de la création de la session de paiement: {e}")

    def handle_webhook(self, payload: str, signature: str) -> Dict[str, Any]:
        """
        Traite un webhook Stripe de manière sécurisée.
        """
        if not self.stripe_webhook_secret:
            raise PaymentError("STRIPE_WEBHOOK_SECRET non configuré dans les variables d'environnement.")

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.stripe_webhook_secret
            )
            logger.info(f"Webhook Stripe reçu: {event['type']}")
            return event.data.object
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Erreur de vérification de signature du webhook Stripe: {e}")
            raise PaymentError("Signature de webhook invalide.")
        except Exception as e:
            logger.error(f"Erreur inattendue lors du traitement du webhook: {e}")
            raise PaymentError("Erreur lors du traitement du webhook.")

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Récupère le statut d'une session de checkout Stripe.
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                "status": session.status,
                "customer_email": session.customer_details.email if session.customer_details else None,
                "subscription_id": session.subscription,
                "payment_status": session.payment_status
            }
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la récupération de la session: {e}")
            raise PaymentError(f"Erreur lors de la récupération de la session de paiement: {e}")

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Annule un abonnement Stripe.
        """
        try:
            subscription = stripe.Subscription.cancel(subscription_id)
            logger.info(f"Abonnement Stripe {subscription_id} annulé.")
            return {"status": subscription.status}
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de l'annulation de l'abonnement: {e}")
            raise PaymentError(f"Erreur lors de l'annulation de l'abonnement: {e}")

    def reactivate_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Réactive un abonnement Stripe.
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            if subscription.status == 'canceled' and subscription.cancel_at_period_end:
                # If subscription is set to cancel at period end, remove that setting
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=False,
                )
            elif subscription.status == 'canceled':
                # If already canceled, try to re-enable (might require a new payment)
                # This part might need more complex logic depending on Stripe's exact behavior
                # For simplicity, we'll assume it's a simple re-enable if not already ended
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    items=[{
                        'id': subscription.items.data[0].id,
                        'plan': subscription.items.data[0].plan.id,
                    }],
                    proration_behavior='always_invoice',
                )
            logger.info(f"Abonnement Stripe {subscription_id} réactivé.")
            return {"status": subscription.status}
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la réactivation de l'abonnement: {e}")
            raise PaymentError(f"Erreur lors de la réactivation de l'abonnement: {e}")

    def get_customer_subscriptions(self, customer_id: str) -> Dict[str, Any]:
        """
        Récupère tous les abonnements d'un client Stripe.
        """
        try:
            subscriptions = stripe.Subscription.list(customer=customer_id)
            return [sub.to_dict() for sub in subscriptions.data]
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la récupération des abonnements du client: {e}")
            raise PaymentError(f"Erreur lors de la récupération des abonnements du client: {e}")
