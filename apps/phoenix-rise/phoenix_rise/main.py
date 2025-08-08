import os

import google.generativeai as genai
import streamlit as st
from .core.supabase_client import supabase_client
from .services.ai_coach_service import AICoachService
from .services.auth_service import AuthService
from .services.mock_db_service import MockDBService
from .ui.auth_ui import render_auth_ui
from .ui.coaching_ui import render_coaching_ui
from .ui.dashboard_ui import render_dashboard_ui
from .ui.journal_ui import render_journal_ui
from .services.renaissance_protocol_service import PhoenixRiseRenaissanceService
# from phoenix_shared_ui.components import render_primary_button, render_info_card, render_section_header, render_alert, render_metric_card

# Import du style global du Design System
# with open("../../packages/phoenix-shared-ui/style.css") as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
    
    # 🚀 PHOENIX RISE - VERSION MINIMALE POUR TESTS
    st.title("🦋 Phoenix Rise")
    st.subheader("Coach IA pour Reconversion - En Construction")
    
    # 🔬 BANNIÈRE RECHERCHE-ACTION PHOENIX
    render_research_action_banner()
    
    st.info("🚧 Application en cours de développement. Les fonctionnalités complètes seront bientôt disponibles.")
    
    # Version simplifiée pour tests
    st.markdown("### 🎯 Fonctionnalités à venir :")
    st.markdown("- 📔 Journal de bord interactif")  
    st.markdown("- 🎯 Dashboard de progression")
    st.markdown("- 🤖 Coach IA personnalisé")
    st.markdown("- 🔮 Protocole Renaissance")
    
    # Test des services de base (commenté pour éviter les erreurs)
    # auth_service = get_auth_service()
    # db_service = get_db_service() 
    # ai_coach_service = get_ai_coach_service()
