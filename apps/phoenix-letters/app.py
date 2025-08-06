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

import asyncio
import logging
from datetime import datetime

# === IMPORTS ABSOLUS - CONTRÔLE TOTAL DU CONTEXTE ===
import streamlit as st
from config.settings import Settings
from core.entities.user import UserTier
from core.services.job_offer_parser import JobOfferParser
from core.services.letter_service import LetterService
from core.services.prompt_service import PromptService
from infrastructure.ai.gemini_client import GeminiClient
from infrastructure.auth.jwt_manager import JWTManager
from infrastructure.auth.streamlit_auth_middleware import StreamlitAuthMiddleware
from infrastructure.auth.user_auth_service import UserAuthService
from infrastructure.database.db_connection import DatabaseConnection
from infrastructure.monitoring.performance_monitor import PerformanceMonitor
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
from utils.monitoring import (
    APIUsageTracker,
    diagnostic_urgence_50_requetes,
    render_api_monitoring_dashboard,
    render_detailed_monitoring,
)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Fonctions de Rendu des Pages ---


def render_choice_page():
    """Affiche la page d'accueil avec message clair et parcours guidé."""
    # Hero Section Claire et Rassurante
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; margin-bottom: 1rem; font-weight: 600;">✨ Phoenix Letters</h1>
            <h2 style="font-size: 1.5rem; margin-bottom: 1.5rem; opacity: 0.9; font-weight: 400;">Votre Assistant Lettres de Motivation Personnalisées</h2>
            <p style="font-size: 1.2rem; margin-bottom: 0; opacity: 0.8;">Créez une lettre unique qui valorise votre reconversion en 3 minutes</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Promesse Claire et Rassurante
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            ### 🎯 Démarrez maintenant
            
            **Aucune inscription requise** • **Données sécurisées** • **Résultat immédiat**
            
            Votre lettre sera générée en transformant votre expérience passée en atout pour votre nouvelle carrière.
            """
        )
        
        # CTA Principal Clair
        if st.button(
            "▶️ Créer ma première lettre",
            type="primary",
            use_container_width=True,
            key="start_letter_button",
        ):
            st.session_state.auth_flow_choice = "guest"
            st.session_state.guest_user_id = (
                f"guest_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            st.session_state.user_tier = UserTier.FREE
            st.rerun()
        
        # Option Secondaire Claire
        st.markdown("---")
        st.markdown("##### 💾 Vous avez déjà un compte ?")
        if st.button(
            "🔑 Me connecter pour retrouver mes lettres",
            use_container_width=True,
            key="login_existing_button",
        ):
            st.session_state.auth_flow_choice = "login"
            st.rerun()


def render_iris_floating_widget():
    """Widget Iris flottant qui suit le scroll - Style chat support client."""
    
    # Initialiser l'état
    if "iris_chat_open" not in st.session_state:
        st.session_state.iris_chat_open = False
    if "iris_messages" not in st.session_state:
        st.session_state.iris_messages = []
    
    # CSS pour widget vraiment flottant avec position fixed
    st.markdown("""
    <style>
    /* Widget flottant qui suit le scroll */
    .iris-floating-widget {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 9999 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
    }
    
    /* Bouton Iris circulaire */
    .iris-chat-bubble {
        width: 60px !important;
        height: 60px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        cursor: pointer !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 24px !important;
        color: white !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }
    
    .iris-chat-bubble:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Animation pulse pour attirer l'attention */
    .iris-pulse {
        animation: iris-pulse-animation 2s infinite !important;
    }
    
    @keyframes iris-pulse-animation {
        0% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4); }
        50% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.8), 0 0 0 10px rgba(102, 126, 234, 0.1); }
        100% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4); }
    }
    
    /* Fenêtre de chat */
    .iris-chat-window {
        position: fixed !important;
        bottom: 90px !important;
        right: 20px !important;
        width: 380px !important;
        height: 500px !important;
        background: white !important;
        border-radius: 12px !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.15) !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        display: flex !important;
        flex-direction: column !important;
        z-index: 9998 !important;
        animation: iris-slide-up 0.3s ease-out !important;
    }
    
    @keyframes iris-slide-up {
        from {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* Header de chat */
    .iris-chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        padding: 16px 20px !important;
        border-radius: 12px 12px 0 0 !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    .iris-close-btn {
        background: none !important;
        border: none !important;
        color: white !important;
        font-size: 20px !important;
        cursor: pointer !important;
        padding: 0 !important;
        width: 24px !important;
        height: 24px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 50% !important;
        transition: background 0.2s !important;
    }
    
    .iris-close-btn:hover {
        background: rgba(255,255,255,0.2) !important;
    }
    
    /* Corps du chat */
    .iris-chat-body {
        flex: 1 !important;
        padding: 20px !important;
        overflow-y: auto !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 15px !important;
    }
    
    /* Input zone */
    .iris-input-zone {
        padding: 15px 20px !important;
        border-top: 1px solid #eee !important;
        background: #f9f9f9 !important;
        border-radius: 0 0 12px 12px !important;
    }
    
    /* Messages */
    .iris-message {
        max-width: 80% !important;
        padding: 12px 16px !important;
        border-radius: 18px !important;
        font-size: 14px !important;
        line-height: 1.4 !important;
    }
    
    .iris-message-bot {
        background: #f1f3f4 !important;
        align-self: flex-start !important;
        border-bottom-left-radius: 6px !important;
    }
    
    .iris-message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        align-self: flex-end !important;
        border-bottom-right-radius: 6px !important;
    }
    
    /* Responsive */
    @media (max-width: 480px) {
        .iris-chat-window {
            width: calc(100vw - 40px) !important;
            height: 400px !important;
        }
        
        .iris-floating-widget {
            right: 15px !important;
            bottom: 15px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Widget HTML pur avec JavaScript intégré
    chat_open = st.session_state.get("iris_chat_open", False)
    
    if not chat_open:
        # Solution simple et efficace : bouton en bas à droite avec colonnes
        st.markdown("---")  # Séparation claire
        
        # Créer l'espace pour le bouton flottant
        col1, col2, col3 = st.columns([8, 1, 1])
        
        with col3:
            # Bouton stylé qui ressemble à un widget flottant
            if st.button("🤖 Iris", key="iris_open_btn", 
                        help="💬 Discuter avec Iris, votre conseillère reconversion",
                        type="primary", use_container_width=True):
                st.session_state.iris_chat_open = True
                st.rerun()
        
        # CSS pour améliorer l'apparence
        st.markdown("""
        <style>
        /* Styling pour le bouton Iris */
        div[data-testid="column"]:nth-child(3) button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border-radius: 25px !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
            font-weight: 600 !important;
            animation: iris-gentle-pulse 3s infinite !important;
        }
        
        div[data-testid="column"]:nth-child(3) button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6) !important;
        }
        
        @keyframes iris-gentle-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Fenêtre de chat ouverte
        render_iris_chat_window_fixed()

def render_iris_chat_window_fixed():
    """Fenêtre de chat Iris simplifiée - juste Streamlit."""
    
    # Header simple et propre
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("### 🤖 Iris")
        st.caption("💡 Votre conseillère en reconversion professionnelle")
    
    with col2:
        if st.button("✕", key="iris_real_close", type="secondary", 
                    help="Fermer Iris", use_container_width=True):
            st.session_state.iris_chat_open = False
            st.rerun()
    
    # Message d'accueil si c'est la première fois
    if "iris_welcomed" not in st.session_state:
        st.info("👋 **Salut !** Je suis Iris, votre conseillère en reconversion professionnelle. Comment puis-je vous accompagner aujourd'hui ?")
        st.session_state.iris_welcomed = True
    
    # Interface de chat propre sans HTML
    from ui.components.iris_ui import render_chat_ui
    render_chat_ui()
    
    # Suggestions rapides
    st.markdown("---")
    st.markdown("**💡 Suggestions rapides :**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Aide lettre", key="iris_quick_letter", use_container_width=True):
            # Ajouter un message pré-rempli (si possible)
            st.info("💬 Posez votre question sur les lettres de motivation...")
    
    with col2:
        if st.button("🎯 Reconversion", key="iris_quick_career", use_container_width=True):
            st.info("💬 Parlez-moi de votre projet de reconversion...")
            
    with col3:
        if st.button("🚀 Fonctionnalités", key="iris_quick_features", use_container_width=True):
            st.info("💬 Demandez-moi tout sur Phoenix Letters...")



def render_login_page(auth_middleware):
    """Affiche le formulaire de connexion/inscription esthétique."""
    # Hero Section de connexion
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white; margin-bottom: 2rem;">
            <h1 style="font-size: 2.2rem; margin-bottom: 0.5rem; font-weight: 600;">🔑 Connexion Phoenix Letters</h1>
            <p style="font-size: 1.1rem; margin-bottom: 0; opacity: 0.9;">Accédez à vos lettres sauvegardées et fonctionnalités Premium</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Centrage du formulaire
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Formulaire d'authentification centré
        with st.container():
            st.markdown(
                """
                <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border: 1px solid #e1e5e9;">
                """,
                unsafe_allow_html=True,
            )
            
            auth_middleware.login_form()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Informations rassurantes
        st.markdown("---")
        st.info(
            "🔒 **Sécurité garantie** : Vos données sont chiffrées et protégées selon les standards RGPD. "
            "Création de compte gratuite et sans engagement."
        )


def render_main_app(current_user, auth_middleware, settings, db_connection):
    """Affiche l'application principale une fois l'utilisateur authentifié ou en mode invité."""
    if current_user:
        st.title(f"🔥 Phoenix Letters - Bienvenue, {current_user.email}")
        if st.sidebar.button("Se déconnecter"):
            auth_middleware.logout()
            st.rerun()
    else:  # Mode invité
        st.title("🔥 Phoenix Letters - Mode Invité")
        st.sidebar.info(
            "🚀 **Débloquez tout le potentiel de Phoenix Letters !**\n\n"
            "En créant un compte gratuit, vous pourrez :\n"
            "- **Sauvegarder** et retrouver toutes vos lettres\n"
            "- Accéder à l'**historique** de vos générations\n"
            "- Bénéficier de **fonctionnalités Premium** exclusives (bientôt !)\n"
            "- Recevoir des **conseils personnalisés** pour votre carrière\n\n"
            "**N'attendez plus, inscrivez-vous !**"
        )
        if "user_id" not in st.session_state:
            st.session_state.user_id = st.session_state.get(
                "guest_user_id", "guest_fallback"
            )
        if "user_tier" not in st.session_state:
            st.session_state.user_tier = UserTier.FREE

    # --- AIGUILLAGE API (INTERRUPTEUR) ---
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

    # --- DÉVELOPPEUR : SIMULATION MODE PREMIUM ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Zone Développeur")
    
    current_tier = st.session_state.get('user_tier', UserTier.FREE)
    if current_tier == UserTier.FREE:
        if st.sidebar.button("🚀 Activer Mode Premium (Dev)", type="primary"):
            st.session_state.user_tier = UserTier.PREMIUM
            st.sidebar.success("✅ Mode Premium activé !")
            st.rerun()
    else:
        if st.sidebar.button("⬇️ Revenir en Mode Free", type="secondary"):
            st.session_state.user_tier = UserTier.FREE
            st.sidebar.info("🔄 Mode Free activé !")
            st.rerun()
        st.sidebar.success(f"✨ Mode {current_tier.value.upper()} actif")
    
    # Affichage du statut actuel
    st.sidebar.caption(f"👤 Tier actuel: **{current_tier.value.upper()}**")

    # Initialisation des services et composants UI
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

    render_api_monitoring_dashboard()

    tabs = st.tabs(
        [
            "Générateur de Lettres",
            "Offres Premium",
            "Paramètres",
            "À Propos",
            "Dev Monitoring",
        ]
    )

    with tabs[0]:
        generator_page.render()
    with tabs[1]:
        premium_page.render()
    with tabs[2]:
        settings_page.render()
    with tabs[3]:
        about_page.render()
    with tabs[4]:
        render_detailed_monitoring()
        if st.checkbox("Mode Debug - Diagnostic 50 Requêtes"):
            diagnostic_urgence_50_requetes()
    
    # --- Widget Iris Flottant ---
    render_iris_floating_widget()
    


# --- Aiguilleur Principal ---


def main():
    """Point d'entrée et aiguilleur principal de l'application."""
    st.set_page_config(layout="wide", page_title="Phoenix Letters")

    settings = Settings()

    if "async_service_runner" not in st.session_state:
        st.session_state.async_service_runner = AsyncServiceRunner()
        st.session_state.async_service_runner.start()

    @st.cache_resource
    def get_db_connection(_settings: Settings) -> DatabaseConnection:
        """Initialise et retourne une connexion à la base de données."""
        return DatabaseConnection(_settings)

    db_connection = get_db_connection(settings)
    jwt_manager = JWTManager(settings)
    auth_service = UserAuthService(jwt_manager, db_connection)
    auth_middleware = StreamlitAuthMiddleware(auth_service, jwt_manager)

    current_user = auth_middleware.get_current_user()

    if "auth_flow_choice" not in st.session_state:
        st.session_state.auth_flow_choice = None

    # Aiguillage
    if current_user is None and st.session_state.auth_flow_choice is None:
        render_choice_page()
    elif current_user is None and st.session_state.auth_flow_choice == "login":
        render_login_page(auth_middleware)
    else:  # L'utilisateur est soit connecté, soit en mode invité
        render_main_app(current_user, auth_middleware, settings, db_connection)


if __name__ == "__main__":
    main()
