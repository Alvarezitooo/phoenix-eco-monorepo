import logging
import google.generativeai as genai
import json
import re
import time # Ajout de l'importation de time

from services.api_client import APIError
from models.user_profile import UserProfile
from models.reconversion_plan import ReconversionPlan

def generate_reconversion_plan(profile: UserProfile, target_role: str, max_retries: int = 3) -> ReconversionPlan:
    """Génère un plan de reconversion détaillé basé sur le profil de l'utilisateur et le rôle cible."""
    for tentative in range(max_retries):
        try:
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            prompt = f"""
            Tu es un coach en carrière spécialisé dans la reconversion professionnelle.
            Ton objectif est de créer un plan de reconversion détaillé et réaliste pour un individu.

            Voici le profil de l'utilisateur:
            - Compétences actuelles: {', '.join(profile.current_skills)}
            - Expérience actuelle: {profile.current_experience}
            - Aspirations: {profile.aspirations}

            Rôle cible de reconversion: {target_role}

            Génère un plan de reconversion structuré au format JSON. Le JSON doit contenir les clés suivantes:
            -   `goal`: L'objectif de reconversion (chaîne de caractères).
            -   `summary`: Un résumé concis du plan (chaîne de caractères).
            -   `skills_gap_analysis`: Une analyse détaillée des écarts de compétences entre le profil actuel et le rôle cible (chaîne de caractères, optionnel).
            -   `steps`: Une liste d'étapes. Chaque étape doit être un objet avec les clés:
                -   `title`: Titre de l'étape (ex: "Formation Python", "Certification Cloud").
                -   `description`: Description détaillée de l'étape.
                -   `duration_weeks`: Durée estimée de l'étape en semaines (entier, optionnel).
                -   `resources`: Liste de ressources suggérées. Chaque ressource doit être un objet avec les clés:
                    -   `type`: Type de ressource (chaîne de caractères parmi "cours_en_ligne", "livre", "certification", "mentorat", "projet_pratique", "article", "outil", "autre").
                    -   `name`: Nom de la ressource.
                    -   `link`: Lien vers la ressource (URL, optionnel).
                    -   `description`: Description de la ressource (optionnel).
            -   `estimated_total_duration_weeks`: Durée totale estimée du plan en semaines (entier, optionnel).
            -   `success_probability`: Probabilité de succès estimée (flottant entre 0 et 1, optionnel).

            Assure-toi que le JSON est valide et complet.
            """
            response = model.generate_content(prompt)
            if not response.text:
                raise APIError("Réponse API vide pour la génération du plan de reconversion.")
            
            json_match = re.search(r'```json\n(.*)\n```', response.text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                json_string = response.text

            plan_data = json.loads(json_string)
            
            logging.info("Plan de reconversion généré avec succès.")
            return ReconversionPlan(**plan_data)

        except json.JSONDecodeError as e:
            logging.error(f"Erreur de décodage JSON de la réponse de l'IA (tentative {tentative + 1}/{max_retries}): {e}. Réponse brute: {response.text}")
            if tentative < max_retries - 1:
                time.sleep(2 ** tentative)
            else:
                raise APIError(f"Échec du décodage JSON après {max_retries} tentatives.")
        except Exception as e:
            logging.warning(f"Erreur lors de la génération du plan de reconversion (tentative {tentative + 1}/{max_retries}): {e}")
            if tentative < max_retries - 1:
                time.sleep(2 ** tentative)
            else:
                raise APIError(f"Échec de la génération du plan de reconversion après {max_retries} tentatives.")
    raise APIError("Toutes les tentatives de génération de plan de reconversion ont échoué.")
