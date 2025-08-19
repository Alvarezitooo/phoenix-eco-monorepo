"""
🚀 Phoenix Letters - Main Application (Refactorisé)
Architecture modulaire pour déploiement Docker/Render
"""

import logging
import os
import sys
from pathlib import Path

import streamlit as st

# Configuration des paths monorepo - Architecture "Boîte à Outils Commune"
MONOREPO_ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGES_PATH = MONOREPO_ROOT / "packages"
if str(PACKAGES_PATH) not in sys.path:
    sys.path.insert(0, str(PACKAGES_PATH))
    
# Ajout du root monorepo pour accès direct aux packages/
if str(MONOREPO_ROOT) not in sys.path:
    sys.path.insert(0, str(MONOREPO_ROOT))

# Imports refactorisés
from config.settings import Settings
from services import (
    PhoenixLettersServiceManager,
    EnvironmentValidator,
    SessionCleanupManager,
    DiagnosticManager,
)
from auth_manager import PhoenixLettersAuthManager, AuthenticatedUser
from ui_components import PhoenixUIComponents
from infrastructure.database.db_connection import DatabaseConnection
# Import direct depuis packages/ - Architecture Monorepo  
from packages.phoenix_shared_auth.stripe_manager import StripeManager
from core.services.subscription_service import SubscriptionService
from core.services.renaissance_integration_service import (
    PhoenixLettersRenaissanceService,
)
from infrastructure.security.input_validator import InputValidator
from utils.async_runner import AsyncServiceRunner
from core.entities.user import UserTier

