"""
🚀 Phoenix Letters - Point d'entrée principal
Redirection intelligente vers version fonctionnelle selon disponibilité

Author: Claude Phoenix DevSecOps Guardian
Version: Smart-Deploy - Adaptive Entry Point
"""

# Point d'entrée principal - utilise la fonction main() de ce fichier

import logging

# === IMPORTS ABSOLUS - CONTRÔLE TOTAL DU CONTEXTE ===
import streamlit as st
from config.settings import Settings
from core.entities.user import UserTier
from core.services.job_offer_parser import JobOfferParser
from core.services.letter_service import LetterService
from core.services.prompt_service import PromptService
from core.services.renaissance_integration_service import PhoenixLettersRenaissanceService
from infrastructure.ai.gemini_client import GeminiClient
# Authentification unifiée Phoenix
import sys
sys.path.append('../../packages')
from phoenix_shared_auth.client import AuthManager
from infrastructure.database.db_connection import DatabaseConnection
from infrastructure.security.input_validator import InputValidator
from infrastructure.storage.session_manager import SecureSessionManager
from ui.components.file_uploader import SecureFileUploader
from ui.components.letter_editor import LetterEditor
from ui.components.progress_bar import ProgressIndicator
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

# Import du style global du Design System
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(current_dir, "../packages/phoenix_shared_ui/phoenix_shared_ui/style.css")
try:
    if os.path.exists(style_path):
        with open(style_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback pour Streamlit Cloud - essayer chemin alternatif
        alt_style_path = os.path.join(current_dir, "../../packages/phoenix_shared_ui/phoenix_shared_ui/style.css")
        if os.path.exists(alt_style_path):
            with open(alt_style_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    # Gestion silencieuse pour ne pas casser l'app
    pass

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


def render_research_action_banner():
    """🔬 Bannière de sensibilisation à la recherche-action Phoenix"""
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <p style="margin: 0; font-size: 0.95rem; font-weight: 500;">
                🎓 <strong>Participez à une recherche-action sur l'impact de l'IA dans la reconversion professionnelle.</strong>
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.9; line-height: 1.4;">
                En utilisant Phoenix, vous contribuez anonymement à une étude sur l'IA éthique et la réinvention de soi. 
                Vos données (jamais nominatives) aideront à construire des outils plus justes et plus humains.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


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
    
    # 🔐 Authentification Phoenix unifiée
    auth_manager = AuthManager()
    
    # Pour compatibilité avec le code existant, création d'un wrapper simple
    class SimpleAuthWrapper:
        def __init__(self, auth_manager):
            self.auth_manager = auth_manager
            
        def get_current_user(self):
            # Retourne None pour guest, ou user_data si connecté
            return None  # Mode guest pour l'instant
            
        def login_form(self):
            # Formulaire de connexion simple
            st.info("🚀 Authentification Phoenix en cours de migration...")
            
    auth_middleware = SimpleAuthWrapper(auth_manager)
    current_user = auth_middleware.get_current_user()
    
    # 🔬 BANNIÈRE RECHERCHE-ACTION PHOENIX (désactivable via ENV)
    try:
        import os
        enable_banner = os.getenv("ENABLE_RESEARCH_BANNER", "false").lower() == "true"
    except Exception:
        enable_banner = False
    if enable_banner:
        render_research_action_banner()
    
    # 🔮 PROTOCOLE RENAISSANCE - Vérification si utilisateur connecté
    if current_user and hasattr(current_user, 'id'):
        renaissance_service = PhoenixLettersRenaissanceService(db_connection)
        
        if renaissance_service.should_show_renaissance_banner_letters(current_user.id):
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
                    animation: pulse 2s ease-in-out infinite alternate;
                ">
                    <h3 style="margin: 0; font-size: 1.3rem; font-weight: bold;">
                        🔮 PROTOCOLE RENAISSANCE DÉTECTÉ
                    </h3>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
                        Vos patterns de candidature suggèrent qu'un accompagnement personnalisé pourrait vous aider. 
                        Explorons ensemble de nouvelles stratégies ! ✨
                    </p>
                </div>
                <style>
                @keyframes pulse {
                    from { box-shadow: 0 8px 25px rgba(236,72,153,0.3); }
                    to { box-shadow: 0 12px 35px rgba(236,72,153,0.5); }
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # Affichage des recommandations Renaissance pour les lettres
            recommendations = renaissance_service.get_renaissance_letter_recommendations(current_user.id)
            if recommendations:
                st.markdown("### 🎯 Recommandations Renaissance - Lettres")
                for rec in recommendations:
                    st.markdown(f"• {rec}")
                st.markdown("---")

    # Initialize GeminiClient here to pass it to _initialize_app_components
    use_mock = st.sidebar.checkbox(
        "Utiliser le Mock API (Mode Développeur)", value=False
    )
    if use_mock:
        from infrastructure.ai.mock_gemini_client import MockGeminiClient
        gemini_client = MockGeminiClient()
        st.sidebar.warning("Mode Mock API activé.")
    else:
        gemini_client = GeminiClient(settings)
        st.sidebar.success("Mode API Réelle activé.")

    initialized_components = _initialize_app_components(settings, db_connection, gemini_client)

    # Bannière de mise à niveau pour les utilisateurs Free
    if current_user and current_user.user_tier == UserTier.FREE:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%); padding: 0.8rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <p style="margin: 0; font-size: 0.95rem; font-weight: 500; color: #333;">
                    Vous utilisez la version gratuite. Libérez toute la puissance de Phoenix.
                </p>
                <div style="margin-top: 0.5rem;">
                    <a href="/premium" target="_self" style="text-decoration: none;">
                        <button style="background: #f97316; color: white; border: none; padding: 0.4rem 1rem; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 0.85rem;">
                            Voir les offres
                        </button>
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    _route_app_pages(current_user, auth_middleware, settings, db_connection, initialized_components)

if __name__ == "__main__":
    main()
