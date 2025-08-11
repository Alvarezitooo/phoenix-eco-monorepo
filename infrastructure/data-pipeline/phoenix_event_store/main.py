import psycopg2
import json
import pika
import uuid
from datetime import datetime, timezone
from packages.phoenix_shared_models.events import BaseEvent

import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
# SÉCURITÉ: Mot de passe depuis variable d'environnement
DB_PASSWORD = os.getenv("DB_PASSWORD", "change_me_in_production")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
EXCHANGE_NAME = 'phoenix_events'
QUEUE_NAME = 'event_store_queue'
ROUTING_KEY = 'phoenix.#' # Listen to all phoenix events
PAUSE_RABBITMQ_CONSUMER = os.getenv('PAUSE_RABBITMQ', 'true').lower() in ('1','true','yes')

def get_db_connection():
    """Établit une connexion à la base de données PostgreSQL."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

def create_events_table():
    """Crée la table 'events' si elle n'existe pas."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id UUID PRIMARY KEY,
                stream_id UUID NOT NULL,
                event_type VARCHAR(255) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                payload JSONB NOT NULL,
                version INT NOT NULL
            );
        """)
        conn.commit()
        print("Table 'events' ensured to exist.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if conn:
            conn.close()

def save_event(event: BaseEvent):
    """Sauvegarde un événement dans l'Event Store."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (event_id, stream_id, event_type, timestamp, payload, version)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (
            str(event.event_id),
            str(event.stream_id),
            event.event_type,
            event.timestamp,
            json.dumps(event.payload),
            event.version
        ))
        conn.commit()
        print(f"Event {event.event_type} for stream {event.stream_id} saved successfully.")
    except Exception as e:
        print(f"Error saving event: {e}")
    finally:
        if conn:
            conn.close()

def get_events_for_stream(stream_id: str) -> list[dict]:
    """Récupère tous les événements pour un stream donné."""
    conn = None
    events = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT event_id, stream_id, event_type, timestamp, payload, version
            FROM events
            WHERE stream_id = %s
            ORDER BY timestamp ASC;
        """, (stream_id,))
        rows = cur.fetchall()
        for row in rows:
            event_data = {
                "event_id": str(row[0]),
                "stream_id": str(row[1]),
                "event_type": row[2],
                "timestamp": row[3].isoformat(),
                "payload": row[4],
                "version": row[5]
            }
            events.append(event_data)
    except Exception as e:
        print(f"Error retrieving events: {e}")
    finally:
        if conn:
            conn.close()
    return events

def callback(ch, method, properties, body):
    """Fonction de rappel pour traiter les messages RabbitMQ."""
    try:
        event_data = json.loads(body)
        print(f" [x] Received {method.routing_key}: {event_data}")

        # Reconstruct BaseEvent object
        event = BaseEvent(
            event_id=uuid.UUID(event_data["event_id"]),
            stream_id=uuid.UUID(event_data["stream_id"]),
            timestamp=datetime.fromisoformat(event_data["timestamp"]).replace(tzinfo=timezone.utc),
            payload=event_data["payload"],
            version=event_data["version"]
        )
        # Note: event_type is not part of BaseEvent constructor, but is in event_data
        event.event_type = event_data["event_type"]

        save_event(event)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) # Nack and don't requeue on error

def main():
    print("Phoenix Event Store service initialized.")
    create_events_table()

    # Connexion à RabbitMQ et consommation des événements
    if PAUSE_RABBITMQ_CONSUMER:
        print("RabbitMQ consumer is paused (PAUSE_RABBITMQ=true). Using Supabase Event Bridge as standard.")
        return
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=ROUTING_KEY)

        print(f" [*] Waiting for messages. To exit press CTRL+C")
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}. Make sure RabbitMQ is running at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    except KeyboardInterrupt:
        print("Exiting Event Store service.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()

if __name__ == "__main__":
    main()