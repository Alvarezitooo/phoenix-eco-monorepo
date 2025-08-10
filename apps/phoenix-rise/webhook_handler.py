import os
import logging
from flask import Flask, request, jsonify
from services.stripe_service import StripeService, PaymentError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize StripeService (ensure environment variables are loaded)
stripe_service = StripeService()

@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')

    if not sig_header:
        logger.error("Signature Stripe manquante dans l'en-tête.")
        return jsonify({'error': 'Signature Stripe manquante'}), 400

    try:
        event = stripe_service.handle_webhook(payload, sig_header)
    except PaymentError as e:
        logger.error(f"Erreur de traitement du webhook: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la vérification du webhook: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    # Handle the event
    event_type = event['type']
    data_object = event['data']['object']

    logger.info(f"Traitement de l'événement Stripe: {event_type}")

    try:
        if event_type == 'checkout.session.completed':
            # Fulfill the purchase
            session_id = data_object['id']
            customer_id = data_object['customer']
            subscription_id = data_object.get('subscription')
            customer_email = data_object['customer_details']['email'] if 'customer_details' in data_object else None
            logger.info(f"Checkout session {session_id} completed for customer {customer_id}. Subscription ID: {subscription_id}")

        elif event_type == 'customer.subscription.created':
            subscription_id = data_object['id']
            customer_id = data_object['customer']
            status = data_object['status']
            logger.info(f"Subscription {subscription_id} created for customer {customer_id} with status {status}.")

        elif event_type == 'customer.subscription.updated':
            subscription_id = data_object['id']
            customer_id = data_object['customer']
            status = data_object['status']
            logger.info(f"Subscription {subscription_id} updated for customer {customer_id} to status {status}.")

        elif event_type == 'customer.subscription.deleted':
            subscription_id = data_object['id']
            customer_id = data_object['customer']
            logger.info(f"Subscription {subscription_id} deleted for customer {customer_id}.")

        elif event_type == 'invoice.payment_succeeded':
            invoice_id = data_object['id']
            customer_id = data_object['customer']
            subscription_id = data_object.get('subscription')
            logger.info(f"Payment succeeded for invoice {invoice_id}, customer {customer_id}, subscription {subscription_id}.")

        elif event_type == 'invoice.payment_failed':
            invoice_id = data_object['id']
            customer_id = data_object['customer']
            subscription_id = data_object.get('subscription')
            logger.warning(f"Payment failed for invoice {invoice_id}, customer {customer_id}, subscription {subscription_id}.")

        else:
            logger.info(f"Type d'événement non géré: {event_type}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de l'événement {event_type}: {e}")
        return jsonify({'error': "Erreur interne du serveur lors du traitement de l'evenement"}), 500

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    # This is for local testing. In production, use a proper WSGI server (e.g., Gunicorn).
    app.run(port=os.getenv("PORT", 5000))
