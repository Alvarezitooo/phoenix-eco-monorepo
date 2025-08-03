"""
🔥 Phoenix CV - Intégration Phoenix Shared Auth
Intégration avec le système d'authentification partagé Phoenix

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import os
import requests
import logging
from typing import Dict, Optional, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class PhoenixAuthIntegration:
    """
    Service d'intégration avec Phoenix Shared Auth.
    Gère la synchronisation des statuts utilisateurs après paiements Stripe.
    """
    
    def __init__(self):
        load_dotenv()
        self.auth_service_url = os.getenv("PHOENIX_AUTH_SERVICE_URL", "https://phoenix-auth.herokuapp.com")
        self.auth_api_key = os.getenv("PHOENIX_AUTH_API_KEY")
        
        if not self.auth_api_key:
            logger.warning("PHOENIX_AUTH_API_KEY non configuré - mode dégradé")
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_api_key}" if self.auth_api_key else "",
            "User-Agent": "Phoenix-CV/1.0"
        }
        
        logger.info("Service Phoenix Auth Integration initialisé")

    def update_user_subscription(
        self, 
        phoenix_user_id: str, 
        plan_id: str, 
        subscription_id: str,
        status: str = "active"
    ) -> bool:
        """
        Met à jour le statut d'abonnement d'un utilisateur.
        
        Args:
            phoenix_user_id: ID utilisateur Phoenix
            plan_id: ID du plan (pro, enterprise)
            subscription_id: ID de l'abonnement Stripe
            status: Statut de l'abonnement
            
        Returns:
            True si succès, False sinon
        """
        if not self.auth_api_key:
            logger.warning(f"Impossible de mettre à jour l'utilisateur {phoenix_user_id} - API Key manquante")
            return False
            
        try:
            update_data = {
                "phoenix_user_id": phoenix_user_id,
                "subscription_plan": plan_id,
                "subscription_id": subscription_id,
                "subscription_status": status,
                "service": "phoenix_cv"
            }
            
            response = requests.post(
                f"{self.auth_service_url}/api/subscription/update",
                json=update_data,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Statut utilisateur {phoenix_user_id} mis à jour avec succès - Plan: {plan_id}")
                return True
            else:
                logger.error(f"Erreur mise à jour utilisateur {phoenix_user_id}: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau mise à jour utilisateur {phoenix_user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur inattendue mise à jour utilisateur {phoenix_user_id}: {e}")
            return False

    def get_user_subscription_status(self, phoenix_user_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le statut d'abonnement d'un utilisateur.
        
        Args:
            phoenix_user_id: ID utilisateur Phoenix
            
        Returns:
            Données de l'abonnement ou None
        """
        if not self.auth_api_key:
            logger.warning(f"Impossible de récupérer le statut de l'utilisateur {phoenix_user_id} - API Key manquante")
            return None
            
        try:
            response = requests.get(
                f"{self.auth_service_url}/api/user/{phoenix_user_id}/subscription",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Statut utilisateur {phoenix_user_id} récupéré avec succès")
                return data
            elif response.status_code == 404:
                logger.info(f"Utilisateur {phoenix_user_id} non trouvé ou pas d'abonnement")
                return None
            else:
                logger.error(f"Erreur récupération utilisateur {phoenix_user_id}: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau récupération utilisateur {phoenix_user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue récupération utilisateur {phoenix_user_id}: {e}")
            return None

    def cancel_user_subscription(self, phoenix_user_id: str, subscription_id: str) -> bool:
        """
        Annule l'abonnement d'un utilisateur.
        
        Args:
            phoenix_user_id: ID utilisateur Phoenix
            subscription_id: ID de l'abonnement Stripe
            
        Returns:
            True si succès, False sinon
        """
        if not self.auth_api_key:
            logger.warning(f"Impossible d'annuler l'abonnement de l'utilisateur {phoenix_user_id} - API Key manquante")
            return False
            
        try:
            cancel_data = {
                "phoenix_user_id": phoenix_user_id,
                "subscription_id": subscription_id,
                "service": "phoenix_cv",
                "reason": "stripe_cancellation"
            }
            
            response = requests.post(
                f"{self.auth_service_url}/api/subscription/cancel",
                json=cancel_data,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Abonnement utilisateur {phoenix_user_id} annulé avec succès")
                return True
            else:
                logger.error(f"Erreur annulation abonnement {phoenix_user_id}: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau annulation abonnement {phoenix_user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur inattendue annulation abonnement {phoenix_user_id}: {e}")
            return False

    def log_subscription_event(
        self, 
        phoenix_user_id: str, 
        event_type: str, 
        details: Dict[str, Any]
    ) -> bool:
        """
        Log un événement d'abonnement pour audit.
        
        Args:
            phoenix_user_id: ID utilisateur Phoenix
            event_type: Type d'événement
            details: Détails de l'événement
            
        Returns:
            True si succès, False sinon
        """
        if not self.auth_api_key:
            return False
            
        try:
            log_data = {
                "phoenix_user_id": phoenix_user_id,
                "service": "phoenix_cv",
                "event_type": event_type,
                "details": details,
                "timestamp": details.get("timestamp")
            }
            
            response = requests.post(
                f"{self.auth_service_url}/api/audit/subscription-event",
                json=log_data,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Événement {event_type} loggé pour utilisateur {phoenix_user_id}")
                return True
            else:
                logger.warning(f"Erreur log événement {event_type}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur log événement {event_type}: {e}")
            return False


# Instance globale
phoenix_auth = PhoenixAuthIntegration()