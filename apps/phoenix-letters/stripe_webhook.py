"""
🔥 Phoenix Letters - Stripe Webhook Handler
Handler pour webhooks Stripe déployé en parallèle de Streamlit

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready

Usage:
- Déployer ce script comme application Flask séparée
- Configurer l'URL webhook dans Stripe Dashboard
- Exemple: https://your-webhook-app.herokuapp.com/stripe/webhook
"""

import logging
import os
from flask import Flask, request, jsonify
import asyncio

from config.settings import Settings
from infrastructure.payment.stripe_service import StripeService
from infrastructure.security.input_validator import InputValidator
from infrastructure.database.db_connection import DatabaseConnection
from core.services.subscription_service import SubscriptionService

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialisation Flask
app = Flask(__name__)

# Initialisation des services
settings = Settings()
input_validator = InputValidator()
stripe_service = StripeService(settings, input_validator)
db_connection = DatabaseConnection(settings)
subscription_service = SubscriptionService(
    settings, stripe_service, db_connection, input_validator
)


@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """
    Endpoint webhook Stripe pour gérer les événements d'abonnement.
    
    Returns:
        JSON response avec statut du traitement
    """
    try:
        # Récupération des données webhook
        payload = request.get_data()
        signature = request.headers.get('Stripe-Signature')
        
        if not signature:
            logger.error("Signature Stripe manquante")
            return jsonify({'error': 'Missing signature'}), 400
            
        # Traitement du webhook via StripeService
        webhook_data = stripe_service.handle_webhook(payload, signature)
        
        # Traitement asynchrone via SubscriptionService
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                subscription_service.handle_subscription_webhook(webhook_data)
            )
            
            if result:
                logger.info(f"Webhook traité avec succès: {webhook_data.get('status')}")
                return jsonify({
                    'status': 'success',
                    'message': 'Webhook processed successfully',
                    'webhook_type': webhook_data.get('status')
                }), 200
            else:
                logger.warning(f"Webhook ignoré: {webhook_data.get('status')}")
                return jsonify({
                    'status': 'ignored',
                    'message': 'Webhook ignored',
                    'webhook_type': webhook_data.get('status')
                }), 200
                
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Erreur traitement webhook: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An internal error occurred while processing the webhook.'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé pour monitoring.
    
    Returns:
        JSON response avec statut de santé
    """
    try:
        # Test basique de connectivité
        db_client = db_connection.get_client()
        
        return jsonify({
            'status': 'healthy',
            'message': 'Webhook service operational',
            'services': {
                'database': 'connected',
                'stripe': 'configured'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': 'Health check failed due to internal error.'
        }), 500


@app.route('/test', methods=['POST'])
def test_webhook():
    """
    Endpoint de test pour vérifier la configuration webhook.
    ATTENTION: À supprimer en production !
    
    Returns:
        JSON response avec détails de test
    """
    if os.getenv('FLASK_ENV') == 'production':
        return jsonify({'error': 'Test endpoint disabled in production'}), 403
        
    try:
        test_data = request.get_json()
        
        logger.info(f"Test webhook reçu: {test_data}")
        
        return jsonify({
            'status': 'test_success',
            'message': 'Test webhook received',
            'received_data': test_data,
            'environment': os.getenv('FLASK_ENV', 'development')
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur test webhook: {e}")
        return jsonify({
            'status': 'test_error',
            'message': 'An internal error occurred during test webhook processing.'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handler pour erreurs 404."""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'available_endpoints': [
            '/stripe/webhook (POST)',
            '/health (GET)',
            '/test (POST - dev only)'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handler pour erreurs 500."""
    logger.error(f"Erreur interne: {error}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Configuration pour développement
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    logger.info(f"Démarrage webhook server sur port {port}")
    logger.info(f"Mode debug: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )