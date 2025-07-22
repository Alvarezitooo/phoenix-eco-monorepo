import os
import logging
import time
from typing import Optional, Dict, Union
import requests
import google.generativeai as genai
import re
import json
from tenacity import retry, stop_after_attempt, wait_fixed, stop_after_delay, retry_if_exception_type
from collections import defaultdict
from datetime import datetime, timedelta

# --- Exceptions Personnalisées ---
class APIError(Exception):
    """Exception personnalisée pour les erreurs API."""
    pass

class RateLimiter:
    def __init__(self, max_requests=10, window=timedelta(hours=1)):
        self.requests = defaultdict(list)
        self.max_requests = max_requests
        self.window = window

    def is_allowed(self, user_id: str) -> bool:
        now = datetime.now()
        # Nettoyer anciennes requêtes
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window
        ]

        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
        return False

# --- Configuration des APIs ---
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
FRANCETRAVAIL_CLIENT_ID = os.getenv('FRANCETRAVAIL_CLIENT_ID')
FRANCETRAVAIL_CLIENT_SECRET = os.getenv('FRANCETRAVAIL_CLIENT_SECRET')
FRANCETRAVAIL_API_BASE_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres"
FRANCETRAVAIL_AUTH_URL = "https://francetravail.io/connexion/oauth2/access_token"

# Initialisation des clients/configurations
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Initialisation du Rate Limiter
api_rate_limiter = RateLimiter(max_requests=5, window=timedelta(minutes=1)) # Exemple: 5 requêtes par minute

# Variable globale pour le token France Travail
FRANCETRAVAIL_ACCESS_TOKEN: Dict[str, Optional[Union[str, float]]] = {'value': None, 'expires_at': 0.0}

# --- Fonctions de Service API ---

def get_france_travail_access_token() -> str:
    """Obtient un jeton d'accès depuis l'API d'authentification de France Travail."""
    global FRANCETRAVAIL_ACCESS_TOKEN
    if FRANCETRAVAIL_ACCESS_TOKEN['value'] and time.time() < FRANCETRAVAIL_ACCESS_TOKEN['expires_at']:
        return FRANCETRAVAIL_ACCESS_TOKEN['value']

    logging.info("Récupération d'un nouveau jeton d'accès France Travail...")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": FRANCETRAVAIL_CLIENT_ID,
        "client_secret": FRANCETRAVAIL_CLIENT_SECRET,
        "scope": "api_offresdemploiv2 o2dsoffre"
    }
    try:
        response = requests.post(f"{FRANCETRAVAIL_AUTH_URL}?realm=%2Fpartenaire", headers=headers, data=data, timeout=10)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in', 0)
        if not access_token:
            raise APIError("Jeton d'accès non trouvé dans la réponse de l'API d'authentification.")
        FRANCETRAVAIL_ACCESS_TOKEN['value'] = access_token
        FRANCETRAVAIL_ACCESS_TOKEN['expires_at'] = time.time() + expires_in - 60
        logging.info("Jeton d'accès France Travail récupéré avec succès.")
        return access_token
    except requests.RequestException as e:
        logging.error(f"Erreur lors de la récupération du jeton d'accès France Travail: {e}")
        raise APIError(f"Erreur API France Travail (authentification): {e}")

@retry(stop=(stop_after_attempt(3) | stop_after_delay(60)), wait=wait_fixed(2), retry=retry_if_exception_type(requests.RequestException))
def get_france_travail_offer_details(offer_id: str) -> Optional[dict]:
    """Récupère les détails d'une offre d'emploi depuis l'API France Travail."""
    if not api_rate_limiter.is_allowed("default_user"): # Utilisation d'un user_id générique
        raise APIError("Limite de requêtes atteinte pour la récupération des détails d'offre France Travail. Veuillez réessayer plus tard.")
    access_token = get_france_travail_access_token()
    url = f"{FRANCETRAVAIL_API_BASE_URL}/{offer_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    logging.info(f"Tentative de récupération des détails de l'offre {offer_id}...")
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    logging.info(f"Détails de l'offre {offer_id} récupérés avec succès.")
    return response.json()

@retry(stop=(stop_after_attempt(3) | stop_after_delay(60)), wait=wait_fixed(2), retry=retry_if_exception_type(APIError))
def suggerer_competences_transferables(ancien_domaine: str, nouveau_domaine: str) -> str:
    """Suggère des compétences transférables entre deux domaines d'activité en utilisant Google Gemini."""
    if not api_rate_limiter.is_allowed("default_user"): # Utilisation d'un user_id générique
        raise APIError("Limite de requêtes atteinte pour les compétences transférables. Veuillez réessayer plus tard.")
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    prompt = f"""
    Tu es un expert en ressources humaines spécialisé dans la reconversion professionnelle.
    Ta mission est de suggérer une liste de compétences clés transférables entre deux domaines d'activité.

    Ancien domaine d'activité : {ancien_domaine}
    Nouveau domaine d'activité souhaité : {nouveau_domaine}

    Liste les compétences transférables pertinentes, séparées par des virgules.
    Exemple : "Gestion de projet, Communication, Analyse de données, Résolution de problèmes, Adaptabilité"
    """
    response = model.generate_content(prompt, request_options={"timeout": 30})
    if not response.text or len(response.text) < 10:
        raise APIError("Réponse API invalide ou trop courte pour les compétences transférables.")
    logging.info("Compétences transférables suggérées avec succès.")
    return response.text.strip()

@retry(stop=(stop_after_attempt(3) | stop_after_delay(60)), wait=wait_fixed(2), retry=retry_if_exception_type((APIError, json.JSONDecodeError)))
def analyser_culture_entreprise(about_page: str, linkedin_posts: str) -> dict:
    """Analyse la culture d'entreprise via Google Gemini et retourne des insights structurés."""
    if not api_rate_limiter.is_allowed("default_user"): # Utilisation d'un user_id générique
        raise APIError("Limite de requêtes atteinte pour l'analyse de culture d'entreprise. Veuillez réessayer plus tard.")
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    prompt = f"""
    Tu es un expert en analyse de culture d'entreprise.
    Analyse le texte suivant et les posts LinkedIn pour déterminer :
    1.  Les 3 valeurs principales de l'entreprise.
    2.  Son ton de communication (ex: formel, décontracté, innovant, traditionnel).
    3.  Ses défis business actuels ou ses axes de développement majeurs.
    4.  Le profil de candidat qu'elle recherche probablement (ex: autonome, collaboratif, créatif, rigoureux).

    Retourne ces informations au format JSON, avec les clés 'valeurs', 'ton_communication', 'defis_business', 'profil_candidat'.
    Les valeurs et défis doivent être des listes de chaînes de caractères.

    Contenu de la page 'À propos' de l'entreprise :
    ---
    {about_page}
    ---

    Posts LinkedIn récents (séparés par des tirets) :
    ---
    {linkedin_posts}
    ---
    """
    response = model.generate_content(prompt, request_options={"timeout": 30})
    if not response.text:
        raise APIError("Réponse API vide pour l'analyse de culture d'entreprise.")
    
    json_match = re.search(r'```json\n(.*)\n```', response.text, re.DOTALL)
    if json_match:
        json_string = json_match.group(1)
    else:
        json_string = response.text

    insights = json.loads(json_string)
    logging.info("Analyse de culture d'entreprise réussie.")
    return insights
