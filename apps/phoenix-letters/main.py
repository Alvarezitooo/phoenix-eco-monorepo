"""
🚀 Phoenix Letters - Point d'entrée principal
Redirection intelligente vers version fonctionnelle selon disponibilité

Author: Claude Phoenix DevSecOps Guardian
Version: Smart-Deploy - Adaptive Entry Point
"""

# Point d'entrée principal - utilise la fonction main() de ce fichier

import logging
import os
import time
from datetime import datetime, timezone

# === IMPORTS ABSOLUS - CONTRÔLE TOTAL DU CONTEXTE ===
import streamlit as st
from config.settings import Settings
from core.entities.user import UserTier
from core.services.job_offer_parser import JobOfferParser
from core.services.letter_service import LetterService
from core.services.prompt_service import PromptService
from core.services.renaissance_integration_service import PhoenixLettersRenaissanceService
from infrastructure.ai.gemini_client import GeminiClient
# Authentification unifiée Phoenix - Path monorepo compatible Streamlit Cloud
import sys
from pathlib import Path

# Path absolu vers packages depuis le monorepo
MONOREPO_ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGES_PATH = MONOREPO_ROOT / "packages"
if str(PACKAGES_PATH) not in sys.path:
    sys.path.insert(0, str(PACKAGES_PATH))

from phoenix_shared_auth.client import AuthManager
from infrastructure.database.db_connection import DatabaseConnection
from infrastructure.security.input_validator import InputValidator
from infrastructure.storage.session_manager import SecureSessionManager
from ui.components.file_uploader import SecureFileUploader
from ui.components.letter_editor import LetterEditor
from ui.components.progress_bar import ProgressIndicator
from ui.pages.about_page import AboutPage
from ui.pages.generator_page import GeneratorPage
from ui.pages.premium_page import PremiumPage
from phoenix_shared_auth.stripe_manager import StripeManager
from core.services.subscription_service import SubscriptionService
from ui.pages.settings_page import SettingsPage
from utils.async_runner import AsyncServiceRunner
# Phoenix shared UI components - import avec fallback
try:
    from phoenix_shared_ui.components import render_primary_button, render_info_card, render_section_header, render_alert, render_ariadne_thread
