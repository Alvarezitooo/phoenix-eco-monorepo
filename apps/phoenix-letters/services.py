"""
🔧 Phoenix Letters Services
Services métier centralisés et configurables
"""

import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from config.settings import Settings
from infrastructure.ai.gemini_client import GeminiClient
from infrastructure.ai.mock_gemini_client import MockGeminiClient
from infrastructure.database.db_connection import DatabaseConnection
from infrastructure.security.input_validator import InputValidator
from infrastructure.storage.session_manager import SecureSessionManager
from ui.components.file_uploader import SecureFileUploader
from ui.components.letter_editor import LetterEditor
from ui.components.progress_bar import ProgressIndicator
from core.services.letter_service import LetterService
from core.services.job_offer_parser import JobOfferParser
from core.services.prompt_service import PromptService


logger = logging.getLogger(__name__)


@dataclass
class ServiceContainer:
    """Container pour tous les services Phoenix Letters"""

    gemini_client: Any
    settings: Settings
    db_connection: DatabaseConnection
    session_manager: SecureSessionManager
    input_validator: InputValidator
    file_uploader: SecureFileUploader
    progress_indicator: ProgressIndicator
    letter_editor: LetterEditor
    letter_service: LetterService
    job_offer_parser: JobOfferParser
    prompt_service: PromptService
    mirror_match_service: Optional[Any] = None
    ats_analyzer_service: Optional[Any] = None
    smart_coach_service: Optional[Any] = None
    trajectory_builder_service: Optional[Any] = None
    error: Optional[str] = None


class PhoenixLettersServiceManager:
    """Gestionnaire centralisé des services Phoenix Letters"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)

    def create_gemini_client(self, use_mock: bool = False) -> Any:
        """Crée le client Gemini (réel ou mock)"""
        if use_mock:
            self.logger.info("Utilisation du Mock Gemini Client")
            return MockGeminiClient()
        else:
            self.logger.info("Utilisation du Gemini Client réel")
            return GeminiClient(self.settings)

    def initialize_all_services(
        self, gemini_client: Any, db_connection: DatabaseConnection
    ) -> ServiceContainer:
        """Initialise tous les services Phoenix Letters"""
        try:
            # Services de base
            session_manager = SecureSessionManager(self.settings)
            input_validator = InputValidator()

            # Services UI
            file_uploader = SecureFileUploader(input_validator, self.settings)
            progress_indicator = ProgressIndicator()
            letter_editor = LetterEditor()

            # Services métier Phoenix
            letter_service = LetterService(gemini_client, self.settings)
            job_offer_parser = JobOfferParser()
            prompt_service = PromptService()

            # Services Premium (avec fallback sécurisé)
            mirror_match_service = self._safe_import_service(
                "core.services.mirror_match_service", "MirrorMatchService"
            )
            ats_analyzer_service = self._safe_import_service(
                "core.services.ats_analyzer_service", "ATSAnalyzerService"
            )
            smart_coach_service = self._safe_import_service(
                "core.services.smart_coach_service", "SmartCoachService"
            )
            trajectory_builder_service = self._safe_import_service(
                "core.services.trajectory_builder_service", "TrajectoryBuilderService"
            )

            return ServiceContainer(
                gemini_client=gemini_client,
                settings=self.settings,
                db_connection=db_connection,
                session_manager=session_manager,
                input_validator=input_validator,
                file_uploader=file_uploader,
                progress_indicator=progress_indicator,
                letter_editor=letter_editor,
                letter_service=letter_service,
                job_offer_parser=job_offer_parser,
                prompt_service=prompt_service,
                mirror_match_service=mirror_match_service,
                ats_analyzer_service=ats_analyzer_service,
                smart_coach_service=smart_coach_service,
                trajectory_builder_service=trajectory_builder_service,
            )

        except Exception as e:
            self.logger.error(f"Erreur initialisation services: {e}")
            # Fallback sécurisé avec services minimaux
            return ServiceContainer(
                gemini_client=gemini_client,
                settings=self.settings,
                db_connection=db_connection,
                session_manager=SecureSessionManager(self.settings),
                input_validator=InputValidator(),
                file_uploader=None,
                progress_indicator=None,
                letter_editor=None,
                letter_service=None,
                job_offer_parser=None,
                prompt_service=None,
                error=str(e),
            )

    def _safe_import_service(self, module_path: str, class_name: str) -> Optional[Any]:
        """Import sécurisé d'un service avec fallback"""
        try:
            module = __import__(module_path, fromlist=[class_name])
            service_class = getattr(module, class_name)
            return service_class()
        except ImportError as e:
            self.logger.warning(f"Service {class_name} non disponible: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erreur initialisation {class_name}: {e}")
            return None


