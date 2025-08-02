"""
🚀 Phoenix Letters - Intégration Authentification Unifiée
Migration vers Phoenix Shared Auth pour connexion Supabase centralisée

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Unified Authentication Integration
"""

import os
import sys

import streamlit as st
from dotenv import load_dotenv

# Import du module d'authentification Phoenix
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.settings import Settings
from core.services.letter_service import LetterService
from infrastructure.ai.gemini_client import GeminiClient
from phoenix_shared_auth import (
    JWTManager,
    PhoenixApp,
    PhoenixAuthService,
    PhoenixStreamlitAuth,
    get_phoenix_db_connection,
    get_phoenix_settings,
)
from ui.pages.about_page import AboutPage

# Import des services Phoenix Letters existants
from ui.pages.generator_page import GeneratorPage
from ui.pages.premium_page import PremiumPage
from ui.pages.settings_page import SettingsPage
from utils.monitoring import APIUsageTracker, render_api_monitoring_dashboard

# Import Event-Sourcing Bridge
from phoenix_event_bridge import PhoenixEventFactory


class PhoenixLettersAuthApp:
    """
    Application Phoenix Letters avec authentification unifiée Supabase
    """

    def __init__(self):
        """Initialise l'application avec l'authentification Phoenix"""
        # Chargement configuration avec .env
        load_dotenv()

        # Configuration Phoenix Settings
        self.settings = get_phoenix_settings(".env")

        # Connexion base de données
        self.db_connection = get_phoenix_db_connection()

        # JWT Manager
        self.jwt_manager = JWTManager(self.settings.jwt.secret_key)

        # Service d'authentification
        self.auth_service = PhoenixAuthService(self.db_connection, self.jwt_manager)

        # Middleware Streamlit pour Phoenix Letters
        self.streamlit_auth = PhoenixStreamlitAuth(
            auth_service=self.auth_service, app=PhoenixApp.LETTERS
        )

        # Services Phoenix Letters legacy
        self._setup_legacy_services()

        # Event-Sourcing Bridge
        self.event_helper = PhoenixEventFactory.create_letters_helper()

        # Configuration page Streamlit
        self._configure_page()

    def _setup_legacy_services(self):
        """Configuration des services Phoenix Letters existants"""
        # Configuration legacy pour compatibilité
        self.phoenix_settings = Settings()
        self.gemini_client = GeminiClient(self.phoenix_settings)
        self.letter_service = LetterService(
            gemini_client=self.gemini_client, settings=self.phoenix_settings
        )
        self.api_tracker = APIUsageTracker()

        # Pages existantes
        self.generator_page = GeneratorPage()
        self.about_page = AboutPage()
        self.premium_page = PremiumPage()
        self.settings_page = SettingsPage()

    def _configure_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(
            page_title="🔥 Phoenix Letters - Générateur IA",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # CSS Phoenix Letters
        st.markdown(
            """
        <style>
        .main-header {
            background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .phoenix-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            border-left: 5px solid #FF6B6B;
        }
        
        .stats-container {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .tier-badge {
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #333;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.8rem;
            display: inline-block;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def render_authenticated_app(self):
        """Rendu de l'application pour utilisateur connecté"""
        user = self.streamlit_auth.get_current_user()

        # En-tête Phoenix Letters
        st.markdown(
            f"""
        <div class="main-header">
            <h1>🔥 Phoenix Letters - Bienvenue {user.display_name or user.email}!</h1>
            <p>Générateur IA de lettres de motivation ultra-personnalisées</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Barre supérieure avec stats et déconnexion
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            letters_generated = user.app_stats.get("letters", {}).get(
                "letters_generated", 0
            )
            st.metric("🎯 Lettres générées", letters_generated)

        with col2:
            st.markdown(
                f'<span class="tier-badge">{user.current_tier.value.upper()}</span>',
                unsafe_allow_html=True,
            )

        with col3:
            coaching_sessions = user.app_stats.get("letters", {}).get(
                "coaching_sessions", 0
            )
            st.metric("🎓 Sessions coaching", coaching_sessions)

        with col4:
            if st.button("🚪 Déconnexion", type="secondary"):
                self.streamlit_auth.logout_user()
                st.rerun()

        # Navigation sidebar Phoenix Letters
        st.sidebar.title("🎯 Phoenix Letters")
        st.sidebar.markdown(f"**Utilisateur:** {user.display_name or user.email}")
        st.sidebar.markdown(f"**Tier:** {user.current_tier.value}")

        # Menu navigation
        page_options = {
            "🔥 Générateur": "generator",
            "💎 Premium": "premium",
            "📊 Monitoring": "monitoring",
            "ℹ️ À propos": "about",
            "⚙️ Paramètres": "settings",
        }

        selected_page = st.sidebar.selectbox(
            "Navigation", list(page_options.keys()), key="phoenix_letters_nav"
        )

        # Statistiques sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Vos Statistiques Phoenix")

        with st.sidebar:
            st.markdown('<div class="stats-container">', unsafe_allow_html=True)
            st.metric("Lettres créées", letters_generated)
            st.metric(
                "Premium utilisées",
                user.app_stats.get("letters", {}).get("premium_features_used", 0),
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Cross-app navigation
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🌐 Écosystème Phoenix")

        if st.sidebar.button("🔍 Phoenix CV", help="Générateur de CV"):
            st.info("🔄 Bientôt disponible - Navigation cross-app Phoenix!")

        if st.sidebar.button("🎯 Phoenix Rise", help="Coach reconversion"):
            st.info("🔄 Bientôt disponible - Navigation cross-app Phoenix!")

        # Rendu de la page sélectionnée
        page_key = page_options[selected_page]
        self._render_page(page_key, user)

    def _render_page(self, page_key: str, user):
        """Rendu des pages Phoenix Letters"""
        if page_key == "generator":
            # Page générateur avec context utilisateur Phoenix
            self._render_generator_page(user)

        elif page_key == "premium":
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
            self.premium_page.render()
            st.markdown("</div>", unsafe_allow_html=True)

        elif page_key == "monitoring":
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
            render_api_monitoring_dashboard(self.api_tracker)
            st.markdown("</div>", unsafe_allow_html=True)

        elif page_key == "about":
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
            self.about_page.render()
            st.markdown("</div>", unsafe_allow_html=True)

        elif page_key == "settings":
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
            self.settings_page.render()
            st.markdown("</div>", unsafe_allow_html=True)

    def _render_generator_page(self, user):
        """Page générateur avec contexte utilisateur Phoenix"""
        st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)

        # Intégration du générateur existant avec context Phoenix
        # Stockage des infos utilisateur dans session pour compatibilité
        st.session_state.phoenix_user = user
        st.session_state.user_tier = user.current_tier
        st.session_state.authenticated = True

        # Rendu page générateur existante
        self.generator_page.render()

        st.markdown("</div>", unsafe_allow_html=True)

    def render_guest_mode(self):
        """Mode invité avec fonctionnalités limitées Phoenix Letters"""
        st.markdown(
            """
        <div class="main-header">
            <h1>🔥 Phoenix Letters - Mode Démonstration</h1>
            <p>Découvrez la puissance de l'IA pour vos lettres de motivation</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.info(
            "🎯 **Mode Invité** - Générez 3 lettres gratuites, puis créez votre compte Phoenix!"
        )

        # Fonctionnalités limitées pour invité
        tab1, tab2 = st.tabs(["🔥 Générateur Gratuit", "💎 Rejoindre Phoenix"])

        with tab1:
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)

            # Mode invité avec limitations
            st.session_state.guest_mode = True
            st.session_state.authenticated = False
            st.session_state.user_tier = "FREE"

            # Rendu générateur en mode limité
            self.generator_page.render()

            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="phoenix-card">', unsafe_allow_html=True)
            st.markdown("### 🚀 Rejoignez l'Écosystème Phoenix!")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    """
                **🔥 Phoenix Letters Premium:**
                - ✅ Lettres illimitées
                - ✅ Templates premium
                - ✅ IA coaching avancé
                - ✅ Analyse ATS
                - ✅ Optimisation reconversion
                """
                )

            with col2:
                st.markdown(
                    """
                **🌐 Écosystème Phoenix:**
                - 🔍 Phoenix CV - Générateur CV
                - 🎯 Phoenix Rise - Coach carrière
                - 🌐 Site vitrine Phoenix
                - 📊 Dashboard unifié
                - 🔄 Synchronisation data
                """
                )

            if st.button(
                "📝 Créer mon compte Phoenix", type="primary", use_container_width=True
            ):
                st.info(
                    "👆 Utilisez le formulaire d'inscription ci-dessus pour rejoindre Phoenix!"
                )

            st.markdown("</div>", unsafe_allow_html=True)

    def run(self):
        """Point d'entrée principal de l'application"""
        # Rendu de l'interface d'authentification si non connecté
        if not self.streamlit_auth.is_authenticated():
            # Page d'authentification avec branding Phoenix Letters
            st.markdown(
                """
            <div class="main-header">
                <h1>🔥 Phoenix Letters</h1>
                <p>Générateur IA de lettres de motivation pour reconversions</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            self.streamlit_auth.render_auth_page()

            # Option mode invité
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])

            with col2:
                if st.button(
                    "🎯 Essayer gratuitement",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state["guest_mode"] = True
                    st.rerun()

        # Mode invité
        elif st.session_state.get("guest_mode", False):
            self.render_guest_mode()

            # Option pour s'inscrire depuis le mode invité
            if st.sidebar.button("📝 Créer un compte Phoenix"):
                st.session_state["guest_mode"] = False
                st.rerun()

        # Utilisateur authentifié
        else:
            self.render_authenticated_app()


def main():
    """Fonction principale"""
    app = PhoenixLettersAuthApp()
    app.run()


if __name__ == "__main__":
    main()
