"""
🚀 Phoenix CV - Intégration Authentification Unifiée
Nouvelle architecture avec Phoenix Shared Auth pour connexion Supabase

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Unified Authentication Integration
"""

import os

# Import du module d'authentification Phoenix
import sys

import streamlit as st
from dotenv import load_dotenv

load_dotenv() # Déplacé ici pour s'assurer que les variables d'environnement sont chargées tôt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from phoenix_shared_auth import (
    JWTManager,
    PhoenixApp,
    PhoenixAuthService,
    PhoenixStreamlitAuth,
    get_phoenix_db_connection,
    get_phoenix_settings,
)

# Import des services Phoenix CV existants
from services.enhanced_gemini_client import get_enhanced_gemini_client
from services.phoenix_ecosystem_bridge import phoenix_bridge
from ui.create_cv_page import render_create_cv_page
from ui.home_page import render_home_page
from ui.pricing_page import render_pricing_page
from ui.templates_page import render_templates_page
from ui.upload_cv_page import render_upload_cv_page


class PhoenixCVAuthApp:
    """
    Application Phoenix CV avec authentification unifiée Supabase
    """

    def __init__(self):
        """Initialise l'application avec l'authentification Phoenix"""
        # Chargement configuration avec .env
        load_dotenv()

        # Vérification variables critiques pour éviter les erreurs de config legacy
        if not os.getenv("PHOENIX_MASTER_KEY"):
            os.environ["PHOENIX_MASTER_KEY"] = "dev-master-key-phoenix-cv-2025-secure"

        # Configuration Phoenix Settings
        self.settings = get_phoenix_settings(".env")

        # Connexion base de données
        self.db_connection = get_phoenix_db_connection()

        # JWT Manager
        self.jwt_manager = JWTManager(self.settings.jwt.secret_key)

        # Service d'authentification
        self.auth_service = PhoenixAuthService(self.db_connection, self.jwt_manager)

        # Middleware Streamlit pour Phoenix CV
        self.streamlit_auth = PhoenixStreamlitAuth(
            auth_service=self.auth_service, app=PhoenixApp.CV
        )

        # Configuration page Streamlit
        self._configure_page()

    def _configure_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(
            page_title="Phoenix CV - Générateur IA Perfect",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="auto",
        )

        # CSS et styles personnalisés
        st.markdown(
            """
        <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .auth-container {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
        }
        
        .feature-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def _handle_stripe_redirect(self):
        query_params = st.experimental_get_query_params()
        if "success" in query_params:
            st.success("✅ Paiement réussi ! Votre compte Premium est activé.")
            # Simuler un événement webhook Stripe pour la mise à jour du tier
            user = self.streamlit_auth.get_current_user()
            if user:
                # Mettre à jour le tier de l'utilisateur dans la base de données
                self.auth_service.update_user_tier(user.user_id, "premium")
                user.current_tier = "premium" # Mettre à jour l'objet utilisateur en session
                st.session_state["user_tier"] = "premium" # Mettre à jour la session Streamlit
            st.experimental_set_query_params()
        elif "cancel" in query_params:
            st.error("❌ Paiement annulé. Vous pouvez réessayer à tout moment.")
            st.experimental_set_query_params()

    def render_authenticated_app(self):
        """Rendu de l'application pour utilisateur connecté"""
        user = self.streamlit_auth.get_current_user()

        # En-tête avec info utilisateur
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown(
                f"""
            <div class="main-header">
                <h1>🚀 Phoenix CV - Bienvenue {user.display_name or user.email}!</h1>
                <p>Générateur IA de CV optimisés pour reconversions</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.info(f"**Tier:** {user.current_tier.value}")
            st.info(
                f"**CVs créés:** {user.app_stats.get('cv', {}).get('cvs_created', 0)}"
            )

        with col3:
            if st.button("🚪 Déconnexion", type="secondary"):
                self.streamlit_auth.logout_user()
                st.rerun()

        # Navigation principale
        st.sidebar.title("🎯 Navigation Phoenix CV")

        pages = {
            "🏠 Accueil": "home",
            "📝 Créer CV": "create_cv",
            "📤 Analyser CV": "upload_cv",
            "🎨 Templates": "templates",
            "💎 Premium": "pricing",
        }

        selected_page = st.sidebar.selectbox(
            "Choisir une page", list(pages.keys()), key="nav_selectbox"
        )

        # Statistiques utilisateur dans sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Vos Statistiques")
        st.sidebar.metric(
            "CVs créés", user.app_stats.get("cv", {}).get("cvs_created", 0)
        )
        st.sidebar.metric(
            "Sessions coaching",
            user.app_stats.get("cv", {}).get("coaching_sessions", 0),
        )

        # Rendu de la page sélectionnée
        page_key = pages[selected_page]

        if page_key == "home":
            render_home_page()
        elif page_key == "create_cv":
            render_create_cv_page()
        elif page_key == "upload_cv":
            render_upload_cv_page()
        elif page_key == "templates":
            render_templates_page()
        elif page_key == "pricing":
            render_pricing_page()

    def render_guest_mode(self):
        """Mode invité avec fonctionnalités limitées"""
        st.markdown(
            """
        <div class="main-header">
            <h1>🚀 Phoenix CV - Mode Démonstration</h1>
            <p>Découvrez nos fonctionnalités gratuitement</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.info(
            "🎯 **Mode Invité** - Créez un compte pour débloquer toutes les fonctionnalités!"
        )

        # Fonctionnalités limitées pour invité
        tab1, tab2 = st.tabs(["🎨 Aperçu Templates", "💎 Créer un Compte"])

        with tab1:
            render_templates_page()

        with tab2:
            st.markdown("### 🚀 Rejoignez Phoenix Ecosystem!")
            st.markdown(
                """
            **Avantages compte Phoenix:**
            - ✅ Création CV illimitée
            - ✅ Templates premium
            - ✅ IA coaching personnalisé
            - ✅ Synchronisation Phoenix Letters
            - ✅ Statistiques détaillées
            """
            )

            if st.button("📝 Créer mon compte", type="primary"):
                st.info(
                    "👆 Utilisez le formulaire d'inscription en haut pour créer votre compte!"
                )

    def run(self):
        """Point d'entrée principal de l'application"""
        self._handle_stripe_redirect()
        # Rendu de l'interface d'authentification si non connecté
        if not self.streamlit_auth.is_authenticated():
            # Page d'authentification avec mode invité
            self.streamlit_auth.render_auth_page()

            # Option mode invité
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])

            with col2:
                if st.button("🎯 Continuer en mode invité", type="secondary"):
                    st.session_state["guest_mode"] = True
                    st.rerun()

        # Mode invité
        elif st.session_state.get("guest_mode", False):
            self.render_guest_mode()

            # Option pour s'inscrire depuis le mode invité
            if st.sidebar.button("📝 Créer un compte"):
                st.session_state["guest_mode"] = False
                st.rerun()

        # Utilisateur authentifié
        else:
            self.render_authenticated_app()


def main():
    """Fonction principale"""
    app = PhoenixCVAuthApp()
    app.run()


if __name__ == "__main__":
    main()
