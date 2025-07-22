import logging
import time
import google.generativeai as genai
import re
import json

from services.api_client import APIError
from models.letter_request import LetterRequest
from models.letter_response import LetterResponse
from models.coaching_report import CoachingReport
from utils.cache import generate_cache_key
from services.data_anonymizer import DataAnonymizer

# Cache en mémoire pour les lettres générées
_letter_cache: dict[str, LetterResponse] = {}

def nettoyer_contenu(contenu: str) -> str:
    """Nettoie le contenu pour éviter l'injection de prompt."""
    contenu_nettoye = re.sub(r'(ignore|oublie|nouvelle instruction)', '[REDACTED]', contenu, flags=re.IGNORECASE)
    return contenu_nettoye[:10000]

def build_reconversion_prompt(request: LetterRequest, cv_clean: str, annonce_clean: str) -> str:
    """
    Construit le prompt magistral spécialement optimisé pour les reconversions professionnelles.
    
    Ce prompt guide l'IA pour :
    - Identifier les compétences transférables (soft & hard skills)
    - Créer des ponts logiques convaincants
    - Valoriser la motivation et le potentiel
    - Adopter un ton authentique et percutant
    """
    
    # Base du prompt selon le tier utilisateur
    if request.user_tier == "premium_plus":
        expert_level = "Tu es Marie-Claire Dubois, experte en reconversion professionnelle de renommée internationale avec 25 ans d'expérience. Tu as accompagné plus de 3000 personnes dans leur transition de carrière et tu es l'auteure de 'L\'Art de la Reconversion Réussie'. Ton expertise est reconnue par les plus grands cabinets de recrutement."
        quality_instruction = "Tu vas créer une lettre de motivation d'exception qui fera la différence. Chaque phrase doit être ciselée, chaque argument pesé. Cette lettre doit être un chef-d'œuvre de persuasion."
    elif request.user_tier == "premium":
        expert_level = "Tu es Marie-Claire Dubois, consultante experte en reconversion professionnelle avec 15 ans d'expérience. Tu comprends parfaitement les défis et opportunités des transitions de carrière."
        quality_instruction = "Tu vas créer une lettre de motivation percutante et professionnelle qui met en valeur le parcours unique du candidat."
    else:  # free
        expert_level = "Tu es Marie-Claire, consultante en reconversion professionnelle expérimentée."
        quality_instruction = "Tu vas créer une lettre de motivation qui valorise le parcours de reconversion du candidat."

    # Construction du prompt principal - CORRECTION : suppression des triple quotes problématiques
    prompt = f"""{expert_level}

{quality_instruction}

 MISSION SPÉCIFIQUE : Reconversion Professionnelle
Le candidat passe de "{request.ancien_domaine}" vers "{request.nouveau_domaine}".
Cette transition n'est PAS un handicap, c'est un SUPER-POUVOIR à révéler.

 ANALYSE PRÉALABLE OBLIGATOIRE :

1.  DETECTIVE DES COMPÉTENCES TRANSFÉRABLES :
   • Identifie dans le CV TOUTES les compétences (techniques et humaines) réutilisables
   • Hard Skills : outils, méthodes, certifications, connaissances techniques
   • Soft Skills : leadership, gestion de crise, communication, adaptation, rigueur
   • Compétences cachées : ce que l'ancien métier a développé implicitement

2.  ARCHITECTE DE PONTS LOGIQUES :
   • Trouve les liens naturels entre l'ancien et le nouveau domaine
   • Explique POURQUOI cette expérience passée est un ATOUT unique
   • Montre comment les défis du passé préparent aux défis futurs
   • Transforme chaque "mais je n'ai pas d'expérience en X" en "j'apporte une perspective unique grâce à Y"

3.  STORYTELLER DE LA MOTIVATION :
   • Révèle le "déclic" de la reconversion (évolution naturelle, recherche de sens, passion découverte)
   • Montre que c'est un choix réfléchi, pas une fuite
   • Prouve la détermination par les actions concrètes (formations, projets, veille)

 STRUCTURE DE LA LETTRE (250-350 mots) :

**ACCROCHE MAGNÉTIQUE (2-3 lignes)**
Ouvre avec IMPACT. Évite "Je me permets de vous écrire". 
Commence par ce qui rend ce candidat unique dans sa transition.

**PARAGRAPHE 1 : Le Pont d'Excellence (70-90 mots)**
"Mon parcours de [X années] en [ancien domaine] m'a forgé des compétences directement transférables à [nouveau domaine] : [2-3 compétences concrètes]. Cette expérience unique me permet d'apporter [valeur spécifique] à votre équipe."

**PARAGRAPHE 2 : La Transformation Active (100-120 mots)**
Prouve l'engagement dans la reconversion :
- Formations suivies / en cours
- Projets personnels ou bénévoles
- Veille active, communautés rejointes
- Première réalisations concrètes
Montre que la reconversion est déjà en cours, pas juste une intention.

**PARAGRAPHE 3 : La Valeur Ajoutée Unique (60-80 mots)**
"Mon profil atypique est un atout : [perspective unique apportée]. Ma capacité d'adaptation prouvée et ma motivation profonde pour [nouveau domaine] me permettront de [contribution spécifique à l'entreprise]."

**CONCLUSION CALL-TO-ACTION (30-40 mots)**
Termine sur la valeur et l'envie de contribuer. Évite la formule bateau.

 STYLE ET TON ({request.ton_souhaite}) :
• AUTHENTIQUE : Évite le jargon RH, parle comme un humain passionné
• CONFIANT sans arrogance : "Je suis convaincu" plutôt que "j'espère"
• CONCRET : Chiffres, exemples, réalisations tangibles
• POSITIF : Focus sur ce qu'apporte le candidat, pas sur ce qui manque
• PERSONNALISÉ : Intègre les mots-clés de l'offre naturellement

 À ÉVITER ABSOLUMENT :
• "Malgré mon manque d'expérience en..."
• "Bien que je ne connaisse pas encore..."
• "Je souhaiterais me reconvertir..."
• Phrases négatives ou d'excuses
• Généralités creuses ("dynamique, motivé")

 COMPÉTENCES TRANSFÉRABLES IDENTIFIÉES :
{request.competences_transferables}

Utilise cette liste comme base, mais enrichis-la en analysant le CV."""

    # Ajout des insights entreprise si disponibles
    if request.company_insights:
        prompt += f"""

 INTELLIGENCE ENTREPRISE (À intégrer subtilement) :
• Valeurs clés : {', '.join(request.company_insights.get('valeurs', []))}
• Style de communication : {request.company_insights.get('ton_communication', 'professionnel')}
• Défis business : {', '.join(request.company_insights.get('defis_business', []))}
• Profil recherché : {request.company_insights.get('profil_candidat', 'polyvalent')}

Adapte le vocabulaire et les arguments pour résonner avec cette culture."""

    # Détails de l'offre si disponibles
    if request.offer_details:
        intitule = request.offer_details.get('intitule', 'ce poste')
        entreprise = request.offer_details.get('entreprise', {}).get('nom', 'votre entreprise')
        prompt += f"""

 CONTEXTE OFFRE :
• Poste : {intitule}
• Entreprise : {entreprise}
• Personnalise spécifiquement pour ce binôme poste/entreprise"""

    prompt += f"""

 DOCUMENTS À ANALYSER :

=== CV DU CANDIDAT ===
{cv_clean}

=== OFFRE D'EMPLOI ===
{annonce_clean}

 MAINTENANT, CRÉE LA LETTRE DE RECONVERSION PARFAITE !

Analyse d'abord, puis rédige une lettre qui transformera cette reconversion en argument de vente irrésistible. Le recruteur doit finir la lecture en pensant : "Cette personne apporte exactement la perspective unique dont nous avons besoin !"

LETTRE DE MOTIVATION :"""

    return prompt

