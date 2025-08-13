"""
💳 Phoenix Stripe Integration Service - Gestion des Abonnements Production
Service d'intégration Stripe avec les vrais Price IDs pour l'écosystème Phoenix

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import logging
import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import json

try:
    import stripe
    from ..entities.phoenix_subscription import (
        STRIPE_PRICE_IDS, BUNDLE_PRICE_IDS, STRIPE_PUBLISHABLE_KEY,
        PhoenixApp, SubscriptionTier, PackageType
    )
    from .phoenix_subscription_service import get_phoenix_subscription_service
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

logger = logging.getLogger(__name__)


class PhoenixStripeIntegrationService:
    """
    Service d'intégration Stripe pour l'écosystème Phoenix
    Gère les checkouts, webhooks et synchronisation des abonnements
    """
    
    def __init__(self, stripe_secret_key: str = None, webhook_secret: str = None):
        self.stripe_available = STRIPE_AVAILABLE
        self.publishable_key = STRIPE_PUBLISHABLE_KEY
        self.webhook_secret = webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if self.stripe_available:
            if stripe_secret_key:
                stripe.api_key = stripe_secret_key
                logger.info("✅ Stripe initialisé avec clé de production")
            elif os.getenv("STRIPE_SECRET_KEY"):
                stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
                logger.info("✅ Stripe initialisé depuis variables d'environnement")
            else:
                logger.warning("⚠️ Clé secrète Stripe manquante")
        else:
            logger.warning("⚠️ Stripe non disponible")
        
        # Service d'abonnements Phoenix
        self.subscription_service = get_phoenix_subscription_service()
    
    def create_checkout_session_cv_premium(
        self, 
        user_id: str, 
        user_email: str,
        success_url: str,
        cancel_url: str
    ) -> Tuple[bool, Optional[str], str]:
        """
        Crée une session Stripe Checkout pour Phoenix CV Premium
        
        Args:
            user_id: ID utilisateur Phoenix
            user_email: Email utilisateur
            success_url: URL de succès
            cancel_url: URL d'annulation
            
        Returns:
            Tuple[bool, Optional[str], str]: (success, checkout_url, message)
        """
        if not self.stripe_available:
            return False, None, "Stripe non disponible"
        
        try:
            price_id = STRIPE_PRICE_IDS[PhoenixApp.CV][SubscriptionTier.PREMIUM]
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                customer_email=user_email,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'phoenix_user_id': user_id,
                    'phoenix_app': 'cv',
                    'subscription_type': 'premium',
                    'package_type': 'single_app'
                },
                allow_promotion_codes=True,
                billing_address_collection='auto',
                subscription_data={
                    'metadata': {
                        'phoenix_user_id': user_id,
                        'phoenix_app': 'cv'
                    }
                }
            )
            
            logger.info(f"✅ Session Checkout CV Premium créée pour {user_email}: {session.id}")
            return True, session.url, "Session de paiement créée"
            
        except Exception as e:
            logger.error(f"❌ Erreur création session CV Premium: {e}")
            return False, None, f"Erreur Stripe: {str(e)}"
    
    def create_checkout_session_letters_premium(
        self, 
        user_id: str, 
        user_email: str,
        success_url: str,
        cancel_url: str
    ) -> Tuple[bool, Optional[str], str]:
        """
        Crée une session Stripe Checkout pour Phoenix Letters Premium
        """
        if not self.stripe_available:
            return False, None, "Stripe non disponible"
        
        try:
            price_id = STRIPE_PRICE_IDS[PhoenixApp.LETTERS][SubscriptionTier.PREMIUM]
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                customer_email=user_email,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'phoenix_user_id': user_id,
                    'phoenix_app': 'letters',
                    'subscription_type': 'premium',
                    'package_type': 'single_app'
                },
                allow_promotion_codes=True,
                billing_address_collection='auto',
                subscription_data={
                    'metadata': {
                        'phoenix_user_id': user_id,
                        'phoenix_app': 'letters'
                    }
                }
            )
            
            logger.info(f"✅ Session Checkout Letters Premium créée pour {user_email}: {session.id}")
            return True, session.url, "Session de paiement créée"
            
        except Exception as e:
            logger.error(f"❌ Erreur création session Letters Premium: {e}")
            return False, None, f"Erreur Stripe: {str(e)}"
    
    def create_checkout_session_pack_cv_letters(
        self, 
        user_id: str, 
        user_email: str,
        success_url: str,
        cancel_url: str
    ) -> Tuple[bool, Optional[str], str]:
        """
        Crée une session Stripe Checkout pour le Pack CV + Letters
        """
        if not self.stripe_available:
            return False, None, "Stripe non disponible"
        
        try:
            price_id = BUNDLE_PRICE_IDS["phoenix_pack_cv_letters"]
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                customer_email=user_email,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'phoenix_user_id': user_id,
                    'phoenix_app': 'pack_cv_letters',
                    'subscription_type': 'premium',
                    'package_type': 'pack_cv_letters'
                },
                allow_promotion_codes=True,
                billing_address_collection='auto',
                subscription_data={
                    'metadata': {
                        'phoenix_user_id': user_id,
                        'phoenix_package': 'cv_letters'
                    }
                }
            )
            
            logger.info(f"✅ Session Checkout Pack CV+Letters créée pour {user_email}: {session.id}")
            return True, session.url, "Session de paiement Pack créée"
            
        except Exception as e:
            logger.error(f"❌ Erreur création session Pack CV+Letters: {e}")
            return False, None, f"Erreur Stripe: {str(e)}"
    
    def handle_webhook_subscription_created(self, event_data: Dict[str, Any]) -> bool:
        """
        Traite le webhook Stripe customer.subscription.created
        
        Args:
            event_data: Données de l'événement Stripe
            
        Returns:
            bool: Succès du traitement
        """
        try:
            subscription = event_data['data']['object']
            subscription_id = subscription['id']
            customer_id = subscription['customer']
            
            # Récupérer métadonnées
            metadata = subscription.get('metadata', {})
            phoenix_user_id = metadata.get('phoenix_user_id')
            
            if not phoenix_user_id:
                logger.warning(f"⚠️ Webhook subscription sans phoenix_user_id: {subscription_id}")
                return False
            
            # Déterminer le type d'abonnement
            phoenix_package = metadata.get('phoenix_package')
            phoenix_app = metadata.get('phoenix_app')
            
            if phoenix_package == 'cv_letters':
                # Pack CV + Letters
                success, message = self.subscription_service.subscribe_to_pack_cv_letters(
                    user_id=phoenix_user_id,
                    stripe_subscription_id=subscription_id
                )
                logger.info(f"✅ Pack CV+Letters activé via webhook: {phoenix_user_id}")
                
            elif phoenix_app == 'cv':
                # Phoenix CV Premium seul
                success, message = self.subscription_service.subscribe_to_app(
                    user_id=phoenix_user_id,
                    app=PhoenixApp.CV,
                    tier=SubscriptionTier.PREMIUM,
                    stripe_subscription_id=subscription_id
                )
                logger.info(f"✅ CV Premium activé via webhook: {phoenix_user_id}")
                
            elif phoenix_app == 'letters':
                # Phoenix Letters Premium seul
                success, message = self.subscription_service.subscribe_to_app(
                    user_id=phoenix_user_id,
                    app=PhoenixApp.LETTERS,
                    tier=SubscriptionTier.PREMIUM,
                    stripe_subscription_id=subscription_id
                )
                logger.info(f"✅ Letters Premium activé via webhook: {phoenix_user_id}")
                
            else:
                logger.warning(f"⚠️ Type d'abonnement webhook non reconnu: {metadata}")
                return False
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement webhook subscription.created: {e}")
            return False
    
    def handle_webhook_subscription_updated(self, event_data: Dict[str, Any]) -> bool:
        """
        Traite le webhook Stripe customer.subscription.updated
        """
        try:
            subscription = event_data['data']['object']
            subscription_id = subscription['id']
            status = subscription['status']
            
            metadata = subscription.get('metadata', {})
            phoenix_user_id = metadata.get('phoenix_user_id')
            
            if not phoenix_user_id:
                return False
            
            # Mettre à jour le statut selon Stripe
            if status == 'active':
                # Réactiver si nécessaire
                logger.info(f"✅ Abonnement réactivé: {phoenix_user_id} ({subscription_id})")
            elif status in ['canceled', 'unpaid']:
                # Désactiver abonnements
                logger.info(f"⚠️ Abonnement annulé/impayé: {phoenix_user_id} ({subscription_id})")
                # TODO: Implémenter logique de désactivation
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement webhook subscription.updated: {e}")
            return False
    
    def handle_webhook_subscription_deleted(self, event_data: Dict[str, Any]) -> bool:
        """
        Traite le webhook Stripe customer.subscription.deleted
        """
        try:
            subscription = event_data['data']['object']
            subscription_id = subscription['id']
            
            metadata = subscription.get('metadata', {})
            phoenix_user_id = metadata.get('phoenix_user_id')
            phoenix_package = metadata.get('phoenix_package')
            phoenix_app = metadata.get('phoenix_app')
            
            if not phoenix_user_id:
                return False
            
            # Annuler abonnements selon le type
            if phoenix_package == 'cv_letters':
                # Annuler Pack CV + Letters
                cv_success, _ = self.subscription_service.cancel_app_subscription(
                    phoenix_user_id, PhoenixApp.CV, cancel_immediately=True
                )
                letters_success, _ = self.subscription_service.cancel_app_subscription(
                    phoenix_user_id, PhoenixApp.LETTERS, cancel_immediately=True
                )
                logger.info(f"✅ Pack CV+Letters annulé via webhook: {phoenix_user_id}")
                
            elif phoenix_app == 'cv':
                success, _ = self.subscription_service.cancel_app_subscription(
                    phoenix_user_id, PhoenixApp.CV, cancel_immediately=True
                )
                logger.info(f"✅ CV Premium annulé via webhook: {phoenix_user_id}")
                
            elif phoenix_app == 'letters':
                success, _ = self.subscription_service.cancel_app_subscription(
                    phoenix_user_id, PhoenixApp.LETTERS, cancel_immediately=True
                )
                logger.info(f"✅ Letters Premium annulé via webhook: {phoenix_user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement webhook subscription.deleted: {e}")
            return False
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de tarification pour l'affichage
        
        Returns:
            Dict contenant les prix et Price IDs
        """
        return {
            "price_ids": {
                "cv_premium": STRIPE_PRICE_IDS[PhoenixApp.CV][SubscriptionTier.PREMIUM],
                "letters_premium": STRIPE_PRICE_IDS[PhoenixApp.LETTERS][SubscriptionTier.PREMIUM],
                "pack_cv_letters": BUNDLE_PRICE_IDS["phoenix_pack_cv_letters"]
            },
            "publishable_key": self.publishable_key,
            "pricing_display": {
                "cv_premium": {
                    "name": "Phoenix CV Premium",
                    "price": "9.99€",
                    "features": ["CV illimités", "Templates premium", "Optimisation ATS", "Mirror Match"]
                },
                "letters_premium": {
                    "name": "Phoenix Letters Premium", 
                    "price": "9.99€",
                    "features": ["Lettres illimitées", "IA avancée", "Analyse offres", "Templates premium"]
                },
                "pack_cv_letters": {
                    "name": "Pack CV + Letters",
                    "price": "14.99€",
                    "original_price": "19.98€",
                    "savings": "30%",
                    "features": ["Tout CV Premium", "Tout Letters Premium", "Synchronisation avancée", "Support prioritaire"]
                }
            }
        }
    
    def verify_webhook_signature(self, payload: bytes, sig_header: str, webhook_secret: str) -> bool:
        """
        Vérifie la signature d'un webhook Stripe
        
        Args:
            payload: Corps de la requête webhook
            sig_header: Header Stripe-Signature
            webhook_secret: Secret du webhook Stripe
            
        Returns:
            bool: Signature valide
        """
        if not self.stripe_available:
            return False
        
        try:
            stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            return True
        except stripe.error.SignatureVerificationError:
            logger.error("❌ Signature webhook Stripe invalide")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur vérification webhook: {e}")
            return False


# Instance singleton pour import facile
phoenix_stripe_service = None

def get_phoenix_stripe_service(stripe_secret_key: str = None) -> PhoenixStripeIntegrationService:
    """Factory function pour service Stripe Phoenix"""
    global phoenix_stripe_service
    if phoenix_stripe_service is None and stripe_secret_key:
        phoenix_stripe_service = PhoenixStripeIntegrationService(stripe_secret_key)
    return phoenix_stripe_service