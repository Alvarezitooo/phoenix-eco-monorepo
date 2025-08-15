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
# Authentification unifiée Phoenix - Path monorepo compatible Streamlit Cloud
import sys
from pathlib import Path

# Path absolu vers packages depuis le monorepo
MONOREPO_ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGES_PATH = MONOREPO_ROOT / "packages"
if str(PACKAGES_PATH) not in sys.path:
    sys.path.insert(0, str(PACKAGES_PATH))

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
from phoenix_shared_auth.stripe_manager import StripeManager
from core.services.subscription_service import SubscriptionService
from ui.pages.settings_page import SettingsPage
from utils.async_runner import AsyncServiceRunner
# Phoenix shared UI components - import avec fallback
try:
    from phoenix_shared_ui.components import render_primary_button, render_info_card, render_section_header, render_alert, render_ariadne_thread
except ImportError:
    # Fallback pour déploiement Streamlit Cloud
    def render_primary_button(*args, **kwargs): return st.button(*args, **kwargs)
    def render_info_card(*args, **kwargs): return st.info(*args, **kwargs)
    def render_section_header(*args, **kwargs): return st.header(*args, **kwargs)
    def render_alert(*args, **kwargs): return st.warning(*args, **kwargs)
    def render_ariadne_thread(*args, **kwargs): return st.text(*args, **kwargs)

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


def render_login_page(auth_manager, subscription_service, async_runner):
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
            
            st.subheader("Se connecter")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Mot de passe", type="password", key="login_password")
            
            if st.button("Se connecter", key="login_btn", type="primary"):
                if not email or not password:
                    st.error("Veuillez entrer votre email et mot de passe.")
                else:
                    try:
                        success, message, user_id, access_token = auth_manager.sign_in(email, password)
                        if success:
                            st.session_state.user_id = user_id
                            st.session_state.user_email = email
                            st.session_state.access_token = access_token
                            st.session_state.is_authenticated = True
                            
                            # Récupérer le statut d'abonnement
                            if async_runner:
                                future = async_runner.run_coro_in_thread(subscription_service.get_user_subscription(user_id))
                                subscription = future.result(timeout=10)
                                if subscription:
                                    st.session_state.user_tier = subscription.current_tier
                                else:
                                    st.session_state.user_tier = UserTier.FREE
                            else:
                                st.session_state.user_tier = UserTier.FREE # Fallback
                            
                            st.success(f"Bienvenue, {email} !")
                            st.rerun()
                        else:
                            st.error(f"Erreur de connexion : {message}")
                    except Exception as e:
                        st.error(f"Une erreur inattendue est survenue : {e}")
            
            st.markdown("--- ")
            st.subheader("Créer un compte")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Mot de passe", type="password", key="signup_password")
            
            if st.button("Créer un compte", key="signup_btn"):
                if not new_email or not new_password:
                    st.error("Veuillez entrer un email et un mot de passe.")
                else:
                    try:
                        success, message, user_id = auth_manager.sign_up(new_email, new_password)
                        if success:
                            st.session_state.user_id = user_id
                            st.session_state.user_email = new_email
                            st.session_state.is_authenticated = True
                            st.session_state.user_tier = UserTier.FREE # Nouveau compte est Free par défaut
                            st.success(f"Compte créé avec succès pour {new_email} ! Vous êtes maintenant connecté.")
                            st.rerun()
                        else:
                            st.error(f"Erreur d'inscription : {message}")
                    except Exception as e:
                        st.error(f"Une erreur inattendue est survenue : {e}")

            st.markdown("</div>", unsafe_allow_html=True)
        
        st.info("🔒 **Sécurité garantie** : Vos données sont chiffrées et protégées selon les standards RGPD. "
                "Création de compte gratuite et sans engagement.")

def _route_app_pages(current_user, auth_manager, settings, db_connection, initialized_components, subscription_service, async_runner):
    """Gère l'aiguillage des pages de l'application."""
    if "auth_flow_choice" not in st.session_state:
        st.session_state.auth_flow_choice = None

    # Aiguillage
    if not st.session_state.get("is_authenticated", False):
        if st.session_state.auth_flow_choice == "login":
            render_login_page(auth_manager, subscription_service, async_runner)
        else: # guest mode
            render_choice_page()
    else:  # L'utilisateur est connecté
        render_main_app(current_user, auth_manager, settings, db_connection, initialized_components)

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
    
    # Initialisation des services nécessaires
    session_manager = SecureSessionManager(settings)
    input_validator = InputValidator()
    auth_manager = AuthManager()  # Contrat V5: AuthManager unifié sans paramètres

    # Initialisation des services de paiement (safe mode)
    try:
        stripe_service = StripeService(settings, input_validator)
        subscription_service = SubscriptionService(
            settings=settings,
            stripe_service=stripe_service,
            db_connection=db_connection,
            input_validator=input_validator
        )
    except Exception as e:
        logger.warning(f"Services de paiement non disponibles: {e}")
        stripe_service = None
        subscription_service = None

    # Récupération de l'utilisateur courant (si déjà authentifié dans la session)
    current_user = None
    if st.session_state.get("is_authenticated", False):
        # Ici, on pourrait rafraîchir les données utilisateur si nécessaire
        # Pour l'instant, on se base sur ce qui est en session
        current_user = {
            "id": st.session_state.user_id,
            "email": st.session_state.user_email,
            "user_tier": st.session_state.user_tier
        }

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
        
        if renaissance_service.should_show_renaissance_banner_letters(current_user["id"]):
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
            recommendations = renaissance_service.get_renaissance_letter_recommendations(current_user["id"])
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

    # Components initialisés directement (fix NameError)
    initialized_components = {
        'gemini_client': gemini_client,
        'settings': settings,
        'db_connection': db_connection
    }

    # Bannière de mise à niveau pour les utilisateurs Free
    if current_user and current_user["user_tier"] == UserTier.FREE:
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

    _route_app_pages(current_user, auth_manager, settings, db_connection, initialized_components, subscription_service, st.session_state.async_service_runner)

if __name__ == "__main__":
    main()
