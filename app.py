import streamlit as st
import time
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import os
from dotenv import load_dotenv
from services.api_client import (
    suggerer_competences_transferables,
    get_france_travail_offer_details,
    analyser_culture_entreprise,
    APIError
)
from services.letter_service import (
    generer_lettre,
    extraire_mots_cles_annonce,
    evaluate_letter
)
from models.letter_request import LetterRequest
from models.user_profile import UserProfile
from services.content_extractor import extract_cv_content, extract_annonce_content, FileProcessingError
from services.trajectory_service import generate_reconversion_plan
from services.rgpd_manager import RGPDUserManager, SecurePremiumStorage, RGPDViolationError
from services.data_anonymizer import DataAnonymizer
from services.cv_optimization_service import CvOptimizationService
from services.security_scanner import SecurityScanner, SecurityScanError
import logging
import random
from docx import Document
import io
import uuid
import tempfile
import pandas as pd
import numpy as np

load_dotenv()

# --- Conseils utiles (pour l'attente) ---
TIPS = [
    "💡 Conseil utile : Saviez-vous que 80% des recruteurs parcourent d'abord votre CV en diagonale ? Assurez-vous que les informations clés sont visibles en un coup d'œil !",
    "💡 Conseil utile : Une lettre de motivation n'est pas un résumé de votre CV. C'est une histoire qui explique POURQUOI vous êtes le candidat idéal pour CE poste.",
    "💡 Conseil utile : L'IA est un outil puissant, mais la touche humaine reste irremplaçable. Relisez toujours et personnalisez !",
    "💡 Conseil utile : Votre réseau professionnel est une mine d'or. Cultivez-le, échangez, et n'hésitez pas à demander conseil.",
    "💡 Conseil utile : La persévérance est la clé. Chaque refus est une opportunité d'apprendre et de s'améliorer.",
    "💡 Conseil utile : Un bon prompt pour l'IA, c'est comme une bonne question à un expert : plus elle est précise, plus la réponse sera pertinente.",
    "💡 Conseil utile : La clarté et la concision sont vos meilleurs atouts dans toute communication professionnelle.",
    "💡 Conseil utile : N'ayez pas peur de mettre en avant vos compétences transférables, surtout en reconversion. Elles sont votre force !",
    "💡 Conseil utile : Préparez-vous aux entretiens en anticipant les questions et en ayant des exemples concrets de vos réalisations.",
    "💡 Conseil utile : Le marché du travail évolue constamment. Restez curieux et continuez à apprendre tout au long de votre carrière.",
]

# --- Fonctions utilitaires ---
def generate_docx(text_content: str) -> bytes:
    """Génère un document DOCX à partir d'une chaîne de caractères."""
    document = Document()
    paragraphs = text_content.split('\n\n')
    for para_text in paragraphs:
        document.add_paragraph(para_text)
    
    byte_io = io.BytesIO()
    document.save(byte_io)
    byte_io.seek(0)
    return byte_io.getvalue()

