"""
Point d'entrée principal de Phoenix Rise.
Assemble tous les composants dans une application cohérente.
"""

import streamlit as st
from services.auth_service import AuthService
from services.db_service import DBService
from services.ai_coach_service import AICoachService
from ui.journal_ui import render_journal_ui
from ui.dashboard_ui import render_dashboard_ui
from ui.coaching_ui import render_coaching_ui

# Configuration de la page
st.set_page_config(
    page_title="Phoenix Rise - Coach IA Reconversion",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_custom_css():
    """Charge le CSS personnalisé pour l'identité Phoenix."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    .phoenix-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
    }
    
    .phoenix-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .phoenix-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Sidebar personnalisée */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_auth_service():
    """Service d'authentification avec cache."""
    return AuthService()

@st.cache_resource  
def get_ai_service():
    """Service IA avec cache."""
    return AICoachService()

def get_db_service(auth_client):
    """Service de BDD (pas de cache car dépend de l'utilisateur)."""
    return DBService(auth_client)

def render_auth_interface(auth_service: AuthService):
    """Interface de connexion/inscription."""
    st.markdown("""
    <div class="phoenix-header">
        <div class="phoenix-title">🦋 Phoenix Rise</div>
        <div class="phoenix-subtitle">
            Votre coach IA personnel pour réussir votre reconversion professionnelle
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Onglets pour connexion/inscription
    tab1, tab2 = st.tabs(["🔑 Se Connecter", "📝 S'Inscrire"])
    
    with tab1:
        _render_signin_form(auth_service)
    
    with tab2:
        _render_signup_form(auth_service)

def _render_signin_form(auth_service: AuthService):
    """Formulaire de connexion."""
    st.subheader("Bienvenue ! Connectez-vous à votre compte")
    
    with st.form("signin_form"):
        email = st.text_input("📧 Email", placeholder="votre@email.com")
        password = st.text_input("🔐 Mot de passe", type="password")
        
        if st.form_submit_button("Se Connecter", type="primary", use_container_width=True):
            if email and password:
                success, error = auth_service.sign_in(email, password)
                if success:
                    st.success("🎉 Connexion réussie !")
                    st.rerun()
                else:
                    st.error(f"❌ {error}")
            else:
                st.warning("⚠️ Veuillez remplir tous les champs")

def _render_signup_form(auth_service: AuthService):
    """Formulaire d'inscription."""
    st.subheader("Créez votre compte Phoenix Rise")
    
    with st.form("signup_form"):
        email = st.text_input("📧 Email", placeholder="votre@email.com")
        password = st.text_input("🔐 Mot de passe", type="password", help="Minimum 6 caractères")
        password_confirm = st.text_input("🔐 Confirmer le mot de passe", type="password")
        
        terms = st.checkbox("J'accepte les conditions d'utilisation et la politique de confidentialité")
        
        if st.form_submit_button("Créer mon Compte", type="primary", use_container_width=True):
            if not all([email, password, password_confirm]):
                st.warning("⚠️ Veuillez remplir tous les champs")
            elif password != password_confirm:
                st.error("❌ Les mots de passe ne correspondent pas")
            elif len(password) < 6:
                st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
            elif not terms:
                st.warning("⚠️ Veuillez accepter les conditions d'utilisation")
            else:
                success, error = auth_service.sign_up(email, password)
                if success:
                    st.success("🎉 Compte créé avec succès !")
                    st.info("📧 Vérifiez votre email pour confirmer votre compte")
                    st.rerun()
                else:
                    st.error(f"❌ {error}")

def render_main_app(user, auth_service: AuthService):
    """Application principale pour utilisateur connecté."""
    # Stockage du client DB pour le cache
    st.session_state.db_client = auth_service.client
    
    # Initialisation des services
    db_service = get_db_service(auth_service.client)
    ai_service = get_ai_service()

    # Sidebar utilisateur
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 12px; margin-bottom: 1rem;">
            <h3>👋 Salut, {user.get_display_name()}</h3>
            <p style="opacity: 0.8; font-size: 0.9rem;">{user.email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Statistiques rapides
        stats = db_service.get_user_stats(user.id)
        if stats.get('total_entries', 0) > 0:
            st.markdown("#### 📊 Vos Stats")
            st.metric("Jours suivis", stats['total_entries'])
            st.metric("Humeur moy.", f"{stats.get('avg_mood', 0)}/10")
            st.metric("Confiance moy.", f"{stats.get('avg_confidence', 0)}/10")
        
        st.markdown("---")
        
        # Bouton de déconnexion
        if st.button("🚪 Se Déconnecter", type="secondary", use_container_width=True):
            auth_service.sign_out()
            st.cache_data.clear()  # Nettoyage des caches
            if 'db_client' in st.session_state:
                del st.session_state.db_client
            st.success("👋 À bientôt !")
            st.rerun()

    # Header principal
    st.markdown("""
    <div class="phoenix-header">
        <div class="phoenix-title">🦋 Phoenix Rise</div>
        <div class="phoenix-subtitle">Transformez vos doutes en confiance authentique</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation principale par onglets
    tab1, tab2, tab3 = st.tabs([
        "**🖋️ Mon Journal**", 
        "**📈 Mon Dashboard**", 
        "**🎯 Coaching Entretien**"
    ])

    with tab1:
        render_journal_ui(user.id, db_service, ai_service)
    
    with tab2:
        render_dashboard_ui(user.id, db_service)
    
    with tab3:
        render_coaching_ui(ai_service)

def main():
    """Fonction principale de l'application."""
    # Chargement du CSS
    load_custom_css()
    
    # Initialisation des services
    auth_service = get_auth_service()
    
    # Routage selon l'état d'authentification
    current_user = auth_service.get_current_user()
    
    if not current_user:
        render_auth_interface(auth_service)
    else:
        render_main_app(current_user, auth_service)

if __name__ == "__main__":
    main()
