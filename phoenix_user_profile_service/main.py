import pika
import json
import uuid
from datetime import datetime
from phoenix_shared_models.user_profile import UserProfile
from phoenix_shared_models.events import BaseEvent, UserProfileCreatedEvent, UserProfileUpdatedEvent

RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
EXCHANGE_NAME = 'phoenix_events'
EXCHANGE_TYPE = 'topic'

def publish_event(channel, event: BaseEvent):
    """Publie un événement sur RabbitMQ."""
    routing_key = f"phoenix.{event.event_type.lower()}"
    message = json.dumps({
        "event_id": str(event.event_id),
        "stream_id": str(event.stream_id),
        "event_type": event.event_type,
        "timestamp": event.timestamp.isoformat(),
        "payload": event.payload,
        "version": event.version
    })
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=routing_key,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Rendre le message persistant
        )
    )
    print(f" [x] Sent '{routing_key}':'{message}'")

def main():
    print("UserProfileService initialized. UserProfile model imported successfully.")

    # Connexion à RabbitMQ
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        channel = connection.channel()

        # Déclarer l'exchange (il sera créé s'il n'existe pas)
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True)
        print(f"Connected to RabbitMQ and declared exchange '{EXCHANGE_NAME}'.")

        # Exemple de création d'un utilisateur et publication d'un événement
        user_id = str(uuid.uuid4())
        new_user_profile = UserProfile(
            user_id=user_id,
            email="test@example.com",
            first_name="John",
            last_name="Doe"
        )

        user_created_event = UserProfileCreatedEvent(
            event_id=uuid.uuid4(),
            stream_id=new_user_profile.user_id,
            timestamp=datetime.now(datetime.UTC),
            payload={
                "user_id": new_user_profile.user_id,
                "email": new_user_profile.email,
                "first_name": new_user_profile.first_name,
                "last_name": new_user_profile.last_name
            }
        )
        publish_event(channel, user_created_event)

        # Fermer la connexion
        connection.close()
        print("RabbitMQ connection closed.")

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}. Make sure RabbitMQ is running at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()