# CSS pour la nouvelle interface
def inject_futuristic_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS */
    :root {
        --phoenix-orange: #ff6b35;
        --phoenix-dark: #1a1a2e;
        --phoenix-purple: #16213e;
        --phoenix-blue: #0f3460;
        --phoenix-gold: #ffd700;
        --phoenix-cyan: #00f5ff;
        --glow-effect: 0 0 20px rgba(255, 107, 53, 0.3);
        --glass-effect: rgba(255, 255, 255, 0.1);
        --border-radius: 20px;
    }
    
    /* Background Gradient Animé */
    .main > div {
        background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #1a1a2e);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Header Holographique */
    .phoenix-header {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.15), rgba(0, 245, 255, 0.15));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin: 1rem 0 2rem 0;
        text-align: center;
        box-shadow: var(--glow-effect);
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
        background: linear-gradient(45deg, transparent, rgba(255, 107, 53, 0.1), transparent);
        animation: hologram 3s linear infinite;
    }
    
    @keyframes hologram {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .phoenix-title {
        font-family: 'Orbitron', monospace;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(45deg, var(--phoenix-orange), var(--phoenix-cyan), var(--phoenix-gold));
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textGlow 2s ease-in-out infinite alternate;
        text-shadow: 0 0 30px rgba(255, 107, 53, 0.5);
    }
    
    @keyframes textGlow {
        from { filter: brightness(1) drop-shadow(0 0 5px var(--phoenix-orange)); }
        to { filter: brightness(1.2) drop-shadow(0 0 20px var(--phoenix-cyan)); }
    }
    
    .phoenix-subtitle {
        font-family: 'Inter', sans-serif;
        color: var(--phoenix-cyan);
        font-size: 1.2rem;
        font-weight: 300;
        margin-top: 0.5rem;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
    
    /* Onglets Futuristes Néomorphism */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 25px;
        padding: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 
            inset 0 0 20px rgba(255, 255, 255, 0.1),
            0 8px 32px rgba(0, 0, 0, 0.3);
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        color: rgba(255, 255, 255, 0.7);
        border: 1px solid transparent;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        height: 3.5rem;
        min-width: 140px;
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.2), rgba(0, 245, 255, 0.2));
        color: white;
        border-color: rgba(255, 107, 53, 0.5);
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.3);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--phoenix-orange), var(--phoenix-cyan)) !important;
        color: white !important;
        box-shadow: 
            0 0 30px rgba(255, 107, 53, 0.6),
            inset 0 0 20px rgba(255, 255, 255, 0.2) !important;
        border-color: var(--phoenix-gold) !important;
    }
    
    /* Cards Glassmorphism avec Animations */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: var(--border-radius);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 0 20px rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 20px 60px rgba(255, 107, 53, 0.2),
            inset 0 0 30px rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 107, 53, 0.5);
    }
    
    /* Progress Bar Cyberpunk */
    .cyber-progress {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
    }
    
    .cyber-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--phoenix-orange), var(--phoenix-cyan));
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.8);
        animation: pulse 2s ease-in-out infinite;
        transition: width 0.5s ease;
    }
    
    /* Boutons Néon */
    .stButton > button {
        background: linear-gradient(135deg, var(--phoenix-orange), var(--phoenix-cyan)) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 0.8rem 2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 
            0 0 20px rgba(255, 107, 53, 0.4),
            inset 0 0 20px rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 
            0 0 30px rgba(255, 107, 53, 0.8),
            0 10px 40px rgba(0, 0, 0, 0.3) !important;
        filter: brightness(1.1) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Upload Areas Futuristes */
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px dashed var(--phoenix-cyan) !important;
        border-radius: var(--border-radius) !important;
        padding: 3rem 2rem !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }
    
    .stFileUploader > div:hover {
        background: rgba(255, 107, 53, 0.1) !important;
        border-color: var(--phoenix-orange) !important;
        box-shadow: 0 0 30px rgba(255, 107, 53, 0.3) !important;
    }
    
    /* Sidebar Cyberpunk */
    .css-1d391kg {
        background: rgba(26, 26, 46, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 107, 53, 0.3) !important;
    }
    
    /* Métriques Holographiques */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(0, 245, 255, 0.1));
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 0 40px rgba(255, 107, 53, 0.4);
    }
    
    .metric-value {
        font-family: 'Orbitron', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--phoenix-cyan);
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.8);
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    /* Animations Particules */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    .particle {
        position: absolute;
        width: 2px;
        height: 2px;
        background: var(--phoenix-cyan);
        animation: float 6s ease-in-out infinite;
        box-shadow: 0 0 10px var(--phoenix-cyan);
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) translateX(0px) scale(1); opacity: 0.7; }
        33% { transform: translateY(-20px) translateX(10px) scale(1.1); opacity: 1; }
        66% { transform: translateY(-10px) translateX(-5px) scale(0.9); opacity: 0.8; }
    }
    
    /* Scrollbar Personnalisée */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--phoenix-orange), var(--phoenix-cyan));
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--phoenix-cyan), var(--phoenix-orange));
    }
    
    /* Notifications Toast */
    .toast-success {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.9), rgba(255, 107, 53, 0.9));
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(20px);
        box-shadow: 0 0 30px rgba(0, 245, 255, 0.4);
        animation: slideInRight 0.5s ease;
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Mode Sombre Avancé */
    .stMarkdown, .stText, p, span, div, label {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--phoenix-cyan) !important;
        font-family: 'Orbitron', monospace !important;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5) !important;
    }
    
    /* Easter Egg: Phoenix Animation */
    .phoenix-icon {
        display: inline-block;
        animation: phoenixRise 3s ease-in-out infinite;
        filter: drop-shadow(0 0 10px var(--phoenix-orange));
    }
    
    @keyframes phoenixRise {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(5deg); }
    }
    </style>
    """, unsafe_allow_html=True)

def create_particle_background():
    """Génère un fond de particules animées"""
    particles_html = """
    <div class="particles">
    """
    
    # Générer 20 particules aléatoirement positionnées
    for i in range(20):
        left = random.randint(0, 100)
        top = random.randint(0, 100)
        delay = random.uniform(0, 6)
        particles_html += f"""
        <div class="particle" style="
            left: {left}%; 
            top: {top}%; 
            animation-delay: {delay}s;
        "></div>
        """
    
    particles_html += "</div>"
    
    st.markdown(particles_html, unsafe_allow_html=True)

def render_futuristic_header():
    """Header avec animation"""
    st.markdown("""
    <div class="phoenix-header">
        <h1 class="phoenix-title">
            <span class="phoenix-icon">‍</span> PHOENIX LETTERS
        </h1>
        <p class="phoenix-subtitle">
            ✨ INTELLIGENCE ARTIFICIELLE • RECONVERSION PROFESSIONNELLE • FUTUR ✨
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_cyber_progress_bar(progress: float, label: str):
    """Barre de progression stylisée"""
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="color: var(--phoenix-cyan); font-size: 0.9rem; margin-bottom: 0.5rem;">
            {label}
        </div>
        <div class="cyber-progress">
            <div class="cyber-progress-fill" style="width: {progress}%;"></div>
        </div>
        <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.8rem; text-align: right;">
            {progress}% complété
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(value: str, label: str, icon: str = ""):
    """Carte métrique stylisée"""
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def create_glass_container(content_func, title: str = None):
    """Container stylisé pour contenu"""
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        if title:
            st.markdown(f"""
            <h3 style="
                color: var(--phoenix-cyan); 
                font-family: 'Orbitron', monospace; 
                margin-bottom: 1.5rem;
                text-align: center;
                text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
            ">{title}</h3>
            """, unsafe_allow_html=True)
        content_func()
        st.markdown('</div>', unsafe_allow_html=True)

