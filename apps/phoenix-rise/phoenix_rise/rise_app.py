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


def load_custom_css():
    """Charge le CSS personnalisé pour l'identité Phoenix Rise."""
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #333333;
    }
    
    .main {
        background: linear-gradient(135deg, #f0f2f5 0%, #e0e5ec 100%); /* Light, subtle gradient */
    }
    
    .stApp {
        background: none; /* Ensure the app background is transparent to show main gradient */
    }

    .phoenix-header {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%); /* Deep purple to vibrant blue */
        color: white;
        padding: 2.5rem 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
    }
    .phoenix-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at center, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
        transform: rotate(45deg);
        opacity: 0.6;
    }
    .phoenix-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        text-shadow: 0 3px 6px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    .phoenix-subtitle {
        font-size: 1.4rem;
        font-weight: 400;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
        background: linear-gradient(45deg, #2575fc 0%, #6a11cb 100%) !important; /* Reverse gradient on hover */
    }
    
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #cccccc;
        padding: 0.75rem 1rem;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #2575fc;
        box-shadow: 0 0 0 0.2rem rgba(37, 117, 252, 0.25);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: #ffffff; /* Clean white sidebar */
        box-shadow: 2px 0 15px rgba(0,0,0,0.05);
    }
    .css-1d391kg .css-1v0mbdj {
        color: #333333; /* Darker text for better contrast */
    }
    .css-1d391kg .stButton > button {
        background: #f0f2f5 !important; /* Lighter buttons in sidebar */
        color: #333333 !important;
        box-shadow: none !important;
    }
    .css-1d391kg .stButton > button:hover {
        background: #e0e5ec !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: nowrap;
        background-color: #f0f2f5;
        border-radius: 8px 8px 0 0;
        gap: 10px;
        padding-left: 20px;
        padding-right: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] svg {
        display: none; /* Hide icons if any */
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
        border-bottom: 3px solid #6a11cb; /* Active tab indicator */
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_auth_service():
    return AuthService(supabase_client)


@st.cache_resource
def get_db_service():
    return MockDBService()


@st.cache_resource
def get_ai_coach_service():
    return AICoachService()


def render_profile_ui(user, db_service: MockDBService):
    """Affiche et gère l'interface utilisateur du profil."""
    st.header(f"Profil de {user.email.split('@')[0]}")
    profile = db_service.get_profile(user.id)
    if not profile:
        st.info("Complétez votre profil pour commencer.")
        with st.form("profile_form"):
            full_name = st.text_input("Nom complet")
            submitted = st.form_submit_button("Enregistrer")
            if submitted and full_name:
                db_service.create_profile(user.id, user.email, full_name)
                st.success("Profil enregistré !")
                st.rerun()
    else:
        st.write(f"**Nom:** {profile['full_name']}")


def main():
    """Point d'entrée principal de l'application."""
    load_custom_css()  # Load custom CSS

    auth_service = get_auth_service()
    db_service = get_db_service()
    ai_coach_service = get_ai_coach_service()

    if not auth_service.is_logged_in():
        render_auth_ui(auth_service)
    else:
        user = st.session_state["user"]

        # Custom Header for logged-in users
        st.markdown(
            """
            <div class="phoenix-header">
                <h1 class="phoenix-title">🦋 Phoenix Rise</h1>
                <p class="phoenix-subtitle">Transformez votre parcours de reconversion avec l'IA</p>
            </div>
            """,
            unsafe_allow_html=True,
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

            if st.button("🚪 Se Déconnecter"):
                auth_service.sign_out()
                st.rerun()

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


if __name__ == "__main__":
    main()
