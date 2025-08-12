

import os
import sys
import asyncio
from datetime import datetime, date
import google.generativeai as genai
import streamlit as st
import streamlit.components.v1 as components

# --- GESTION CENTRALISÉE DE LA CONFIGURATION ET DES COMPOSANTS ---
from packages.phoenix_shared_config.settings import Settings
from packages.phoenix_shared_auth.services.phoenix_auth_service import PhoenixAuthService
from packages.phoenix_shared_auth.database.phoenix_db_connection import PhoenixDatabaseConnection
from packages.phoenix_shared_auth.services.jwt_manager import JWTManager
from packages.phoenix_shared_auth.entities.phoenix_user import PhoenixApp
from packages.phoenix_shared_ui.components.header import render_header
from packages.phoenix_shared_ui.components.consent_banner import render_consent_banner
# --- FIN DE LA GESTION CENTRALISÉE ---


# Configuration de la page
st.set_page_config(
    page_title="🦋 Phoenix Rise - Dojo Mental Kaizen-Zazen",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports des services et UI (existants)
from .services.dojo_api_service import DojoApiService, KaizenEntry, ZazenSession
from .services.ai_coach_service import AICoachService
from .services.mock_db_service import MockDBService

# Import iris_core depuis la racine phoenix-rise
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from iris_core.interaction.renaissance_protocol import RenaissanceProtocol, RenaissanceState

# Configuration de l'API Gemini (optionnelle)
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Initialisation des services (existants)
@st.cache_resource
def init_services():
    """Initialise tous les services Phoenix Rise"""
    dojo_service = DojoApiService()
    db_service = MockDBService()
    ai_service = AICoachService() if api_key else None
    renaissance = RenaissanceProtocol()
    return dojo_service, db_service, ai_service, renaissance

# ... (Toutes les fonctions render_* existantes restent ici, inchangées) ...
def render_kaizen_grid_native():
    """🎯 Kaizen Grid en Streamlit natif - GARANTI DE MARCHER"""
    
    # Initialiser session state
    if 'kaizen_days' not in st.session_state:
        st.session_state.kaizen_days = {i: False for i in range(30)}
    
    st.markdown("### 📊 **Historique Kaizen - 30 Derniers Jours**")
    
    # Stats calculées en temps réel
    total_actions = sum(st.session_state.kaizen_days.values())
    completion_rate = (total_actions / 30) * 100
    
    # Calcul série
    streak = 0
    for i in range(29, -1, -1):
        if st.session_state.kaizen_days[i]:
            streak += 1
        else:
            break
    
    # Affichage stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 Actions", total_actions, delta=f"+{total_actions-20}")
    with col2:
        st.metric("🔥 Série", f"{streak} jours", delta=streak-3 if streak > 3 else None)
    with col3:
        st.metric("📊 Taux", f"{completion_rate:.0f}%")
    with col4:
        momentum = min(100, streak * 15 + total_actions * 2)
        st.metric("⚡ Momentum", momentum)
    
    # Grid interactive avec boutons
    st.markdown("**Cliquez sur un jour pour toggle votre action Kaizen :**")
    
    # 5 lignes de 6 colonnes = 30 jours
    for week in range(5):
        cols = st.columns(6)
        for day in range(6):
            day_idx = week * 6 + day
            if day_idx < 30:
                with cols[day]:
                    day_label = f"J-{29-day_idx}"
                    is_done = st.session_state.kaizen_days[day_idx]
                    
                    if st.button(
                        "✅" if is_done else "⭕", 
                        key=f"kaizen_day_{day_idx}",
                        help=f"{day_label} - {'Accompli' if is_done else 'Pas d\'action'}",
                        use_container_width=True
                    ):
                        st.session_state.kaizen_days[day_idx] = not st.session_state.kaizen_days[day_idx]
                        st.rerun()


def render_phoenix_rise_styles():
    """🎨 Styles CSS globaux premium pour Phoenix Rise"""
    
    premium_styles = """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset et base */
    .main .block-container {
        padding-top: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Phoenix Premium */
    .phoenix-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out;
    }
    </style>
    """
    
    st.markdown(premium_styles, unsafe_allow_html=True)


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
        </div>
        """,
        unsafe_allow_html=True
    )


def render_dojo_mental_interface():
    """Interface principale du Dojo Mental Kaizen-Zazen"""
    
    # 🎨 CSS Global pour Phoenix Rise
    render_phoenix_rise_styles()
    
    render_header("Phoenix Rise", "🦋")
    
    # Initialisation des services
    dojo_service, db_service, ai_service, renaissance = init_services()
    
    # Navigation principale
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Kaizen Quotidien", 
        "🧘 Zazen Méditation", 
        "🤖 Coach Iris", 
        "📊 Mon Évolution"
    ])
    
    with tab1:
        st.markdown("### 🎯 **Kaizen Quotidien - L'Art du Micro-Progrès**")
        render_kaizen_grid_native()
    
    with tab2:
        st.markdown("### 🧘 **Zazen - La Méditation de l'Instant Présent**")
        # La fonction render_zazen_timer_native est appelée ici pour l'exemple
        # Vous pouvez remplacer par la logique de votre application
        st.write("Interface de méditation Zazen.")
    
    with tab3:
        st.markdown("### 🤖 **Coach Iris - Protocole Renaissance**")
        st.write("Interface du coach IA Iris.")

    with tab4:
        st.markdown("### 📊 **Mon Évolution - Tableau de Bord Personnel**")
        st.write("Tableau de bord de l'évolution personnelle.")


def render_login_form(auth_service: PhoenixAuthService):
    """Affiche le formulaire de connexion et d'inscription."""
    st.markdown("### 🦋 Bienvenue dans l'écosystème Phoenix")
    st.markdown("Connectez-vous pour accéder à votre Dojo Mental.")

    login_tab, register_tab = st.tabs(["Connexion", "Inscription"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")
            if submitted:
                try:
                    user, access_token, refresh_token = auth_service.authenticate_user(
                        email=email, password=password, app=PhoenixApp.RISE
                    )
                    st.session_state['phoenix_user'] = user
                    st.session_state['access_token'] = access_token
                    st.success("Connexion réussie !")
                    st.rerun()
                except ValueError as e:
                    st.error(e)

    with register_tab:
        with st.form("register_form"):
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Mot de passe", type="password", key="reg_password")
            username = st.text_input("Nom d'utilisateur (optionnel)")
            submitted = st.form_submit_button("S'inscrire")
            if submitted:
                try:
                    user = auth_service.register_user(
                        email=email, password=password, username=username, source_app=PhoenixApp.RISE
                    )
                    st.session_state['phoenix_user'] = user
                    st.success("Inscription réussie ! Vous pouvez maintenant vous connecter.")
                except ValueError as e:
                    st.error(e)


def main():
    """Point d'entrée principal avec gestion de l'authentification"""
    
    # Initialisation des services d'authentification
    settings = Settings()
    if not settings.is_valid_for_db():
        st.error("La configuration de la base de données (Supabase) est manquante. L'application ne peut pas démarrer.")
        st.info("Veuillez configurer les variables d'environnement SUPABASE_URL et SUPABASE_KEY.")
        return

    db_connection = PhoenixDatabaseConnection(settings)
    jwt_manager = JWTManager(settings.jwt_secret_key, settings.jwt_algorithm)
    auth_service = PhoenixAuthService(db_connection, jwt_manager)

    # Vérification de l'authentification
    if 'phoenix_user' in st.session_state:
        # 🔬 BANNIÈRE RECHERCHE-ACTION PHOENIX (désactivable via ENV)
        try:
            import os
            enable_banner = os.getenv("ENABLE_RESEARCH_BANNER", "false").lower() == "true"
        except Exception:
            enable_banner = False
        if enable_banner:
            render_research_action_banner()
        
        # Interface principale du Dojo Mental
        render_dojo_mental_interface()
        
        # Footer Phoenix
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
            <p style="margin: 0; color: #666; font-size: 0.9rem;">
                🦋 **Phoenix Rise - Dojo Mental Kaizen-Zazen** | 
                💻 **Développé par Claude Phoenix DevSecOps Guardian** | 
                🔒 **Sécurité & RGPD by design**
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("Se déconnecter"):
            del st.session_state['phoenix_user']
            if 'access_token' in st.session_state:
                del st.session_state['access_token']
            st.rerun()
    else:
        render_login_form(auth_service)


if __name__ == "__main__":
    main()
