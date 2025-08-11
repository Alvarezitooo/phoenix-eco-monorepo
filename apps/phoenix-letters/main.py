"""
🚀 Phoenix Letters - Point d'entrée principal
Redirection intelligente vers version fonctionnelle selon disponibilité

Author: Claude Phoenix DevSecOps Guardian
Version: Smart-Deploy - Adaptive Entry Point
"""

# Point d'entrée principal - utilise la fonction main() de ce fichier
# (Commenté le fallback pour forcer l'utilisation de l'app complète)
# if __name__ == "__main__":
#     main()

import logging

# === IMPORTS ABSOLUS - CONTRÔLE TOTAL DU CONTEXTE ===
import streamlit as st
from config.settings import Settings
from core.entities.user import UserTier
from core.services.job_offer_parser import JobOfferParser
from core.services.letter_service import LetterService
from core.services.prompt_service import PromptService
from infrastructure.ai.gemini_client import GeminiClient
# from phoenix_shared_auth.services.jwt_manager import JWTManager  # Module non trouvé
from infrastructure.auth.streamlit_auth_middleware import StreamlitAuthMiddleware
from infrastructure.auth.user_auth_service import UserAuthService
from infrastructure.database.db_connection import DatabaseConnection
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
# from phoenix_shared_ui.components import render_primary_button, render_info_card, render_section_header, render_alert, render_ariadne_thread  # Module non trouvé

# Configuration du logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# DISABLED: Phoenix Shared UI style supprimé - utilisation styles intégrés
# try:
#     import os
#     style_path = os.path.join(os.path.dirname(__file__), "..", "..", "packages", "phoenix-shared-ui", "phoenix_shared_ui", "style.css")
#     with open(style_path) as f:
#         st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# except FileNotFoundError:
#     logger.warning("Phoenix Shared UI style non trouvé - utilisation styles par défaut")