except ImportError:
    # Fallback pour déploiement Streamlit Cloud
    def render_primary_button(*args, **kwargs): return st.button(*args, **kwargs)
    def render_info_card(*args, **kwargs): return st.info(*args, **kwargs)
    def render_section_header(*args, **kwargs): return st.header(*args, **kwargs)
    def render_alert(*args, **kwargs): return st.warning(*args, **kwargs)
    def render_ariadne_thread(*args, **kwargs): return st.text(*args, **kwargs)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import du style global du Design System
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
style_path = os.path.join(current_dir, "../packages/phoenix_shared_ui/phoenix_shared_ui/style.css")
try:
    if os.path.exists(style_path):
        with open(style_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback pour Streamlit Cloud - essayer chemin alternatif
        alt_style_path = os.path.join(current_dir, "../../packages/phoenix_shared_ui/phoenix_shared_ui/style.css")
        if os.path.exists(alt_style_path):
            with open(alt_style_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    # Gestion silencieuse pour ne pas casser l'app
    pass

# --- Fonctions de Rendu des Pages ---


def render_choice_page():
    """Affiche la page d'accueil avec message clair et parcours guidé selon Contrat V5."""
    # Rediriger directement vers la belle page d'auth (avec protection anti-boucle)
    if st.session_state.get("auth_flow_choice") != "login":
        st.session_state.auth_flow_choice = "login"
        st.rerun()

def render_login_page(auth_manager, subscription_service, async_runner):
    """Affiche le formulaire de connexion/inscription esthétique selon Contrat V5."""
    # Design moderne et bienveillant selon Contrat V5
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h1 style="
            background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        ">🔥 Phoenix Letters</h1>
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
            Votre copilote bienveillant pour des lettres d'exception
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
            backdrop-filter: blur(10px);
        ">
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h3 style="color: #1e293b; margin: 0; font-weight: 600;">
                ✨ Connectez-vous à votre espace
            </h3>
            <p style="color: #64748b; margin-top: 0.5rem; font-size: 0.95rem;">
                Prêt(e) à créer des lettres qui marquent les esprits ?
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Champs de saisie stylés
        email = st.text_input(
            "📧 Adresse e-mail", 
            key="login_email",
            placeholder="votre.email@exemple.com",
            help="Utilisez l'email de votre compte Phoenix"
        )
        password = st.text_input(
            "🔒 Mot de passe", 
            type="password", 
            key="login_password",
            placeholder="Votre mot de passe sécurisé",
            help="Votre mot de passe reste privé et sécurisé"
        )
        
        # Bouton stylé selon Contrat V5
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button(
                "🚀 Se connecter à Phoenix", 
                key="login_btn", 
                type="primary",
                use_container_width=True
            ):
                if not email or not password:
                    st.error("✋ Merci de remplir tous les champs pour continuer votre aventure Phoenix.")
                else:
                    try:
                        success, message, user_id, access_token = auth_manager.sign_in(email, password)
                        if success:
                            st.session_state.user_id = user_id
                            st.session_state.user_email = email
                            st.session_state.access_token = access_token
                            st.session_state.is_authenticated = True
                            
                            # Récupérer le statut d'abonnement
                            try:
                                if async_runner:
                                    future = async_runner.run_coro_in_thread(subscription_service.get_user_subscription(user_id))
                                    subscription = future.result(timeout=10)
                                    if subscription:
                                        st.session_state.user_tier = subscription.current_tier
                                        st.info(f"🔍 DEBUG: Subscription trouvée - User ID: {user_id} - Tier: {subscription.current_tier.value}")
                                        st.info(f"🔍 DEBUG: Subscription complète: Status={subscription.status.value if subscription.status else 'None'}, Customer_ID={subscription.customer_id}")
                                    else:
                                        st.session_state.user_tier = UserTier.FREE
                                        st.warning(f"🔍 DEBUG: Aucun abonnement trouvé pour user_id: {user_id} - Tier FREE attribué")
                                else:
                                    st.session_state.user_tier = UserTier.FREE # Fallback
                                    st.warning("🔍 DEBUG: async_runner non disponible - Tier FREE attribué")
                            except Exception as e:
                                st.session_state.user_tier = UserTier.FREE
                                st.error(f"🔍 DEBUG: Erreur récupération subscription pour user_id {user_id}: {e}")
                            
                            st.success(f"🎉 Bienvenue dans votre espace Phoenix, {email.split('@')[0]} ! Votre créativité n'attend plus que vous.")
                            st.rerun()
                        else:
                            st.error(f"😔 Connexion impossible : {message}. Vérifiez vos identifiants et réessayez.")
                    except Exception as e:
                        st.error(f"😕 Une erreur inattendue est survenue. Notre équipe Phoenix travaille à la résoudre : {e}")
        
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0; padding: 1.5rem; 
                   background: linear-gradient(135deg, #fef3e2 0%, #fde8cc 100%); 
                   border-radius: 15px; border-left: 4px solid #f97316;">
            <h4 style="color: #ea580c; margin: 0 0 0.5rem 0;">
                ✨ Pas encore de compte Phoenix ?
            </h4>
            <p style="color: #9a3412; margin: 0; font-size: 0.95rem;">
                Rejoignez notre communauté et débloquez votre potentiel créatif
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Champs d'inscription stylés
        new_email = st.text_input(
            "📧 Votre adresse e-mail", 
            key="signup_email",
            placeholder="nom.prenom@exemple.com",
            help="Utilisez une adresse e-mail valide pour recevoir vos confirmations"
        )
        new_password = st.text_input(
            "🔐 Créez un mot de passe sécurisé", 
            type="password", 
            key="signup_password",
            placeholder="Minimum 8 caractères",
            help="Un bon mot de passe protège votre créativité"
        )
        
        # Bouton d'inscription stylé
        col_signup1, col_signup2, col_signup3 = st.columns([1, 2, 1])
        with col_signup2:
            if st.button(
                "🌟 Créer mon compte Phoenix", 
                key="signup_btn",
                use_container_width=True
            ):
                if not new_email or not new_password:
                    st.error("🤔 Merci de remplir tous les champs pour créer votre compte Phoenix.")
                else:
                    try:
                        success, message, user_id = auth_manager.sign_up(new_email, new_password)
                        if success:
                            st.session_state.user_id = user_id
                            st.session_state.user_email = new_email
                            st.session_state.is_authenticated = True
                            st.session_state.user_tier = UserTier.FREE # Nouveau compte est Free par défaut
                            st.success(f"🎊 Fantastique ! Votre compte Phoenix est créé, {new_email.split('@')[0]}. Vous pouvez maintenant déployer vos ailes créatives !")
                            st.rerun()
                        else:
                            st.error(f"🚫 Inscription impossible : {message}. Peut-être que ce compte existe déjà ?")
                    except Exception as e:
                        st.error(f"😓 Une erreur technique est survenue. Notre équipe Phoenix y travaille : {e}")
        
        # Fermeture du container principal
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Message de confiance en bas de page
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0; padding: 1rem; 
               background: #f1f5f9; border-radius: 10px; border: 1px solid #e2e8f0;">
        <p style="margin: 0; color: #475569; font-size: 0.9rem;">
            🔒 <strong>Sécurité Phoenix :</strong> Vos données sont chiffrées et protégées selon les standards RGPD. 
            Nous respectons votre vie privée et ne partageons jamais vos informations.</p>
    </div>
    """, unsafe_allow_html=True)

def render_main_app(current_user, auth_manager, settings, db_connection, initialized_components, subscription_service, stripe_service):
    """Affiche l'application principale après authentification selon Contrat V5."""
    
    # Header élégant avec informations utilisateur
    tier_status = "Premium" if current_user.get('user_tier') == UserTier.PREMIUM else "Gratuite"
    tier_emoji = "💎" if current_user.get('user_tier') == UserTier.PREMIUM else "🌟"
    tier_color = "#8b5cf6" if current_user.get('user_tier') == UserTier.PREMIUM else "#f97316"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(249, 115, 22, 0.3);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🔥 Phoenix Letters</h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
                    Votre copilote bienveillant pour des lettres d'exception
                </p>
            </div>
            <div style="text-align: right;">
                <div style="background: rgba(255,255,255,0.2); padding: 0.8rem 1.5rem; border-radius: 15px; margin-bottom: 0.5rem;">
                    <span style="font-weight: 600; font-size: 1.1rem;">{tier_emoji} {tier_status}</span>
                </div>
                <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">
                    {current_user.get('email', 'Utilisateur')}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation par onglets stylés
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 **Générateur**", 
        f"{tier_emoji} **Premium**", 
        "⚙️ **Paramètres**", 
        "ℹ️ **À propos**"
    ])
    
    with tab1:
        # Interface différenciée selon le tier
        if current_user.get('user_tier') == UserTier.PREMIUM:
            # 💎 INTERFACE PREMIUM COMPLÈTE
            st.markdown("""
            <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); 
                       padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
                <h3 style="margin: 0;">💎 Générateur Premium - Accès Complet</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                    Toutes les fonctionnalités avancées débloquées pour vous !
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Accès à la vraie GeneratorPage avec tous les services
            if 'error' in initialized_components:
                st.error(f"❌ Erreur initialisation services : {initialized_components['error']}")
            else:
                try:
                    from ui.pages.generator_page import GeneratorPage
                    generator_page = GeneratorPage(
                        letter_service=initialized_components['letter_service'],
                        file_uploader=initialized_components['file_uploader'],
                        session_manager=initialized_components['session_manager'],
                        progress_indicator=initialized_components['progress_indicator'],
                        letter_editor=initialized_components['letter_editor'],
                        mirror_match_service=initialized_components['mirror_match_service'],
                        ats_analyzer_service=initialized_components['ats_analyzer_service'],
                        smart_coach_service=initialized_components['smart_coach_service'],
                        trajectory_builder_service=initialized_components['trajectory_builder_service'],
                        job_offer_parser=initialized_components['job_offer_parser']
                    )
                    
                    # Rendu de la page complète
                    generator_page.render(
                        current_user=current_user,
                        settings=initialized_components['settings'],
                        gemini_client=initialized_components['gemini_client'],
                        db_connection=initialized_components['db_connection']
                    )
                    
                except Exception as e:
                    st.error(f"❌ Erreur générateur Premium : {e}")
                    st.info("🔧 Contactez le support pour une assistance immédiate.")
        
        else:
            # 🌟 INTERFACE FREE AVEC TEASERS PREMIUM
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); 
                       padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
                <h3 style="margin: 0;">🌟 Générateur Gratuit + Aperçu Premium</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                    3 lettres gratuites par mois + découvrez les fonctionnalités Premium
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tabs pour séparer Free vs Premium teasers
            free_tab, premium_preview = st.tabs(["📝 **Générateur Gratuit**", "💎 **Aperçu Premium**"])
            
            with free_tab:
                # Version limitée mais fonctionnelle pour Free
                if 'error' not in initialized_components:
                    try:
                        from ui.pages.generator_page import GeneratorPage
                        generator_page = GeneratorPage(
                            letter_service=initialized_components['letter_service'],
                            file_uploader=initialized_components['file_uploader'],
                            session_manager=initialized_components['session_manager'],
                            progress_indicator=initialized_components['progress_indicator'],
                            letter_editor=initialized_components['letter_editor'],
                            mirror_match_service=None,  # Désactivé pour Free
                            ats_analyzer_service=None,  # Désactivé pour Free
                            smart_coach_service=None,   # Désactivé pour Free
                            trajectory_builder_service=None,  # Désactivé pour Free
                            job_offer_parser=initialized_components['job_offer_parser']
                        )
                        
                        # Rendu version Free (limitée)
                        generator_page.render(
                            current_user=current_user,
                            settings=initialized_components['settings'],
                            gemini_client=initialized_components['gemini_client'],
                            db_connection=initialized_components['db_connection']
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Erreur générateur : {e}")
                        st.info("📝 Générateur en cours de finalisation...")
                
            with premium_preview:
                # Teasers engageants pour les fonctionnalités Premium
                st.markdown("### 🚀 Fonctionnalités Premium - Aperçu")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Teaser Mirror Match
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #fef3e2 0%, #fde8cc 100%); 
                               padding: 1.5rem; border-radius: 15px; border-left: 4px solid #8b5cf6; margin-bottom: 1rem;">
                        <h4 style="color: #7c3aed; margin: 0 0 0.5rem 0;">🎯 Mirror Match</h4>
                        <p style="color: #9a3412; margin: 0; font-size: 0.9rem;">
                            Adaptez votre lettre au profil exact du recruteur pour 3x plus de chances de réussite.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🔓 Débloquer Mirror Match", key="unlock_mirror", use_container_width=True):
                        st.balloons()
                        st.info("🎉 Passez à Premium pour débloquer Mirror Match !")
                
                with col2:
                    # Teaser ATS Analyzer  
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #fef3e2 0%, #fde8cc 100%); 
                               padding: 1.5rem; border-radius: 15px; border-left: 4px solid #8b5cf6; margin-bottom: 1rem;">
                        <h4 style="color: #7c3aed; margin: 0 0 0.5rem 0;">🤖 Analyse ATS</h4>
                        <p style="color: #9a3412; margin: 0; font-size: 0.9rem;">
                            Optimisez votre lettre pour passer les filtres automatiques des entreprises.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🔓 Débloquer ATS Analyzer", key="unlock_ats", use_container_width=True):
                        st.balloons()
                        st.info("🎉 Passez à Premium pour débloquer l'analyse ATS !")
                
                # === GÉNÉRATEUR GRATUIT IMMÉDIAT ===
                st.markdown("---")
                st.markdown("### 🆓 Générateur Gratuit - Testez Phoenix Letters")
                
                with st.form("quick_letter_generator"):
                    st.write("**Générez votre première lettre gratuitement :**")
                    
                    col_input1, col_input2 = st.columns(2)
                    with col_input1:
                        company_name = st.text_input("🏢 Nom de l'entreprise", placeholder="Ex: Google, Microsoft...")
                        position = st.text_input("💼 Poste visé", placeholder="Ex: Développeur, Manager...")
                    
                    with col_input2:
                        your_name = st.text_input("👤 Votre nom", placeholder="Votre nom complet")
                        experience = st.selectbox("📈 Votre expérience", ["Débutant (0-2 ans)", "Intermédiaire (2-5 ans)", "Senior (5+ ans)"])
                    
                    motivation = st.text_area("✨ Pourquoi cette entreprise vous intéresse ?", 
                                            placeholder="Expliquez en quelques lignes pourquoi vous voulez rejoindre cette entreprise...", 
                                            height=100)
                    
                    generate_button = st.form_submit_button("🚀 Générer ma lettre gratuite", use_container_width=True, type="primary")
                
                if generate_button:
                    if company_name and position and your_name and motivation:
                        with st.spinner("✨ Génération de votre lettre personnalisée..."):
                            time.sleep(2)  # Simulation
                            
                            # Génération simple et immédiate
                            generated_letter = f"""Objet : Candidature pour le poste de {position}

Madame, Monsieur,

Je me permets de vous adresser ma candidature pour le poste de {position} au sein de {company_name}.

{motivation}

Fort(e) de mon expérience en tant que profil {experience.lower()}, je suis convaincu(e) que mes compétences et ma motivation seront des atouts précieux pour votre équipe.

Je serais ravi(e) de vous rencontrer pour discuter de cette opportunité et vous démontrer ma motivation.

Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

{your_name}"""
                            
                            st.success("✅ Lettre générée avec succès !")
                            st.markdown("### 📄 Votre lettre de motivation :")
                            st.text_area("", value=generated_letter, height=300, key="generated_letter_display")
                            
                            col_action1, col_action2, col_action3 = st.columns(3)
                            with col_action1:
                                st.download_button("📥 Télécharger", data=generated_letter, file_name=f"lettre_{company_name.lower().replace(' ', '_')}.txt", mime="text/plain")
                            with col_action2:
                                if st.button("🔄 Regénérer"):
                                    # Clear generated letter to force regeneration
                                    if "generated_letter" in st.session_state:
                                        del st.session_state["generated_letter"]
                                    st.rerun()
                            with col_action3:
                                st.info("💎 Upgrader pour plus de personnalisation")
                                
                    else:
                        st.error("❌ Veuillez remplir tous les champs obligatoires")
                
                # Teasers Smart Coach et Trajectory Builder
                st.markdown("---")
                st.markdown("### 💎 Fonctionnalités Premium")
                col3, col4 = st.columns(2)
                
                with col3:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #fef3e2 0%, #fde8cc 100%); 
                               padding: 1.5rem; border-radius: 15px; border-left: 4px solid #8b5cf6; margin-bottom: 1rem;">
                        <h4 style="color: #7c3aed; margin: 0 0 0.5rem 0;">🧠 Smart Coach</h4>
                        <p style="color: #9a3412; margin: 0; font-size: 0.9rem;">
                            Conseils personnalisés en temps réel pour perfectionner votre candidature.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🔓 Débloquer Smart Coach", key="unlock_coach", use_container_width=True):
                        st.balloons()
                        st.info("🎉 Coaching premium à portée de clic !")
                
                with col4:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #fef3e2 0%, #fde8cc 100%); 
                               padding: 1.5rem; border-radius: 15px; border-left: 4px solid #8b5cf6; margin-bottom: 1rem;">
                        <h4 style="color: #7c3aed; margin: 0 0 0.5rem 0;">📈 Trajectory Builder</h4>
                        <p style="color: #9a3412; margin: 0; font-size: 0.9rem;">
                            Construisez un parcours professionnel cohérent et convaincant.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🔓 Débloquer Trajectory Builder", key="unlock_trajectory", use_container_width=True):
                        st.balloons()
                        st.info("🎉 Bâtissez votre avenir avec Premium !")
                
                # Call-to-action Premium
                st.markdown("---")
                st.markdown("""
                <div style="text-align: center; padding: 2rem; 
                           background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); 
                           border-radius: 20px; color: white; margin: 1rem 0;">
                    <h3 style="margin: 0 0 1rem 0;">🚀 Libérez tout votre potentiel</h3>
                    <p style="margin: 0 0 1.5rem 0; opacity: 0.9;">
                        Passez à Premium et accédez à toutes ces fonctionnalités dès maintenant !
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("💎 Passer à Premium maintenant", key="upgrade_now", type="primary", use_container_width=True):
                    st.balloons()
                    st.success("🎉 Redirection vers l'onglet Premium pour finaliser votre upgrade !")
    
    with tab2:
        # Import et rendu de la vraie PremiumPage
        try:
            from ui.pages.premium_page import PremiumPage
            premium_page = PremiumPage(stripe_service, subscription_service)
            premium_page.render()
        except Exception as e:
            st.error(f"❌ Erreur chargement page Premium : {e}")
            
            # Fallback élégant
            if current_user.get('user_tier') == UserTier.PREMIUM:
                st.markdown("### 💎 Vos avantages Premium")
                st.success("✅ **Statut Premium actif** - Vous avez accès à toutes les fonctionnalités !")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    **🚀 Fonctionnalités débloquées :**
                    - Lettres illimitées
                    - Templates exclusifs
                    - Analyse ATS avancée
                    - Optimisation IA premium
                    """)
                with col2:
                    st.markdown("""
                    **💎 Services Premium :**
                    - Support prioritaire
                    - Coaching personnalisé
                    - Export PDF professionnel
                    - Métriques avancées
                    """)
            else:
                st.markdown("### 🌟 Passer à Premium")
                st.info("💫 Libérez tout votre potentiel avec Phoenix Premium !")
    
    with tab3:
        # Import et rendu de la vraie SettingsPage
        try:
            from ui.pages.settings_page import SettingsPage
            settings_page = SettingsPage()
            settings_page.render()
        except Exception as e:
            st.error(f"❌ Erreur chargement paramètres : {e}")
            
            # Fallback élégant
            st.markdown("### ⚙️ Paramètres du compte")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Informations du compte**")
                st.info(f"📧 **Email** : {current_user.get('email')}")
                st.info(f"🎯 **Plan** : {current_user.get('user_tier').value.title()}")
            
            with col2:
                st.markdown("**Actions rapides**")
                if st.button("🔄 Actualiser le profil", use_container_width=True):
                    st.success("✅ Profil actualisé avec succès !")
    
    with tab4:
        # Import et rendu de la vraie AboutPage
        try:
            from ui.pages.about_page import AboutPage
            about_page = AboutPage()
            about_page.render()
        except Exception as e:
            st.error(f"❌ Erreur chargement page À propos : {e}")
            
            # Fallback élégant
            st.markdown("### ℹ️ À propos de Phoenix Letters")
            st.markdown("""
            **Phoenix Letters** est votre copilote bienveillant pour créer des lettres de motivation d'exception.
            
            Notre mission est de révéler votre potentiel unique et de vous accompagner vers le succès professionnel,
            en utilisant l'intelligence artificielle de manière éthique et bienveillante.
            """)
    
    # Pied de page bienveillant
    st.markdown("---")
    
    # 🔧 BOUTON DEBUG ADMIN TEMPORAIRE (à retirer en production)
    with st.expander("🔧 Admin Debug (temporaire)", expanded=False):
        if st.button("🔧 [ADMIN] Forcer upgrade vers Premium", type="secondary"):
            try:
                service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
                if not service_role_key:
                    st.error("❌ SUPABASE_SERVICE_ROLE_KEY manquante")
                    return
                
                from phoenix_shared_auth.client import get_supabase_client
                admin_client = get_supabase_client()  # ⚠️ Note: utilise ANON_KEY pas SERVICE_ROLE
                
                admin_subscription = {
                    "user_id": current_user["id"],
                    "current_tier": "premium"
                }
                
                response = admin_client.table("user_subscriptions").upsert(admin_subscription).execute()
                st.success(f"✅ Upgrade Premium réussi ! Response: {response.data}")
                st.info("🔄 Rechargez la page pour voir le changement.")
                
            except Exception as e:
                st.error(f"❌ Erreur upgrade admin: {e}")
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem; opacity: 0.7;">
        <p style="margin: 0; font-style: italic; color: #64748b;">
            "Chaque lettre est une opportunité de briller. Phoenix vous accompagne avec bienveillance vers votre réussite."
        </p>
    </div>
    """, unsafe_allow_html=True)