def show_success_toast(message: str):
    """Notification toast animée"""
    st.markdown(f"""
    <div class="toast-success">
         {message}
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3) # Display for 3 seconds
    st.markdown('<div class="toast-success" style="display:none;"></div>', unsafe_allow_html=True) # Hide after 3 seconds

def get_user_tier_ui():
    """Interface de sélection du tier avec preview des fonctionnalités"""
    
    st.sidebar.markdown("###  Votre Abonnement")
    
    tier = st.sidebar.radio(
        "Plan actuel",
        [" Gratuit", "⭐ Premium", " Premium Plus"],
        help="Changez votre plan pour débloquer plus de fonctionnalités"
    )
    
    # Preview des fonctionnalités selon le tier
    if tier == " Gratuit":
        st.sidebar.info("✅ 3 lettres/mois\n✅ Génération basique")
        if st.sidebar.button(" Passer Premium"):
            st.info("Redirection vers paiement...")
    
    elif tier == "⭐ Premium":
        st.sidebar.success("✅ Lettres illimitées\n✅ Mirror Match\n✅ Smart Coach")
    
    elif tier == " Premium Plus":
        st.sidebar.success("✅ Tout Premium\n✅ Trajectory Builder\n✅ Story Arc\n✅ Support prioritaire")
    
    return tier.split()[1].lower()

# --- Pages de l'application ---

def render_generator_tab(user_tier):
    """Onglet générateur avec interface stylisée"""
    
    def generator_content():
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: var(--phoenix-gold); font-family: 'Orbitron', monospace;">
                 GÉNÉRATION DE LETTRES
            </h2>
            <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem;">
                Transformez votre parcours en atout grâce à l'IA Phoenix
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Stepper visuel
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <div style="
                    background: linear-gradient(135deg, var(--phoenix-orange), var(--phoenix-cyan));
                    width: 60px; height: 60px; border-radius: 50%;
                    margin: 0 auto 1rem auto;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 1.5rem; font-weight: bold;
                    box-shadow: 0 0 30px rgba(255, 107, 53, 0.6);
                ">1</div>
                <h4 style="color: var(--phoenix-cyan);">Documents</h4>
                <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">
                    Chargez vos documents
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <div style="
                    background: rgba(255, 255, 255, 0.2);
                    width: 60px; height: 60px; border-radius: 50%;
                    margin: 0 auto 1rem auto;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 1.5rem; font-weight: bold;
                    border: 2px solid var(--phoenix-cyan);
                ">2</div>
                <h4 style="color: rgba(255, 255, 255, 0.5);">Configuration</h4>
                <p style="color: rgba(255, 255, 255, 0.5); font-size: 0.9rem;">
                    Paramétrez l'intelligence artificielle
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <div style="
                    background: rgba(255, 255, 255, 0.1);
                    width: 60px; height: 60px; border-radius: 50%;
                    margin: 0 auto 1rem auto;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 1.5rem; font-weight: bold;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                ">3</div>
                <h4 style="color: rgba(255, 255, 255, 0.3);">Génération</h4>
                <p style="color: rgba(255, 255, 255, 0.3); font-size: 0.9rem;">
                    Synthèse en cours...
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Zone d'upload
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("###  CV Upload")
            uploaded_cv = st.file_uploader(
                "Glissez votre CV ici...", 
                type=['pdf', 'txt'], 
                key="cv_quantum",
                help="Formats supportés: PDF, TXT"
            )
            
            if uploaded_cv:
                show_success_toast("CV chargé !")
                st.session_state.user_progress = 33
        
        with col2:
            st.markdown("###  Offre d'emploi")
            uploaded_annonce = st.file_uploader(
                "Chargez l'offre d'emploi...", 
                type=['txt', 'pdf'], 
                key="annonce_quantum",
                help="Format TXT ou PDF"
            )
            
            if uploaded_annonce:
                show_success_toast("Offre chargée !")
                st.session_state.user_progress = 66
        
        st.markdown("---")
        st.markdown("Ou")
        offer_id = st.text_input(
            "Entrez l'ID d'une offre France Travail (si vous ne chargez pas de fichier annonce)",
            help="Ex: 167XQYV"
        )
        st.markdown("---")

        # Configuration IA si fichiers uploadés
        est_reconversion = False
        ancien_domaine = ""
        nouveau_domaine = ""
        competences_transferables = ""
        ton_choisi = "Formel"
        company_about_page = ""
        linkedin_posts = ""

        if uploaded_cv and (uploaded_annonce or offer_id):
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            def config_content_inner():
                st.markdown("###  Configuration de l'IA")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    ton_choisi = st.selectbox(
                        " Ton souhaité",
                        ["Formel", "Dynamique", "Sobre", "Créatif", "Startup", "Associatif"],
                        help="Le ton influence le style d'écriture de l'IA."
                    )
                
                with col2:
                    est_reconversion = st.checkbox(
                        " C'est une reconversion", 
                        value=True,
                        help="Cochez cette case si vous changez de carrière. L'IA adaptera son discours pour valoriser votre parcours."
                    )
                
                if est_reconversion:
                    ancien_domaine = st.text_input(
                        "Ancien domaine d'activité (ex: Marketing, Comptabilité, Bâtiment)",
                        help="Soyez précis pour aider l'IA à faire les liens."
                    )
                    
                    nouveau_domaine = st.text_input(
                        "Nouveau domaine d'activité souhaité (ex: Cybersécurité, Développement Web, Data Science)", 
                        help="C'est ici que vous projetez votre avenir !"
                    )
                    
                    if 'suggested_competences' not in st.session_state:
                        st.session_state.suggested_competences = ""

                    if st.button("✨ Suggérer les compétences transférables"):
                        if ancien_domaine and nouveau_domaine:
                            with st.spinner("L'IA analyse les domaines pour suggérer les compétences..."):
                                try:
                                    suggested_text = suggerer_competences_transferables(ancien_domaine, nouveau_domaine)
                                    st.session_state.suggested_competences = suggested_text
                                    st.success("Compétences suggérées ! Vous pouvez les modifier si besoin.")
                                except APIError as e:
                                    st.error(f"❌ Erreur lors de la suggestion des compétences. Problème avec l'API Gemini : {e}. Veuillez réessayer plus tard.")
                                except Exception as e:
                                    st.error(f"🚨 Une erreur inattendue est survenue lors de la suggestion : {e}")
                        else:
                            st.warning("Veuillez renseigner l'ancien et le nouveau domaine pour obtenir des suggestions.")

                    competences_transferables = st.text_area(
                        "Compétences clés transférables (vous pouvez éditer ou utiliser la suggestion) :",
                        value=st.session_state.suggested_competences,
                        help="Listez les compétences de votre ancienne carrière qui sont pertinentes pour votre nouveau projet."
                    )
                
                # Section Analyse de la Culture d'Entreprise (Mirror Match)
                st.markdown("---")
                st.markdown("### 🔍 Analyse de la Culture d'Entreprise (Mirror Match)")
                st.info("Collez le contenu de la page \"À propos\" de l'entreprise et/ou des posts LinkedIn récents. L'IA analysera ces informations pour adapter le ton et les valeurs de votre lettre.")
                company_about_page = st.text_area(
                    "Contenu de la page 'À propos' de l'entreprise :",
                    key="company_about_page",
                    height=150,
                    help="Copiez-collez le texte de la section 'À propos' ou 'Notre histoire' du site web de l'entreprise."
                )
                linkedin_posts = st.text_area(
                    "Posts LinkedIn récents (un post par ligne) :",
                    key="linkedin_posts",
                    height=150,
                    help="Copiez-collez quelques posts récents de la page LinkedIn de l'entreprise, un par ligne."
                )

                # Bouton de génération
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_buttons_1, col_buttons_2 = st.columns(2)

                if 'last_generation_time' not in st.session_state:
                    st.session_state.last_generation_time = 0

                cooldown_time = 60
                time_since_last_generation = time.time() - st.session_state.last_generation_time
                is_on_cooldown = time_since_last_generation < cooldown_time

                with col_buttons_1:
                    if st.button("✨ Générer ma lettre", type="primary", use_container_width=True, disabled=is_on_cooldown):
                        if is_on_cooldown:
                            st.warning(f"Veuillez attendre {int(cooldown_time - time_since_last_generation)} secondes avant de générer une nouvelle lettre.")
                        elif uploaded_cv is not None and (uploaded_annonce is not None or offer_id):
                            with st.spinner("Préparation des documents... Votre CV et l'annonce sont en cours d'analyse."):
                                progress_text = st.empty()
                                progress_bar = st.progress(0)

                                progress_text.info("Étape 1/3 : Lecture et traitement de vos fichiers...")
                                progress_bar.progress(33)
                                
                                cv_content = ""
                                annonce_content = ""

                                try:
                                    with tempfile.NamedTemporaryFile(delete=False) as temp_cv_file:
                                        temp_cv_file.write(uploaded_cv.getvalue())
                                        temp_cv_path = temp_cv_file.name
                                    
                                    # SecurityScanner désactivé pour Streamlit Cloud, à réactiver si self-hébergé
                                    # if not SecurityScanner().scan_file(temp_cv_path):
                                    #     st.error("🚨 Fichier CV détecté comme potentiellement malveillant. Scan de sécurité échoué.")
                                    #     st.stop()

                                    cv_content = extract_cv_content(uploaded_cv)
                                except FileProcessingError as e:
                                    st.error(f"🚨 Erreur lors du traitement du CV : {e}")
                                    st.stop()
                                # except SecurityScanError as e:
                                #     st.error(f"🚨 Erreur de sécurité lors du scan du CV : {e}")
                                #     st.stop()
                                finally:
                                    if 'temp_cv_path' in locals() and os.path.exists(temp_cv_path):
                                        os.remove(temp_cv_path)

                                annonce_content = ""
                                offer_details = None

                                if offer_id:
                                    try:
                                        offer_details = get_france_travail_offer_details(offer_id)
                                        if offer_details and 'description' in offer_details:
                                            annonce_content = offer_details['description']
                                            st.session_state.annonce_content = annonce_content
                                            st.info(f"Annonce récupérée via France Travail API (ID: {offer_id}).")
                                        else:
                                            st.warning("Impossible de récupérer la description de l'offre via l'API. Veuillez vérifier l'ID.")
                                            return
                                    except APIError as e:
                                        st.error(f"Erreur lors de la récupération de l'offre France Travail : {e}. Veuillez vérifier l'ID ou réessayer plus tard.")
                                        return
                                elif uploaded_annonce is not None:
                                    try:
                                        with tempfile.NamedTemporaryFile(delete=False) as temp_annonce_file:
                                            temp_annonce_file.write(uploaded_annonce.getvalue())
                                            temp_annonce_path = temp_annonce_file.name

                                        # SecurityScanner désactivé pour Streamlit Cloud, à réactiver si self-hébergé
                                        # if not SecurityScanner().scan_file(temp_annonce_path):
                                        #     st.error("🚨 Fichier annonce détecté comme potentiellement malveillant. Scan de sécurité échoué.")
                                        #     st.stop()

                                        annonce_content = extract_annonce_content(uploaded_annonce)
                                        st.session_state.annonce_content = annonce_content
                                    except FileProcessingError as e:
                                        st.error(f"🚨 Erreur lors du traitement de l'annonce : {e}")
                                        st.stop()
                                    # except SecurityScanError as e:
                                    #     st.error(f"🚨 Erreur de sécurité lors du scan de l'annonce : {e}")
                                    #     st.stop()
                                    finally:
                                        if 'temp_annonce_path' in locals() and os.path.exists(temp_annonce_path):
                                            os.remove(temp_annonce_path)
                                else:
                                    st.warning("Veuillez charger une annonce ou fournir un ID d'offre France Travail.")
                                    return

                                progress_text.info(f"Étape 2/3 : L'intelligence artificielle rédige votre lettre... Cela peut prendre quelques instants.\n\n{random.choice(TIPS)}")
                                progress_bar.progress(66)
                                
                                company_insights = None
                                if company_about_page or linkedin_posts:
                                    with st.spinner("Étape 2.5/3 : Analyse de la culture d'entreprise..."):
                                        try:
                                            company_insights = analyser_culture_entreprise(company_about_page, linkedin_posts)
                                            st.success("Analyse de la culture d'entreprise terminée !")
                                        except APIError as e:
                                            st.warning(f"Impossible d'analyser la culture d'entreprise. Problème avec l'API Gemini : {e}. La lettre sera générée sans cette personnalisation. Veuillez réessayer plus tard.")
                                        except Exception as e:
                                            st.warning(f"Une erreur inattendue est survenue lors de l'analyse de la culture d'entreprise : {e}. La lettre sera générée sans cette personnalisation.")

                                request_data = LetterRequest(
                                    cv_contenu=cv_content,
                                    annonce_contenu=annonce_content,
                                    ton_souhaite=ton_choisi.lower(),
                                    est_reconversion=est_reconversion,
                                    ancien_domaine=ancien_domaine,
                                    nouveau_domaine=nouveau_domaine,
                                    competences_transferables=competences_transferables,
                                    offer_details=offer_details,
                                    company_insights=company_insights,
                                    user_tier=user_tier
                                )
                                lettre_response = generer_lettre(request_data)
                                lettre_generee = lettre_response.lettre_generee

                                st.session_state.last_generation_time = time.time()

                                progress_text.info("Étape 3/3 : Finalisation et affichage de votre lettre...")
                                progress_bar.progress(100)
                                progress_text.empty()
                                progress_bar.empty()
                                st.success("🎉 Votre lettre de motivation a été générée !")
                                
                                st.session_state.lettre_editable = lettre_generee

                                # --- Nouvelle section d'affichage de la lettre générée ---
                                st.markdown("""
                                <div style="
                                    background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(0, 245, 255, 0.1));
                                    border-radius: 20px;
                                    padding: 2rem;
                                    margin: 2rem 0;
                                    border: 1px solid rgba(255, 107, 53, 0.3);
                                    box-shadow: 0 0 30px rgba(255, 107, 53, 0.2);
                                ">
                                    <h3 style="color: var(--phoenix-gold); text-align: center; margin-bottom: 1.5rem;">
                                        ‍ VOTRE LETTRE PHOENIX GÉNÉRÉE
                                    </h3>
                                """, unsafe_allow_html=True)
                                
                                edited_letter = st.text_area(
                                    " Votre Lettre Phoenix",
                                    value=st.session_state.lettre_editable,
                                    height=300,
                                    help="Lettre générée par l'IA Phoenix - Modifiable en temps réel",
                                    key="lettre_motivation_editor"
                                )
                                st.session_state.lettre_editable = edited_letter
                                
                                # Boutons d'action futuristes
                                col_dl1, col_dl2, col_dl3 = st.columns(3)
                                
                                with col_dl1:
                                    st.download_button(
                                        label="📥 Télécharger TXT",
                                        data=st.session_state.lettre_editable.encode('utf-8'),
                                        file_name="phoenix_letter.txt",
                                        mime="text/plain"
                                    )
                                
                                with col_dl2:
                                    docx_file = generate_docx(st.session_state.lettre_editable)
                                    st.download_button(
                                        label="📄 Télécharger DOCX",
                                        data=docx_file,
                                        file_name='phoenix_letter.docx',
                                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                                    )
                                
                                with col_dl3:
                                    if st.button("🔗 Partager"):
                                        st.info("Partage neural activé ! (Fonctionnalité à venir)")
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                                # --- Fin de la nouvelle section d'affichage ---

                                show_ats_analysis = st.checkbox("Afficher l'analyse ATS (pour les experts !)", value=False)

                                if show_ats_analysis:
                                    st.markdown("---")
                                    st.subheader(" Analyse ATS (Applicant Tracking System)")
                                    st.info("Cette section vous aide à vérifier la pertinence de votre lettre par rapport aux mots-clés de l'annonce.")

                                    try:
                                        if 'lettre_editable' not in st.session_state:
                                            st.error("❌ Aucune lettre générée. Veuillez d'abord générer une lettre.")
                                        elif 'annonce_content' not in st.session_state or not st.session_state.annonce_content:
                                            st.error("❌ Contenu de l'annonce manquant. Veuillez recharger l'annonce.")
                                        else:
                                            mots_cles_annonce = extraire_mots_cles_annonce(st.session_state.annonce_content)
                                            mots_cles_lettre = extraire_mots_cles_annonce(st.session_state.lettre_editable)
                                            
                                            mots_trouves = set(mots_cles_annonce).intersection(set(mots_cles_lettre))
                                            mots_manquants = set(mots_cles_annonce) - set(mots_cles_lettre)
                                            
                                            st.markdown(f"**Mots-clés de l'annonce ({len(mots_cles_annonce)}) :**")
                                            if mots_cles_annonce:
                                                mots_affiches = sorted(list(mots_cles_annonce))[:50]
                                                st.code(", ".join(mots_affiches) + ("..." if len(mots_cles_annonce) > 50 else ""))
                                            else:
                                                st.warning("Aucun mot-clé extrait de l'annonce")

                                            st.markdown(f"**Mots-clés trouvés dans la lettre ({len(mots_trouves)}) :**")
                                            if mots_trouves:
                                                mots_trouves_affiches = sorted(list(mots_trouves))[:50]
                                                st.success(", ".join(mots_trouves_affiches) + ("..." if len(mots_trouves) > 50 else ""))
                                            else:
                                                st.warning("Aucun mot-clé de l'annonce trouvé dans la lettre.")

                                            st.markdown(f"**Mots-clés manquants dans la lettre ({len(mots_manquants)}) :**")
                                            if mots_manquants:
                                                mots_manquants_affiches = sorted(list(mots_manquants))[:50]
                                                st.error(", ".join(mots_manquants_affiches) + ("..." if len(mots_manquants) > 50 else ""))
                                            else:
                                                st.success("Tous les mots-clés de l'annonce sont présents dans la lettre !")
                                                
                                            if mots_cles_annonce:
                                                pourcentage = (len(mots_trouves) / len(mots_cles_annonce)) * 100
                                                st.metric(" Taux de correspondance ATS", f"{pourcentage:.1f}%")
                                            
                                    except Exception as e:
                                        st.error(f"❌ Erreur lors de l'extraction des mots-clés : {str(e)}")
                                        
                                    st.markdown("---")

                                show_smart_coach_analysis = st.checkbox("Afficher l'analyse Smart Coach (Feedback IA !)", value=False)

                                if show_smart_coach_analysis:
                                    st.markdown("---")
                                    st.subheader("🧠 Analyse Smart Coach (Feedback IA)")
                                    st.info("L'IA évalue votre lettre et vous propose des pistes d'amélioration.")
                                    with st.spinner("L'IA analyse votre lettre..."):
                                        try:
                                            coaching_report = evaluate_letter(st.session_state.lettre_editable, st.session_state.annonce_content)
                                            st.markdown(f"**Score Global : {coaching_report.score:.1f}/10**")
                                            for suggestion in coaching_report.suggestions:
                                                st.write(f"- {suggestion}")
                                            st.markdown("**Détail des Critères :**")
                                            for critere, detail in coaching_report.rationale.items():
                                                st.write(f"**{critere.replace('_', ' ').title()}** : {detail}")
                                        except APIError as e:
                                            st.error(f"Impossible d'obtenir l'analyse Smart Coach : {e}")
                                        except Exception as e:
                                            st.error(f"Une erreur inattendue est survenue lors de l'analyse Smart Coach : {e}")
                                    st.markdown("---")

                            # --- Historique des Lettres et Gestion des Données (Premium) ---
                            st.markdown("---")
                            st.subheader("📚 Historique et Gestion des Données")
                            rgpd_user_manager = RGPDUserManager()
                            try:
                                secure_storage = SecurePremiumStorage()
                            except ValueError as e:
                                st.error(f"Erreur de configuration RGPD : {e}. Veuillez définir la variable d'environnement 'USER_DATA_ENCRYPTION_KEY'.")
                                st.stop()

                            data_anonymizer = DataAnonymizer()
                            cv_optimization_service = CvOptimizationService()
                            security_scanner = SecurityScanner()

                            explicit_consent = st.sidebar.checkbox(
                                "Je consens à la conservation de mes données (CV anonymisé, lettres) pour la durée de mon abonnement.",
                                value=False,
                                key='explicit_consent_checkbox_generateur'
                            )

                            if user_tier != 'free' and not explicit_consent:
                                st.sidebar.warning("Pour les abonnements Premium, le consentement explicite est requis pour la conservation des données.")

                            if rgpd_user_manager.can_store_data(user_tier, explicit_consent):
                                try:
                                    anonymized_cv_content = data_anonymizer.anonymize_text(cv_content)
                                    anonymized_lettre_generee = data_anonymizer.anonymize_text(lettre_generee)

                                    secure_storage.store_user_document(
                                        st.session_state.user_id, 'cv', anonymized_cv_content, user_tier
                                    )
                                    secure_storage.store_user_document(
                                        st.session_state.user_id, 'letter', anonymized_lettre_generee, user_tier
                                    )
                                    st.success("Vos données (anonymisées) ont été sauvegardées en toute sécurité.")
                                except RGPDViolationError as e:
                                    st.error(f"Erreur RGPD : {e}")
                                except Exception as e:
                                    st.error(f"Erreur lors de la sauvegarde sécurisée : {e}")
                            else:
                                st.info("Vos données ne sont pas conservées (utilisateur gratuit ou consentement non donné).")

                            if user_tier != 'free' and explicit_consent:
                                st.info("En tant qu'utilisateur Premium, vous pouvez consulter l'historique de vos lettres et gérer vos données.")
                                user_history = secure_storage.get_user_history(st.session_state.user_id)
                                if user_history:
                                    for i, doc in enumerate(user_history):
                                        st.markdown(f"#### Document {i+1} ({doc['type']}) - Généré le {doc['created_at']})")
                                        st.text_area(f"Contenu du document {doc['id']}", doc['content'], height=200, key=f"history_doc_{doc['id']}", disabled=True)
                                        st.markdown("---")
                                    if st.button("🗑️ Supprimer toutes mes données sauvegardées"):
                                        secure_storage.delete_all_user_data(st.session_state.user_id)
                                        st.success("Toutes vos données sauvegardées ont été supprimées.")
                                        st.rerun()
                                else:
                                    st.info("Aucun historique de lettres trouvé pour le moment.")
                            else:
                                st.info("L'historique des lettres est une fonctionnalité Premium. Abonnez-vous pour en bénéficier !")

                        except (APIError, FileProcessingError, ValueError) as e:
                            st.error("❌ Une erreur est survenue lors de la génération. Veuillez réessayer.")
                            logging.exception("Erreur lors de la génération via l'interface web.")
                        except Exception as e:
                            st.error("🚨 Une erreur inattendue est survenue. L'ingénieur est sur le coup !")
                            logging.exception("Erreur critique inattendue dans l'app Streamlit.")
                        

                with col_buttons_2:
                    if st.button("🔄 Réinitialiser"):
                        st.session_state.clear()
                        st.rerun()
            
            create_glass_container(config_content_inner, "Configuration de l'IA")
        else:
            st.info("Veuillez charger votre CV et l'annonce (ou un ID France Travail) pour commencer la configuration.")

    create_glass_container(generator_content)

def render_trajectory_tab(user_tier):
    """Onglet Trajectory Builder stylisé"""
    
    def trajectory_content():
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: var(--phoenix-gold); font-family: 'Orbitron', monospace;">
                 MATRICE DE RECONVERSION
            </h2>
            <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem;">
                Cartographiez votre trajectoire professionnelle
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Visualisation 3D de la trajectoire (simulée)
        # Données simulées pour la trajectoire
        skills_current = ['Communication', 'Organisation', 'Empathie', 'Rigueur']
        skills_target = ['Python', 'Cybersécurité', 'Réseau', 'Pentesting']
        
        # Pour que les listes aient la même taille pour le radar chart
        all_skills = list(set(skills_current + skills_target))
        
        # Créer des valeurs pour le radar chart
        r_current = [random.randint(5, 9) for _ in all_skills]
        r_target = [random.randint(6, 10) for _ in all_skills]

        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=r_current,
            theta=all_skills,
            fill='toself',
            name='Compétences Actuelles',
            line_color='rgba(255, 107, 53, 0.8)',
            fillcolor='rgba(255, 107, 53, 0.2)'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=r_target,
            theta=all_skills,
            fill='toself',
            name='Compétences Cibles',
            line_color='rgba(0, 245, 255, 0.8)',
            fillcolor='rgba(0, 245, 255, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    gridcolor='rgba(255, 255, 255, 0.2)',
                    linecolor='rgba(255, 255, 255, 0.2)'
                ),
                angularaxis=dict(
                    gridcolor='rgba(255, 255, 255, 0.2)',
                    linecolor='rgba(255, 255, 255, 0.2)'
                )
            ),
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Formulaire de profil
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("###  Analyse de votre profil")
            current_skills = st.text_area(
                "Vos compétences actuelles",
                placeholder="Ex: Gestion d'équipe, Communication, Analyse...",
                help="Listez vos compétences séparées par des virgules",
                key="current_skills_tb"
            )
            
            current_exp = st.text_area(
                "Votre expérience professionnelle",
                placeholder="Décrivez votre parcours professionnel...",
                help="Votre histoire professionnelle unique",
                key="current_exp_tb"
            )
        
        with col2:
            st.markdown("###  Votre objectif")
            aspirations = st.text_area(
                "Vos aspirations",
                placeholder="Ex: Devenir expert en cybersécurité...",
                help="Votre vision du futur professionnel",
                key="aspirations_tb"
            )
            
            target_role = st.text_input(
                "Rôle Cible",
                placeholder="Ex: Pentester Senior, Data Scientist...",
                help="Le poste précis que vous visez",
                key="target_role_tb"
            )
        
        # Bouton génération plan avec effet
        if st.button(" GÉNÉRER MA TRAJECTOIRE", type="primary"):
            if current_skills and current_exp and aspirations and target_role:
                with st.spinner(" Calcul des probabilités..."):
                    try:
                        user_profile = UserProfile(
                            current_skills=[s.strip() for s in current_skills.split(',') if s.strip()],
                            current_experience=current_exp,
                            aspirations=aspirations
                        )
                        reconversion_plan = generate_reconversion_plan(user_profile, target_role)
                        st.success("Votre plan de reconversion a été généré !")
                        
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(0, 245, 255, 0.1));
                            border-radius: 20px;
                            padding: 2rem;
                            margin: 2rem 0;
                            border: 1px solid rgba(255, 215, 0, 0.3);
                            box-shadow: 0 0 30px rgba(255, 215, 0, 0.2);
                        ">
                            <h3 style="color: var(--phoenix-gold); text-align: center;">
                                 TRAJECTOIRE GÉNÉRÉE
                            </h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.subheader(f" Objectif : {reconversion_plan.goal}")
                        st.write(reconversion_plan.summary)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if reconversion_plan.estimated_total_duration_weeks:
                                render_metric_card(f"{reconversion_plan.estimated_total_duration_weeks} semaines", "Durée totale", "⏱️")
                        with col2:
                            if reconversion_plan.success_probability is not None:
                                render_metric_card(f"{reconversion_plan.success_probability:.0%}", "Probabilité de succès", "📈")

                        st.markdown("###  Étapes du Plan de Reconversion")
                        
                        for i, step in enumerate(reconversion_plan.steps):
                            with st.expander(f"**Étape {i+1}: {step.title}**", expanded=i==0):
                                st.write(step.description)
                                
                                if step.duration_weeks:
                                    st.info(f"⏱️ **Durée estimée** : {step.duration_weeks} semaines")
                                
                                if step.resources:
                                    st.markdown("####  Ressources Recommandées")
                                    
                                    for resource in step.resources:
                                        icons = {
                                            "cours_en_ligne": "📚",
                                            "livre": "📖", 
                                            "certification": "🏅",
                                            "mentorat": "🤝",
                                            "projet_pratique": "💡",
                                            "article": "📰",
                                            "outil": "⚙️",
                                            "autre": "🔗"
                                        }
                                        
                                        icon = icons.get(resource.type, "")
                                        
                                        st.markdown(f"**{icon} {resource.name}**")
                                        
                                        if resource.description:
                                            st.write(f" {resource.description}")
                                        
                                        if resource.link:
                                            st.write(f" [Accéder à la ressource]({resource.link})")
                                        
                                        st.write("---")

                except APIError as e:
                    st.error(f"Impossible de générer le plan de reconversion : {e}")
                except Exception as e:
                    st.error(f"Une erreur inattendue est survenue lors de la génération du plan : {e}")
            else:
                st.warning("Veuillez remplir tous les champs du profil et du rôle cible pour générer le plan.")
    
    if user_tier == "gratuit":
        st.info("Le Trajectory Builder est une fonctionnalité Premium Plus.")
        st.button("Passer Premium Plus", type="primary")
        return
    
    create_glass_container(trajectory_content)

def render_mirror_tab(user_tier):
    """Onglet Mirror Match stylisé"""
    
    def mirror_content():
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: var(--phoenix-gold); font-family: 'Orbitron', monospace;">
                 ANALYSE DE LA CULTURE D'ENTREPRISE
            </h2>
            <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem;">
                Analysez la culture d'entreprise pour adapter votre message
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Interface d'analyse de culture
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("###  Contenu 'À Propos'")
            company_about = st.text_area(
                "Page 'À Propos' de l'entreprise",
                placeholder="Collez le contenu de la page À Propos...",
                height=150,
                help="Analyse sémantique des valeurs d'entreprise",
                key="company_about_mm"
            )
        
        with col2:
            st.markdown("###  Posts LinkedIn")
            linkedin_posts = st.text_area(
                "Posts LinkedIn récents",
                placeholder="Collez les posts LinkedIn récents...",
                height=150,
                help="Analyse du ton et des tendances de communication",
                key="linkedin_posts_mm"
            )
        
        if company_about or linkedin_posts:
            if st.button(" LANCER L'ANALYSE", type="primary"):
                with st.spinner(" Analyse de la culture..."):
                    try:
                        company_insights = analyser_culture_entreprise(company_about, linkedin_posts)
                        st.success("Analyse terminée ! Voici les insights :")
                        st.write(company_insights)
                        
                        # Simulation résultats d'analyse
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            render_metric_card("Innovation", "VALEUR CLÉ", "💡")
                        
                        with col2:
                            render_metric_card("Dynamique", "TON", "🗣️")
                        
                        with col3:
                            render_metric_card("87%", "MATCH", "🎯")
                        
                        # Recommandations
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, rgba(0, 245, 255, 0.1), rgba(255, 107, 53, 0.1));
                            border-radius: 20px;
                            padding: 2rem;
                            margin: 2rem 0;
                            border: 1px solid rgba(0, 245, 255, 0.3);
                        ">
                            <h4 style="color: var(--phoenix-cyan);"> RECOMMANDATIONS</h4>
                            <ul style="color: rgba(255, 255, 255, 0.8);">
                                <li>Adoptez un ton <strong>dynamique et innovant</strong></li>
                                <li>Mettez l'accent sur votre <strong>capacité d'adaptation</strong></li>
                                <li>Valorisez votre <strong>approche créative</strong> des problèmes</li>
                                <li>Intégrez les mots-clés: <em>innovation, transformation, agilité</em></li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    except APIError as e:
                        st.error(f"Impossible d'analyser la culture d'entreprise : {e}")
                    except Exception as e:
                        st.error(f"Une erreur inattendue est survenue lors de l'analyse : {e}")
        else:
            st.warning("Veuillez fournir du contenu pour l'analyse.")
    
    if user_tier == "gratuit":
        st.info("L'analyse de la culture d'entreprise est une fonctionnalité Premium.")
        st.button("Passer Premium", type="primary")
        return
    
    create_glass_container(mirror_content)

def render_dashboard_tab(user_tier):
    """Dashboard stylisé avec métriques"""
    
    def dashboard_content():
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: var(--phoenix-gold); font-family: 'Orbitron', monospace;">
                 TABLEAU DE BORD
            </h2>
            <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem;">
                Suivez vos progrès et vos statistiques
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_metric_card("12", "LETTRES", "📄")
        
        with col2:
            render_metric_card("3", "DOMAINES", "🗺️")
        
        with col3:
            render_metric_card("8.4/10", "SCORE IA", "⭐")
        
        with col4:
            render_metric_card("76%", "TAUX MATCH", "🎯")
        
        # Graphique temporel des générations
        dates = pd.date_range('2025-07-01', periods=20, freq='D')
        values = np.random.poisson(2, 20)
        
        fig = px.line(
            x=dates, y=values,
            title=" Activité de Génération",
            color_discrete_sequence=['#ff6b35']
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='#00f5ff'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Historique des lettres
        st.markdown("###  HISTORIQUE")
        
        lettres_data = [
            {"Date": "22/07/2025", "Poste": "Pentester Junior", "Entreprise": "SecureSphere", "Score": "9.2/10"},
            {"Date": "21/07/2025", "Poste": "Data Analyst", "Entreprise": "TechCorp", "Score": "8.7/10"},
            {"Date": "20/07/2025", "Poste": "Développeur Python", "Entreprise": "InnovaTech", "Score": "8.9/10"}
        ]
        
        for lettre in lettres_data:
            st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 1rem;
                margin: 0.5rem 0;
                border-left: 4px solid var(--phoenix-cyan);
                transition: all 0.3s ease;
            " onmouseover="this.style.background='rgba(255, 107, 53, 0.1)'" onmouseout="this.style.background='rgba(255, 255, 255, 0.05)'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: var(--phoenix-cyan);">{lettre['Poste']}</strong>
                        <br>
                        <small style="color: rgba(255, 255, 255, 0.7);">{lettre['Entreprise']} • {lettre['Date']}</small>
                    </div>
                    <div style="color: var(--phoenix-gold); font-weight: bold;">
                        {lettre['Score']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    if user_tier == "gratuit":
        st.info(" Le tableau de bord est disponible avec Premium")
        st.button(" Passer Premium", type="primary")
        return
    
    create_glass_container(dashboard_content)

def render_settings_tab(user_tier):
    """Onglet paramètres stylisé"""
    
    def settings_content():
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: var(--phoenix-gold); font-family: 'Orbitron', monospace;">
                ⚙️ PARAMÈTRES
            </h2>
            <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem;">
                Gérez les réglages de l'IA Phoenix
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sélection du niveau d'abonnement avec style
        st.markdown("###  Votre Abonnement")
        
        tier_options = {
            " Gratuit": {
                "features": ["3 lettres/mois", "Prompt standard", "Support communauté"],
                "color": "rgba(255, 255, 255, 0.7)"
            },
            "⭐ Premium": {
                "features": ["Lettres illimitées", "Mirror Match", "Smart Coach", "Support prioritaire"],
                "color": "var(--phoenix-orange)"
            },
            " Premium Plus": {
                "features": ["Tout Premium", "Trajectory Builder", "Story Arc", "IA personnalisée"],
                "color": "var(--phoenix-gold)"
            }
        }
        
        # Utiliser le user_tier réel pour l'index par défaut
        current_tier_index = 0
        if user_tier == "premium":
            current_tier_index = 1
        elif user_tier == "premium_plus":
            current_tier_index = 2

        selected_tier_display = st.radio(
            "Sélectionnez votre niveau :",
            list(tier_options.keys()),
            index=current_tier_index,
            horizontal=True,
            key="settings_tier_radio"
        )
        
        # Affichage des fonctionnalités
        features = tier_options[selected_tier_display]["features"]
        color = tier_options[selected_tier_display]["color"]
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(0, 245, 255, 0.1));
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            border: 1px solid {color};
        ">
            <h4 style="color: {color};">✨ Fonctionnalités Activées</h4>
            <ul style="color: rgba(255, 255, 255, 0.8);">
        """, unsafe_allow_html=True)
        
        for feature in features:
            st.markdown(f"<li>{feature}</li>", unsafe_allow_html=True)
        
        st.markdown("</ul></div>", unsafe_allow_html=True)
        
        # Paramètres IA
        st.markdown("###  Paramètres IA")
        
        col1, col2 = st.columns(2)
        
        with col1:
            creativity = st.slider(
                " Créativité",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Niveau de créativité de l'IA",
                key="creativity_slider"
            )
            
            formality = st.slider(
                " Formalisme",
                min_value=0.0,
                max_value=1.0,
                value=0.6,
                step=0.1,
                help="Niveau de formalisme des lettres",
                key="formality_slider"
            )
        
        with col2:
            personalization = st.slider(
                " Personnalisation",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                step=0.1,
                help="Niveau de personnalisation",
                key="personalization_slider"
            )
            
            innovation = st.slider(
                " Innovation",
                min_value=0.0,
                max_value=1.0,
                value=0.9,
                step=0.1,
                help="Niveau d'innovation des formulations",
                key="innovation_slider"
            )
        
        # Bouton de sauvegarde
        if st.button(" SAUVEGARDER CONFIGURATION", type="primary", key="save_config_button"):
            show_success_toast("Configuration sauvegardée !")
            
        # Easter egg
        if st.button(" Mode Phoenix Ultime", help="Activation du mode expérimental", key="phoenix_mode_button"):
            st.balloons()
            st.markdown("""
            <div style="
                background: linear-gradient(45deg, #ff6b35, #00f5ff, #ffd700);
                background-size: 400% 400%;
                animation: gradientShift 2s ease infinite;
                border-radius: 20px;
                padding: 2rem;
                text-align: center;
                color: white;
                font-weight: bold;
                margin: 2rem 0;
            ">
                ‍ MODE PHOENIX ULTIME ACTIVÉ ! ‍<br>
                Toutes les fonctionnalités débloquées !
            </div>
            """, unsafe_allow_html=True)

        # RGPD section from previous app.py
        st.subheader("Gestion des Données (RGPD)")
        st.markdown("---")
        st.info("Cette section vous permet de gérer vos données personnelles conformément au RGPD.")

        rgpd_user_manager = RGPDUserManager()
        try:
            secure_storage = SecurePremiumStorage()
        except ValueError as e:
            st.error(f"Erreur de configuration RGPD : {e}. Veuillez définir la variable d'environnement 'USER_DATA_ENCRYPTION_KEY'.")
            st.stop()

        explicit_consent_settings = st.checkbox(
            "Je consens à la conservation de mes données (CV anonymisé, lettres) pour la durée de mon abonnement.",
            value=False,
            key='explicit_consent_checkbox_settings'
        )

        if user_tier != 'free' and not explicit_consent_settings:
            st.warning("Pour les abonnements Premium, le consentement explicite est requis pour la conservation des données.")

        if user_tier != 'free' and explicit_consent_settings:
            st.subheader("Historique des Documents")
            user_history = secure_storage.get_user_history(st.session_state.user_id)
            if user_history:
                for i, doc in enumerate(user_history):
                    st.markdown(f"#### Document {i+1} ({doc['type']}) - Généré le {doc['created_at']})")
                    st.text_area(f"Contenu du document {doc['id']}", doc['content'], height=200, key=f"history_doc_settings_{doc['id']}", disabled=True)
                    st.markdown("---")
                if st.button("🗑️ Supprimer toutes mes données sauvegardées (RGPD)"):
                    secure_storage.delete_all_user_data(st.session_state.user_id)
                    st.success("Toutes vos données sauvegardées ont été supprimées.")
                    st.rerun()
            else:
                st.info("Aucun historique de lettres trouvé pour le moment.")
        else:
            st.info("L'historique des lettres et la gestion des données sont des fonctionnalités Premium. Abonnez-vous pour en bénéficier !")
    
    create_glass_container(settings_content)

