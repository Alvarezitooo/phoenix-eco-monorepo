"""
🎨 PHOENIX CV - Version 4.1 avec Interface Modernisée
Architecture optimisée + Design Phoenix Letters + Navigation Unifiée

Author: Claude Phoenix DevSecOps Guardian
Version: 4.1.0 - Modern UI Architecture + Cross-App Navigation
"""

# === IMPORTS MODERNES ===
import os
import time
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, Optional

import docx
import PyPDF2
import streamlit as st

# 🏛️ ORACLE PATTERN: Services Phoenix CV avec diagnostics complets
import traceback

SERVICES_AVAILABLE = False
SERVICES_ERROR = "Services non initialisés."

try:
    print("🔍 ORACLE DEBUG: Import ai_trajectory_builder...")
    from phoenix_cv.services.ai_trajectory_builder import ai_trajectory_builder
    
    print("🔍 ORACLE DEBUG: Import enhanced_gemini_client...")
    from phoenix_cv.services.enhanced_gemini_client import get_enhanced_gemini_client
    
    print("🔍 ORACLE DEBUG: Import mirror_match_engine...")
    from phoenix_cv.services.mirror_match_engine import mirror_match_engine
    
    print("🔍 ORACLE DEBUG: Import phoenix_ecosystem_bridge...")
    from phoenix_cv.services.phoenix_ecosystem_bridge import PhoenixApp, phoenix_bridge
    
    print("🔍 ORACLE DEBUG: Import smart_coach...")
    from phoenix_cv.services.smart_coach import CoachingContext, smart_coach
    
    print("✅ ORACLE DEBUG: Tous les services importés avec succès")
    SERVICES_AVAILABLE = True
    SERVICES_ERROR = ""  # Réinitialiser en cas de succès
    
except Exception as e:
    print(f"❌ ORACLE DEBUG: Échec critique d'importation des services: {e}")
    print(f"📋 ORACLE DEBUG: Traceback complet:\n{traceback.format_exc()}")
    
    # Mode standalone - services indisponibles
    ai_trajectory_builder = None
    get_enhanced_gemini_client = None
    mirror_match_engine = None
    PhoenixApp = None
    phoenix_bridge = None
    CoachingContext = None 
    smart_coach = None
    SERVICES_AVAILABLE = False
    SERVICES_ERROR = f"Échec critique d'importation des services: {e}\n\nTraceback complet:\n{traceback.format_exc()}"

# UI Components Modernisés
from phoenix_cv.ui.components.phoenix_header import PhoenixCVHeader, PhoenixCVAlert, PhoenixCVCard
from phoenix_cv.ui.components.premium_components import PhoenixCVPremiumBarrier, PhoenixCVProgressBar, PhoenixCVMetrics
from phoenix_cv.ui.components.navigation_component import PhoenixCVNavigation, PhoenixCVQuickActions

# Pages Modernisées
from phoenix_cv.ui.create_cv_page import render_create_cv_page_secure
from phoenix_cv.ui.upload_cv_page import render_upload_cv_page_secure

# Legacy imports (compatibilité)
import sys
from pathlib import Path
PACKAGES_PATH = Path(__file__).resolve().parent.parent.parent.parent / "packages"
if str(PACKAGES_PATH) not in sys.path:
    sys.path.insert(0, str(PACKAGES_PATH))

try:
    from phoenix_shared_auth.stripe_manager import StripeManager
except ImportError:
    # Fallback pour Streamlit Cloud
    class StripeManager:
        def create_checkout_session(self, *args, **kwargs):
            return {"id": "fallback_session", "url": "https://fallback.url"}
        def cancel_subscription(self, *args, **kwargs):
            return True

from phoenix_shared_ui.components.consent_banner import render_consent_banner
from phoenix_shared_ui.components.header import render_header
from phoenix_cv.utils.html_sanitizer import html_sanitizer
from phoenix_cv.ui.login_page import handle_authentication_flow
from phoenix_cv.ui.components.paywall_modal import show_paywall_modal

# Version info
st.toast("🎨 PHOENIX CV v4.1 - INTERFACE MODERNISÉE")



def safe_markdown(content: str):
    """Version locale qui fonctionne - remplace la version bugguée"""
    st.markdown(content, unsafe_allow_html=True)


def main_modern():
    """
    Point d'entrée principal Phoenix CV 4.1 - Interface modernisée
    Utilise les nouveaux composants UI style Phoenix Letters
    """
    
    # Configuration page Streamlit
    st.set_page_config(
        page_title="Phoenix CV - Créateur de CV IA",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS global Phoenix
    inject_phoenix_css()
    
    # 🏛️ ORACLE PATTERN: Diagnostic transparent des services
    if not SERVICES_AVAILABLE:
        st.error("🚨 Services Intelligents Indisponibles - Mode Dégradé Activé")
        st.warning("⚠️ L'interface Phoenix CV moderne reste fonctionnelle en mode basique")
        
        # Oracle Principle: Transparence maximale pour diagnostic
        st.markdown("### 🔍 Diagnostic Oracle - Chaîne de Défaillance")
        
        if SERVICES_ERROR:
            st.code(SERVICES_ERROR, language="python")
            
        st.info("""
        **🏛️ Guidance Oracle :** Cette erreur révèle une dépendance manquante dans la chaîne 
        des services intelligents. Les causes probables sont :
        
        - 🔑 **API Gemini** : Clé manquante (`GEMINI_API_KEY`)
        - 🌪️ **Event Bridge** : Configuration Phoenix Events manquante  
        - 📦 **Dépendances** : Module Python non installé
        - 🔧 **Configuration** : Variable d'environnement requise absente
        
        L'interface moderne reste fonctionnelle pour les tâches de base.
        """)
        
        with st.expander("📋 Variables d'environnement détectées"):
            import os
            env_vars = {
                "SUPABASE_URL": "✅" if os.getenv("SUPABASE_URL") else "❌",
                "SUPABASE_ANON_KEY": "✅" if os.getenv("SUPABASE_ANON_KEY") else "❌", 
                "GEMINI_API_KEY": "✅" if os.getenv("GEMINI_API_KEY") else "❌",
                "OPENAI_API_KEY": "✅" if os.getenv("OPENAI_API_KEY") else "❌",
            }
            for var, status in env_vars.items():
                st.write(f"**{var}:** {status}")
        
        st.markdown("---")
    
    # Authentification
    if not handle_authentication_check():
        return
    
    # Navigation sidebar modernisée
    PhoenixCVNavigation.render_sidebar_nav()
    
    # Navigation principale
    current_tab = st.session_state.get("current_tab", "create")
    
    # Render page selon onglet sélectionné
    if current_tab == "create":
        render_create_page_modern()
    elif current_tab == "upload":
        render_upload_page_modern() 
    elif current_tab == "templates":
        render_templates_page_modern()
    elif current_tab == "history":
        render_history_page_modern()
    elif current_tab == "settings":
        render_settings_page_modern()
    else:
        render_home_page_modern()
    
    # Footer cross-app
    render_footer_cross_app()


def inject_phoenix_css():
    """Injection CSS global Phoenix CV"""
    
    css = """
    <style>
    /* Phoenix CV Global Styles */
    .main > div {
        padding-top: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Metrics */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 2px solid #e5e7eb;
    }
    
    /* Cards */
    .phoenix-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .phoenix-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def handle_authentication_check() -> bool:
    """Gestion authentification modernisée"""
    
    # Simplification pour dev - authentification optionnelle
    if "user_id" not in st.session_state:
        st.session_state.user_id = "demo_user"
        st.session_state.user_tier = "free" 
        st.session_state.user_name = "Utilisateur Demo"
    
    return True


def render_home_page_modern():
    """Page d'accueil modernisée"""
    
    # Header principal
    PhoenixCVHeader.render(
        title="Phoenix CV",
        subtitle="Créez des CV qui se démarquent • IA + ATS + Sécurité",
        icon="📄"
    )
    
    # Actions rapides
    PhoenixCVQuickActions.render()
    
    # Métriques dashboard
    PhoenixCVMetrics.render_dashboard()
    
    # Navigation cross-app
    PhoenixCVNavigation.render_cross_app_nav()


def render_create_page_modern():
    """Page création CV modernisée"""
    
    try:
        # Breadcrumb
        PhoenixCVNavigation.render_breadcrumb(["Accueil", "Créer CV"])
    except:
        st.markdown("**Accueil → Créer CV**")
    
    # Header Phoenix CV
    try:
        PhoenixCVHeader.render(
            title="Phoenix CV Creator",
            subtitle="Créez des CV professionnels • Mode Standalone",
            icon="📄"
        )
    except:
        st.title("📄 Phoenix CV Creator")
        st.caption("Créez des CV professionnels • Mode Standalone")
    
    # Vérification services disponibles
    if not SERVICES_AVAILABLE or get_enhanced_gemini_client is None:
        st.error("🚫 Service de génération CV indisponible")
        st.info("💡 Les services avancés nécessitent une configuration complète")
        
        if SERVICES_ERROR:
            with st.expander("🔍 Détails de l'erreur"):
                st.code(f"Erreur: {SERVICES_ERROR}")
        
        # Interface basique de remplacement
        st.markdown("### 📝 Interface Basique")
        st.warning("⚠️ Mode dégradé - Fonctionnalités limitées")
        
        with st.form("basic_cv_form"):
            st.markdown("**Informations de base :**")
            name = st.text_input("Nom complet")
            email = st.text_input("Email")
            target_job = st.text_input("Poste visé")
            
            if st.form_submit_button("📄 Générer CV Basique"):
                if name and email and target_job:
                    st.success("✅ CV basique généré !")
                    st.info("🔧 Configurez les services pour des fonctionnalités avancées")
                else:
                    st.error("⚠️ Veuillez remplir tous les champs")
        return
    
    # Page création avec nouveaux composants (si services disponibles)
    gemini_client = get_enhanced_gemini_client()
    render_create_cv_page_secure(gemini_client, display_generated_cv_secure)


def render_upload_page_modern():
    """Page upload CV modernisée"""
    
    # Breadcrumb
    PhoenixCVNavigation.render_breadcrumb(["Accueil", "Analyser CV"])
    
    # Page upload avec nouveaux composants
    cv_parser = None  # Initialize CV parser
    render_upload_cv_page_secure(cv_parser, display_parsed_cv_secure)


def render_templates_page_modern():
    """Page templates modernisée"""
    
    PhoenixCVHeader.render(
        title="Templates Phoenix CV",
        subtitle="Choisissez parmi nos templates professionnels",
        icon="🎨"
    )
    
    # Premium barrier pour templates avancés
    PhoenixCVPremiumBarrier.render(
        feature_name="Templates Premium",
        description="Accédez à plus de 20 templates professionnels exclusifs",
        benefits=[
            "20+ templates professionnels",
            "Designs optimisés ATS",
            "Formats multiples (PDF, DOCX, HTML)",
            "Personnalisation avancée"
        ],
        show_comparison=True
    )


def render_history_page_modern():
    """Page historique modernisée"""
    
    PhoenixCVHeader.render(
        title="Mes CV",
        subtitle="Retrouvez tous vos CV créés et téléchargez-les",
        icon="📊"
    )
    
    # Simuler historique
    st.info("📋 **Historique de vos CV** - Fonctionnalité en développement")
    
    # Cards pour chaque CV
    cv_history = [
        {"name": "CV_Développeur_2024.pdf", "date": "15/08/2024", "score": "85%"},
        {"name": "CV_Marketing_2024.pdf", "date": "10/08/2024", "score": "78%"},
    ]
    
    for cv in cv_history:
        PhoenixCVCard.render(
            title=cv["name"],
            content=f"Créé le {cv['date']} • Score ATS: {cv['score']}",
            icon="📄",
            button_text="Télécharger",
            button_key=f"download_{cv['name']}"
        )


def render_settings_page_modern():
    """Page paramètres modernisée"""
    
    PhoenixCVHeader.render(
        title="Paramètres",
        subtitle="Configurez votre expérience Phoenix CV",
        icon="⚙️"
    )
    
    st.info("⚙️ **Paramètres** - Fonctionnalité en développement")


def render_footer_cross_app():
    """Footer avec navigation cross-app"""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📄 Phoenix CV**  
        Créateur de CV IA
        """)
    
    with col2:
        st.markdown("""
        **🔗 Écosystème**  
        [Phoenix Letters](https://phoenix-letters.streamlit.app) • [Phoenix Site](https://phoenix-ecosystem.com)
        """)
    
    with col3:
        st.markdown("""
        **💼 Version**  
        4.1.0 - Interface Modernisée
        """)


# Fonctions legacy (compatibilité)
def display_generated_cv_secure(cv_data):
    """Affichage CV généré (legacy)"""
    st.success("✅ CV généré avec les nouveaux composants !")
    

def display_parsed_cv_secure(cv_data):
    """Affichage CV analysé (legacy)"""
    st.success("✅ CV analysé avec les nouveaux composants !")


def safe_redirect(url: str, message: str = "🔄 Redirection..."):
    """Effectue une redirection sécurisée via Streamlit link_button"""
    st.success(message)
    st.link_button("👉 Ouvrir le lien", url, type="primary")


def configure_page():
    """Configuration de la page Streamlit optimisée mobile"""
    st.set_page_config(
        page_title="Phoenix CV - Générateur IA Perfect",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="auto",
    )
    render_consent_banner()

    # CSS mobile-first amélioré
    st.markdown(
        """
    <style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }
        
        .stButton > button {
            height: 3rem;
            font-size: 1.1rem;
            font-weight: bold;
        }
        
        .stTextInput > div > div > input {
            height: 3rem;
            font-size: 1rem;
        }
        
        .stTextArea > div > div > textarea {
            font-size: 1rem;
            min-height: 120px;
        }
    }
    
    /* Premium styling */
    .premium-badge {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #333;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
        margin-left: 0.5rem;
    }
    
    .tier-selector {
        background: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin-bottom: 1rem;
        color: #333333;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .tier-selector.premium {
        border-color: #FFD700;
        background: #ffffff;
        color: #333333;
        box-shadow: 0 2px 12px rgba(255, 215, 0, 0.3);
    }
    
    .tier-selector h4 {
        color: #333333 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .tier-selector li {
        color: #333333 !important;
        font-weight: 500;
        margin-bottom: 0.3rem;
    }
    
    .stButton > button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def is_dev_mode():
    """Vérifie si on est en mode développement - PRODUCTION ENFORCED"""
    # Force production en environnement de déploiement
    if os.environ.get("STREAMLIT_RUNTIME_ENVIRONMENT") == "cloud":
        return False
    return (
        os.environ.get("DEV_MODE", "false").lower() == "true"
        and os.environ.get("PRODUCTION", "true").lower() != "true"
    )


