"""
🔥 Phoenix CV - Stripe Payment Service
Service de paiement Stripe professionnel avec sécurité renforcée

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import os
import stripe
import streamlit as st
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from phoenix_cv.services.phoenix_auth_integration import phoenix_auth

logger = logging.getLogger(__name__)


@dataclass
class CVPlan:
    """Modèle des plans CV."""
    id: str
    name: str
    price_amount: int  # en centimes
    currency: str = "eur"
    interval: str = "month"
    features: List[str] = None


class StripeService:
    """
    Service Stripe professionnel pour Phoenix CV.
    Gère abonnements Premium avec sécurité maximale.
    """
    
    def __init__(self):
        load_dotenv()
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        if not stripe.api_key:
            st.error("STRIPE_SECRET_KEY non configurée dans .env")
            raise ValueError("STRIPE_SECRET_KEY non configurée")
            
        # Plans d'abonnement Phoenix CV
        self.cv_plans = {
            "premium": CVPlan(
                id="premium",
                name="Phoenix CV Premium",
                price_amount=799,  # 7.99€
                features=[
                    "CV illimités",
                    "Templates premium",
                    "ATS Optimizer avancé",
                    "Mirror Match précis",
                    "Smart Coach IA",
                    "Export multi-formats",
                    "Support prioritaire"
                ]
            )
        }
        
        logger.info("Service Stripe Phoenix CV initialisé")

    def create_subscription_checkout(
        self, 
        user_id: str, 
        plan_id: str, 
        success_url: str, 
        cancel_url: str,
        user_email: Optional[str] = None
    ) -> Optional[str]:
        """
        Crée une session de checkout Stripe pour abonnement.
        
        Args:
            user_id: ID utilisateur Phoenix CV
            plan_id: ID du plan (pro, enterprise)
            success_url: URL de redirection succès
            cancel_url: URL de redirection annulation
            user_email: Email utilisateur (optionnel)
            
        Returns:
            URL de checkout ou None si erreur
        """
        try:
            if plan_id not in self.cv_plans:
                st.error(f"Plan '{plan_id}' non disponible")
                return None
                
            plan = self.cv_plans[plan_id]
            
            # Création du customer Stripe
            customer_data = {
                "metadata": {
                    "phoenix_cv_user_id": user_id,
                    "plan_id": plan_id
                }
            }
            
            if user_email:
                customer_data["email"] = user_email
                
            customer = stripe.Customer.create(**customer_data)
            
            # Configuration de la session de checkout
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card", "sepa_debit"],
                line_items=[{
                    'price_data': {
                        'currency': plan.currency,
                        'product_data': {
                            'name': plan.name,
                            'description': f"Abonnement {plan.name} - {len(plan.features)} fonctionnalités premium"
                        },
                        'unit_amount': plan.price_amount,
                        'recurring': {
                            'interval': plan.interval
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=cancel_url,
                metadata={
                    'phoenix_cv_user_id': user_id,
                    'plan_id': plan_id
                },
                subscription_data={
                    "metadata": {
                        'phoenix_cv_user_id': user_id,
                        'plan_id': plan_id
                    }
                },
                automatic_tax={"enabled": True},
                billing_address_collection="required"
            )
            
            logger.info(f"Session checkout créée pour user {user_id}, plan {plan_id}")
            return checkout_session.url
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors création session: {e}")
            st.error(f"Erreur Stripe: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue création session: {e}")
            st.error(f"Erreur inattendue: {e}")
            return None

    def create_one_time_payment(self, user_id: str, product_name: str, amount: int, success_url: str, cancel_url: str):
        """Méthode legacy pour paiements uniques."""
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': product_name,
                            },
                            'unit_amount': amount,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=user_id,
                metadata={
                    'product_name': product_name,
                    'user_id': user_id,
                }
            )
            return checkout_session.url
        except stripe.error.StripeError as e:
            st.error(f"Erreur Stripe lors de la création de la session: {e}")
            return None
        except Exception as e:
            st.error(f"Erreur inattendue: {e}")
            return None

    def handle_webhook(self, payload: bytes, sig_header: str) -> Optional[Dict[str, Any]]:
        """
        Traite un webhook Stripe de manière sécurisée.
        
        Args:
            payload: Corps de la requête webhook
            sig_header: Signature Stripe
            
        Returns:
            Données de l'événement traité ou None
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET non configuré")
            return None
            
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
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
                
        except ValueError as e:
            logger.error(f"Erreur payload webhook: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Erreur signature webhook: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur traitement webhook: {e}")
            return None

    def _handle_checkout_completed(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Traite la completion d'un checkout."""
        phoenix_user_id = session.get('metadata', {}).get('phoenix_cv_user_id')
        plan_id = session.get('metadata', {}).get('plan_id')
        subscription_id = session.get('subscription')
        
        logger.info(f"Checkout complété pour user {phoenix_user_id}, plan {plan_id}")
        
        # Mise à jour du statut utilisateur via Phoenix Auth
        if phoenix_user_id and plan_id and subscription_id:
            success = phoenix_auth.update_user_subscription(
                phoenix_user_id=phoenix_user_id,
                plan_id=plan_id,
                subscription_id=subscription_id,
                status="active"
            )
            
            # Log de l'événement pour audit
            phoenix_auth.log_subscription_event(
                phoenix_user_id=phoenix_user_id,
                event_type="checkout_completed",
                details={
                    "plan_id": plan_id,
                    "subscription_id": subscription_id,
                    "customer_id": session.get('customer'),
                    "auth_update_success": success
                }
            )
        
        return {
            "status": "checkout_completed",
            "phoenix_user_id": phoenix_user_id,
            "plan_id": plan_id,
            "customer_id": session.get('customer'),
            "subscription_id": subscription_id,
            "auth_updated": phoenix_user_id and plan_id and subscription_id
        }

    def _handle_subscription_created(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Traite la création d'un abonnement."""
        phoenix_user_id = subscription.get('metadata', {}).get('phoenix_cv_user_id')
        plan_id = subscription.get('metadata', {}).get('plan_id')
        
        logger.info(f"Abonnement créé pour user {phoenix_user_id}, plan {plan_id}")
        
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
        phoenix_user_id = subscription.get('metadata', {}).get('phoenix_cv_user_id')
        subscription_id = subscription.get('id')
        
        logger.info(f"Abonnement supprimé pour user {phoenix_user_id}")
        
        # Annulation de l'abonnement via Phoenix Auth
        if phoenix_user_id and subscription_id:
            success = phoenix_auth.cancel_user_subscription(
                phoenix_user_id=phoenix_user_id,
                subscription_id=subscription_id
            )
            
            # Log de l'événement pour audit
            phoenix_auth.log_subscription_event(
                phoenix_user_id=phoenix_user_id,
                event_type="subscription_deleted",
                details={
                    "subscription_id": subscription_id,
                    "auth_update_success": success
                }
            )
        
        return {
            "status": "subscription_deleted",
            "subscription_id": subscription_id,
            "phoenix_user_id": phoenix_user_id,
            "auth_updated": phoenix_user_id and subscription_id
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

    def get_available_plans(self) -> Dict[str, CVPlan]:
        """Retourne les plans CV disponibles."""
        return self.cv_plans.copy()

    def get_subscription_status(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le statut d'un abonnement.
        
        Args:
            subscription_id: ID de l'abonnement Stripe
            
        Returns:
            Informations de l'abonnement ou None
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "customer_id": subscription.customer
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur récupération abonnement {subscription_id}: {e}")
            return None

    def get_user_plan_status(self, phoenix_user_id: str) -> Dict[str, Any]:
        """
        Récupère le statut complet d'un utilisateur (Phoenix Auth + Stripe).
        
        Args:
            phoenix_user_id: ID utilisateur Phoenix
            
        Returns:
            Statut complet de l'utilisateur
        """
        # Récupération du statut depuis Phoenix Auth
        auth_status = phoenix_auth.get_user_subscription_status(phoenix_user_id)
        
        if not auth_status:
            return {
                "plan": "free",
                "status": "inactive",
                "features": ["CV de base", "Templates limités", "Export PDF simple"],
                "source": "default"
            }
        
        # Récupération des détails Stripe si disponible
        subscription_id = auth_status.get("subscription_id")
        stripe_status = None
        
        if subscription_id:
            stripe_status = self.get_subscription_status(subscription_id)
        
        # Détermination du plan et des fonctionnalités
        plan_id = auth_status.get("subscription_plan", "free")
        plan_config = self.cv_plans.get(plan_id)
        
        return {
            "plan": plan_id,
            "status": auth_status.get("subscription_status", "inactive"),
            "features": plan_config.features if plan_config else ["Fonctionnalités de base"],
            "subscription_id": subscription_id,
            "stripe_status": stripe_status.get("status") if stripe_status else None,
            "current_period_end": stripe_status.get("current_period_end") if stripe_status else None,
            "source": "phoenix_auth"
        }
            
# Instance globale du service Stripe
stripe_service = StripeService()
