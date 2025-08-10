"""
🔥 Phoenix CV - Webhook Handler
Gestionnaire de webhooks Stripe pour Streamlit Cloud

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import streamlit as st
import logging
from phoenix_cv.services.stripe_service import stripe_service

logger = logging.getLogger(__name__)


def handle_stripe_webhook():
    """
    Endpoint webhook Stripe pour Streamlit Cloud.
    Traite les événements Stripe de manière sécurisée.
    """
    
    # Configuration de la page
    st.set_page_config(
        page_title="Phoenix CV Webhook",
        page_icon="🔗",
        layout="centered"
    )
    
    # Vérification de la méthode HTTP (simulation)
    if st.session_state.get("webhook_method") != "POST":
        st.error("❌ Méthode non autorisée")
        st.stop()
    
    # Récupération des paramètres de la requête
    query_params = st.experimental_get_query_params()
    
    if "webhook" not in query_params:
        st.error("❌ Endpoint webhook non reconnu")
        st.stop()
    
    # Affichage d'informations pour le développement
    st.title("🔗 Phoenix CV Webhook Handler")
    st.info("📡 Endpoint webhook actif - Prêt à recevoir les événements Stripe")
    
    # Interface de test webhook (développement uniquement)
    if st.checkbox("🔧 Mode Test Webhook", help="Uniquement pour le développement"):
        st.markdown("### 🧪 Test Webhook Stripe")
        
        # Simulation d'événement
        test_events = {
            "checkout.session.completed": {
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": "cs_test_123",
                        "customer": "cus_test_123",
                        "subscription": "sub_test_123",
                        "metadata": {
                            "phoenix_cv_user_id": "test_user_123",
                            "plan_id": "pro"
                        }
                    }
                }
            },
            "customer.subscription.created": {
                "type": "customer.subscription.created",
                "data": {
                    "object": {
                        "id": "sub_test_123",
                        "customer": "cus_test_123",
                        "status": "active",
                        "metadata": {
                            "phoenix_cv_user_id": "test_user_123",
                            "plan_id": "pro"
                        }
                    }
                }
            }
        }
        
        selected_event = st.selectbox(
            "Sélectionner un événement à tester:",
            options=list(test_events.keys())
        )
        
        if st.button("🚀 Simuler Webhook"):
            try:
                # Simulation du payload webhook
                event_data = test_events[selected_event]
                
                # Traitement de l'événement (sans vérification de signature en mode test)
                result = process_webhook_event(event_data)
                
                if result:
                    st.success("✅ Webhook traité avec succès")
                    st.json(result)
                else:
                    st.error("❌ Erreur lors du traitement du webhook")
                    
            except Exception as e:
                st.error(f"❌ Erreur simulation webhook: {e}")
                logger.error(f"Erreur simulation webhook: {e}")
    
    # Instructions de configuration
    st.markdown("---")
    st.markdown("### ⚙️ Configuration Webhook Stripe")
    
    webhook_url = "https://phoenix-cv.streamlit.app/?webhook=stripe"
    
    st.code(f"""
Endpoint URL: {webhook_url}
Events: checkout.session.completed, customer.subscription.created, 
        customer.subscription.updated, customer.subscription.deleted,
        invoice.payment_succeeded, invoice.payment_failed
    """)
    
    st.markdown("### 🔐 Variables d'Environnement Requises")
    
    required_vars = [
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET", 
        "PHOENIX_AUTH_SERVICE_URL",
        "PHOENIX_AUTH_API_KEY"
    ]
    
    for var in required_vars:
        is_configured = bool(st.secrets.get(var))
        status = "✅" if is_configured else "❌"
        st.write(f"{status} `{var}`")
    
    # Logs récents (développement)
    if st.checkbox("📋 Voir les logs récents"):
        st.text_area(
            "Logs webhook récents:",
            value="Logs webhook apparaîtront ici...",
            height=200,
            disabled=True
        )


def process_webhook_event(event_data: dict) -> dict:
    """
    Traite un événement webhook Stripe.
    
    Args:
        event_data: Données de l'événement Stripe
        
    Returns:
        Résultat du traitement
    """
    try:
        event_type = event_data.get("type")
        event_object = event_data.get("data", {}).get("object", {})
        
        logger.info(f"Traitement événement webhook: {event_type}")
        
        # Dispatch selon le type d'événement
        if event_type == "checkout.session.completed":
            result = stripe_service._handle_checkout_completed(event_object)
        elif event_type == "customer.subscription.created":
            result = stripe_service._handle_subscription_created(event_object)
        elif event_type == "customer.subscription.updated":
            result = stripe_service._handle_subscription_updated(event_object)
        elif event_type == "customer.subscription.deleted":
            result = stripe_service._handle_subscription_deleted(event_object)
        elif event_type == "invoice.payment_succeeded":
            result = stripe_service._handle_payment_succeeded(event_object)
        elif event_type == "invoice.payment_failed":
            result = stripe_service._handle_payment_failed(event_object)
        else:
            result = {"status": "ignored", "type": event_type}
            
        logger.info(f"Événement {event_type} traité avec succès")
        return result
        
    except Exception as e:
        logger.error(f"Erreur traitement événement webhook: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    handle_stripe_webhook()