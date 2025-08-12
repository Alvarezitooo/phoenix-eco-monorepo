import logging
import streamlit as st

# --- CONFIGURATION LOCALE (STREAMLIT CLOUD COMPATIBLE) ---
try:
    from packages.phoenix_shared_config.settings import Settings as SharedSettings
    from packages.phoenix_shared_auth.database.phoenix_db_connection import PhoenixDatabaseConnection
    from packages.phoenix_shared_auth.services.jwt_manager import JWTManager
    from packages.phoenix_shared_auth.services.phoenix_auth_service import PhoenixAuthService
    from packages.phoenix_shared_auth.entities.phoenix_user import PhoenixApp
    from packages.phoenix_shared_ui.components.header import render_header
    from packages.phoenix_shared_ui.components.consent_banner import render_consent_banner
    SHARED_PACKAGES_AVAILABLE = True
except ImportError:
    logging.warning("Packages partagés non disponibles - mode autonome activé")
    SHARED_PACKAGES_AVAILABLE = False
    # Fallback vers configuration locale
    from config.settings import Settings as SharedSettings

# Imports spécifiques à Phoenix Letters (à conserver)
from core.entities.user import UserTier
from core.services.job_offer_parser import JobOfferParser
from core.services.letter_service import LetterService
from core.services.prompt_service import PromptService
from infrastructure.ai.gemini_client import GeminiClient
from infrastructure.security.input_validator import InputValidator
from infrastructure.storage.session_manager import SecureSessionManager
from ui.components.file_uploader import SecureFileUploader
from ui.components.letter_editor import LetterEditor
from ui.components.progress_bar import ProgressIndicator
from ui.components.iris_widget import render_iris_floating_widget
from ui.pages.about_page import AboutPage
from ui.pages.generator_page import GeneratorPage
from ui.pages.premium_page import PremiumPage
from infrastructure.payment.stripe_service import StripeService
from core.services.subscription_service import SubscriptionService
from ui.pages.settings_page import SettingsPage
from utils.async_runner import AsyncServiceRunner

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _initialize_app_components(settings, db_connection, gemini_client):
    """Initialise les composants de l'application"""
    try:
        session_manager = SecureSessionManager(settings)
        input_validator = InputValidator()
        prompt_service = PromptService(settings)
        letter_service = LetterService(gemini_client, input_validator, prompt_service, session_manager)
        
        return {
            "generator_page": GeneratorPage(
                letter_service, 
                SecureFileUploader(input_validator, settings), 
                session_manager, 
                ProgressIndicator(), 
                LetterEditor(), 
                None, None, None, None, 
                JobOfferParser()
            )
        }
    except Exception as e:
        logger.error(f"Erreur initialisation composants: {e}")
        return None

def main():
    """Point d'entrée principal - compatible Streamlit Cloud"""
    
    if SHARED_PACKAGES_AVAILABLE:
        # Mode complet avec authentification
        logger.info("Mode complet avec packages partagés")
        main_with_shared_packages()
    else:
        # Mode autonome pour Streamlit Cloud
        logger.info("Mode autonome - Streamlit Cloud")
        main_standalone()

def main_standalone():
    """Version autonome pour Streamlit Cloud"""
    st.set_page_config(
        page_title="Phoenix Letters - IA de Motivation",
        page_icon="✍️",
        layout="wide"
    )
    
    try:
        # Configuration locale
        from config.settings import Settings
        settings = Settings()
        
        # Client IA
        gemini_client = GeminiClient(settings)
        
        # Interface simplifiée
        st.title("🚀 Phoenix Letters")
        st.subheader("Générateur IA de Lettres de Motivation")
        
        # Page de génération basique
        generator_page = GeneratorPage()
        generator_page.render()
        
    except Exception as e:
        logger.error(f"Erreur en mode autonome: {e}")
        st.error(f"Erreur de démarrage: {e}")
        st.info("💡 Essayez de rafraîchir la page ou contactez le support.")

def main_with_shared_packages():
    """Version complète avec packages partagés"""
    # Code original ici
    pass

def render_main_app(current_user, auth_service, settings, db_connection, initialized_components):
    render_header("Phoenix Letters", "✉️")
    st.sidebar.title("🚀 Phoenix Letters")
    page = st.sidebar.selectbox("Navigation", ["generator", "premium", "settings", "about"])
    if page == "generator":
        initialized_components["generator_page"].render()
    # ... etc.

def render_login_form(auth_service: PhoenixAuthService):
    st.markdown("### ✉️ Bienvenue sur Phoenix Letters")
    login_tab, register_tab = st.tabs(["Connexion", "Inscription"])
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter"):
                try:
                    user, _, _ = auth_service.authenticate_user(email, password, PhoenixApp.LETTERS)
                    st.session_state['phoenix_user'] = user
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
    with register_tab:
        with st.form("register_form"):
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Mot de passe", type="password", key="reg_password")
            if st.form_submit_button("S'inscrire"):
                try:
                    user = auth_service.register_user(email, password, source_app=PhoenixApp.LETTERS)
                    st.session_state['phoenix_user'] = user
                    st.success("Inscription réussie ! Vous pouvez maintenant vous connecter.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

def main():
    st.set_page_config(layout="wide", page_title="Phoenix Letters")
    render_consent_banner()

    settings = Settings()
    if not settings.is_valid_for_db():
        st.error("Configuration de la base de données manquante.")
        return

    db_connection = PhoenixDatabaseConnection(settings)
    jwt_manager = JWTManager(settings.jwt_secret_key, settings.jwt_algorithm)
    auth_service = PhoenixAuthService(db_connection, jwt_manager)

    if 'phoenix_user' in st.session_state:
        gemini_client = GeminiClient(settings)
        initialized_components = _initialize_app_components(settings, db_connection, gemini_client)
        render_main_app(st.session_state['phoenix_user'], auth_service, settings, db_connection, initialized_components)
        if st.sidebar.button("Se déconnecter"):
            del st.session_state['phoenix_user']
            st.rerun()
    else:
        render_login_form(auth_service)

if __name__ == "__main__":
    main()