def build_standard_prompt(request: LetterRequest, cv_clean: str, annonce_clean: str) -> str:
    """
    Construit le prompt standard pour les candidatures non-reconversion.
    Conserve la logique originale mais améliorée.
    """
    
    intitule_poste = request.offer_details.get('intitule', 'non spécifié') if request.offer_details else 'non spécifié'
    nom_entreprise = request.offer_details.get('entreprise', {}).get('nom', 'non spécifié') if request.offer_details else 'non spécifié'

    prompt_lines = []

    # Adaptation du prompt en fonction du niveau d'abonnement (user_tier)
    if request.user_tier == "premium_plus":
        prompt_lines.append(
            "Tu es Marie, une experte en ressources humaines de renommée internationale avec 20 ans d'expérience, "
            "spécialisée dans la rédaction de lettres de motivation d'élite et l'accompagnement stratégique des candidatures. "
            "Ton analyse est d'une profondeur inégalée, ton style est persuasif et ton argumentation est irréfutable. "
            "Chaque mot est choisi pour maximiser l'impact et la résonance avec le recruteur."
        )
        prompt_lines.append(
            f"Ta mission est de générer une lettre de motivation EXCEPTIONNELLE et hautement personnalisée pour le poste de {intitule_poste} chez {nom_entreprise} avec un ton {request.ton_souhaite}. "
            "Va au-delà de la simple rédaction : anticipe les attentes implicites du recruteur, crée un lien émotionnel fort et positionne le candidat comme la solution idéale à leurs besoins."
        )
    elif request.user_tier == "premium":
        prompt_lines.append(
            "Tu es Marie, une experte en ressources humaines avec 15 ans d'expérience, spécialisée dans la rédaction de lettres de motivation percutantes. "
        )
        prompt_lines.append(
            f"Ta mission est de générer une lettre de motivation convaincante et personnalisée pour le poste de {intitule_poste} chez {nom_entreprise} avec un ton {request.ton_souhaite}."
        )
    else:  # free tier
        prompt_lines.append(
            "Tu es Marie, une experte en ressources humaines, spécialisée dans la rédaction de lettres de motivation. "
        )
        prompt_lines.append(
            f"Ta mission est de générer une lettre de motivation pour le poste de {intitule_poste} chez {nom_entreprise} avec un ton {request.ton_souhaite}."
        )
    
    if request.company_insights:
        prompt_lines.append(
            "\n--- Insights sur l'entreprise (à intégrer subtilement) ---"
            f"Valeurs clés: {', '.join(request.company_insights.get('valeurs', []))}. "
            f"Ton de communication: {request.company_insights.get('ton_communication', 'non spécifié')}. "
            f"Défis business: {', '.join(request.company_insights.get('defis_business', []))}. "
            f"Profil candidat recherché: {request.company_insights.get('profil_candidat', 'non spécifié')}. "
            "Utilise ces informations pour adapter le style, le vocabulaire et les arguments de la lettre afin qu'elle résonne parfaitement avec la culture de l'entreprise."
        )

    prompt_lines.extend([
        "Avant de rédiger, suis ce processus de réflexion étape par étape:\n1. Analyse le CV pour identifier les expériences et compétences clés.\n2. Analyse l'annonce pour comprendre les exigences du poste et les mots-clés importants.\n3. Structure la lettre (introduction, pourquoi ce poste, pourquoi moi, conclusion) en intégrant les mots-clés de l'annonce et en valorisant le parcours du candidat.\n4. Adopte le ton demandé (formel, dynamique, etc.).",
        "Voici le CV :", "---", cv_clean, "---",
        "Voici l'annonce :", "---", annonce_clean, "---",
        "Objectif : Génère une lettre de 250-350 mots, structurée (intro, pourquoi ce poste, pourquoi moi, conclusion), qui utilise les mots-clés de l'annonce et adopte un ton humble mais confiant.",
        "Génère la lettre ci-dessous ⬇️"
    ])
    
    return "\n".join(prompt_lines)