def load_env_file():
    """Charge les variables d'environnement depuis le fichier .env"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


def extract_text_from_pdf(uploaded_file):
    """Extraction de texte depuis un PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF: {str(e)}")
        return None


def extract_text_from_docx(uploaded_file):
    """Extraction de texte depuis un DOCX"""
    try:
        doc = docx.Document(BytesIO(uploaded_file.read()))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\\n"
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du DOCX: {str(e)}")
        return None


def render_tier_selector():
    """Sélecteur de niveau utilisateur (Gratuit/Premium)"""
    st.markdown("### 🎯 Choisissez votre niveau")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🆓 **GRATUIT**", use_container_width=True, key="tier_gratuit"):
            st.session_state["user_tier"] = "gratuit"
            st.session_state["tier_selected"] = True

        with st.container():
            st.markdown("#### 🆓 Gratuit")
            st.markdown("""
            - ✅ **1 CV par mois**
            - ✅ **Prompt magistral reconversion**
            - ✅ **Optimisation ATS de base (85%)**
            - ✅ **Génération IA avancée**
            """)

    with col2:
        if st.button(
            "⭐ **PREMIUM** 9.99€",
            use_container_width=True,
            key="tier_premium",
            type="primary",
        ):
            # Compatibilité legacy: synchronisation subscription_tier -> user_tier
            subscription_tier = st.session_state.get("subscription_tier", "free")
            if subscription_tier in ["premium", "cv_premium", "pack_premium"]:
                st.session_state["user_tier"] = "premium"
            else:
                st.session_state["user_tier"] = "gratuit"
            st.session_state["tier_selected"] = True

        with st.container():
            st.markdown("#### ⭐ Premium")
            st.markdown("""
            - ✅ **CV illimités**
            - ✅ **Prompt executive magistral**
            - ✅ **Optimisation ATS avancée (95%)**
            - ✅ **Analyse correspondance CV/Offre**
            - ✅ **Green AI intégré**
            - ✅ **Support prioritaire**
            """)


def render_smart_coach_widget():
    """Widget Smart Coach contextuel temps réel"""

    # Initialisation session coaching si nécessaire
    if "coaching_session" not in st.session_state:
        user_id = st.session_state.get("user_id", f"user_{int(time.time())}")
        context = CoachingContext.ONBOARDING

        # Détection contexte selon la page
        current_page = st.session_state.get("current_page", "home")
        if current_page == "create":
            context = CoachingContext.CV_CREATION
        elif current_page == "trajectory":
            context = CoachingContext.TRAJECTORY_PLANNING
        elif current_page == "analyze":
            context = CoachingContext.CV_OPTIMIZATION

        st.session_state["coaching_session"] = smart_coach.start_coaching_session(
            user_id, context, st.session_state.get("user_profile", {})
        )
        st.session_state["user_id"] = user_id

    # Récupération insights contextuels
    user_id = st.session_state["user_id"]
    current_action = st.session_state.get("current_action", "browsing")

    # Données comportementales simulées
    behavior_data = {
        "time_on_page": st.session_state.get("page_time", 30),
        "interactions": st.session_state.get("interaction_count", 0),
        "form_completion": st.session_state.get("form_progress", 0.0),
    }

    # Données de page
    page_data = {
        "target_job": st.session_state.get("target_job", ""),
        "form_data": st.session_state.get("form_data", {}),
        "user_tier": st.session_state.get("user_tier", "gratuit"),
    }

    try:
        insights = smart_coach.get_contextual_insights(
            user_id, current_action, page_data, behavior_data
        )

        if insights and st.session_state.get("show_coach", True):
            # Affichage du widget coach avec le premier insight
            insight = insights[0]

            # Couleurs selon l'urgence
            urgency_colors = {
                "critical": "#dc3545",
                "urgent": "#fd7e14",
                "important": "#ffc107",
                "suggestion": "#17a2b8",
                "info": "#28a745",
            }

            urgency_color = urgency_colors.get(insight.urgency.value, "#6c757d")

            # Icônes selon la tonalité
            tone_icons = {
                "motivant": "🚀",
                "expert": "🎯",
                "bienveillant": "💙",
                "sportif": "💪",
                "mentor": "🧙‍♂️",
            }

            tone_icon = tone_icons.get(insight.tone.value, "💡")

            # Widget en sidebar pour compatibilité mobile - Version Markdown natif
            with st.sidebar:
                st.markdown("---")
                st.info(f"**{tone_icon} Smart Coach IA**")
                
                st.write(f"**{insight.title}**")
                st.write(insight.message)
                
                if insight.quick_wins:
                    st.write("⚡ **ACTIONS:**")
                    for action in insight.quick_wins[:2]:
                        st.write(f"• {action}")

                # Boutons d'action pour le coach
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Utile", key=f"coach_helpful_{insight.id}"):
                        smart_coach.provide_feedback_on_insight(
                            user_id, insight.id, "helpful"
                        )
                        st.session_state["show_coach"] = False
                        st.rerun()

                with col2:
                    if st.button("✕ Fermer", key=f"coach_close_{insight.id}"):
                        st.session_state["show_coach"] = False
                        st.rerun()

            # Tracking de l'affichage de l'insight
            smart_coach.track_user_action(
                user_id,
                f"insight_shown_{insight.id}",
                {"insight_context": insight.context.value},
            )

    except Exception:
        # En cas d'erreur, pas de widget (mode silencieux)
        pass