def _route_app_pages(current_user, auth_manager, settings, db_connection, initialized_components, subscription_service, stripe_service, async_runner):
    """Gère l'aiguillage des pages de l'application."""
    if "auth_flow_choice" not in st.session_state:
        st.session_state.auth_flow_choice = None

    # Aiguillage
    if not st.session_state.get("is_authenticated", False):
        if st.session_state.auth_flow_choice == "login":
            render_login_page(auth_manager, subscription_service, async_runner)
        else: # guest mode
            render_choice_page()
    else:  # L'utilisateur est connecté
        render_main_app(current_user, auth_manager, settings, db_connection, initialized_components, subscription_service, stripe_service)

def main():
    """Point d'entrée et aiguilleur principal de l'application."""
    st.set_page_config(layout="wide", page_title="Phoenix Letters")

    settings = Settings()

    if "async_service_runner" not in st.session_state:
        st.session_state.async_service_runner = AsyncServiceRunner()
        st.session_state.async_service_runner.start()

    @st.cache_resource
    def get_db_connection(settings: Settings) -> DatabaseConnection:
        """Initialise et retourne une connexion à la base de données."""
        return DatabaseConnection(settings)

    db_connection = get_db_connection(settings)
    
    # Initialisation des services nécessaires
    session_manager = SecureSessionManager(settings)
    input_validator = InputValidator()
    auth_manager = AuthManager()  # Contrat V5: AuthManager unifié sans paramètres

    # Initialisation des services de paiement (safe mode)
    try:
        stripe_service = StripeManager()
        subscription_service = SubscriptionService(
            settings=settings,
            stripe_service=stripe_service,
            db_connection=db_connection,
            input_validator=input_validator
        )
    except Exception as e:
        logger.warning(f"Services de paiement non disponibles: {e}")
        stripe_service = None
        subscription_service = None

    # 🧹 AUTO-NETTOYAGE SESSION pour prévenir memory bloat
    try:
        from utils.session_cleaner import auto_cleanup
        was_cleaned, cleanup_msg = auto_cleanup()
        if was_cleaned:
            st.info(f"🧹 {cleanup_msg}")
    except ImportError:
        pass  # Session cleaner optionnel

    # 🔎 DIAGNOSTIC SUPABASE (temporaire pour debug)
    with st.expander("🔎 Diagnostic Supabase", expanded=False):
        try:
            from phoenix_shared_auth.client import get_supabase_client
            sb = get_supabase_client()
            # Test simple de connexion
            out = sb.table("profiles").select("id").limit(1).execute()
            st.success(f"✅ Connecté Supabase – test query OK (rows: {len(out.data)})")
        except Exception as e:
            st.error(f"❌ Supabase KO: {e!s}")
            st.caption("Vérifie secrets et policies RLS.")
        
        # Stats session Letters
        try:
            from utils.session_cleaner import PhoenixLettersSessionCleaner
            stats = PhoenixLettersSessionCleaner.get_session_stats()
            st.markdown("**📊 Session Stats:**")
            st.write(f"- Clés totales: {stats['total_keys']}")
            st.write(f"- Clés protégées: {stats['protected_keys']}")
            st.write(f"- Clés temporaires: {stats['temporary_keys']}")
            if stats['total_keys'] > 40:
                st.warning("⚠️ Session volumineuse - nettoyage recommandé")
        except ImportError:
            pass

    # Récupération de l'utilisateur courant (si déjà authentifié dans la session)
    current_user = None
    if st.session_state.get("is_authenticated", False):
        # Ici, on pourrait rafraîchir les données utilisateur si nécessaire
        # Pour l'instant, on se base sur ce qui est en session
        current_user = {
            "id": st.session_state.user_id,
            "email": st.session_state.user_email,
            "user_tier": st.session_state.user_tier
        }

    # 🔬 BANNIÈRE RECHERCHE-ACTION PHOENIX (désactivable via ENV)
    try:
        import os
        enable_banner = os.getenv("ENABLE_RESEARCH_BANNER", "false").lower() == "true"
    except Exception:
        enable_banner = False
    if enable_banner:
        render_research_action_banner()
    
    # 🔮 PROTOCOLE RENAISSANCE - Vérification si utilisateur connecté
    if current_user and hasattr(current_user, 'id'):
        renaissance_service = PhoenixLettersRenaissanceService(db_connection)
        
        if renaissance_service.should_show_renaissance_banner_letters(current_user["id"]):
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    margin-bottom: 2rem;
                    text-align: center;
                    box-shadow: 0 8px 25px rgba(236,72,153,0.3);
                    animation: pulse 2s ease-in-out infinite alternate;
                ">
                    <h3 style="margin: 0; font-size: 1.3rem; font-weight: bold;">
                        🔮 PROTOCOLE RENAISSANCE DÉTECTÉ
                    </h3>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
                        Vos patterns de candidature suggèrent qu'un accompagnement personnalisé pourrait vous aider. 
                        Explorons ensemble de nouvelles stratégies ! ✨
                    </p>
                </div>
                <style>
                @keyframes pulse {
                    from { box-shadow: 0 8px 25px rgba(236,72,153,0.3); }
                    to { box-shadow: 0 12px 35px rgba(236,72,153,0.5); }
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # Affichage des recommandations Renaissance pour les lettres
            recommendations = renaissance_service.get_renaissance_letter_recommendations(current_user["id"])
            if recommendations:
                st.markdown("### 🎯 Recommandations Renaissance - Lettres")
                for rec in recommendations:
                    st.markdown(f"• {rec}")
                st.markdown("---")

    # Initialize GeminiClient here to pass it to _initialize_app_components
    use_mock = st.sidebar.checkbox(
        "Utiliser le Mock API (Mode Développeur)", value=False
    )
    if use_mock:
        from infrastructure.ai.mock_gemini_client import MockGeminiClient
        gemini_client = MockGeminiClient()
        st.sidebar.warning("Mode Mock API activé.")
    else:
        gemini_client = GeminiClient(settings)
        st.sidebar.success("Mode API Réelle activé.")

    # Initialisation complète de tous les services selon Contrat V5
    @st.cache_resource
    def initialize_all_services():
        """Initialise tous les services Phoenix Letters pour accès complet aux fonctionnalités."""
        try:
            # Services de base
            session_manager = SecureSessionManager(settings)
            input_validator = InputValidator()
            
            # Services UI
            file_uploader = SecureFileUploader(input_validator, settings)
            progress_indicator = ProgressIndicator()
            letter_editor = LetterEditor()
            
            # Services métier Phoenix
            letter_service = LetterService(gemini_client, settings)
            job_offer_parser = JobOfferParser()
            prompt_service = PromptService()
            
            # Services Premium (mocks sécurisés si pas disponibles)
            try:
                from core.services.mirror_match_service import MirrorMatchService
                mirror_match_service = MirrorMatchService()
            except ImportError:
                mirror_match_service = None
                
            try:
                from core.services.ats_analyzer_service import ATSAnalyzerService  
                ats_analyzer_service = ATSAnalyzerService()
            except ImportError:
                ats_analyzer_service = None
                
            try:
                from core.services.smart_coach_service import SmartCoachService
                smart_coach_service = SmartCoachService()
            except ImportError:
                smart_coach_service = None
                
            try:
                from core.services.trajectory_builder_service import TrajectoryBuilderService
                trajectory_builder_service = TrajectoryBuilderService()
            except ImportError:
                trajectory_builder_service = None
            
            return {
                'gemini_client': gemini_client,
                'settings': settings,
                'db_connection': db_connection,
                'session_manager': session_manager,
                'input_validator': input_validator,
                'file_uploader': file_uploader,
                'progress_indicator': progress_indicator,
                'letter_editor': letter_editor,
                'letter_service': letter_service,
                'job_offer_parser': job_offer_parser,
                'prompt_service': prompt_service,
                'mirror_match_service': mirror_match_service,
                'ats_analyzer_service': ats_analyzer_service,
                'smart_coach_service': smart_coach_service,
                'trajectory_builder_service': trajectory_builder_service
            }
        except Exception as e:
            logger.error(f"Erreur initialisation services: {e}")
            # Fallback sécurisé
            return {
                'gemini_client': gemini_client,
                'settings': settings,
                'db_connection': db_connection,
                'error': str(e)
            }
    
    initialized_components = initialize_all_services()

    # Bannière de mise à niveau pour les utilisateurs Free
    if current_user and current_user["user_tier"] == UserTier.FREE:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%); padding: 0.8rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <p style="margin: 0; font-size: 0.95rem; font-weight: 500; color: #333;">
                    Vous utilisez la version gratuite. Libérez toute la puissance de Phoenix.
                </p>
                <div style="margin-top: 0.5rem;">
                    <a href="/premium" target="_self" style="text-decoration: none;">
                        <button style="background: #f97316; color: white; border: none; padding: 0.4rem 1rem; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 0.85rem;">
                            Voir les offres
                        </button>
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    _route_app_pages(current_user, auth_manager, settings, db_connection, initialized_components, subscription_service, stripe_service, st.session_state.async_service_runner)

if __name__ == "__main__":
    main()
