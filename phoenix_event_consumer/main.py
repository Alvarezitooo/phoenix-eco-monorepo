# PHOENIX EVENT CONSUMER
# Ce service écoute les événements du PhoenixEventBridge et met à jour la base de données.
# C'est le composant clé qui complète l'architecture Event-Sourcing.

import logging
import os
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import Client, create_client

# Assumer que les packages locaux sont dans le PYTHONPATH
# Dans un vrai déploiement, cela serait géré par Poetry ou un Dockerfile.
try:
    from phoenix_event_bridge import PhoenixEventBridge, PhoenixEventType
except ImportError:
    print("Erreur: Assurez-vous que les packages locaux (phoenix_event_bridge) sont dans le PYTHONPATH.")
    exit(1)

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Charger les variables d'environnement
load_dotenv()

# ================= HANDLERS D'ÉVÉNEMENTS =================

def get_db_client() -> Client:
    """Crée et retourne un client Supabase."""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("Les variables d'environnement SUPABASE_URL et SUPABASE_KEY sont requises.")
    return create_client(supabase_url, supabase_key)

async def handle_subscription_cancelled(event: dict):
    """
    Gère l'événement SUBSCRIPTION_CANCELLED.
    Met à jour la BDD pour refléter l'annulation.
    """
    user_id = event.get("stream_id")
    if not user_id:
        logging.warning("Événement SUBSCRIPTION_CANCELLED sans user_id. Ignoré.")
        return

    logging.info(f"[SUBSCRIPTION_CANCELLED] Traitement pour l'utilisateur {user_id}.")
    
    try:
        db_client = get_db_client()
        db_client.table("user_subscriptions").update({
            "auto_renewal": False,
            "status": "cancelled",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("user_id", user_id).execute()
        logging.info(f"[SUBSCRIPTION_CANCELLED] Succès: Abonnement pour l'utilisateur {user_id} mis à jour.")
    except Exception as e:
        logging.error(f"[SUBSCRIPTION_CANCELLED] Échec: Impossible de mettre à jour l'abonnement pour {user_id}. Erreur: {e}")

async def handle_payment_succeeded(event: dict):
    """
    Gère l'événement PAYMENT_SUCCEEDED.
    Met à jour le statut et la date de dernier paiement.
    """
    user_id = event.get("stream_id")
    if not user_id:
        logging.warning("Événement PAYMENT_SUCCEEDED sans user_id. Ignoré.")
        return

    logging.info(f"[PAYMENT_SUCCEEDED] Traitement pour l'utilisateur {user_id}.")

    try:
        db_client = get_db_client()
        db_client.table("user_subscriptions").update({
            "last_payment_date": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }).eq("user_id", user_id).execute()
        logging.info(f"[PAYMENT_SUCCEEDED] Succès: Statut de paiement pour {user_id} mis à jour.")
    except Exception as e:
        logging.error(f"[PAYMENT_SUCCEEDED] Échec: Impossible de mettre à jour le statut de paiement pour {user_id}. Erreur: {e}")

async def handle_payment_failed(event: dict):
    """
    Gère l'événement PAYMENT_FAILED.
    Met à jour le statut de l'abonnement en 'past_due'.
    """
    user_id = event.get("stream_id")
    if not user_id:
        logging.warning("Événement PAYMENT_FAILED sans user_id. Ignoré.")
        return

    logging.info(f"[PAYMENT_FAILED] Traitement pour l'utilisateur {user_id}.")

    try:
        db_client = get_db_client()
        db_client.table("user_subscriptions").update({
            "status": "past_due",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("user_id", user_id).execute()
        logging.info(f"[PAYMENT_FAILED] Succès: Statut de l'abonnement pour {user_id} mis à jour.")
    except Exception as e:
        logging.error(f"[PAYMENT_FAILED] Échec: Impossible de mettre à jour l'abonnement pour {user_id}. Erreur: {e}")

async def handle_user_tier_updated(event: dict):
    """
    Gère l'événement USER_TIER_UPDATED.
    Crée ou met à jour l'abonnement de l'utilisateur en base de données.
    """
    user_id = event.get("stream_id")
    payload = event.get("payload", {})
    new_tier = payload.get("new_tier")

    if not user_id or not new_tier:
        logging.warning("Événement USER_TIER_UPDATED incomplet. Ignoré.")
        return

    logging.info(f"[USER_TIER_UPDATED] Traitement pour l'utilisateur {user_id} vers le tier {new_tier}.")

    try:
        db_client = get_db_client()
        
        subscription_data = {
            "user_id": user_id,
            "current_tier": new_tier,
            "status": "active" if new_tier != "free" else "cancelled",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "subscription_id": payload.get("subscription_id"),
            "stripe_customer_id": payload.get("customer_id")
        }

        if new_tier != "free":
            subscription_data["subscription_start"] = datetime.now(timezone.utc).isoformat()
            subscription_data["subscription_end"] = (datetime.now(timezone.utc) + timedelta(days=31)).isoformat()
            subscription_data["auto_renewal"] = True
        else:
            subscription_data["auto_renewal"] = False
            subscription_data["subscription_end"] = datetime.now(timezone.utc).isoformat()

        db_client.table("user_subscriptions").upsert(subscription_data).execute()
        logging.info(f"[USER_TIER_UPDATED] Succès: Abonnement pour {user_id} mis à jour vers {new_tier}.")

    except Exception as e:
        logging.error(f"[USER_TIER_UPDATED] Échec: Impossible de mettre à jour l'abonnement pour {user_id}. Erreur: {e}")


# Mapper les types d'événements aux fonctions de traitement
EVENT_HANDLERS = {
    PhoenixEventType.SUBSCRIPTION_CANCELLED: handle_subscription_cancelled,
    PhoenixEventType.PAYMENT_SUCCEEDED: handle_payment_succeeded,
    PhoenixEventType.PAYMENT_FAILED: handle_payment_failed,
    PhoenixEventType.USER_TIER_UPDATED: handle_user_tier_updated,
    # ... Ajouter d'autres gestionnaires ici
}


# ================= BOUCLE PRINCIPALE DU CONSOMMATEUR =================

async def main():
    """
    Boucle principale du service consommateur.
    """
    logging.info("🚀 Démarrage du service consommateur d'événements Phoenix...")
    
    try:
        event_bridge = PhoenixEventBridge()
    except ValueError as e:
        logging.error(f"Erreur fatale à l'initialisation: {e}")
        return

    # Démarrer le polling depuis l'heure actuelle pour ne pas traiter les anciens événements
    last_processed_timestamp = datetime.now(timezone.utc)
    
    logging.info(f"Démarrage de l'écoute des événements à partir de {last_processed_timestamp.isoformat()}")

    while True:
        try:
            logging.info("Polling pour de nouveaux événements...")
            
            # Récupérer les événements depuis le dernier timestamp traité
            # Note: C'est une approche de polling simple. Pour la production, on utiliserait
            # Supabase Realtime, des webhooks, ou un système de file d'attente.
            response = event_bridge.supabase.table('events').select('*') \
                .gt('timestamp', last_processed_timestamp.isoformat()) \
                .order('timestamp', desc=False) \
                .execute()

            if response.data:
                logging.info(f"{len(response.data)} nouveaux événements trouvés.")
                
                for event in response.data:
                    event_type_str = event.get("event_type")
                    
                    try:
                        # Convertir la string en membre de l'Enum PhoenixEventType
                        event_type = PhoenixEventType(event_type_str)
                    except ValueError:
                        logging.warning(f"Type d'événement inconnu: '{event_type_str}'. Ignoré.")
                        continue

                    # Vérifier si un gestionnaire existe pour cet événement
                    if event_type in EVENT_HANDLERS:
                        handler = EVENT_HANDLERS[event_type]
                        logging.info(f"Déclenchement du gestionnaire pour {event_type.value}...")
                        await handler(event)
                    else:
                        logging.info(f"Aucun gestionnaire pour l'événement {event_type.value}. Ignoré.")
                    
                    # Mettre à jour le timestamp du dernier événement traité
                    last_processed_timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))

            else:
                logging.info("Aucun nouvel événement.")

            # Attendre avant le prochain polling
            time.sleep(15) # Polling toutes les 15 secondes

        except Exception as e:
            logging.error(f"Une erreur est survenue dans la boucle principale: {e}")
            logging.info("Attente de 60 secondes avant de réessayer...")
            time.sleep(60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())