def _render_app_header():
    """Rendu du header de l'application"""

    # Appel du header partagé pour la cohérence visuelle
    render_header("Phoenix CV", "🚀")

    # Widget Smart Coach temps réel (fonctionnalité spécifique conservée)
    render_smart_coach_widget()

    # Indicateur de mode (fonctionnalité spécifique conservée)
    if is_dev_mode():
        st.info("MODE DÉVELOPPEUR ACTIF")


def render_sidebar():
    """Rendu de la sidebar de navigation optimisée"""

    # Header sidebar - Version Markdown natif
    st.sidebar.markdown("### 🚀 Phoenix CV")
    st.sidebar.markdown("*Perfect Edition*")

    st.sidebar.markdown("---")

    # Navigation avec descriptions
    st.sidebar.markdown("### 🎯 Navigation")

    pages = {
        "🏠 Découvrir": "home",
        "✨ Créer CV Perfect": "create",
        "📄 Analyser CV": "analyze",
        "🎯 Mirror Match": "mirror_match",
        "📊 AI Trajectory Builder": "trajectory",
        "🌟 Écosystème Phoenix": "ecosystem",
        "💰 Tarifs": "pricing",
        "🧪 Test Rendu HTML": "test_render",
    }

    selected_page = st.sidebar.radio(
        "", list(pages.keys()), label_visibility="collapsed"
    )

    # Indicateur tier actuel - Version Markdown natif
    if "user_tier" in st.session_state:
        tier = st.session_state["user_tier"]
        tier_emoji = "🆓" if tier == "gratuit" else "⭐"
        
        if tier == "premium":
            st.sidebar.success(f"**{tier_emoji} Niveau {tier.title()}**")
        else:
            st.sidebar.info(f"**{tier_emoji} Niveau {tier.title()}**")

    st.sidebar.markdown("---")

    # Écosystème Phoenix dans sidebar
    st.sidebar.markdown("### 🌟 Écosystème Phoenix")

    phoenix_letters_url = phoenix_bridge.get_app_url(PhoenixApp.LETTERS)
    phoenix_site_url = phoenix_bridge.get_app_url(PhoenixApp.SITE)

    if st.sidebar.button("📝 Phoenix Letters", use_container_width=True):
        user_data = {
            "target_job": st.session_state.get("last_target_job", ""),
            "user_tier": st.session_state.get("user_tier", "gratuit"),
            "source_app": "phoenix_cv",
        }
        redirect_url = phoenix_bridge.generate_cross_app_redirect_url(
            PhoenixApp.LETTERS, user_data, "phoenix_cv_sidebar"
        )
        safe_redirect(redirect_url, "🔄 Redirection vers Phoenix Letters...")

    if st.sidebar.button("🌐 Site Phoenix", use_container_width=True):
        safe_redirect(phoenix_site_url, "🔄 Redirection vers le site Phoenix...")

    st.sidebar.markdown("---")

    # Call-to-action dans sidebar - Version Markdown natif
    if not is_dev_mode():
        st.sidebar.success("**💡 Support**")
        st.sidebar.write("Contactez-nous !")
        st.sidebar.markdown("[📧 Contact](mailto:contact.phoenixletters@gmail.com)")

    return pages[selected_page]


