"""Service métier pour la génération de lettres de motivation."""

import logging
from datetime import datetime
from typing import Optional
try:
    import streamlit as st
except Exception:  # pragma: no cover - allow tests without streamlit installed
    class _Stub:
        def cache_data(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    st = _Stub()  # type: ignore

from core.entities.letter import GenerationRequest, Letter, UserTier
from core.services.job_offer_parser import JobOfferParser
from core.services.letter_analyzer import LetterAnalysisResult, LetterAnalyzer
from core.services.user_limit_manager import UserLimitManager
from shared.exceptions.specific_exceptions import (
    AIServiceError,
    LetterGenerationError,
    ValidationError,
)
from tenacity import RetryError
from shared.interfaces.ai_interface import AIServiceInterface
from shared.interfaces.prompt_interface import PromptServiceInterface
from shared.interfaces.validation_interface import ValidationServiceInterface
from utils.monitoring import track_api_call

# Import Event Bridge pour data pipeline
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
from phoenix_event_bridge import PhoenixEventBridge, PhoenixEventData, PhoenixEventType

logger = logging.getLogger(__name__)


class LetterService:
    """Service orchestrant la génération de lettres avec architecture refactorisée."""

    def __init__(
        self,
        ai_service: AIServiceInterface,
        validation_service: ValidationServiceInterface,
        prompt_service: PromptServiceInterface,
        session_manager,
    ):
        """
        Initialise le service de génération de lettres.

        Args:
            ai_service: Service d'IA pour la génération
            validation_service: Service de validation des données
            prompt_service: Service de construction des prompts
            session_manager: Gestionnaire de session pour les données utilisateur
        """
        self._ai_service = ai_service
        self._validation_service = validation_service
        self._prompt_service = prompt_service
        
        # Initialiser Event Bridge pour data pipeline
        self._event_bridge = PhoenixEventBridge()

        # Services spécialisés refactorisés
        self._job_parser = JobOfferParser()
        self._letter_analyzer = LetterAnalyzer(ai_service, prompt_service)
        self._limit_manager = UserLimitManager(session_manager)

        logger.info("LetterService initialized with refactored architecture")

    def generate_letter(self, request: GenerationRequest, user_id: str) -> Letter:
        """
        Génère une lettre de motivation personnalisée.

        Args:
            request: Requête de génération validée
            user_id: Identifiant de l'utilisateur

        Returns:
            Letter: Lettre générée avec métadonnées

        Raises:
            ValidationError: Si les données sont invalides
            LetterGenerationError: Si la génération échoue
            AIServiceError: Si le service IA échoue
        """
        try:
            # IMPORTANT: ValidationError doit être propagée, pas transformée
            self._validation_service.validate_generation_request(request)

            # Vérification thread-safe de la limite de génération
            self._limit_manager.check_generation_limit(request.user_tier, user_id)

            logger.info(
                f"Starting letter generation for user {user_id}",
                extra={
                    "user_tier": request.user_tier.value,
                    "is_career_change": request.is_career_change,
                    "tone": request.tone.value if request.tone else "default",
                },
            )

            # Construction du prompt
            prompt = self._prompt_service.build_letter_prompt(request)

            # Génération via IA
            try:
                content = self._ai_service.generate_content(
                    prompt=prompt,
                    user_tier=request.user_tier,
                    max_tokens=2000,
                    temperature=0.7,
                )
            except (AIServiceError, RetryError) as e:
                # Gérer les erreurs d'IA et les erreurs de retry
                logger.error(f"AI service error: {e}")
                if isinstance(e, RetryError) and e.last_attempt:
                    original_error = e.last_attempt.exception()
                    raise LetterGenerationError(f"Service temporairement indisponible: {original_error}")
                else:
                    raise LetterGenerationError(f"Erreur du service IA: {e}")

            # Création de l'entité Letter
            letter = Letter(
                content=content,
                generation_request=request,
                created_at=datetime.now(),
                user_id=user_id,
            )

            # Mettre à jour le compteur de manière thread-safe
            self._limit_manager.increment_generation_count(request.user_tier, user_id)

            # 🔥 PUBLIER ÉVÉNEMENT DANS DATA PIPELINE
            try:
                event_data = PhoenixEventData(
                    event_type=PhoenixEventType.LETTER_GENERATED,
                    user_id=user_id,
                    app_source="phoenix-letters",
                    payload={
                        "job_title": request.job_title,
                        "company_name": request.company_name,
                        "user_tier": request.user_tier.value,
                        "is_career_change": request.is_career_change,
                        "letter_length": len(content),
                        "generation_time": datetime.now().isoformat()
                    },
                    metadata={
                        "prompt_tokens": len(prompt),
                        "response_tokens": len(content),
                        "tone": request.tone.value if request.tone else "default"
                    }
                )
                # Publier l'événement (async dans un thread séparé pour ne pas bloquer)
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Si on est déjà dans un event loop, on schedule la tâche
                        asyncio.create_task(self._event_bridge.publish_event(event_data))
                    else:
                        # Sinon on run dans le loop courant
                        asyncio.run(self._event_bridge.publish_event(event_data))
                except Exception:
                    # Fallback: run dans un nouveau thread
                    asyncio.run(self._event_bridge.publish_event(event_data))
                    
                logger.info(f"✅ Event LETTER_GENERATED published for user {user_id}")
            except Exception as e:
                # Event publishing ne doit pas faire crasher la génération
                logger.warning(f"⚠️ Failed to publish event: {e}")

            logger.info(f"Letter generated successfully for user {user_id}")
            return letter

        except ValidationError:
            # ValidationError doit être propagée telle quelle
            raise
        except AIServiceError:
            # Déjà gérée dans le try interne
            raise
        except LetterGenerationError:
            # Déjà une LetterGenerationError, on la propage
            raise
        except Exception as e:
            # Seulement les erreurs vraiment inattendues
            logger.exception(f"Unexpected error in letter generation: {e}")
            raise LetterGenerationError(f"Erreur système inattendue: {str(e)}")

    def analyze_letter(
        self, letter: Letter, user_tier: UserTier
    ) -> LetterAnalysisResult:
        """
        Analyse une lettre générée (fonctionnalité premium) avec service spécialisé.

        Args:
            letter: Lettre à analyser
            user_tier: Niveau d'abonnement de l'utilisateur

        Returns:
            LetterAnalysisResult: Analyse détaillée et structurée de la lettre

        Raises:
            ValidationError: Si l'utilisateur n'a pas accès à cette fonction
            LetterGenerationError: Si l'analyse échoue
        """
        # Vérification des droits
        if user_tier == UserTier.FREE:
            raise ValidationError(
                "L'analyse de lettre est réservée aux utilisateurs Premium"
            )

        # Délégation au service spécialisé
        return self._letter_analyzer.analyze_letter(letter, user_tier)

    def extract_job_details_from_offer(
        self, job_offer_content: str
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Extrait le titre du poste et le nom de l'entreprise de manière sécurisée.

        Args:
            job_offer_content: Contenu de l'offre d'emploi

        Returns:
            tuple: (job_title, company_name) ou (None, None) si extraction échoue
        """
        try:
            job_details = self._job_parser.extract_job_details(job_offer_content)
            return job_details.job_title, job_details.company_name
        except Exception as e:
            logger.error(f"Job details extraction failed: {e}")
            return None, None

    @track_api_call("suggest_transferable_skills")
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def suggest_transferable_skills(
        _self, old_domain: str, new_domain: str, user_tier: UserTier
    ) -> str:
        """
        Suggère des compétences transférables basées sur les domaines.

        Args:
            old_domain: Ancien domaine professionnel.
            new_domain: Nouveau domaine professionnel.
            user_tier: Niveau d'abonnement de l'utilisateur.

        Returns:
            str: Suggestions de compétences transférables.

        Raises:
            AIServiceError: Si le service IA échoue.
        """
        try:
            prompt = _self._prompt_service.build_skills_suggestion_prompt(
                old_domain, new_domain
            )
            suggestions = _self._ai_service.generate_content(
                prompt=prompt, user_tier=user_tier, max_tokens=500, temperature=0.7
            )
            return suggestions
        except (AIServiceError, RetryError) as e:
            logger.error(f"AI service error during skills suggestion: {e}")
            if isinstance(e, RetryError) and e.last_attempt:
                original_error = e.last_attempt.exception()
                raise AIServiceError(f"Service de suggestions temporairement indisponible: {original_error}")
            else:
                raise AIServiceError(f"Erreur du service IA lors de la suggestion de compétences: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in skills suggestion: {e}")
            raise LetterGenerationError(
                f"Erreur inattendue lors de la suggestion de compétences: {str(e)}"
            )

    def get_remaining_generations(self, user_tier: UserTier) -> Optional[int]:
        """
        Retourne le nombre de générations restantes pour un utilisateur.

        Args:
            user_tier: Niveau d'abonnement de l'utilisateur

        Returns:
            Optional[int]: Nombre de générations restantes (None pour Premium)
        """
        return self._limit_manager.get_remaining_generations(user_tier)

    def get_analysis_summary(self, analysis_result: LetterAnalysisResult) -> dict:
        """
        Génère un résumé de l'analyse pour l'affichage.

        Args:
            analysis_result: Résultat d'analyse structuré

        Returns:
            dict: Résumé formaté de l'analyse
        """
        return self._letter_analyzer.get_analysis_summary(analysis_result)
