"""
💳 Phoenix Stripe Manager - Intégration Stratégique Monétisation
Implémentation de la vision Freemium avec Stripe Checkout + Webhooks
pour débloquer fonctionnalités Premium et assurer viabilité économique

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Strategic Vision Implementation
"""

import os
import logging
from typing import Optional, Dict, Any, Tuple
import stripe
from .client import get_auth_manager

logger = logging.getLogger(__name__)

class StripeManager:
    """
    Gestionnaire Stripe unifié pour l'écosystème Phoenix
    
    Gère les sessions de paiement, webhooks et synchronisation
    avec le système d'authentification unifié
    """
    
    # Prix des produits Phoenix (configurables via env)
    PRICE_IDS = {
        "phoenix_letters_premium": os.getenv("STRIPE_PRICE_LETTERS_PREMIUM", "price_1RraAcDcM3VIYgvyEBNFXfbR"),
        "phoenix_cv_premium": os.getenv("STRIPE_PRICE_CV_PREMIUM", "price_1RraUoDcM3VIYgvy0NXiKmKV"),
        "phoenix_bundle": os.getenv("STRIPE_PRICE_BUNDLE", "price_1RraWhDcM3VIYgvyGykPghCc"),
    }
    
    def __init__(self):
        """Initialise Stripe avec clés secrètes"""
        secret_key = os.getenv("STRIPE_SECRET_KEY")
        if not secret_key:
            raise ValueError("STRIPE_SECRET_KEY must be set in environment")
        
        stripe.api_key = secret_key
        self.auth_manager = get_auth_manager()
        
        logger.info("✅ StripeManager initialized")
    
    def create_checkout_session(
        self, 
        user_id: str, 
        product_type: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, Optional[str], str]:
        """
        Crée une session Stripe Checkout
        
        Args:
            user_id: ID utilisateur Phoenix (stream_id)
            product_type: 'letters_premium', 'cv_premium', ou 'bundle'
            success_url: URL de succès après paiement
            cancel_url: URL d'annulation
            metadata: Métadonnées additionnelles
            
        Returns:
            Tuple[success: bool, checkout_url: Optional[str], message: str]
        """
        try:
            # Récupérer le Price ID selon le type de produit
            price_id = self.PRICE_IDS.get(f"phoenix_{product_type}")
            if not price_id:
                return False, None, f"Product type '{product_type}' not found"
            
            # Récupérer info utilisateur pour l'email
            user_data = self.auth_manager.get_user_profile(user_id)
            if not user_data:
                return False, None, "User not found"
            
            # Créer session Stripe
            checkout_session = stripe.checkout.Session.create(
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',  # Abonnement récurrent
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                
                # ⭐ CLÉS CRITIQUES POUR LA VISION STRATÉGIQUE
                client_reference_id=user_id,  # Lien avec user_id Phoenix
                customer_email=user_data.get('email'),
                
                # Métadonnées pour traçabilité
                metadata={
                    'phoenix_user_id': user_id,
                    'product_type': product_type,
                    'source': 'phoenix_ecosystem',
                    **(metadata or {})
                },
                
                # Configuration abonnement
                subscription_data={
                    'metadata': {
                        'phoenix_user_id': user_id,
                        'product_type': product_type
                    }
                },
                
                # Options UX
                allow_promotion_codes=True,
                billing_address_collection='auto',
            )
            
            logger.info(f"✅ Checkout session created: {user_id} -> {product_type}")
            return True, checkout_session.url, "Checkout session created"
            
        except Exception as e:
            logger.error(f"❌ Checkout creation error for {user_id}: {e}")
            return False, None, f"Checkout error: {str(e)}"
    
    def handle_webhook_event(self, payload: bytes, signature: str) -> Tuple[bool, str]:
        """
        Traite les événements webhook de Stripe
        
        Args:
            payload: Corps de la requête webhook
            signature: Signature Stripe-Signature
            
        Returns:
            Tuple[success: bool, message: str]
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            return False, "Webhook secret not configured"
        
        try:
            # Vérifier signature
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            logger.info(f"📥 Webhook received: {event['type']}")
            
            # Traiter selon type d'événement
            if event['type'] == 'checkout.session.completed':
                return self._handle_checkout_completed(event['data']['object'])
            
            elif event['type'] == 'customer.subscription.created':
                return self._handle_subscription_created(event['data']['object'])
            
            elif event['type'] == 'customer.subscription.updated':
                return self._handle_subscription_updated(event['data']['object'])
            
            elif event['type'] == 'customer.subscription.deleted':
                return self._handle_subscription_cancelled(event['data']['object'])
            
            elif event['type'] == 'invoice.payment_succeeded':
                return self._handle_payment_succeeded(event['data']['object'])
            
            elif event['type'] == 'invoice.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            
            else:
                logger.info(f"🔔 Unhandled webhook event: {event['type']}")
                return True, f"Event {event['type']} ignored"
                
        except stripe.error.SignatureVerificationError:
            logger.error("❌ Invalid webhook signature")
            return False, "Invalid signature"
        except Exception as e:
            logger.error(f"❌ Webhook processing error: {e}")
            return False, f"Webhook error: {str(e)}"
    
    def _handle_checkout_completed(self, session) -> Tuple[bool, str]:
        """Traite la complétion d'une session de checkout"""
        try:
            user_id = session.get('client_reference_id')
            subscription_id = session.get('subscription')
            
            if not user_id:
                logger.error("❌ No client_reference_id in checkout session")
                return False, "Missing user ID"
            
            logger.info(f"💳 Checkout completed: {user_id} -> {subscription_id}")
            
            # Publier événement dans Event Store via PhoenixEventBridge
            # TODO: Intégrer avec Event Store quand disponible
            # self.event_bridge.publish_event({
            #     'event_type': 'CheckoutCompleted',
            #     'stream_id': user_id,
            #     'data': {
            #         'subscription_id': subscription_id,
            #         'session_id': session['id']
            #     }
            # })
            
            return True, "Checkout completed processed"
            
        except Exception as e:
            logger.error(f"❌ Checkout completion error: {e}")
            return False, f"Checkout processing error: {str(e)}"
    
    def _handle_subscription_created(self, subscription) -> Tuple[bool, str]:
        """Traite la création d'abonnement"""
        try:
            metadata = subscription.get('metadata', {})
            user_id = metadata.get('phoenix_user_id')
            product_type = metadata.get('product_type')
            
            if not user_id:
                logger.error("❌ No phoenix_user_id in subscription metadata")
                return False, "Missing user ID in subscription"
            
            # Déterminer le tier selon le produit
            tier_mapping = {
                'letters_premium': 'letters_premium',
                'cv_premium': 'cv_premium',
                'bundle': 'pack_premium'
            }
            
            subscription_tier = tier_mapping.get(product_type, 'premium')
            
            # Mettre à jour en base via Supabase
            success = self._update_user_subscription(
                user_id=user_id,
                stripe_customer_id=subscription['customer'],
                stripe_subscription_id=subscription['id'],
                subscription_tier=subscription_tier,
                status='active'
            )
            
            if success:
                logger.info(f"✅ Subscription activated: {user_id} -> {subscription_tier}")
                
                # Publier événement UserTierUpdated pour Event Store
                # TODO: Intégrer avec PhoenixEventBridge
                # self.event_bridge.publish_event({
                #     'event_type': 'UserTierUpdated', 
                #     'stream_id': user_id,
                #     'data': {
                #         'old_tier': 'free',
                #         'new_tier': subscription_tier,
                #         'subscription_id': subscription['id']
                #     }
                # })
                
                return True, f"Subscription {subscription_tier} activated"
            else:
                return False, "Failed to update user subscription"
                
        except Exception as e:
            logger.error(f"❌ Subscription creation error: {e}")
            return False, f"Subscription processing error: {str(e)}"
    
    def _handle_subscription_updated(self, subscription) -> Tuple[bool, str]:
        """Traite la mise à jour d'abonnement"""
        try:
            metadata = subscription.get('metadata', {})
            user_id = metadata.get('phoenix_user_id')
            
            if not user_id:
                return False, "Missing user ID"
            
            # Mettre à jour statut selon Stripe
            status_mapping = {
                'active': 'active',
                'past_due': 'past_due',
                'canceled': 'cancelled',
                'unpaid': 'past_due'
            }
            
            status = status_mapping.get(subscription['status'], 'inactive')
            
            success = self._update_subscription_status(user_id, status)
            
            if success:
                logger.info(f"✅ Subscription updated: {user_id} -> {status}")
                return True, f"Subscription status updated to {status}"
            else:
                return False, "Failed to update subscription status"
                
        except Exception as e:
            logger.error(f"❌ Subscription update error: {e}")
            return False, f"Subscription update error: {str(e)}"
    
    def _handle_subscription_cancelled(self, subscription) -> Tuple[bool, str]:
        """Traite l'annulation d'abonnement"""
        try:
            metadata = subscription.get('metadata', {})
            user_id = metadata.get('phoenix_user_id')
            
            if not user_id:
                return False, "Missing user ID"
            
            # Remettre en tier gratuit
            success = self._update_user_subscription(
                user_id=user_id,
                subscription_tier='free',
                status='cancelled'
            )
            
            if success:
                logger.info(f"✅ Subscription cancelled: {user_id} -> free")
                
                # Publier événement de dégradation
                # TODO: Event Store integration
                # self.event_bridge.publish_event({
                #     'event_type': 'UserTierDowngraded',
                #     'stream_id': user_id,
                #     'data': {
                #         'old_tier': 'premium',
                #         'new_tier': 'free',
                #         'reason': 'subscription_cancelled'
                #     }
                # })
                
                return True, "Subscription cancelled and user downgraded"
            else:
                return False, "Failed to downgrade user"
                
        except Exception as e:
            logger.error(f"❌ Subscription cancellation error: {e}")
            return False, f"Cancellation processing error: {str(e)}"
    
    def _handle_payment_succeeded(self, invoice) -> Tuple[bool, str]:
        """Traite un paiement réussi"""
        try:
            subscription_id = invoice.get('subscription')
            if subscription_id:
                logger.info(f"💰 Payment succeeded for subscription: {subscription_id}")
            
            return True, "Payment success processed"
            
        except Exception as e:
            logger.error(f"❌ Payment success processing error: {e}")
            return False, f"Payment processing error: {str(e)}"
    
    def _handle_payment_failed(self, invoice) -> Tuple[bool, str]:
        """Traite un paiement échoué"""
        try:
            subscription_id = invoice.get('subscription')
            if subscription_id:
                logger.warning(f"⚠️ Payment failed for subscription: {subscription_id}")
                
                # Marquer abonnement en past_due
                # TODO: Logique de gestion des paiements échoués
            
            return True, "Payment failure processed"
            
        except Exception as e:
            logger.error(f"❌ Payment failure processing error: {e}")
            return False, f"Payment failure error: {str(e)}"
    
    def _update_user_subscription(
        self,
        user_id: str,
        stripe_customer_id: Optional[str] = None,
        stripe_subscription_id: Optional[str] = None,
        subscription_tier: Optional[str] = None,
        status: Optional[str] = None
    ) -> bool:
        """Met à jour l'abonnement utilisateur en base"""
        try:
            from supabase import create_client
            
            supabase = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Clé service pour écriture
            )
            
            update_data = {}
            if stripe_customer_id:
                update_data['stripe_customer_id'] = stripe_customer_id
            if stripe_subscription_id:
                update_data['stripe_subscription_id'] = stripe_subscription_id
            if subscription_tier:
                update_data['subscription_tier'] = subscription_tier
            if status:
                update_data['status'] = status
            
            # Mettre à jour user_subscriptions
            sub_response = supabase.table('user_subscriptions').upsert({
                'user_id': user_id,
                **update_data
            }).execute()
            
            # Mettre à jour profiles
            if subscription_tier:
                profile_response = supabase.table('profiles').update({
                    'subscription_tier': subscription_tier
                }).eq('id', user_id).execute()
            
            return bool(sub_response.data)
            
        except Exception as e:
            logger.error(f"❌ Database update error for {user_id}: {e}")
            return False
    
    def _update_subscription_status(self, user_id: str, status: str) -> bool:
        """Met à jour seulement le statut d'abonnement"""
        return self._update_user_subscription(user_id=user_id, status=status)


# Instance globale
stripe_manager = None

def get_stripe_manager() -> StripeManager:
    """Factory function pour obtenir l'instance StripeManager"""
    global stripe_manager
    if stripe_manager is None:
        stripe_manager = StripeManager()
    return stripe_manager