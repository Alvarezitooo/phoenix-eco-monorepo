import os

import google.generativeai as genai
import streamlit as st
from core.supabase_client import supabase_client
from services.ai_coach_service import AICoachService
from services.auth_service import AuthService
from services.mock_db_service import MockDBService
from ui.auth_ui import render_auth_ui
from ui.coaching_ui import render_coaching_ui
from ui.dashboard_ui import render_dashboard_ui
from ui.journal_ui import render_journal_ui
from phoenix_shared_ui.components import render_primary_button, render_info_card, render_section_header, render_alert, render_metric_card

# Import du style global du Design System
with open("../../packages/phoenix-shared-ui/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Configuration de la page
st.set_page_config(
    page_title="Phoenix Rise - Coach IA Reconversion",
    page_icon="🦋",
    layout="wide",
)

# Configuration de l'API Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Erreur: La variable d'environnement GEMINI_API_KEY n'est pas configurée.")
    st.stop()
genai.configure(api_key=api_key)


def main():
    """Point d'entrée principal de l'application."""
    # load_custom_css()  # Custom CSS now loaded from phoenix-shared-ui/style.css

    auth_service = get_auth_service()
    db_service = get_db_service()
    ai_coach_service = get_ai_coach_service()

    if not auth_service.is_logged_in():
        render_auth_ui(auth_service)
    else:
        user = st.session_state["user"]

        # Custom Header for logged-in users
        render_section_header(
            "🦋 Phoenix Rise",
            "Transformez votre parcours de reconversion avec l'IA"
        )

        # Sidebar for logged-in users
        with st.sidebar:
            st.header(f"👋 Bienvenue, {user.email.split('@')[0]}")

            # Simulate user tier for testing purposes
            user_tier = st.selectbox(
                "Niveau d'utilisateur (pour test)",
                ("free", "premium"),
                key="user_tier_select",
            )

            if render_primary_button("🚪 Se Déconnecter"):
                auth_service.sign_out()
                st.rerun()

            # Fil d'Ariane
            render_ariadne_thread(
                steps=["Mon Journal", "Mon Profil", "Mon Dashboard", "Mon Coach IA"],
                current_step_index=0 # À adapter selon la page active
            )

        # Navigation par onglets
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Mon Journal", "Mon Profil", "Mon Dashboard", "Mon Coach IA"]
        )

        with tab1:
            render_journal_ui(user.id, db_service)

        with tab2:
            render_profile_ui(user, db_service)

        with tab3:
            render_dashboard_ui(user.id, db_service)

        with tab4:
            render_coaching_ui(user.id, ai_coach_service, db_service, user_tier)
