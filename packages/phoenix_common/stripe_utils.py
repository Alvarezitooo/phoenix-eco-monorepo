# packages/phoenix_common/stripe_utils.py
# Utilitaires Stripe production-ready
# Conforme Directive V3 (cycle de vie client)

import streamlit as st
from typing import Optional, Dict, Any
from phoenix_common.settings import get_settings

@st.cache_resource(show_spinner=False)
def get_stripe_client():
    """
    Client Stripe optimisé avec cache.
    
    Returns:
        Module stripe configuré
    """
    settings = get_settings()
    
    if not settings.STRIPE_PUBLISHABLE_KEY or not settings.STRIPE_SECRET_KEY:
        raise RuntimeError("Configuration Stripe incomplète")
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe
    except ImportError:
        raise RuntimeError("Package stripe non installé")

def create_checkout_session(
    price_id: str,
    user_id: str,
    success_url: str,
    cancel_url: str,
    metadata: Optional[Dict[str, str]] = None
) -> str:
    """
    Crée une session de checkout Stripe.
    
    Args:
        price_id: ID du prix Stripe
        user_id: ID utilisateur Phoenix
        success_url: URL de succès
        cancel_url: URL d'annulation
        metadata: Métadonnées additionnelles
        
    Returns:
        URL de checkout Stripe
    """
    stripe = get_stripe_client()
    
    session_metadata = {"phoenix_user_id": user_id}
    if metadata:
        session_metadata.update(metadata)
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=session_metadata,
            billing_address_collection='required',
            allow_promotion_codes=True
        )
        
        return session.url
        
    except Exception as e:
        st.error(f"Erreur création checkout: {e}")
        raise

def get_customer_portal_url(customer_id: str, return_url: str) -> str:
    """
    Génère l'URL du portail client Stripe.
    
    Args:
        customer_id: ID client Stripe
        return_url: URL de retour
        
    Returns:
        URL du portail client
    """
    stripe = get_stripe_client()
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        
        return session.url
        
    except Exception as e:
        st.error(f"Erreur portail client: {e}")
        raise

def test_stripe_connection() -> tuple[bool, str]:
    """
    Test de connexion Stripe (1€).
    
    Returns:
        (success, message)
    """
    try:
        stripe = get_stripe_client()
        
        # Test avec création d'un PaymentIntent de 1€
        intent = stripe.PaymentIntent.create(
            amount=100,  # 1€ en centimes
            currency='eur',
            metadata={'test': 'phoenix_connection_test'}
        )
        
        return True, f"✅ Connexion Stripe OK (Intent: {intent.id})"
        
    except Exception as e:
        return False, f"❌ Erreur Stripe: {e}"

def handle_webhook_event(event_type: str, event_data: Dict[str, Any]) -> bool:
    """
    Gestionnaire d'événements webhook Stripe.
    
    Args:
        event_type: Type d'événement Stripe
        event_data: Données de l'événement
        
    Returns:
        True si traité avec succès
    """
    try:
        if event_type == 'customer.subscription.deleted':
            # Gestion annulation abonnement
            customer_id = event_data['object']['customer']
            # TODO: Mettre à jour statut utilisateur en BDD
            print(f"🔄 Abonnement annulé pour customer: {customer_id}")
            
        elif event_type == 'invoice.payment_failed':
            # Gestion échec paiement
            customer_id = event_data['object']['customer']
            # TODO: Notifier utilisateur + actions de recouvrement
            print(f"❌ Paiement échoué pour customer: {customer_id}")
            
        elif event_type == 'checkout.session.completed':
            # Gestion checkout réussi
            session_id = event_data['object']['id']
            user_id = event_data['object']['metadata'].get('phoenix_user_id')
            # TODO: Activer accès premium utilisateur
            print(f"✅ Checkout réussi: {session_id} pour user: {user_id}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur traitement webhook {event_type}: {e}")
        return False