class EnvironmentValidator:
    """Validateur des variables d'environnement requises"""

    REQUIRED_VARS = ["GOOGLE_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]

    OPTIONAL_VARS = [
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLISHABLE_KEY",
        "FRANCETRAVAIL_CLIENT_ID",
    ]

    @classmethod
    def validate_environment(cls) -> Dict[str, Any]:
        """Valide toutes les variables d'environnement"""
        results = {
            "valid": True,
            "missing_required": [],
            "missing_optional": [],
            "available_features": [],
        }

        # Vérification des variables requises
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                results["missing_required"].append(var)
                results["valid"] = False

        # Vérification des variables optionnelles
        for var in cls.OPTIONAL_VARS:
            if not os.getenv(var):
                results["missing_optional"].append(var)

        # Détermination des fonctionnalités disponibles
        if os.getenv("STRIPE_SECRET_KEY"):
            results["available_features"].append("Paiements Stripe")

        if os.getenv("FRANCETRAVAIL_CLIENT_ID"):
            results["available_features"].append("API France Travail")

        return results

    @classmethod
    def get_validation_summary(cls) -> str:
        """Retourne un résumé de la validation"""
        validation = cls.validate_environment()

        if validation["valid"]:
            summary = "✅ Configuration complète\n"
        else:
            summary = "❌ Configuration incomplète\n"
            summary += (
                f"Variables manquantes: {', '.join(validation['missing_required'])}\n"
            )

        if validation["available_features"]:
            summary += f"🎯 Fonctionnalités disponibles: {', '.join(validation['available_features'])}\n"

        if validation["missing_optional"]:
            summary += f"⚠️ Fonctionnalités optionnelles désactivées: {', '.join(validation['missing_optional'])}"

        return summary


class SessionCleanupManager:
    """Gestionnaire de nettoyage automatique des sessions"""

    @staticmethod
    def auto_cleanup() -> tuple[bool, str]:
        """Nettoyage automatique de la session Streamlit"""
        try:
            from utils.session_cleaner import PhoenixLettersSessionCleaner

            stats = PhoenixLettersSessionCleaner.get_session_stats()

            if stats["total_keys"] > 50:  # Seuil de nettoyage
                cleaned_keys = PhoenixLettersSessionCleaner.cleanup_session()
                return True, f"🧹 Session nettoyée: {cleaned_keys} clés supprimées"
            else:
                return False, f"Session OK: {stats['total_keys']} clés"

        except ImportError:
            return False, "Session cleaner non disponible"
        except Exception as e:
            return False, f"Erreur nettoyage: {e}"


# Utilitaires de diagnostic
class DiagnosticManager:
    """Gestionnaire des outils de diagnostic"""

    @staticmethod
    def test_supabase_connection() -> Dict[str, Any]:
        """Test de connexion Supabase"""
        try:
            from phoenix_shared_auth.client import get_supabase_client

            sb = get_supabase_client()
            result = sb.table("profiles").select("id").limit(1).execute()
            return {
                "success": True,
                "message": f"✅ Connexion Supabase OK ({len(result.data)} rows)",
                "data": result.data,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Erreur Supabase: {e}",
                "data": None,
            }

    @staticmethod
    def test_gemini_api(api_key: str) -> Dict[str, Any]:
        """Test de l'API Gemini"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Test simple
            response = model.generate_content("Hello, respond with 'OK' only")
            return {
                "success": True,
                "message": "✅ API Gemini fonctionnelle",
                "response": (
                    response.text[:50] + "..."
                    if len(response.text) > 50
                    else response.text
                ),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Erreur API Gemini: {e}",
                "response": None,
            }