from tenacity import retry, stop_after_attempt, wait_fixed, stop_after_delay, retry_if_exception_type
import google.generativeai as genai
import logging
import time
import re
import json
from typing import Optional

from .api_client import APIError
from .data_anonymizer import DataAnonymizer
from .file_service import FileProcessingError, extract_cv_content, extract_annonce_content, nettoyer_contenu
from ..models.letter_request import LetterRequest
from ..models.letter_response import LetterResponse
from ..utils.cache import generate_cache_key, _letter_cache

# ... (autres fonctions et code)

@retry(stop=(stop_after_attempt(3) | stop_after_delay(60)), wait=wait_fixed(2), retry=retry_if_exception_type(APIError))
def generer_lettre(request: LetterRequest) -> LetterResponse:
    """
    Génère la lettre de motivation en utilisant le modèle Google Gemini.
    Utilise automatiquement le prompt spécialisé reconversion si nécessaire.
    """
    # Instancier l'anonymiseur
    anonymizer = DataAnonymizer()

    # Anonymiser le contenu du CV et de l'annonce avant de les nettoyer et de les envoyer à l'IA
    cv_anonymized = anonymizer.anonymize_text(request.cv_contenu)
    annonce_anonymized = anonymizer.anonymize_text(request.annonce_contenue)

    # Générer une clé de cache à partir de la requête anonymisée
    anonymized_request_for_cache = request.model_dump()
    anonymized_request_for_cache['cv_contenu'] = cv_anonymized
    anonymized_request_for_cache['annonce_contenu'] = annonce_anonymized
    cache_key = generate_cache_key(anonymized_request_for_cache)

    # Vérifier si la réponse est déjà en cache
    if cache_key in _letter_cache:
        logging.info("Lettre récupérée du cache.")
        return _letter_cache[cache_key]

    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # Nettoyer le contenu anonymisé
    cv_clean = nettoyer_contenu(cv_anonymized)
    annonce_clean = nettoyer_contenu(annonce_anonymized)

    # Choisir le prompt approprié selon le type de candidature
    if request.est_reconversion:
        logging.info("Utilisation du prompt spécialisé reconversion")
        prompt = build_reconversion_prompt(request, cv_clean, annonce_clean)
    else:
        logging.info("Utilisation du prompt standard")
        prompt = build_standard_prompt(request, cv_clean, annonce_clean)

    response = model.generate_content(prompt, request_options={"timeout": 60}) # Ajout du timeout ici
    if not response.text:
        raise APIError("Réponse API vide pour la génération de lettre.")

    lettre_generee = response.text.strip()
    
    # Sauvegarder la réponse en cache
    _letter_cache[cache_key] = LetterResponse(lettre_generee=lettre_generee)
    logging.info("Lettre générée et mise en cache.")
    return _letter_cache[cache_key]