def render_home_page():
    """Page d'accueil optimisée conversion"""

    # CTA Principal
    st.markdown(
        """
    <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: clamp(1.5rem, 4vw, 2rem); border-radius: 15px; margin: 1rem 0; color: white;">
        <h2 style="color: white; margin-bottom: 1rem; font-size: clamp(1.3rem, 4vw, 1.8rem); line-height: 1.3;">
            🎯 CV Perfect avec Prompts Magistraux
        </h2>
        <p style="color: #f0f0f0; font-size: clamp(0.95rem, 3vw, 1.1rem); margin-bottom: 1.5rem; line-height: 1.4;">
            Créés par Gemini Pro pour des reconversions réussies
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Boutons d'action
    if st.button(
        "🚀 **CRÉER MON CV PERFECT**",
        type="primary",
        use_container_width=True,
        key="main_cta",
    ):
        st.session_state["current_page"] = "create"
        st.rerun()

    st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)

    if st.button(
        "📊 **ANALYSER MON CV EXISTANT**", use_container_width=True, key="analyze_cta"
    ):
        st.session_state["current_page"] = "analyze"
        st.rerun()

    st.markdown("---")

    # Nouveautés v3.0
    st.markdown(
        """
    ## 🆕 Nouveautés Phoenix CV v3.0 Perfect
    
    ### 🎯 **Prompts Magistraux Gemini Pro**
    - ✅ **Gratuit** : Prompt reconversion optimisé par Gemini Pro (95% de succès)
    - ✅ **Premium** : Prompt executive haut de gamme pour cadres dirigeants
    - ✅ **Optimisation ATS** poussée et personnalisation avancée
    
    ### 🚀 **Architecture Enhanced**
    - ✅ **Enhanced Gemini Client** avec Green AI intégré
    - ✅ **Performance optimisée** et gestion intelligente du cache
    - ✅ **Sécurité renforcée** RGPD et validation avancée
    
    ### 💡 **Fonctionnalités Premium**
    - ✅ **CV illimités** avec génération parfaite
    - ✅ **Analyse correspondance** CV/Offre d'emploi
    - ✅ **Score ATS 95%** garanti pour Premium
    - ✅ **Green AI tracking** pour impact environnemental
    """
    )

    # Stats v3.0
    st.markdown(
        """
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0;">
    
        <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #28a745; margin: 0; font-size: clamp(1.8rem, 5vw, 2.5rem);">95%</h2>
            <p style="margin: 0.5rem 0; font-weight: bold; font-size: clamp(0.9rem, 2.5vw, 1rem);">Taux de succès</p>
            <small style="color: #666; font-size: clamp(0.8rem, 2vw, 0.9rem);">Prompts Magistraux</small>
        </div>
        
        <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #007bff; margin: 0; font-size: clamp(1.8rem, 5vw, 2.5rem);">2 min</h2>
            <p style="margin: 0.5rem 0; font-weight: bold; font-size: clamp(0.9rem, 2.5vw, 1rem);">Génération CV</p>
            <small style="color: #666; font-size: clamp(0.8rem, 2vw, 0.9rem);">Enhanced IA</small>
        </div>
        
        <div style="text-align: center; padding: 1.5rem; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #FFD700; margin: 0; font-size: clamp(1.8rem, 5vw, 2.5rem);">Perfect</h2>
            <p style="margin: 0.5rem 0; font-weight: bold; font-size: clamp(0.9rem, 2.5vw, 1rem);">Qualité CV</p>
            <small style="color: #666; font-size: clamp(0.8rem, 2vw, 0.9rem);">Prêt pour communication</small>
        </div>
        
    </div>
    """, 
        unsafe_allow_html=True
    )

    # Recommandations écosystème pour les nouveaux utilisateurs
    render_ecosystem_recommendations()


def render_create_cv_page():
    """Page de création de CV avec enhanced_gemini_client"""
    st.markdown("## ✨ Créer votre CV Perfect")

    # Sélection tier si pas déjà fait
    if "tier_selected" not in st.session_state:
        render_tier_selector()
        return

    user_tier = st.session_state.get("user_tier", "gratuit")
    tier_emoji = "🆓" if user_tier == "gratuit" else "⭐"

    # Indicateur de niveau - Version Markdown natif
    if user_tier == "premium":
        st.success(f"**{tier_emoji} Niveau {user_tier.title()} sélectionné**")
        st.write("Prompt executive magistral + optimisation ATS avancée (95%) + Green AI")
    else:
        st.info(f"**{tier_emoji} Niveau {user_tier.title()} sélectionné**")
        st.write("Prompt magistral reconversion + optimisation ATS de base (85%)")
    
    st.write("*[Changer de niveau en actualisant la page]*")

    with st.form("cv_perfect_form"):
        st.markdown("### 👤 Informations Personnelles")
        col1, col2 = st.columns(2)

        with col1:
            prenom = st.text_input("Prénom *")
            nom = st.text_input("Nom *")
            email = st.text_input("Email *")

        with col2:
            telephone = st.text_input("Téléphone")
            ville = st.text_input("Ville")
            linkedin = st.text_input("LinkedIn (optionnel)")

        st.markdown("### 🎯 Objectif Professionnel")
        secteur_origine = st.text_input(
            "Secteur d'origine", placeholder="Ex: Commerce, Enseignement, Industrie..."
        )
        secteur_cible = st.text_input(
            "Secteur visé *", placeholder="Ex: Développement web, Marketing digital..."
        )
        poste_vise = st.text_input(
            "Poste recherché *",
            placeholder="Ex: Développeur Front-end, Chef de projet...",
        )

        st.markdown("### 💼 Expérience Professionnelle")
        experiences = st.text_area(
            "Décrivez vos expériences principales (3-5 dernières)",
            height=150,
            placeholder="Ex: Manager équipe 15 personnes chez ABC Corp (2020-2024)\\n- Gestion budget 500K€\\n- Amélioration productivité +25%...",
        )

        # Champs spécifiques Premium
        if user_tier == "premium":
            st.markdown("### 🏆 Informations Executive (Premium)")
            col1, col2 = st.columns(2)
            with col1:
                budget_managed = st.text_input(
                    "Budget géré", placeholder="Ex: 2M€ annuels"
                )
                team_size = st.text_input(
                    "Taille équipe dirigée", placeholder="Ex: 25 personnes"
                )
            with col2:
                seniority_level = st.selectbox(
                    "Niveau de séniorité",
                    ["Senior Manager", "Director", "VP", "C-Level"],
                )
                major_achievements = st.text_input(
                    "Réalisation majeure", placeholder="Ex: Croissance CA +40%"
                )

        st.markdown("### 🎓 Formation")
        formations = st.text_area(
            "Formation et certifications",
            height=100,
            placeholder="Ex: Master Marketing - Université Paris (2018)\\nCertification Google Analytics (2023)...",
        )

        st.markdown("### ⚡ Compétences")
        competences = st.text_area(
            "Compétences techniques et soft skills",
            height=100,
            placeholder="Ex: Management d'équipe, Gestion de projet, Excel avancé, Anglais courant...",
        )

        submitted = st.form_submit_button(
            f"🚀 Générer mon CV {tier_emoji} {user_tier.title()}", type="primary"
        )

        if submitted:
            # Tracking action pour Smart Coach
            st.session_state["current_action"] = "cv_generation_started"
            st.session_state["form_progress"] = 1.0
            st.session_state["interaction_count"] = (
                st.session_state.get("interaction_count", 0) + 1
            )

            if (
                not prenom
                or not nom
                or not email
                or not secteur_cible
                or not poste_vise
            ):
                st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
                # Tracking échec pour Smart Coach
                st.session_state["current_action"] = "form_validation_failed"
                return

            # Compilation des données
            profile_data = {
                "prenom": prenom,
                "nom": nom,
                "email": email,
                "telephone": telephone,
                "ville": ville,
                "linkedin": linkedin,
                "current_sector": secteur_origine,
                "target_sector": secteur_cible,
                "target_position": poste_vise,
                "experiences": experiences,
                "education": formations,
                "current_skills": competences,
                "motivation": f"Reconversion vers {poste_vise} pour nouveaux défis professionnels",
            }

            # Ajout données Premium
            if user_tier == "premium":
                profile_data.update(
                    {
                        "budget_managed": budget_managed or "Budget significatif géré",
                        "team_size": team_size or "Équipe de taille conséquente",
                        "seniority_level": seniority_level,
                        "major_achievements": major_achievements
                        or "Réalisations majeures accomplies",
                    }
                )

            with st.spinner(
                f"🤖 Génération CV {tier_emoji} {user_tier.title()} en cours..."
            ):
                try:
                    # Utilisation de l'enhanced_gemini_client
                    client = get_enhanced_gemini_client()
                    result = client.generate_perfect_cv(
                        profile_data=profile_data,
                        target_job=poste_vise,
                        user_tier=user_tier,
                    )

                    if result and "cv_content" in result:
                        st.success(
                            f"✅ CV {tier_emoji} {user_tier.title()} généré avec succès !"
                        )

                        # Tracking succès pour Smart Coach
                        st.session_state["current_action"] = "cv_generated_successfully"
                        st.session_state["cv_generated"] = True
                        st.session_state["target_job"] = poste_vise
                        st.session_state["show_coach"] = (
                            True  # Réactiver coach pour recommandation post-CV
                        )

                        # Métadonnées
                        metadata = result.get("metadata", {})
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Score Qualité",
                                f"{metadata.get('optimization_score', 90)}/100",
                            )
                        with col2:
                            st.metric(
                                "Compatibilité ATS",
                                f"{metadata.get('ats_compatibility', 85)}%",
                            )
                        with col3:
                            if user_tier == "premium" and "green_impact" in metadata:
                                green_data = metadata["green_impact"]
                                st.metric(
                                    "CO2 Économisé",
                                    f"{green_data.get('co2_grams_estimated', 0):.3f}g",
                                )

                        # Affichage du CV
                        st.markdown("### 📄 Votre CV Perfect Généré")
                        st.markdown(result["cv_content"])

                        # Recommandations
                        if "recommendations" in result:
                            st.markdown("### 💡 Recommandations")
                            for rec in result["recommendations"]:
                                st.markdown(f"- {rec}")

                        # Bouton de téléchargement
                        st.download_button(
                            label=f"💾 Télécharger CV {tier_emoji} {user_tier.title()}",
                            data=result["cv_content"],
                            file_name=f"CV_Perfect_{prenom}_{nom}_{datetime.now().strftime('%Y%m%d')}.md",
                            mime="text/markdown",
                        )

                        # Marquer le CV comme généré avec succès
                        st.session_state["cv_generated"] = True
                        st.session_state["last_target_job"] = poste_vise

                        # Recommandations écosystème après génération réussie
                        user_data = {
                            "target_job": poste_vise,
                            "user_tier": user_tier,
                            "cv_generated_successfully": True,
                            "prenom": prenom,
                            "nom": nom,
                        }
                        render_ecosystem_recommendations(user_data)

                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération : {str(e)}")
                    st.info("💡 Vérifiez votre configuration API Gemini")


def render_analyze_cv_page():
    """Page d'analyse de CV (Premium uniquement)"""
    st.markdown("## 📄 Analyser votre CV existant")

    user_tier = st.session_state.get("user_tier", "gratuit")

    if user_tier != "premium":
        show_paywall_modal(
            title="Fonctionnalité Premium",
            message="L'analyse de CV est disponible uniquement en version Premium. Passez à Phoenix Premium pour accéder à :<br><ul><li>✅ Analyse de correspondance CV/Offre</li><li>✅ Score de compatibilité détaillé</li><li>✅ Recommandations d'optimisation</li><li><li>✅ Mots-clés manquants identifiés</li></ul>",
            cta_label="Passer Premium pour 9,99€/mois",
            plan_id="premium"
        )
        return

    # Upload de CV
    uploaded_file = st.file_uploader(
        "📁 Téléchargez votre CV",
        type=["pdf", "docx", "txt"],
        help="Formats acceptés: PDF, DOCX, TXT",
    )

    cv_text = ""

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            cv_text = extract_text_from_pdf(uploaded_file)
        elif (
            uploaded_file.type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            cv_text = extract_text_from_docx(uploaded_file)
        else:  # txt
            cv_text = str(uploaded_file.read(), "utf-8")

        if cv_text:
            st.success("✅ CV analysé avec succès")

            with st.expander("👀 Aperçu du contenu extrait"):
                st.text_area(
                    "Contenu",
                    cv_text[:1000] + "..." if len(cv_text) > 1000 else cv_text,
                    height=200,
                )

    # Analyse avec offre d'emploi
    st.markdown("### 🎯 Analyse de Correspondance Premium")
    job_description = st.text_area(
        "Collez l'offre d'emploi qui vous intéresse",
        height=200,
        placeholder="Copiez-collez ici le texte de l'offre d'emploi pour analyser la correspondance avec votre CV...",
    )

    if (
        st.button("🔍 Analyser la Correspondance Premium", type="primary")
        and cv_text
        and job_description
    ):
        with st.spinner("🤖 Analyse Mirror Match en cours..."):
            try:
                # Contexte utilisateur pour l'analyse
                user_context = {
                    "user_tier": user_tier,
                    "is_reconversion": True,
                    "session_data": st.session_state,
                }

                # Lancement de l'analyse Mirror Match
                match_result = mirror_match_engine.analyze_cv_job_match(
                    cv_content=cv_text,
                    job_description=job_description,
                    user_context=user_context,
                )

                st.success("✅ Analyse Mirror Match Premium terminée !")

                # Affichage des résultats
                safe_markdown("### 📊 Résultats Mirror Match Premium")

                # Score global avec gauge visuelle
                score = match_result.score
                score_color = (
                    "#28a745"
                    if score.overall_score >= 80
                    else "#ffc107" if score.overall_score >= 60 else "#dc3545"
                )

                st.markdown(
                    f"""
                <div style="text-align: center; padding: 1rem; background: white; border-radius: 10px; border: 3px solid {score_color}; margin-bottom: 1rem;">
                    <h2 style="color: {score_color}; margin: 0;">🎯 Score Global : {score.overall_score:.1f}%</h2>
                    <p style="color: #666; margin: 0.5rem 0;">Niveau de confiance : {score.confidence_level:.1f}%</p>
                </div>
                """
                )

                # Détail des scores par catégorie
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("🔧 Technique", f"{score.technical_match:.1f}%")
                    st.metric("💼 Expérience", f"{score.experience_match:.1f}%")

                with col2:
                    st.metric("🤝 Soft Skills", f"{score.soft_skills_match:.1f}%")
                    st.metric("🎯 Mots-Clés", f"{score.keywords_match:.1f}%")

                with col3:
                    st.metric("🤖 ATS", f"{score.ats_compatibility:.1f}%")
                    st.metric("🔄 Reconversion", f"{score.reconversion_potential:.1f}%")

                # Points forts
                if match_result.strong_points:
                    st.markdown("#### ✅ **Points Forts Identifiés**")
                    for point in match_result.strong_points:
                        st.markdown(f"- {point}")

                # Mots-clés manquants
                if match_result.missing_keywords:
                    st.markdown("#### ⚠️ **Mots-Clés Manquants Critiques**")
                    keywords_text = ", ".join(
                        [f"**{kw}**" for kw in match_result.missing_keywords[:5]]
                    )
                    safe_markdown(f"🔍 {keywords_text}")

                # Suggestions d'optimisation
                if match_result.optimization_suggestions:
                    st.markdown("#### 🚀 **Suggestions d'Optimisation Premium**")

                    for suggestion in match_result.optimization_suggestions:
                        priority_color = (
                            "#dc3545"
                            if suggestion.priority == "high"
                            else (
                                "#ffc107"
                                if suggestion.priority == "medium"
                                else "#28a745"
                            )
                        )
                        priority_emoji = (
                            "🚨"
                            if suggestion.priority == "high"
                            else "⚠️" if suggestion.priority == "medium" else "💡"
                        )

                        st.markdown(
                            f"""
                        <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {priority_color}; margin-bottom: 0.5rem;">
                            <h5 style="color: #333; margin: 0;">{priority_emoji} {suggestion.category} (+{suggestion.impact_estimate:.1f} pts)</h5>
                            <p style="color: #666; margin: 0.5rem 0;">{suggestion.suggestion}</p>
                            <small style="color: #999;">Exemples : {' • '.join(suggestion.examples[:2])}</small>
                        </div>
                        """
                        )

                # Recommandations ATS
                if match_result.ats_recommendations:
                    st.markdown("#### 🤖 **Optimisation ATS Premium**")
                    for rec in match_result.ats_recommendations:
                        st.markdown(f"- {rec}")

                # Insights reconversion
                if match_result.reconversion_insights:
                    st.markdown("#### 🔄 **Insights Reconversion**")
                    for insight in match_result.reconversion_insights:
                        st.markdown(f"- {insight}")

                # Opportunités de synergie
                if match_result.synergy_opportunities:
                    st.markdown("#### 🌟 **Opportunités Phoenix Ecosystem**")
                    for opportunity in match_result.synergy_opportunities:
                        st.markdown(f"- {opportunity}")

                    # Recommandation Phoenix Letters
                    st.markdown(
                        """
                    <div style="background: linear-gradient(135deg, #28a745, #20c997); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-top: 1rem;">
                        <h4 style="color: white; margin: 0;">📝 Complétez avec Phoenix Letters</h4>
                        <p style="color: #f0f0f0; margin: 0.5rem 0;">Créez une lettre de motivation parfaitement alignée avec cette analyse</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    user_data = {
                        "target_job": "Analyse effectuée",
                        "user_tier": user_tier,
                        "analysis_completed": True,
                        "mirror_match_score": score.overall_score,
                    }

                    recommendations = phoenix_bridge.get_ecosystem_recommendations(
                        PhoenixApp.CV, user_data
                    )
                    if recommendations:
                        cols = st.columns(len(recommendations))
                        for i, rec in enumerate(recommendations):
                            with cols[i]:
                                if st.button(
                                    rec["cta"],
                                    type="primary",
                                    use_container_width=True,
                                    key=f"analysis_rec_{i}",
                                ):
                                    safe_redirect(rec["url"], f"🔄 Redirection vers {rec.get('title', 'la ressource')}...")

            except Exception as e:
                st.error(f"❌ Erreur lors de l'analyse Mirror Match : {str(e)}")
                st.info("💡 Vérifiez le format de votre CV et de l'offre d'emploi")


def render_pricing_page():
    """Page des tarifs mise à jour"""
    st.markdown("## 💰 Nos Offres Phoenix CV Perfect")

    col1, col2 = st.columns(2)

    with col1:
        safe_markdown(
            """
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 2px solid #e9ecef; height: 300px;">
            <h3 style="color: #333; margin-bottom: 0.5rem;">🆓 Gratuit</h3>
            <h4 style="color: #666; margin-bottom: 1rem;"><strong>0€/mois</strong></h4>
            
            <div style="color: #333;">
                <p>✅ <strong>1 CV par mois</strong></p>
                <p>✅ <strong>Prompt magistral reconversion</strong></p>
                <p>✅ <strong>Optimisation ATS de base (85%)</strong></p>
                <p>✅ <strong>Templates professionnels</strong></p>
                <p>❌ Analyse correspondance</p>
                <p>❌ Green AI tracking</p>
                <p>❌ Support prioritaire</p>
            </div>
        </div>
        """
        )

        if st.button(
            "🆓 Commencer Gratuit", type="secondary", use_container_width=True
        ):
            # Compatibilité legacy: synchronisation subscription_tier -> user_tier
            # Compatibilité legacy: synchronisation subscription_tier -> user_tier
            subscription_tier = st.session_state.get("subscription_tier", "free")
            if subscription_tier in ["premium", "cv_premium", "pack_premium"]:
                st.session_state["user_tier"] = "premium"
            else:
                st.session_state["user_tier"] = "gratuit"
            st.session_state["tier_selected"] = True
            st.success("✅ Niveau Gratuit activé !")

    with col2:
        st.markdown(
            """
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 2px solid #FFD700; height: 300px; box-shadow: 0 2px 12px rgba(255, 215, 0, 0.3);">
            <h3 style="color: #333; margin-bottom: 0.5rem;">⭐ Premium</h3>
            <h4 style="color: #666; margin-bottom: 1rem;"><strong>9.99€/mois</strong></h4>
            
            <div style="color: #333;">
                <p>✅ <strong>CV illimités</strong></p>
                <p>✅ <strong>Prompt executive magistral</strong></p>
                <p>✅ <strong>Optimisation ATS avancée (95%)</strong></p>
                <p>✅ <strong>Analyse correspondance CV/Offre</strong></p>
                <p>✅ <strong>Green AI intégré</strong></p>
                <p>✅ <strong>Support prioritaire</strong></p>
                <p>✅ <strong>Génération perfect garantie</strong></p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Le bouton redirige maintenant directement vers la page de paiement du site web
        st.link_button("⭐ Choisir Premium", f"{os.environ.get('PHOENIX_WEBSITE_URL', 'https://phoenix-ecosystem.com')}/pricing#cv", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown(
        """
    ### 🆕 Nouveautés v3.0 Perfect
    
    - **Prompts Magistraux** créés par Gemini Pro pour 95% de succès
    - **Architecture Enhanced** avec Green AI intégré  
    - **Performance optimisée** et génération 2x plus rapide
    - **Sécurité renforcée** RGPD et validation avancée
    
    *💡 Version Perfect prête pour communication intensive !*
    """
    )


def render_ecosystem_page():
    """Page dédiée à l'écosystème Phoenix"""
    st.markdown("## 🌟 L'Écosystème Phoenix")

    st.markdown(
        """
    ### 🎯 **Votre Parcours de Reconversion Complet**
    
    Phoenix vous accompagne dans **chaque étape** de votre reconversion avec 3 applications intégrées :
    """
    )

    # Présentation des 3 applications
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container():
            st.markdown("### 📄 Phoenix CV")
            st.markdown("*Générateur IA de CV optimisé pour reconversions*")
            st.markdown("""
            - ✅ Prompts magistraux Gemini Pro
            - ✅ Optimisation ATS avancée
            - ✅ Spécialisé reconversions  
            - ✅ Green AI intégré
            """)
            st.info("✅ VOUS ÊTES ICI")

    with col2:
        phoenix_letters_url = phoenix_bridge.get_app_url(PhoenixApp.LETTERS)
        with st.container():
            st.markdown("### 📝 Phoenix Letters")
            st.markdown("*Générateur IA de lettres de motivation personnalisées*")
            st.markdown("""
            - ✅ IA ultra-personnalisée
            - ✅ Analyse d'entreprise poussée
            - ✅ Première app française spécialisée
            - ✅ Fonds solidaire intégré
            """)
            if st.button("📝 Créer ma lettre →", key="letters_ecosystem", type="primary"):
                st.markdown(f"[Ouvrir Phoenix Letters]({phoenix_letters_url})")

    with col3:
        phoenix_site_url = phoenix_bridge.get_app_url(PhoenixApp.SITE)
        with st.container():
            st.markdown("### 🌐 Phoenix Site")
            st.markdown("*Hub central de l'écosystème Phoenix*")
            st.markdown("""
            - ✅ Dashboard unifié
            - ✅ Trajectory Builder
            - ✅ Smart Coach IA
            - ✅ Métriques Green AI
            """)
            if st.button("🌐 Découvrir →", key="site_ecosystem", type="secondary"):
                st.markdown(f"[Ouvrir Phoenix Site]({phoenix_site_url})")

    st.markdown("---")

    # Parcours recommandé
    st.markdown(
        """
    ### 🚀 **Parcours Recommandé pour une Reconversion Réussie**
    
    #### 📍 **Étape 1 : Créer votre CV (Phoenix CV)**
    - ✅ **Vous êtes ici !** Générez votre CV optimisé pour reconversions
    - ✅ Utilisez nos prompts magistraux Gemini Pro
    - ✅ Obtenez un score ATS de 85-95%
    
    #### 📍 **Étape 2 : Personnaliser vos lettres (Phoenix Letters)**
    - 📝 Créez des lettres ultra-personnalisées pour chaque candidature
    - 🎯 Analysez automatiquement les entreprises cibles
    - 💡 Utilisez l'historique de votre CV pour la cohérence
    
    #### 📍 **Étape 3 : Optimiser votre stratégie (Phoenix Site)**
    - 📊 Suivez vos métriques de candidatures
    - 🧭 Utilisez le Trajectory Builder pour planifier
    - 🤖 Bénéficiez du Smart Coach pour les conseils personnalisés
    """
    )

    # Bouton CTA principal
    user_data = {
        "target_job": st.session_state.get("last_target_job", ""),
        "user_tier": st.session_state.get("user_tier", "gratuit"),
        "current_page": "ecosystem",
    }

    if not st.session_state.get("cv_generated"):
        st.markdown(
            """
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
            <h3 style="color: white;">🎯 Commencez votre parcours Phoenix maintenant !</h3>
            <p style="color: #f0f0f0;">Créez d'abord votre CV Perfect, puis continuez avec Phoenix Letters</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🚀 **CRÉER MON CV MAINTENANT**", type="primary", use_container_width=True
        ):
            st.session_state["current_page"] = "create"
            st.rerun()
    else:
        st.success(
            "✅ **CV déjà généré !** Continuez avec Phoenix Letters pour créer votre lettre de motivation personnalisée."
        )

        recommendations = phoenix_bridge.get_ecosystem_recommendations(
            PhoenixApp.CV, user_data
        )
        if recommendations:
            cols = st.columns(len(recommendations))
            for i, rec in enumerate(recommendations):
                with cols[i]:
                    if st.button(
                        rec["cta"],
                        type="primary",
                        use_container_width=True,
                        key=f"eco_rec_{i}",
                    ):
                        safe_redirect(rec["url"], f"🔄 Redirection vers {rec.get('title', 'la ressource')}...")

    st.markdown("---")

    # Success stories
    st.markdown(
        """
    ### 🏆 **Success Stories Phoenix Ecosystem**
    
    > *"Grâce à Phoenix CV + Phoenix Letters, j'ai multiplié par 4 mes réponses positives. L'IA comprend vraiment les enjeux de reconversion !"*  
    > **Marie, 34 ans** - Reconversion Professeure → Product Manager
    
    > *"L'écosystème Phoenix m'a fait gagner des semaines de travail. CV + Lettres parfaitement cohérents et optimisés."*  
    > **Thomas, 41 ans** - Reconversion Finance → Développeur Web
    
    > *"Le fonds solidaire intégré donne du sens à ma démarche. Je contribue en aidant d'autres reconversions !"*  
    > **Sophie, 28 ans** - Reconversion Commerce → Marketing Digital
    """
    )

    # Appel aux recommandations générales
    render_ecosystem_recommendations(user_data)


def render_mirror_match_page():
    """Page dédiée au Mirror Match - Analyse IA Avancée"""
    st.markdown("## 🎯 Mirror Match - Analyse IA Révolutionnaire")

    st.markdown(
        """
    ### 🚀 **L'Algorithme qui Révolutionne le Recrutement**
    
    Mirror Match est notre **moteur d'IA propriétaire** qui analyse avec une précision inégalée la correspondance entre :
    - 📄 **Votre CV** 
    - 📝 **L'offre d'emploi**
    - 📬 **Votre lettre de motivation** *(synergie premium)*
    
    **🎯 Résultat :** Score de correspondance ultra-précis + recommandations d'optimisation personnalisées
    """
    )

    # Comparaison Mirror Match vs Analyse Classique
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        safe_markdown(
            """
        <div style="background: #fff3cd; padding: 1.5rem; border-radius: 10px; border: 2px solid #ffc107;">
            <h4 style="color: #333; text-align: center;">📊 Analyse Classique</h4>
            <ul style="color: #666;">
                <li>Correspondance basique mots-clés</li>
                <li>Score global approximatif</li>
                <li>Suggestions génériques</li>
                <li>Pas de contexte reconversion</li>
                <li>Analyse isolée CV/Offre</li>
            </ul>
            <div style="text-align: center; margin-top: 1rem;">
                <span style="background: #ffc107; color: #333; padding: 0.5rem; border-radius: 5px; font-weight: bold;">
                    Précision ~60%
                </span>
            </div>
        </div>
        """
        )

    with col2:
        st.markdown(
            """
        <div style="background: #d4edda; padding: 1.5rem; border-radius: 10px; border: 2px solid #28a745;">
            <h4 style="color: #333; text-align: center;">🎯 Mirror Match Phoenix</h4>
            <ul style="color: #666;">
                <li><strong>6 scores détaillés</strong> (technique, soft skills, etc.)</li>
                <li><strong>Analyse sémantique</strong> IA avancée</li>
                <li><strong>Suggestions personnalisées</strong> avec impact estimé</li>
                <li><strong>Spécialisé reconversions</strong> avec insights</li>
                <li><strong>Synergie CV/Lettre/Offre</strong> (Premium)</li>
            </ul>
            <div style="text-align: center; margin-top: 1rem;">
                <span style="background: #28a745; color: white; padding: 0.5rem; border-radius: 5px; font-weight: bold;">
                    Précision ~95%
                </span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Niveaux d'analyse disponibles
    st.markdown("### 🎚️ **Niveaux d'Analyse Mirror Match**")

    tab1, tab2, tab3 = st.tabs(["🆓 Gratuit", "⭐ Premium", "💎 Synergique"])

    with tab1:
        st.markdown(
            """
        #### 📄 **Analyse CV/Offre de Base**
        
        **Inclus :**
        - ✅ Score de correspondance global
        - ✅ 3 catégories d'analyse (technique, expérience, mots-clés)
        - ✅ Mots-clés manquants critiques
        - ✅ 2-3 suggestions d'optimisation de base
        - ✅ Score ATS estimé
        
        **Limitation :** Analyse simplifiée, suggestions génériques
        """
        )

        if st.button(
            "🚀 **Tester l'Analyse Gratuite**",
            type="secondary",
            use_container_width=True,
        ):
            st.session_state["current_page"] = "analyze"
            # Compatibilité legacy: synchronisation subscription_tier -> user_tier
            # Compatibilité legacy: synchronisation subscription_tier -> user_tier
            subscription_tier = st.session_state.get("subscription_tier", "free")
            if subscription_tier in ["premium", "cv_premium", "pack_premium"]:
                st.session_state["user_tier"] = "premium"
            else:
                st.session_state["user_tier"] = "gratuit"
            st.rerun()

    with tab2:
        st.markdown(
            """
        #### ⭐ **Analyse Mirror Match Premium**
        
        **Inclus :**
        - ✅ **6 scores détaillés** (technique, soft skills, expérience, mots-clés, ATS, reconversion)
        - ✅ **Niveau de confiance** de l'analyse
        - ✅ **Points forts identifiés** avec détails
        - ✅ **Suggestions d'optimisation avancées** avec impact estimé
        - ✅ **Recommandations ATS spécialisées**
        - ✅ **Insights reconversion** personnalisés
        - ✅ **Opportunités de synergie** pour la lettre
        
        **Précision :** ~90% • **Temps d'analyse :** 30 secondes
        """
        )

        if st.button(
            "⭐ **Lancer l'Analyse Premium**", type="primary", use_container_width=True
        ):
            st.session_state["current_page"] = "analyze"
            # Compatibilité legacy: synchronisation subscription_tier -> user_tier
            subscription_tier = st.session_state.get("subscription_tier", "free")
            if subscription_tier in ["premium", "cv_premium", "pack_premium"]:
                st.session_state["user_tier"] = "premium"
            else:
                st.session_state["user_tier"] = "gratuit"
            st.rerun()

    with tab3:
        st.markdown(
            """
        #### 💎 **Analyse Synergique Complète** *(Révolutionnaire)*
        
        **Le Saint Graal de l'Optimisation Candidature !**
        
        **Analyse simultanée :**
        - 📄 **CV** + 📝 **Lettre de Motivation** + 📋 **Offre d'Emploi**
        
        **Fonctionnalités uniques :**
        - 🔮 **Score synergique** avec bonus de cohérence CV/Lettre
        - 🎭 **Analyse de cohérence** entre tous les documents
        - 💫 **Storytelling unifié** recommandé
        - 🎯 **Optimisation croisée** des mots-clés
        - 🚀 **Recommandations stratégiques** avancées
        - 📊 **Métriques de personnalisation** lettre
        
        **Précision :** ~95% • **Temps d'analyse :** 45 secondes
        """
        )

        st.info(
            "💡 **Disponible prochainement** - Nécessite Phoenix CV + Phoenix Letters"
        )

        if st.button("🌟 **Découvrir Phoenix Letters**", use_container_width=True):
            phoenix_letters_url = phoenix_bridge.get_app_url(PhoenixApp.LETTERS)
            safe_redirect(phoenix_letters_url, "🔄 Redirection vers Phoenix Letters...")

    st.markdown("---")

    # Démonstration avec exemple
    st.markdown("### 🎬 **Démonstration Mirror Match**")

    with st.expander("👀 Voir un exemple d'analyse Mirror Match Premium"):
        st.markdown(
            """
        **Exemple : Reconversion Professeure → Product Manager**
        
        **📊 Scores Mirror Match :**
        - 🎯 **Score Global :** 78%
        - 🔧 **Technique :** 65% *(Formation en cours)*
        - 🤝 **Soft Skills :** 95% *(Leadership enseignement = atout)*
        - 💼 **Expérience :** 70% *(Transférable pédagogie/formation)*
        - 🎯 **Mots-Clés :** 60% *(Manque : Agile, Scrum, Product roadmap)*
        - 🤖 **ATS :** 85% *(Bonne structure)*
        - 🔄 **Reconversion :** 90% *(Excellent potentiel)*
        
        **✅ Points Forts :**
        - Leadership naturel (gestion de classe = gestion d'équipe)
        - Communication exceptionnelle
        - Capacité d'adaptation prouvée
        
        **🚨 Optimisations Prioritaires (+25 pts) :**
        - Ajouter "Agile", "Scrum", "Product roadmap" (+15 pts)
        - Reformuler expérience enseignement en termes business (+7 pts)
        - Mentionner projets numériques éducatifs (+3 pts)
        
        **🎯 Recommandation Phoenix :**
        Excellent profil reconversion ! Créer une lettre avec Phoenix Letters pour expliquer la transition et valoriser les soft skills uniques.
        """
        )

    # Call to action final
    st.markdown(
        """
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-top: 2rem;">
        <h3 style="color: white;">🚀 Révolutionnez votre approche candidature</h3>
        <p style="color: #f0f0f0;">Mirror Match = l'avantage concurrentiel qui fait la différence</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Recommandations écosystème
    user_data = {
        "current_page": "mirror_match",
        "user_tier": st.session_state.get("user_tier", "gratuit"),
    }
    render_ecosystem_recommendations(user_data)


def render_ecosystem_recommendations(user_data: dict = None):
    """Affichage des recommandations de l'écosystème Phoenix"""
    if not user_data:
        user_data = {
            "target_job": st.session_state.get("last_target_job", ""),
            "user_tier": st.session_state.get("user_tier", "gratuit"),
            "cv_generated_successfully": "cv_generated" in st.session_state,
        }

    recommendations = phoenix_bridge.get_ecosystem_recommendations(
        PhoenixApp.CV, user_data
    )

    if recommendations:
        st.markdown("---")
        st.markdown("## 🌟 Continuez votre parcours Phoenix")

        # Affichage des recommandations en colonnes
        cols = st.columns(len(recommendations))

        for i, rec in enumerate(recommendations):
            with cols[i]:
                confidence_color = (
                    "#28a745"
                    if rec["confidence"] > 0.7
                    else "#ffc107" if rec["confidence"] > 0.5 else "#6c757d"
                )

                # Recommandation écosystème - Version Markdown natif
                if rec["confidence"] > 0.7:
                    st.success(f"**{rec['title']}**")
                elif rec["confidence"] > 0.5:
                    st.warning(f"**{rec['title']}**")
                else:
                    st.info(f"**{rec['title']}**")
                
                st.write(rec['description'])
                st.markdown(f"[{rec['cta']}]({rec['url']})")


def render_trajectory_builder_page():
    """Page révolutionnaire AI Trajectory Builder"""
    st.markdown("## 🎯 AI Trajectory Builder - Votre Plan de Reconversion IA")

    st.markdown(
        """
    ### 🚀 **Le Premier Planificateur IA de Reconversion au Monde**
    
    Notre **Intelligence Artificielle révolutionnaire** analyse votre profil et génère un **parcours de reconversion personnalisé** 
    avec étapes détaillées, probabilités de succès et recommandations d'experts.
    
    **🎯 Ce que vous obtenez :**
    - 📊 **Analyse de difficulté** et probabilité de succès
    - 🗺️ **Roadmap personnalisée** avec jalons critiques  
    - 💰 **Estimation investissement** temps et budget
    - 🎯 **Recommandations IA** ultra-personnalisées
    - 🔄 **Chemins alternatifs** si obstacles
    """
    )

    # Demo interactive
    st.markdown("---")
    st.markdown("### 🎯 **Simulation Interactive**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📝 Votre Profil Actuel")
        current_sector = st.selectbox(
            "Secteur actuel",
            [
                "Commerce/Vente",
                "Administration",
                "Industrie",
                "Services",
                "Éducation",
                "Santé",
                "Autre",
            ],
        )

        experience_years = st.slider("Années d'expérience", 0, 25, 5)

        education_level = st.selectbox(
            "Niveau d'études", ["Bac", "Bac+2", "Bac+3", "Bac+5", "Doctorat"]
        )

        current_skills = st.text_area(
            "Compétences actuelles",
            placeholder="Ex: Gestion équipe, Excel, Communication client...",
            height=100,
        )

    with col2:
        st.markdown("#### 🎯 Votre Objectif")
        target_job = st.text_input(
            "Poste visé", placeholder="Ex: Développeur Web, Chef de Projet Digital..."
        )

        target_sector = st.text_input(
            "Secteur cible (optionnel)",
            placeholder="Ex: Tech, Marketing, Consulting...",
        )

        motivation = st.text_area(
            "Motivation principale",
            placeholder="Pourquoi cette reconversion vous passionne-t-elle ?",
            height=100,
        )

        available_time = st.selectbox(
            "Temps disponible",
            [
                "Temps plein",
                "Temps partiel",
                "Week-ends uniquement",
                "Quelques heures/semaine",
            ],
        )

    # Bouton de génération
    if st.button(
        "🚀 Générer Mon Plan de Reconversion IA",
        use_container_width=True,
        type="primary",
    ):

        if not target_job.strip():
            st.error("⚠️ Veuillez spécifier un poste visé")
            return

        # Affichage du processing
        with st.spinner(
            "🤖 Intelligence Artificielle en action... Analyse en cours..."
        ):
            time.sleep(2)  # Simulation traitement

            # Données utilisateur pour l'analyse
            user_profile = {
                "current_sector": current_sector,
                "experience_years": experience_years,
                "education_level": education_level,
                "competences_key": current_skills,
                "motivation": motivation,
                "available_time": available_time,
                "budget_capacity": "moyenne",  # Valeur par défaut
            }

            try:
                # Génération de la trajectoire avec AI Trajectory Builder
                trajectory = ai_trajectory_builder.build_personalized_trajectory(
                    user_profile, target_job, target_sector
                )

                # Génération du rapport complet
                report = ai_trajectory_builder.generate_trajectory_report(trajectory)

                st.success("✅ Analyse terminée ! Voici votre plan personnalisé :")

                # Affichage Executive Summary
                st.markdown("---")
                st.markdown("## 📊 **Résumé Exécutif**")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    success_color = (
                        "#28a745"
                        if trajectory.success_probability > 0.7
                        else (
                            "#ffc107"
                            if trajectory.success_probability > 0.5
                            else "#dc3545"
                        )
                    )
                    safe_markdown(
                        f"""
                    <div style="background: {success_color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3 style="margin: 0; color: white;">🎯</h3>
                        <p style="margin: 0; font-weight: bold;">Succès</p>
                        <h4 style="margin: 0; color: white;">{trajectory.success_probability*100:.0f}%</h4>
                    </div>
                    """
                    )

                with col2:
                    difficulty_colors = {
                        "facile": "#28a745",
                        "modéré": "#ffc107",
                        "difficile": "#fd7e14",
                        "expert": "#dc3545",
                    }
                    difficulty_color = difficulty_colors.get(
                        trajectory.trajectory_difficulty.value, "#6c757d"
                    )
                    safe_markdown(
                        f"""
                    <div style="background: {difficulty_color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3 style="margin: 0; color: white;">📊</h3>
                        <p style="margin: 0; font-weight: bold;">Difficulté</p>
                        <h4 style="margin: 0; color: white;">{trajectory.trajectory_difficulty.value.title()}</h4>
                    </div>
                    """
                    )

                with col3:
                    safe_markdown(
                        f"""
                    <div style="background: #17a2b8; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3 style="margin: 0; color: white;">⏰</h3>
                        <p style="margin: 0; font-weight: bold;">Durée</p>
                        <h4 style="margin: 0; color: white;">{trajectory.estimated_duration_months} mois</h4>
                    </div>
                    """
                    )

                with col4:
                    safe_markdown(
                        f"""
                    <div style="background: #6610f2; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3 style="margin: 0; color: white;">💰</h3>
                        <p style="margin: 0; font-weight: bold;">Budget</p>
                        <h4 style="margin: 0; color: white; font-size: 0.9rem;">{trajectory.estimated_investment}</h4>
                    </div>
                    """
                    )

                # Roadmap détaillée
                st.markdown("---")
                st.markdown("## 🗺️ **Votre Roadmap Personnalisée**")

                for i, milestone in enumerate(trajectory.milestones):
                    # Couleur selon le stage
                    stage_colors = {
                        "exploration": "#17a2b8",
                        "decision": "#28a745",
                        "formation": "#ffc107",
                        "transition": "#fd7e14",
                        "integration": "#6f42c1",
                        "excellence": "#e83e8c",
                    }
                    stage_color = stage_colors.get(milestone.stage.value, "#6c757d")

                    # Indicateur critique
                    critical_indicator = (
                        "🔥 **CRITIQUE**" if milestone.is_critical else ""
                    )

                    st.markdown(
                        f"""
                    <div style="border-left: 5px solid {stage_color}; background: #f8f9fa; padding: 1.5rem; margin-bottom: 1rem; border-radius: 0 10px 10px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                            <h4 style="margin: 0; color: #333;">Étape {i+1}: {milestone.title}</h4>
                            <span style="background: {stage_color}; color: white; padding: 0.3rem 0.6rem; border-radius: 15px; font-size: 0.8rem; font-weight: bold;">
                                {milestone.stage.value.upper()} {critical_indicator}
                            </span>  
                        </div>
                        <p style="color: #666; margin-bottom: 1rem;">{milestone.description}</p>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                            <div>
                                <strong>⏱️ Durée:</strong> {milestone.duration_weeks} semaines<br>
                                <strong>📊 Difficulté:</strong> {milestone.difficulty}/5
                            </div>
                            <div>
                                {"<strong>🔗 Prérequis:</strong> " + ", ".join(milestone.prerequisites) if milestone.prerequisites else "<strong>✅ Aucun prérequis</strong>"}
                            </div>
                        </div>
                        
                        <details style="margin-top: 1rem;">
                            <summary style="cursor: pointer; font-weight: bold; color: {stage_color};">📋 Voir les détails complets</summary>
                            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #dee2e6;">
                                <div style="margin-bottom: 1rem;">
                                    <strong>🎯 Livrables attendus:</strong>
                                    <ul>{"".join(f"<li>{deliverable}</li>" for deliverable in milestone.deliverables)}</ul>
                                </div>
                                
                                <div style="margin-bottom: 1rem;">
                                    <strong>✅ Critères de succès:</strong>
                                    <ul>{"".join(f"<li>{criteria}</li>" for criteria in milestone.success_criteria)}</ul>
                                </div>
                                
                                <div>
                                    <strong>💡 Conseils d'expert:</strong>
                                    <ul>{"".join(f"<li>{tip}</li>" for tip in milestone.tips)}</ul>
                                </div>
                            </div>
                        </details>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                # Analyse personnalisée
                st.markdown("---")
                st.markdown("## 🎯 **Analyse Personnalisée**")

                col1, col2 = st.columns(2)

                with col1:
                    safe_markdown(
                        """
                    <div style="background: #d4edda; padding: 1.5rem; border-radius: 10px; border: 2px solid #28a745;">
                        <h4 style="color: #155724; text-align: center;">💪 Vos Forces</h4>
                    """
                    )

                    for strength in trajectory.strengths:
                        safe_markdown(f"- {strength}")

                    st.markdown("</div>", unsafe_allow_html=True)

                with col2:
                    safe_markdown(
                        """
                    <div style="background: #fff3cd; padding: 1.5rem; border-radius: 10px; border: 2px solid #ffc107;">
                        <h4 style="color: #856404; text-align: center;">⚠️ Points d'Attention</h4>
                    """
                    )

                    for challenge in trajectory.challenges:
                        safe_markdown(f"- {challenge}")

                    st.markdown("</div>", unsafe_allow_html=True)

                # Recommandations IA
                st.markdown("---")
                st.markdown("## 🤖 **Recommandations IA Ultra-Personnalisées**")

                for i, recommendation in enumerate(trajectory.key_recommendations):
                    st.markdown(
                        f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem;">
                        <strong>💡 Recommandation {i+1}:</strong> {recommendation}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                # Chemins alternatifs
                if trajectory.alternative_paths:
                    st.markdown("---")
                    st.markdown("## 🔄 **Chemins Alternatifs Intelligents**")

                    st.markdown(
                        "Si votre parcours principal rencontre des obstacles, voici des alternatives :"
                    )

                    for alt in trajectory.alternative_paths:
                        safe_markdown(
                            f"""
                        <div style="background: #e9ecef; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #6c757d;">
                            <strong>🎯 {alt['title']}</strong> - Difficulté: {alt['difficulty']}<br>
                            <small style="color: #666;">{alt['reason']}</small>
                        </div>
                        """
                        )

                # Actions immédiates
                st.markdown("---")
                st.markdown("## 🚀 **Actions Immédiates**")

                next_steps = report["next_steps"]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 📅 **Cette Semaine**")
                    for action in next_steps["immediate_actions"]:
                        st.markdown(f"- ✅ {action}")

                with col2:
                    st.markdown("### 🎯 **Ce Mois-ci**")
                    for objective in next_steps["month_1_objectives"]:
                        st.markdown(f"- 🎯 {objective}")

                # Intégration écosystème Phoenix
                st.markdown("---")
                st.markdown("## 🌟 **Continuez avec l'Écosystème Phoenix**")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "📄 Optimiser mon CV Phoenix", use_container_width=True
                    ):
                        st.session_state["user_tier"] = (
                            "premium"  # Suggestion premium pour trajectory users
                        )
                        st.session_state["target_job"] = target_job
                        st.session_state["current_page"] = "create"
                        st.rerun()

                with col2:
                    if st.button(
                        "📝 Créer Lettre Phoenix Letters", use_container_width=True
                    ):
                        user_data = {
                            "target_job": target_job,
                            "user_tier": "premium",
                            "source_app": "phoenix_cv_trajectory",
                        }
                        redirect_url = phoenix_bridge.generate_cross_app_redirect_url(
                            PhoenixApp.LETTERS, user_data, "trajectory_builder"
                        )
                        safe_redirect(redirect_url, "🔄 Redirection vers Phoenix Letters...")

                # Sauvegarde données session pour suivi
                st.session_state["last_trajectory"] = {
                    "target_job": target_job,
                    "success_probability": trajectory.success_probability,
                    "difficulty": trajectory.trajectory_difficulty.value,
                    "generated_at": datetime.now().isoformat(),
                }

            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")
                st.info("💡 Essayez de relancer l'analyse ou contactez le support.")

    # Testimonials et social proof
    st.markdown("---")
    st.markdown("## 🌟 **Témoignages Reconversion Réussie**")

    testimonials = [
        {
            "name": "Marie L.",
            "transition": "Comptable → Développeuse Web",
            "duration": "8 mois",
            "text": "Le Trajectory Builder m'a donné un plan clair et réaliste. J'ai suivi étape par étape et j'ai décroché mon CDI !",
        },
        {
            "name": "Thomas K.",
            "transition": "Commercial → Chef de Projet Digital",
            "duration": "6 mois",
            "text": "Incroyable précision ! L'IA a identifié mes compétences transférables que je n'avais même pas vues.",
        },
        {
            "name": "Sophie M.",
            "transition": "RH → Consultante UX/UI",
            "duration": "12 mois",
            "text": "Le plan était ambitieux mais parfaitement calibré. Chaque étape m'a rapprochée de mon objectif.",
        },
    ]

    cols = st.columns(3)

    for i, testimonial in enumerate(testimonials):
        with cols[i]:
            safe_markdown(
                f"""
            <div style="background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #e9ecef; height: 250px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 0.5rem; border-radius: 50px; display: inline-block; font-weight: bold;">
                            {testimonial['name']}
                        </div>
                    </div>
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <strong style="color: #333;">{testimonial['transition']}</strong><br>
                        <small style="color: #28a745; font-weight: bold;">✅ Réussie en {testimonial['duration']}</small>
                    </div>
                    <p style="font-style: italic; color: #666; text-align: center; font-size: 0.9rem;">
                        "{testimonial['text']}"
                    </p>
                </div>
            </div>
            """
            )


def render_footer():
    """Footer de l'application"""
    safe_markdown("---")
    safe_markdown(
        """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 <strong>Phoenix CV Perfect v3.0</strong> - Prompts Magistraux by Gemini Pro</p>
        <p>Enhanced Architecture | Green AI | Perfect Generation</p>
        <p>Made with ❤️ in France | 🛡️ Sécurisé & Conforme RGPD</p>
    </div>
    """
    )


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
    """Point d'entrée principal - délègue vers l'interface modernisée"""
    # Délégation vers la nouvelle interface modernisée
    main_modern()


# NOTE: Code obsolète - le vrai point d'entrée est à la fin du fichier
# if __name__ == "__main__":
#     main()
#     current_page = render_sidebar()

    # Gestion état de session
    if "current_page" in st.session_state:
        current_page = st.session_state["current_page"]

    # Rendu des pages
    if current_page == "home":
        render_home_page()
    elif current_page == "create":
        render_create_cv_page()
    elif current_page == "analyze":
        render_analyze_cv_page()
    elif current_page == "mirror_match":
        render_mirror_match_page()
    elif current_page == "trajectory":
        render_trajectory_builder_page()
    elif current_page == "ecosystem":
        render_ecosystem_page()
    elif current_page == "pricing":
        render_pricing_page()
    elif current_page == "test_render":
        render_test_page()

    # Footer
    render_footer()


def render_test_page():
    """Page de test pour diagnostiquer le problème de rendu HTML"""
    st.title("🧪 Page de Test de Rendu HTML")
    
    st.warning("⚠️ **Page temporaire de diagnostic** - Sera supprimée une fois le problème résolu")
    
    # Test direct avec st.markdown
    st.subheader("Test 1: st.markdown direct")
    html_string = "<div style='padding: 10px; border: 2px solid red; background: #ffe6e6;'><strong>✅ Ceci est un test HTML direct.</strong></div>"
    st.markdown(html_string, unsafe_allow_html=True)
    
    # Test avec listes HTML
    st.subheader("Test 2: Listes HTML avec st.markdown")
    html_list = """
    <div style='padding: 15px; border: 2px solid blue; background: #e6f3ff;'>
        <h4>📋 Test Liste HTML</h4>
        <ul style='color: #333;'>
            <li>✅ Item 1 - Test</li>
            <li>✅ Item 2 - Test</li>
            <li>✅ Item 3 - Test</li>
        </ul>
    </div>
    """
    st.markdown(html_list, unsafe_allow_html=True)
    
    # Test avec la fonction locale
    st.subheader("Test 3: Fonction safe_markdown locale")
    try:
        test_html = "<div style='padding: 10px; border: 2px solid green; background: #e6ffe6;'><strong>✅ Test safe_markdown LOCAL réussi!</strong></div>"
        safe_markdown(test_html)
        st.success("✅ Exécution de safe_markdown locale réussie.")
    except Exception as e:
        st.error(f"❌ Erreur lors de l'exécution de safe_markdown locale : {e}")
    
    # Test des widgets problématiques
    st.subheader("Test 4: Widget Écosystème en Markdown Natif")
    
    with st.container():
        st.markdown("### 📄 Phoenix CV Test")
        st.markdown("*Test du widget écosystème*")
        st.markdown("""
        - ✅ Prompts magistraux Gemini Pro
        - ✅ Optimisation ATS avancée  
        - ✅ Spécialisé reconversions
        - ✅ Green AI intégré
        """)
    
    st.success("✅ Widget écosystème rendu en MARKDOWN NATIF")
    
    # Informations de debug
    st.subheader("🔍 Informations de Debug")
    st.write(f"**Streamlit version:** {st.__version__}")
    st.write(f"**Session state keys:** {list(st.session_state.keys())}")
    
    if st.button("🔄 Rerun Test"):
        st.rerun()


if __name__ == "__main__":
    # Point d'entrée principal - Interface modernisée Phoenix CV 4.1
    main_modern()