# Configuration du logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PhoenixLettersApp:
    """Application principale Phoenix Letters refactorisée"""

    def __init__(self):
        self.settings = Settings()
        self.auth_manager = PhoenixLettersAuthManager()
        self.service_manager = PhoenixLettersServiceManager(self.settings)

        # Initialisation des services async
        if "async_service_runner" not in st.session_state:
            st.session_state.async_service_runner = AsyncServiceRunner()
            st.session_state.async_service_runner.start()

    def initialize_services(self):
        """Initialise tous les services de l'application"""
        # Base de données
        self.db_connection = DatabaseConnection(self.settings)

        # Services de paiement
        try:
            self.stripe_service = StripeManager()
            self.subscription_service = SubscriptionService(
                settings=self.settings,
                stripe_service=self.stripe_service,
                db_connection=self.db_connection,
                input_validator=InputValidator(),
            )
        except Exception as e:
            logger.warning(f"Services de paiement non disponibles: {e}")
            self.stripe_service = None
            self.subscription_service = None

        # Client Gemini
        use_mock = st.sidebar.checkbox("Mode Développeur (Mock API)", value=False)
        self.gemini_client = self.service_manager.create_gemini_client(use_mock)

        if use_mock:
            st.sidebar.warning("🔧 Mode Mock API activé")
        else:
            st.sidebar.success("✅ Mode API Réelle activé")

        # Services complets
        self.service_container = self.service_manager.initialize_all_services(
            self.gemini_client, self.db_connection
        )

    def render_diagnostics(self):
        """Affiche les diagnostics système"""
        with st.expander("🔍 Diagnostics Système", expanded=False):
            # Validation environnement
            env_summary = EnvironmentValidator.get_validation_summary()
            st.text(env_summary)

            # Test Supabase
            supabase_test = DiagnosticManager.test_supabase_connection()
            if supabase_test["success"]:
                st.success(supabase_test["message"])
            else:
                st.error(supabase_test["message"])

            # Stats session
            cleanup_result = SessionCleanupManager.auto_cleanup()
            if cleanup_result[0]:
                st.info(cleanup_result[1])

    def render_research_banner(self):
        """Affiche la bannière recherche-action si activée"""
        try:
            enable_banner = (
                os.getenv("ENABLE_RESEARCH_BANNER", "false").lower() == "true"
            )
            if enable_banner:
                st.info("🔬 Mode Recherche-Action Phoenix activé")
        except Exception:
            pass

    def render_renaissance_protocol(self, user: AuthenticatedUser):
        """Affiche le protocole Renaissance si applicable"""
        try:
            renaissance_service = PhoenixLettersRenaissanceService(self.db_connection)

            if renaissance_service.should_show_renaissance_banner_letters(user.id):
                st.markdown(
                    """
                <div style="
                    background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    margin-bottom: 2rem;
                    text-align: center;
                    box-shadow: 0 8px 25px rgba(236,72,153,0.3);
                ">
                    <h3 style="margin: 0; font-size: 1.3rem; font-weight: bold;">
                        🔮 PROTOCOLE RENAISSANCE DÉTECTÉ
                    </h3>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
                        Votre profil suggère un accompagnement personnalisé. Explorons de nouvelles stratégies ! ✨
                    </p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                recommendations = (
                    renaissance_service.get_renaissance_letter_recommendations(user.id)
                )
                if recommendations:
                    st.markdown("### 🎯 Recommandations Renaissance - Lettres")
                    for rec in recommendations:
                        st.markdown(f"• {rec}")
                    st.markdown("---")
        except Exception as e:
            logger.error(f"Erreur Renaissance Protocol: {e}")

    def render_main_app(self, user: AuthenticatedUser):
        """Affiche l'application principale après authentification"""
        # Header avec informations utilisateur
        PhoenixUIComponents.render_app_header(user.__dict__)

        # Navigation par onglets
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "🚀 **Générateur**",
                f"{'💎' if user.user_tier == UserTier.PREMIUM else '🌟'} **Premium**",
                "⚙️ **Paramètres**",
                "ℹ️ **À propos**",
            ]
        )

        with tab1:
            self.render_generator_tab(user)

        with tab2:
            self.render_premium_tab(user)

        with tab3:
            self.render_settings_tab(user)

        with tab4:
            self.render_about_tab()

        # Panneau debug admin
        self.auth_manager.render_admin_debug_panel()

        # Pied de page inspirant
        PhoenixUIComponents.render_inspirational_footer()

    def render_generator_tab(self, user: AuthenticatedUser):
        """Affiche l'onglet générateur"""
        if user.user_tier == UserTier.PREMIUM:
            # Interface Premium complète
            st.markdown(
                """
            <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); 
                       padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
                <h3 style="margin: 0;">💎 Générateur Premium - Accès Complet</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                    Toutes les fonctionnalités avancées débloquées pour vous !
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            self.render_premium_generator(user)
        else:
            # Interface Free avec teasers
            st.markdown(
                """
            <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); 
                       padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
                <h3 style="margin: 0;">🌟 Générateur Gratuit + Aperçu Premium</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                    3 lettres gratuites par mois + découvrez les fonctionnalités Premium
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            self.render_free_generator_with_teasers(user)

    def render_premium_generator(self, user: AuthenticatedUser):
        """Affiche le générateur Premium complet"""
        if "error" in self.service_container.__dict__:
            st.error(f"❌ Erreur services : {self.service_container.error}")
            return

        try:
            # Import local pour éviter problème de dépendances
            from ui.pages.generator_page import GeneratorPage

            generator_page = GeneratorPage(
                letter_service=self.service_container.letter_service,
                file_uploader=self.service_container.file_uploader,
                session_manager=self.service_container.session_manager,
                progress_indicator=self.service_container.progress_indicator,
                letter_editor=self.service_container.letter_editor,
                mirror_match_service=self.service_container.mirror_match_service,
                ats_analyzer_service=self.service_container.ats_analyzer_service,
                smart_coach_service=self.service_container.smart_coach_service,
                trajectory_builder_service=self.service_container.trajectory_builder_service,
                job_offer_parser=self.service_container.job_offer_parser,
            )

            generator_page.render(
                current_user=user.__dict__,
                settings=self.service_container.settings,
                gemini_client=self.service_container.gemini_client,
                db_connection=self.service_container.db_connection,
            )
        except Exception as e:
            st.error(f"❌ Erreur générateur Premium : {e}")

    def render_free_generator_with_teasers(self, user: AuthenticatedUser):
        """Affiche le générateur gratuit avec teasers Premium"""
        free_tab, premium_preview = st.tabs(
            ["📝 **Générateur Gratuit**", "💎 **Aperçu Premium**"]
        )

        with free_tab:
            # Générateur gratuit immédiat
            PhoenixUIComponents.render_quick_letter_generator()

        with premium_preview:
            st.markdown("### 🚀 Fonctionnalités Premium - Aperçu")

            col1, col2 = st.columns(2)
            with col1:
                PhoenixUIComponents.render_premium_teaser(
                    "Mirror Match",
                    "Adaptez votre lettre au profil exact du recruteur pour 3x plus de chances",
                    "unlock_mirror",
                )
            with col2:
                PhoenixUIComponents.render_premium_teaser(
                    "ATS Analyzer",
                    "Optimisez votre lettre pour passer les filtres automatiques",
                    "unlock_ats",
                )

            col3, col4 = st.columns(2)
            with col3:
                PhoenixUIComponents.render_premium_teaser(
                    "Smart Coach",
                    "Conseils personnalisés en temps réel",
                    "unlock_coach",
                )
            with col4:
                PhoenixUIComponents.render_premium_teaser(
                    "Trajectory Builder",
                    "Construisez un parcours professionnel cohérent",
                    "unlock_trajectory",
                )

    def render_premium_tab(self, user: AuthenticatedUser):
        """Affiche l'onglet Premium"""
        try:
            from ui.pages.premium_page import PremiumPage

            premium_page = PremiumPage(self.stripe_service, self.subscription_service)
            premium_page.render()
        except Exception as e:
            st.error(f"❌ Erreur page Premium : {e}")

    def render_settings_tab(self, user: AuthenticatedUser):
        """Affiche l'onglet Paramètres"""
        try:
            from ui.pages.settings_page import SettingsPage

            settings_page = SettingsPage()
            settings_page.render()
        except Exception as e:
            st.error(f"❌ Erreur paramètres : {e}")

    def render_about_tab(self):
        """Affiche l'onglet À propos"""
        try:
            from ui.pages.about_page import AboutPage

            about_page = AboutPage()
            about_page.render()
        except Exception as e:
            st.error(f"❌ Erreur page À propos : {e}")

    def route_pages(self):
        """Gère le routage des pages"""
        if "auth_flow_choice" not in st.session_state:
            st.session_state.auth_flow_choice = None

        current_user = self.auth_manager.get_current_user()

        if not self.auth_manager.is_authenticated():
            if st.session_state.auth_flow_choice == "login":
                self.auth_manager.render_login_page(
                    self.subscription_service, st.session_state.async_service_runner
                )
            else:
                # Redirection vers login
                if st.session_state.get("auth_flow_choice") != "login":
                    st.session_state.auth_flow_choice = "login"
                    st.rerun()
        else:
            # Utilisateur authentifié - afficher l'app principale
            self.render_main_app(current_user)

    def run(self):
        """Point d'entrée principal de l'application"""
        # Configuration Streamlit
        st.set_page_config(layout="wide", page_title="Phoenix Letters", page_icon="🔥")

        # Chargement des styles CSS
        PhoenixUIComponents.load_css_styles()

        # Initialisation des services
        self.initialize_services()

        # Nettoyage automatique session
        cleanup_result = SessionCleanupManager.auto_cleanup()
        if cleanup_result[0]:
            st.info(f"🧹 {cleanup_result[1]}")

        # Diagnostics (mode développeur)
        self.render_diagnostics()

        # Bannière recherche (si activée)
        self.render_research_banner()

        # Protocole Renaissance (si applicable)
        current_user = self.auth_manager.get_current_user()
        if current_user:
            self.render_renaissance_protocol(current_user)

        # Bannière upgrade pour utilisateurs Free
        if current_user and current_user.user_tier == UserTier.FREE:
            PhoenixUIComponents.render_free_upgrade_banner()

        # Routage principal
        self.route_pages()


def main():
    """Point d'entrée principal"""
    try:
        app = PhoenixLettersApp()
        app.run()
    except Exception as e:
        logger.error(f"Erreur fatale application: {e}")
        st.error(f"❌ Erreur critique : {e}")
        st.info("🔧 Contactez le support si le problème persiste")


if __name__ == "__main__":
    main()