def evaluate_letter(letter_content: str, annonce_content: str, max_retries: int = 3) -> CoachingReport:
    """Évalue la lettre de motivation générée par rapport à l'annonce et retourne un rapport de coaching."""
    anonymizer = DataAnonymizer() # Instancier l'anonymiseur

    for tentative in range(max_retries):
        try:
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            # Anonymiser le contenu de la lettre et de l'annonce avant de les envoyer à l'IA
            letter_anonymized = anonymizer.anonymize_text(letter_content)
            annonce_anonymized = anonymizer.anonymize_text(annonce_content)

            prompt = f"""
            Tu es un coach en carrière expert en analyse de lettres de motivation et d'annonces d'emploi.
            Ton objectif est d'évaluer une lettre de motivation par rapport à une annonce d'emploi.

            Critères d'évaluation (retourne un score de 0 à 10 pour chaque, et une suggestion d'amélioration):
            1.  **Optimisation des mots-clés (pertinence ATS)**: La lettre utilise-t-elle les mots-clés importants de l'annonce ?
            2.  **Storytelling et fluidité**: La lettre raconte-t-elle une histoire convaincante ? Est-elle facile à lire ?
            3.  **Cohérence du ton**: Le ton de la lettre est-il approprié pour le poste et l'entreprise ?
            4.  **Appel à l'action clair**: La lettre invite-t-elle clairement à une prochaine étape (entretien) ?

            Retourne un objet JSON avec les clés suivantes:
            -   `score_global`: Un score global sur 10.
            -   `evaluations`: Un dictionnaire où chaque clé est le critère (ex: "optimisation_mots_cles") et la valeur est un objet avec `score` (int) et `suggestion` (str).
            -   `suggestions_generales`: Une liste de suggestions générales pour améliorer la lettre.

            Lettre de motivation à évaluer:
            ---
            {letter_anonymized}
            ---

            Annonce d'emploi:
            ---
            {annonce_anonymized}
            ---
            """
            response = model.generate_content(prompt)
            if not response.text:
                raise APIError("Réponse API vide pour l'évaluation de la lettre.")
            
            json_match = re.search(r'```json\n(.*)\n```', response.text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                json_string = response.text

            evaluation_data = json.loads(json_string)
            
            # Mapper les données JSON au modèle CoachingReport
            suggestions_list = [f"{k}: {v['suggestion']}" for k, v in evaluation_data.get('evaluations', {}).items()] + evaluation_data.get('suggestions_generales', [])
            rationale_dict = {k: f"Score: {v['score']}, Suggestion: {v['suggestion']}" for k, v in evaluation_data.get('evaluations', {}).items()}

            logging.info("Évaluation de la lettre réussie.")
            return CoachingReport(
                score=evaluation_data.get('score_global', 0.0),
                suggestions=suggestions_list,
                rationale=rationale_dict
            )

        except json.JSONDecodeError as e:
            logging.error(f"Erreur de décodage JSON de la réponse de l'IA (tentative {tentative + 1}/{max_retries}): {e}. Réponse brute: {response.text}")
            if tentative < max_retries - 1:
                time.sleep(2 ** tentative)
            else:
                raise APIError(f"Échec du décodage JSON après {max_retries} tentatives.")
        except Exception as e:
            logging.warning(f"Erreur lors de l'évaluation de la lettre (tentative {tentative + 1}/{max_retries}): {e}")
            if tentative < max_retries - 1:
                time.sleep(2 ** tentative)
            else:
                raise APIError(f"Échec de l'évaluation de la lettre après {max_retries} tentatives.")
    raise APIError("Toutes les tentatives d'évaluation de la lettre ont échoué.")

def extraire_mots_cles_annonce(annonce_contenu: str) -> list[str]:
    """Extrait les mots-clés pertinents d'une annonce d'emploi."""
    # NOTE POUR L'IA : La liste de mots vides originale (plus de 500 mots) a été retirée pour alléger le contexte.
    mots_vides = set([ "le", "la", "les", "de", "et", "en", "vous", "pour", "un", "une", "des", "que", "qui", "dans", "avec", "sur", "votre", "nous", "au", "aux", "ce", "cette", "par", "plus", "pas", "je", "tu", "il", "elle", "on", "ils", "elles", "se", "son", "sa", "ses", "mon", "ma", "mes", "ton", "ta", "tes", "notre", "nos", "votre", "vos", "leur", "leurs", "a", "à", "y", "d'un", "d'une", "l'un", "l'une", "auquel", "duquel", "lequel", "laquelle", "lesquels", "lesquelles", "etc"])
    mots = re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', annonce_contenu.lower())
    mots_cles = [mot for mot in mots if mot not in mots_vides and len(mot) > 2]
    return list(set(mots_cles))