import logging
from typing import Optional

from config.settings import Settings
from core.entities.letter import GenerationRequest, UserTier
from shared.interfaces.prompt_interface import PromptServiceInterface

logger = logging.getLogger(__name__)


def truncate_content(content: str, max_chars: int = 15000) -> str:
    """
    Tronque le contenu pour éviter les prompts trop longs.
    
    Args:
        content: Contenu à tronquer
        max_chars: Nombre maximum de caractères
        
    Returns:
        str: Contenu tronqué avec indication si nécessaire
    """
    if not content:
        return ""
        
    if len(content) <= max_chars:
        return content
        
    # Tronquer au dernier espace pour éviter de couper un mot
    truncated = content[:max_chars].rsplit(' ', 1)[0]
    return f"{truncated}...\n\n[CONTENU TRONQUÉ POUR OPTIMISATION - INFORMATIONS PRINCIPALES CONSERVÉES]"


class PromptService(PromptServiceInterface):
    """Service pour la construction des prompts destinés à l'IA."""

    def __init__(self, settings: Settings):
        self.settings = settings
        logger.info("PromptService initialized")

    def build_letter_prompt(self, request: GenerationRequest) -> str:
        """
        Construit le prompt pour la génération de lettre de motivation.
        """
        # Tronquer le contenu long pour éviter de dépasser les limites de l'API
        cv_content_truncated = truncate_content(request.cv_content or "", max_chars=12000)
        job_offer_truncated = truncate_content(request.job_offer_content or "", max_chars=8000)
        
        # Construction du prompt avec contenu tronqué
        prompt = f"""
        Rédige une lettre de motivation percutante pour un poste de {request.job_title} chez {request.company_name}.
        Voici le contenu de l'offre d'emploi:
        {job_offer_truncated}

        Voici le contenu du CV du candidat:
        {cv_content_truncated}

        Le candidat souhaite adopter un ton {request.tone.value}.
        {f"Le candidat est en reconversion et ses compétences transférables sont: {request.transferable_skills}" if request.is_career_change else ""}

        La lettre doit être concise, professionnelle et mettre en avant l'adéquation entre le profil du candidat et les exigences du poste.
        """
        
        # Log de la taille du prompt pour monitoring
        prompt_length = len(prompt)
        logger.info(f"Generated prompt length: {prompt_length} characters")
        
        if prompt_length > 90000:  # Seuil de sécurité avant la limite de 100k
            logger.warning(f"Prompt très long ({prompt_length} chars), risque de dépassement")
        
        return prompt.strip()

    def build_analysis_prompt(
        self, letter_content: str, generation_request: GenerationRequest
    ) -> str:
        """
        Construit le prompt pour l'analyse d'une lettre de motivation.
        """
        # Exemple de construction de prompt pour l'analyse
        prompt = f"""
        Analyse la lettre de motivation suivante et attribue-lui un score sur 10.
        Identifie les points forts et les points d'amélioration.

        Lettre de motivation:
        {letter_content}

        Contexte de la génération:
        Poste: {generation_request.job_title}
        Entreprise: {generation_request.company_name}
        Ton souhaité: {generation_request.tone.value}

        Format de la réponse:
        Score: [score]/10
        Points forts:
        - [Point fort 1]
        - [Point fort 2]
        Points d'amélioration:
        - [Amélioration 1]
        - [Amélioration 2]
        """
        return prompt.strip()

    def build_skills_suggestion_prompt(self, old_domain: str, new_domain: str) -> str:
        """
        Construit le prompt pour la suggestion de compétences transférables.
        """
        prompt = f"""
        Je suis en reconversion professionnelle. Mon ancien domaine d'activité était "{old_domain}" et je souhaite me reconvertir dans le domaine "{new_domain}".
        Liste 5 à 10 compétences clés de mon ancien domaine qui sont transférables et pertinentes pour mon nouveau domaine.
        Présente ces compétences sous forme de liste à puces, avec une brève explication de leur pertinence pour le nouveau domaine.
        Sois concis et utilise un langage professionnel.
        """
        return prompt.strip()
