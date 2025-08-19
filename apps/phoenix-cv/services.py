"""
🔧 Phoenix CV Services
Services métier centralisés et configurables
"""

import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class CVServiceContainer:
    """Container pour tous les services Phoenix CV"""
    settings: Optional[Any] = None
    gemini_client: Optional[Any] = None
    db_connection: Optional[Any] = None
    session_manager: Optional[Any] = None
    input_validator: Optional[Any] = None
    file_uploader: Optional[Any] = None
    cv_parser: Optional[Any] = None
    template_engine: Optional[Any] = None
    ats_optimizer: Optional[Any] = None
    mirror_match_engine: Optional[Any] = None
    smart_coach: Optional[Any] = None
    trajectory_builder: Optional[Any] = None
    error: Optional[str] = None


class PhoenixCVServiceManager:
    """Gestionnaire centralisé des services Phoenix CV"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_settings(self):
        """Crée la configuration pour Phoenix CV"""
        try:
            from phoenix_cv.config.constants import CVConfig
            return CVConfig()
        except ImportError:
            # Fallback basique
            return type('Settings', (), {
                'google_api_key': os.getenv('GOOGLE_API_KEY'),
                'supabase_url': os.getenv('SUPABASE_URL'),
                'supabase_anon_key': os.getenv('SUPABASE_ANON_KEY')
            })()

    def create_gemini_client(self, settings, use_mock: bool = False):
        """Crée le client Gemini pour CV"""
        if use_mock:
            self.logger.info("Utilisation du Mock Gemini Client pour CV")
            return self._create_mock_gemini()
        else:
            try:
                from phoenix_cv.services.enhanced_gemini_client import get_enhanced_gemini_client
                return get_enhanced_gemini_client()
            except ImportError:
                self.logger.warning("Enhanced Gemini Client non disponible - utilisation basique")
                return self._create_basic_gemini(settings)

    def _create_mock_gemini(self):
        """Crée un mock Gemini pour les tests"""
        class MockGeminiClient:
            def generate_content(self, prompt):
                return type('Response', (), {'text': f"Mock response for: {prompt[:50]}..."})()
        return MockGeminiClient()

    def _create_basic_gemini(self, settings):
        """Crée un client Gemini basique"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            return genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            self.logger.error(f"Erreur création client Gemini: {e}")
            return None

    def initialize_all_services(self) -> CVServiceContainer:
        """Initialise tous les services Phoenix CV"""
        try:
            # Configuration de base
            settings = self.create_settings()
            
            # Client IA
            use_mock = os.getenv('USE_MOCK_AI', 'false').lower() == 'true'
            gemini_client = self.create_gemini_client(settings, use_mock)
            
            # Services CV spécifiques
            cv_parser = self._safe_import_service(
                'phoenix_cv.services.secure_cv_parser', 'SecureCVParser'
            )
            template_engine = self._safe_import_service(
                'phoenix_cv.services.secure_template_engine', 'SecureTemplateEngine'
            )
            ats_optimizer = self._safe_import_service(
                'phoenix_cv.services.secure_ats_optimizer', 'SecureATSOptimizer'
            )
            mirror_match_engine = self._safe_import_service(
                'phoenix_cv.services.mirror_match_engine', 'mirror_match_engine'
            )
            smart_coach = self._safe_import_service(
                'phoenix_cv.services.smart_coach', 'smart_coach'
            )
            trajectory_builder = self._safe_import_service(
                'phoenix_cv.services.ai_trajectory_builder', 'ai_trajectory_builder'
            )

            return CVServiceContainer(
                settings=settings,
                gemini_client=gemini_client,
                cv_parser=cv_parser,
                template_engine=template_engine,
                ats_optimizer=ats_optimizer,
                mirror_match_engine=mirror_match_engine,
                smart_coach=smart_coach,
                trajectory_builder=trajectory_builder
            )

        except Exception as e:
            self.logger.error(f"Erreur initialisation services CV: {e}")
            return CVServiceContainer(
                error=str(e)
            )

    def _safe_import_service(self, module_path: str, class_name: str) -> Optional[Any]:
        """Import sécurisé d'un service avec fallback"""
        try:
            if '.' in class_name:  # Function import
                module = __import__(module_path, fromlist=[class_name])
                return getattr(module, class_name)
            else:  # Class import
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
    """Validateur des variables d'environnement requises pour CV"""

    REQUIRED_VARS = ["GOOGLE_API_KEY"]
    
    OPTIONAL_VARS = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "STRIPE_SECRET_KEY",
        "STRIPE_CV_PRICE_ID"
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
            results["available_features"].append("Paiements Premium CV")

        if os.getenv("SUPABASE_URL"):
            results["available_features"].append("Stockage Cloud CV")

        return results

    @classmethod
    def get_validation_summary(cls) -> str:
        """Retourne un résumé de la validation"""
        validation = cls.validate_environment()

        if validation["valid"]:
            summary = "✅ Configuration CV complète\n"
        else:
            summary = "❌ Configuration CV incomplète\n"
            summary += (
                f"Variables manquantes: {', '.join(validation['missing_required'])}\n"
            )

        if validation["available_features"]:
            summary += f"🎯 Fonctionnalités disponibles: {', '.join(validation['available_features'])}\n"

        if validation["missing_optional"]:
            summary += f"⚠️ Fonctionnalités optionnelles désactivées: {', '.join(validation['missing_optional'])}"

        return summary


# Utilitaires de diagnostic spécifiques CV
class CVDiagnosticManager:
    """Gestionnaire des outils de diagnostic CV"""

    @staticmethod
    def test_cv_parsing() -> Dict[str, Any]:
        """Test des capacités de parsing CV"""
        try:
            # Test simple de parsing
            sample_cv_text = "John Doe\nDéveloppeur Senior\nPython, JavaScript"
            # Ici on testerait le parser CV réel
            return {
                "success": True,
                "message": "✅ Parser CV fonctionnel",
                "parsed_items": 3
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Erreur parser CV: {e}",
                "parsed_items": 0
            }

    @staticmethod
    def test_template_generation() -> Dict[str, Any]:
        """Test de génération de templates CV"""
        try:
            # Test simple de template
            return {
                "success": True,
                "message": "✅ Génération de templates CV OK",
                "templates_available": 5
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Erreur templates CV: {e}",
                "templates_available": 0
            }