# Style CSS intégré Phoenix Letters
st.markdown("""
<style>
/* Phoenix Letters - Style intégré */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}
.feature-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
    border-left: 4px solid #667eea;
}
.success-message {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# --- Fonctions de Rendu des Pages ---


def render_choice_page():
    """Affiche la page d'accueil avec message clair et parcours guidé."""
    st.markdown("### ✨ Phoenix Letters")
    st.markdown("**Votre Assistant Lettres de Motivation Personnalisées**")
    st.markdown(
        """
        <p style="text-align: center; font-size: 1.2rem; margin-bottom: 0; opacity: 0.8;">Créez une lettre unique qui valorise votre reconversion en 3 minutes</p>
        """,
        unsafe_allow_html=True,
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info(
            "🎯 **Démarrez maintenant**\n\n"
            "**Aucune inscription requise** • **Données sécurisées** • **Résultat immédiat**\n\n"
            "Votre lettre sera générée en transformant votre expérience passée en atout pour votre nouvelle carrière."
        )
        
        if st.button(
            "▶️ Créer ma première lettre",
            use_container_width=True,
            key="start_letter_button",
            type="primary"
        ):
            st.session_state.auth_flow_choice = "guest"
            st.session_state.user_tier = UserTier.FREE
            st.rerun()
        
        st.markdown("---")
        st.markdown("##### 💾 Vous avez déjà un compte ?")
        if st.button(
            "🔑 Me connecter pour retrouver mes lettres",
            use_container_width=True,
            key="login_existing_button",
        ):
            st.session_state.auth_flow_choice = "login"
            st.rerun()


def render_login_page(auth_middleware):
    """Affiche le formulaire de connexion/inscription esthétique."""
    st.markdown("### 🔑 Connexion Phoenix Letters")
    st.markdown("**Accédez à vos lettres sauvegardées et fonctionnalités Premium**")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown(
                """
                <div style="background: var(--phoenix-surface); padding: var(--phoenix-spacing-lg); border-radius: var(--phoenix-border-radius-lg); box-shadow: var(--phoenix-shadow-md); border: 1px solid #e1e5e9;">
                """,
                unsafe_allow_html=True,
            )
            
            auth_middleware.login_form()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.info(
            "🔒 **Sécurité garantie** : Vos données sont chiffrées et protégées selon les standards RGPD. "
            "Création de compte gratuite et sans engagement."
        )


def _initialize_app_components(settings, db_connection, gemini_client):
    """Initialise tous les services et composants UI de l'application."""
    session_manager = SecureSessionManager(settings)
    input_validator = InputValidator()
    prompt_service = PromptService(settings)
    from core.services.ats_analyzer_service import ATSAnalyzerService
    from core.services.mirror_match_service import MirrorMatchService
    from core.services.smart_coach_service import SmartCoachService
    from core.services.trajectory_builder_service import TrajectoryBuilderService

    mirror_match_service = MirrorMatchService(gemini_client, input_validator)
    ats_analyzer_service = ATSAnalyzerService(gemini_client, input_validator)
    smart_coach_service = SmartCoachService(gemini_client, input_validator)
    trajectory_builder_service = TrajectoryBuilderService(
        gemini_client, input_validator
    )
    letter_service = LetterService(
        gemini_client, input_validator, prompt_service, session_manager
    )
    job_offer_parser = JobOfferParser()
    file_uploader = SecureFileUploader(input_validator, settings)
    progress_indicator = ProgressIndicator()
    letter_editor = LetterEditor()

    generator_page = GeneratorPage(
        letter_service=letter_service,
        file_uploader=file_uploader,
        session_manager=session_manager,
        progress_indicator=progress_indicator,
        letter_editor=letter_editor,
        mirror_match_service=mirror_match_service,
        ats_analyzer_service=ats_analyzer_service,
        smart_coach_service=smart_coach_service,
        trajectory_builder_service=trajectory_builder_service,
        job_offer_parser=job_offer_parser,
    )
    about_page = AboutPage()
    # Initialisation des services de paiement (safe mode)
    try:
        stripe_service = StripeService(settings, input_validator)
        subscription_service = SubscriptionService(
            settings=settings,
            stripe_service=stripe_service,
            db_connection=db_connection,
            input_validator=input_validator
        )
        premium_page = PremiumPage(
            stripe_service=stripe_service,
            subscription_service=subscription_service
        )
    except Exception as e:
        logger.warning(f"Services de paiement non disponibles: {e}")
        # Mode dégradé - définir les services manquants
        stripe_service = None
        subscription_service = None
        premium_page = PremiumPage()  # Mode dégradé
    settings_page = SettingsPage()

    return {
        "generator_page": generator_page,
        "premium_page": premium_page,
        "settings_page": settings_page,
        "about_page": about_page,
        "session_manager": session_manager,
        "input_validator": input_validator,
        "prompt_service": prompt_service,
        "letter_service": letter_service,
        "job_offer_parser": job_offer_parser,
        "file_uploader": file_uploader,
        "progress_indicator": progress_indicator,
        "letter_editor": letter_editor,
        "mirror_match_service": mirror_match_service,
        "ats_analyzer_service": ats_analyzer_service,
        "smart_coach_service": smart_coach_service,
        "trajectory_builder_service": trajectory_builder_service,
        "stripe_service": stripe_service,
        "subscription_service": subscription_service,
    }


def render_main_app(current_user, auth_middleware, settings, db_connection, initialized_components):
    """Affiche l'application principale."""
    # Navigation sidebar
    st.sidebar.title("🚀 Phoenix Letters")
    
    # --- DEV MODE - Bouton Premium Override ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("🛠️ **Mode Développeur**")
    
    # Initialiser user_tier dans session_state si pas présent
    if "user_tier" not in st.session_state:
        st.session_state.user_tier = UserTier.FREE
    
    current_tier = st.session_state.user_tier
    tier_display = {
        UserTier.FREE: "🆓 FREE",
        UserTier.PREMIUM: "⭐ PREMIUM"
    }
    
    st.sidebar.info(f"**Tier actuel:** {tier_display[current_tier]}")
    
    if st.sidebar.button("🚀 Switcher vers PREMIUM", key="dev_premium_button"):
        st.session_state.user_tier = UserTier.PREMIUM
        st.sidebar.success("✅ Passé en mode PREMIUM !")
        st.rerun()
    
    if st.sidebar.button("🔄 Reset vers FREE", key="dev_reset_button"):
        st.session_state.user_tier = UserTier.FREE
        st.sidebar.info("🔄 Retour en mode FREE")
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Pages disponibles
    if "page" not in st.session_state:
        st.session_state.page = "generator"
    
    page = st.sidebar.selectbox(
        "Navigation",
        ["generator", "premium", "settings", "about"],
        format_func=lambda x: {
            "generator": "📝 Générateur",
            "premium": "⭐ Premium", 
            "settings": "⚙️ Paramètres",
            "about": "ℹ️ À propos"
        }[x]
    )
    
    st.session_state.page = page
    
    # Affichage de la page sélectionnée
    if page == "generator":
        initialized_components["generator_page"].render()
    elif page == "premium":
        initialized_components["premium_page"].render()
    elif page == "settings":
        initialized_components["settings_page"].render()
    elif page == "about":
        initialized_components["about_page"].render()

def _route_app_pages(current_user, auth_middleware, settings, db_connection, initialized_components):
    """Gère l'aiguillage des pages de l'application."""
    if "auth_flow_choice" not in st.session_state:
        st.session_state.auth_flow_choice = None

    # Aiguillage
    if current_user is None and st.session_state.auth_flow_choice is None:
        render_choice_page()
    elif current_user is None and st.session_state.auth_flow_choice == "login":
        render_login_page(auth_middleware)
    else:  # L'utilisateur est soit connecté, soit en mode invité
        render_main_app(current_user, auth_middleware, settings, db_connection, initialized_components)


def main():
    """Point d'entrée et aiguilleur principal de l'application."""
    st.set_page_config(layout="wide", page_title="Phoenix Letters")

    settings = Settings()

    if "async_service_runner" not in st.session_state:
        st.session_state.async_service_runner = AsyncServiceRunner()
        st.session_state.async_service_runner.start()

    @st.cache_resource
    def get_db_connection(settings: Settings) -> DatabaseConnection:
        """Initialise et retourne une connexion à la base de données."""
        return DatabaseConnection(settings)

    db_connection = get_db_connection(settings)
    # jwt_manager = JWTManager(settings.jwt_secret_key, settings.jwt_algorithm) # Module non disponible
    auth_service = UserAuthService(settings, db_connection)  # Utiliser settings directement
    auth_middleware = StreamlitAuthMiddleware(auth_service, settings)

    current_user = auth_middleware.get_current_user()

    # Initialize GeminiClient here to pass it to _initialize_app_components
    use_mock = st.sidebar.checkbox(
        "Utiliser le Mock API (Mode Développeur)", value=True
    )
    if use_mock:
        from infrastructure.ai.mock_gemini_client import MockGeminiClient
        gemini_client = MockGeminiClient()
        st.sidebar.warning("Mode Mock API activé.")
    else:
        gemini_client = GeminiClient(settings)
        st.sidebar.success("Mode API Réelle activé.")

    initialized_components = _initialize_app_components(settings, db_connection, gemini_client)

    _route_app_pages(current_user, auth_middleware, settings, db_connection, initialized_components)
    
    # 🤖 Widget Iris flottant (toujours affiché)
    render_iris_floating_widget()