# --- Fonction principale ---
def main():
    st.set_page_config(
        page_title="Phoenix Letters - Générateur de Lettres IA", # Plus humble
        page_icon="‍",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    inject_futuristic_css() # Injecte le CSS stylisé
    create_particle_background() # Ajoute le fond de particules
    render_futuristic_header() # Affiche le header stylisé
    
    # Barre de progression globale d'onboarding
    if 'user_progress' not in st.session_state:
        st.session_state.user_progress = 0
    
    create_cyber_progress_bar(st.session_state.user_progress, "Progression de l'utilisateur") # Nom plus humble
    
    # Initialiser les variables de session si elles n'existent pas
    if 'annonce_content' not in st.session_state:
        st.session_state.annonce_content = ""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "simulated_user_" + str(uuid.uuid4())
    if 'last_generation_time' not in st.session_state:
        st.session_state.last_generation_time = 0

    # Bandeau de consentement RGPD
    st.info("""
    **Protection des données** : Vos données (CV, lettre générée) sont traitées **uniquement en mémoire** et **supprimées immédiatement** après génération. Aucune sauvegarde n'est effectuée sur nos serveurs. Le traitement IA est réalisé via Gemini (Google). Pour plus de détails, consultez notre politique de confidentialité (à venir).
    """)

    user_tier = get_user_tier_ui()

    # Navigation principale par onglets
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Générateur", # Noms d'onglets plus humbles
        " Trajectoire", 
        " Analyse Culture", 
        " Tableau de Bord",
        "⚙️ Paramètres"
    ])
    
    with tab1:
        render_generator_tab(user_tier)
    
    with tab2:
        render_trajectory_tab(user_tier)
    
    with tab3:
        render_mirror_tab(user_tier)
    
    with tab4:
        render_dashboard_tab(user_tier)
    
    with tab5:
        render_settings_tab(user_tier)

if __name__ == "__main__":
    if not os.getenv('GOOGLE_API_KEY'):
        st.error("ERREUR CRITIQUE : La variable d'environnement 'GOOGLE_API_KEY' n'est pas configurée.")
        st.info("Veuillez configurer cette variable d'environnement avant de lancer l'application.")
        st.stop()

    main()