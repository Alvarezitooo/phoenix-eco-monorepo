
import streamlit as st
import os

# --- GESTION CENTRALISÉE DE LA CONFIGURATION ET DES COMPOSANTS ---
from packages.phoenix_shared_config.settings import Settings
from packages.phoenix_shared_auth.services.phoenix_auth_service import PhoenixAuthService
from packages.phoenix_shared_auth.database.phoenix_db_connection import PhoenixDatabaseConnection
from packages.phoenix_shared_auth.services.jwt_manager import JWTManager
from packages.phoenix_shared_auth.entities.phoenix_user import PhoenixApp
from packages.phoenix_shared_ui.components.header import render_header
from packages.phoenix_shared_ui.components.consent_banner import render_consent_banner
# --- FIN DE LA GESTION CENTRALISÉE ---

# 2. Création d'une classe de configuration minimale
class Settings:
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.jwt_secret_key = os.environ.get("JWT_SECRET_KEY", "a_very_secure_secret_key_for_dev_use_only")
        self.jwt_algorithm = os.environ.get("JWT_ALGORITHM", "HS256")

    def is_valid(self):
        return self.supabase_url and self.supabase_key

# --- FIN DE L'INTÉGRATION DE L'AUTHENTIFICATION PARTAGÉE ---

# Imports originaux de Phoenix Aube
import asyncio
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from ...services.ia_validator import IAFutureValidator
from ...core import TransparencyEngine, PhoenixAubeEventStore, PhoenixAubeOrchestrator
from ...utils.mock_providers import MockEventStore, MockResearchProvider, MockRecommendationEngine
from .components import (
    render_hero_section,
    render_anxiety_test,
    render_career_exploration,
    render_ia_validation,
    render_ecosystem_transition,
    render_anxiety_results,
    render_ia_analysis_results,
    render_analytics_dashboard
)

# Configuration Streamlit
st.set_page_config(
    page_title="Phoenix Aube - Exploration Métier IA-proof",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ... (Le reste des fonctions render_* de Phoenix Aube restent ici) ...

def render_basic_interface():
    """Interface basique Phoenix Aube"""
    st.markdown("<h1>🔮 Phoenix Aube</h1>", unsafe_allow_html=True)
    st.write("Contenu de l'application Phoenix Aube.")

def render_login_form(auth_service: PhoenixAuthService):
    """Affiche le formulaire de connexion et d'inscription."""
    st.markdown("### 🔮 Bienvenue dans l'écosystème Phoenix")
    st.markdown("Connectez-vous pour commencer votre exploration métier.")

    login_tab, register_tab = st.tabs(["Connexion", "Inscription"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")
            if submitted:
                try:
                    user, access_token, refresh_token = auth_service.authenticate_user(
                        email=email, password=password, app=PhoenixApp.AUBE
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
                        email=email, password=password, username=username, source_app=PhoenixApp.AUBE
                    )
                    st.session_state['phoenix_user'] = user
                    st.success("Inscription réussie ! Vous pouvez maintenant vous connecter.")
                except ValueError as e:
                    st.error(e)


def render_aube_app():
    """Le contenu original de l'application Phoenix Aube."""
    render_header("Phoenix Aube", "🔮")
    interface_choice = st.sidebar.selectbox(
        "Mode d'interface:",
        ["Parcours Guidé (Recommandé)", "Trust by Design", "Mode Basique"]
    )
    
    if interface_choice == "Parcours Guidé (Recommandé)":
        # Simuler l'appel à la logique guidée
        st.write("Interface du Parcours Guidé.")
    elif interface_choice == "Trust by Design":
        # Simuler l'appel à la logique trust by design
        st.write("Interface Trust by Design.")
    else:
        render_basic_interface()


def main():
    """Point d'entrée principal avec gestion de l'authentification"""
    
    settings = Settings()
    if not settings.is_valid_for_db():
        st.error("La configuration de la base de données (Supabase) est manquante.")
        return

    db_connection = PhoenixDatabaseConnection(settings)
    jwt_manager = JWTManager(settings.jwt_secret_key, settings.jwt_algorithm)
    auth_service = PhoenixAuthService(db_connection, jwt_manager)

    if 'phoenix_user' in st.session_state:
        render_aube_app()
        if st.sidebar.button("Se déconnecter"):
            del st.session_state['phoenix_user']
            if 'access_token' in st.session_state:
                del st.session_state['access_token']
            st.rerun()
    else:
        render_login_form(auth_service)

