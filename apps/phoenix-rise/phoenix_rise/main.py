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
from services.renaissance_protocol_service import PhoenixRiseRenaissanceService
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


def render_research_action_banner():
    """🔬 Bannière de sensibilisation à la recherche-action Phoenix"""
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        
        # 🔬 BANNIÈRE RECHERCHE-ACTION PHOENIX
        render_research_action_banner()

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
            # 🔮 PROTOCOLE RENAISSANCE - Vérification et affichage
            renaissance_service = PhoenixRiseRenaissanceService(db_service)
            
            # Analyse Renaissance pour cet utilisateur
            if renaissance_service.should_show_renaissance_banner(user.id):
                st.markdown(
                    """
                    <div style="
                        background: linear-gradient(135deg, #7c3aed 0%, #c026d3 100%);
                        color: white;
                        padding: 1.5rem;
                        border-radius: 15px;
                        margin-bottom: 2rem;
                        text-align: center;
                        box-shadow: 0 8px 25px rgba(124,58,237,0.3);
                    ">
                        <h3 style="margin: 0; font-size: 1.3rem; font-weight: bold;">
                            🔮 PROTOCOLE RENAISSANCE ACTIVÉ
                        </h3>
                        <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
                            Notre analyse détecte que vous pourriez bénéficier d'un accompagnement renforcé. 
                            Un nouveau chapitre commence pour vous ! ✨
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Affichage des recommandations Renaissance
                recommendations = renaissance_service.get_renaissance_recommendations(user.id)
                if recommendations:
                    st.markdown("### 🎯 Recommandations Renaissance")
                    for rec in recommendations:
                        st.markdown(f"• {rec}")
                    st.markdown("---")
            
            render_dashboard_ui(user.id, db_service)

        with tab4:
            render_coaching_ui(user.id, ai_coach_service, db_service, user_tier)
