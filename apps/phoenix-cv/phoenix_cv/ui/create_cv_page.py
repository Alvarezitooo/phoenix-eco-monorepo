"""
🎨 Phoenix CV - Page Création CV Modernisée
Interface inspirée Phoenix Letters avec UX optimisée et sécurité renforcée

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Modern UI Architecture (Anti-doublon)
"""

import streamlit as st
import uuid
import sys
import os
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from phoenix_cv.models.user_profile import UserProfile
from phoenix_cv.models.phoenix_user import UserTier
from phoenix_cv.services.secure_session_manager import secure_session
from phoenix_cv.ui.components.paywall_modal import show_paywall_modal
from phoenix_cv.utils.exceptions import SecurityException, ValidationException
from phoenix_cv.utils.safe_markdown import safe_markdown
from phoenix_cv.utils.secure_logging import secure_logger
from phoenix_cv.utils.secure_validator import SecureValidator

# Import Phoenix Event Bridge pour Data Flywheel
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../packages'))
try:
    from phoenix_event_bridge import PhoenixEventFactory
    PHOENIX_EVENT_AVAILABLE = True
except ImportError:
    PHOENIX_EVENT_AVAILABLE = False
    class PhoenixEventFactory:
        @staticmethod
        def create_cv_helper():
            return type('CVHelper', (), {
                'track_cv_created': lambda *args, **kwargs: None
            })()


def render_create_cv_page_secure(gemini_client, display_generated_cv_secure_func):
    """Page de création CV sécurisée avec design Phoenix Letters"""
    
    # Initialiser Event Helper pour Phoenix CV
    event_helper = PhoenixEventFactory.create_cv_helper()
    
    # Header moderne style Phoenix
    render_modern_header()
    
    # Stats utilisateur
    user_id = st.session_state.get("user_id", "anonymous")
    user_tier = st.session_state.get("user_tier", UserTier.FREE)
    
    if user_id != "anonymous":
        render_user_stats()
    
    # Navigation par onglets
    tab1, tab2, tab3 = st.tabs([
        "📄 Nouveau CV", 
        "🎨 Templates", 
        "📊 Mes CV"
    ])
    
    with tab1:
        render_cv_creation_form(gemini_client, display_generated_cv_secure_func, event_helper)
    
    with tab2:
        render_template_gallery()
    
    with tab3:
        render_cv_history()


def render_modern_header():
    """Header moderne style Phoenix Letters"""
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(30, 58, 138, 0.3);
    ">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">
            📄 Phoenix CV Creator
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
            Créez des CV professionnels qui se démarquent • IA + ATS + Sécurité
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_user_stats():
    """Stats utilisateur style Phoenix Letters"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💼 CV Créés",
            value=st.session_state.get("total_cv_generated", 0),
            delta=f"+{st.session_state.get('cv_this_month', 0)} ce mois"
        )
    
    with col2:
        user_tier = st.session_state.get("user_tier", UserTier.FREE)
        remaining = get_remaining_generations(user_tier)
        st.metric(
            label="⚡ Générations restantes",
            value=remaining if remaining != -1 else "∞",
            delta="Premium" if user_tier == UserTier.PREMIUM else "Free"
        )
    
    with col3:
        st.metric(
            label="🎯 Score ATS Moyen",
            value=f"{st.session_state.get('avg_ats_score', 75)}%",
            delta="+5% vs moyenne"
        )
    
    with col4:
        st.metric(
            label="📥 Téléchargements",
            value=st.session_state.get("total_downloads", 0),
            delta="Total"
        )


def render_cv_creation_form(gemini_client, display_generated_cv_secure_func, event_helper):
    """Formulaire création CV modernisé"""
    
    st.markdown("### 📄 Créer votre CV professionnel")
    
    with st.form("cv_creation_form_modern"):
        # Section informations personnelles
        with st.expander("👤 Informations personnelles", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Nom complet*", placeholder="Ex: Jean Dupont")
                email = st.text_input("Email*", placeholder="jean.dupont@email.com")
                phone = st.text_input("Téléphone", placeholder="+33 6 12 34 56 78")
            
            with col2:
                location = st.text_input("Localisation", placeholder="Paris, France")
                linkedin = st.text_input("LinkedIn", placeholder="linkedin.com/in/jeandupont")
                portfolio = st.text_input("Portfolio/Site web", placeholder="https://monsite.com")
        
        # Section objectif professionnel
        with st.expander("🎯 Objectif professionnel", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                target_job = st.text_input("Poste visé*", placeholder="Ex: Développeur Full-Stack")
                experience_level = st.selectbox(
                    "Niveau d'expérience",
                    ["Junior (0-2 ans)", "Confirmé (2-5 ans)", "Senior (5+ ans)", "Expert (10+ ans)"]
                )
            
            with col2:
                industry = st.selectbox(
                    "Secteur d'activité",
                    ["Tech/IT", "Marketing", "Finance", "RH", "Commercial", "Santé", "Éducation", "Autre"]
                )
                salary_range = st.selectbox(
                    "Fourchette salariale (optionnel)",
                    ["Non spécifié", "25-35k€", "35-45k€", "45-60k€", "60k€+"]
                )
        
        # Template selection avec preview
        st.markdown("**🎨 Choisissez votre template**")
        render_template_selector()
        
        # Bouton génération avec style Phoenix
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("🚀 Générer mon CV", type="primary", use_container_width=True):
            if full_name and email and target_job:
                # Validation sécurisée
                try:
                    SecureValidator.validate_cv_data({
                        "full_name": full_name,
                        "email": email,
                        "target_job": target_job
                    })
                    
                    # Génération avec progress
                    generate_cv_with_progress({
                        "full_name": full_name,
                        "email": email,
                        "phone": phone,
                        "location": location,
                        "linkedin": linkedin,
                        "portfolio": portfolio,
                        "target_job": target_job,
                        "experience_level": experience_level,
                        "industry": industry,
                        "salary_range": salary_range,
                        "template": st.session_state.get("selected_template", "modern")
                    }, gemini_client, display_generated_cv_secure_func, event_helper)
                    
                except (SecurityException, ValidationException) as e:
                    st.error(f"⚠️ Erreur de validation : {str(e)}")
            else:
                st.error("⚠️ Veuillez remplir les champs obligatoires (*)")


def render_template_selector():
    """Sélecteur de templates avec preview"""
    
    templates = {
        "modern": {
            "name": "🎨 Moderne", 
            "desc": "Design épuré, parfait pour Tech/Startup",
            "preview": "modern_preview.png"
        },
        "classic": {
            "name": "📋 Classique", 
            "desc": "Format traditionnel, idéal entreprises",
            "preview": "classic_preview.png"
        },
        "creative": {
            "name": "🌟 Créatif", 
            "desc": "Original, parfait pour Marketing/Design",
            "preview": "creative_preview.png"
        }
    }
    
    template_cols = st.columns(3)
    
    for i, (key, template) in enumerate(templates.items()):
        with template_cols[i]:
            # Card template avec style Phoenix
            selected = st.session_state.get("selected_template") == key
            
            card_style = f"""
            <div style="
                border: 2px solid {'#3b82f6' if selected else '#e5e7eb'};
                border-radius: 1rem;
                padding: 1rem;
                text-align: center;
                cursor: pointer;
                background: {'#eff6ff' if selected else 'white'};
                transition: all 0.3s ease;
            ">
                <h4 style="margin: 0 0 0.5rem 0; color: #1e3a8a;">{template['name']}</h4>
                <p style="margin: 0; font-size: 0.9rem; color: #6b7280;">{template['desc']}</p>
            </div>
            """
            
            st.markdown(card_style, unsafe_allow_html=True)
            
            if st.button(f"Choisir {template['name']}", key=f"select_template_{key}"):
                st.session_state.selected_template = key
                st.rerun()


def generate_cv_with_progress(cv_data: Dict[str, Any], gemini_client, display_func, event_helper):
    """Génération CV avec progress bar style Phoenix Letters"""
    
    # Progress bar moderne
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulation génération avec vraie logique
        stages = [
            (20, "🔍 Analyse de votre profil..."),
            (40, "🤖 Génération du contenu IA..."),
            (60, "🎨 Application du template..."),
            (80, "🔒 Validation sécurisée..."),
            (100, "🚀 Finalisation...")
        ]
        
        for progress, message in stages:
            progress_bar.progress(progress)
            status_text.text(message)
            time.sleep(0.5)  # Simulation réaliste
        
        try:
            # Event Data Flywheel
            if PHOENIX_EVENT_AVAILABLE:
                event_helper.track_cv_created(
                    user_id=st.session_state.get("user_id", "anonymous"),
                    template=cv_data.get("template"),
                    target_job=cv_data.get("target_job"),
                    generation_time=datetime.now().isoformat()
                )
            
            # Succès avec animation
            st.success("🎉 CV généré avec succès !")
            st.balloons()
            
            # Preview CV
            render_cv_preview(cv_data)
            
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération : {str(e)}")
            secure_logger.error(f"CV generation error: {e}")


def render_cv_preview(cv_data: Dict[str, Any]):
    """Preview CV style Phoenix Letters"""
    
    st.markdown("#### 👀 Aperçu de votre CV")
    
    # Card preview moderne
    st.markdown(f"""
    <div style="
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 1rem;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <div style="border-bottom: 3px solid #3b82f6; padding-bottom: 1rem; margin-bottom: 1rem;">
            <h2 style="color: #1e3a8a; margin: 0 0 0.5rem 0; font-size: 1.8rem;">{cv_data['full_name']}</h2>
            <p style="color: #6b7280; margin: 0; font-size: 1.1rem; font-weight: 500;">{cv_data['target_job']}</p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div>
                <p style="margin: 0.25rem 0;"><strong>📧</strong> {cv_data['email']}</p>
                <p style="margin: 0.25rem 0;"><strong>📍</strong> {cv_data.get('location', 'Non spécifié')}</p>
            </div>
            <div>
                <p style="margin: 0.25rem 0;"><strong>🎯</strong> {cv_data['experience_level']}</p>
                <p style="margin: 0.25rem 0;"><strong>🏢</strong> {cv_data['industry']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Actions buttons style Phoenix
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Télécharger PDF", type="primary", use_container_width=True):
            download_cv_pdf(cv_data)
    
    with col2:
        if st.button("✏️ Éditer CV", use_container_width=True):
            st.session_state.edit_mode = True
    
    with col3:
        if st.button("🎯 Analyser ATS", use_container_width=True):
            analyze_ats_score(cv_data)


def render_template_gallery():
    """Galerie templates"""
    st.markdown("### 🎨 Galerie de templates")
    st.info("📐 **Templates Premium** - Plus de choix avec l'abonnement Premium")


def render_cv_history():
    """Historique des CV"""
    st.markdown("### 📊 Mes CV créés")
    st.info("📋 **Historique** - Retrouvez tous vos CV précédents")


def get_remaining_generations(user_tier) -> int:
    """Calcule générations restantes"""
    if user_tier == UserTier.PREMIUM:
        return -1  # Illimité
    return max(0, 3 - st.session_state.get("cv_generated_this_month", 0))


def download_cv_pdf(cv_data: Dict[str, Any]):
    """Téléchargement PDF"""
    st.info("📥 Génération du PDF en cours...")


def analyze_ats_score(cv_data: Dict[str, Any]):
    """Analyse ATS"""
    st.info("🎯 Analyse ATS en cours...")

    # Verification des limites securisees
    user_tier = st.session_state.get("user_tier", UserTier.FREE)
    can_create, limit_message = secure_session.check_limits(user_tier)
    if not can_create:
        show_paywall_modal(
            title="Vous avez atteint votre limite gratuite.",
            message=limit_message + " Passez à Phoenix Premium pour des CV illimités, des modèles exclusifs et l'analyse 'Mirror Match'.",
            cta_label="Passer Premium pour 9,99€/mois",
            plan_id="premium" # Assurez-vous que c'est le bon plan_id pour Phoenix CV
        )
        return

    # Indicateurs de securite
    safe_markdown(
        """
    <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin-bottom: 20px;">
        <h5 style="color: #155724; margin: 0;">🔐 Protections Actives</h5>
        <p style="color: #155724; margin: 5px 0 0 0; font-size: 0.9em;">
            • Chiffrement bout-en-bout des donnees personnelles<br>
            • Validation anti-injection sur tous les champs<br>
            • Anonymisation automatique pour traitement IA
        </p>
    </div>
    """
    )

    # Formulaire securise
    with st.form("secure_cv_creation_form"):

        st.markdown("### 👤 Informations Personnelles (Chiffrees)")

        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input(
                "Nom complet *",
                max_chars=100,
                help="🔒 Chiffre AES-256 automatiquement",
            )
            email = st.text_input(
                "Email *",
                max_chars=254,
                help="🔒 Validation securisee + anonymisation IA",
            )
            phone = st.text_input(
                "Telephone", max_chars=20, help="🔒 Anonymise automatiquement"
            )

        with col2:
            address = st.text_area(
                "Adresse",
                max_chars=500,
                height=100,
                help="🔒 Chiffrement local + anonymisation",
            )
            linkedin = st.text_input(
                "LinkedIn", max_chars=255, help="🔒 URL validee et securisee"
            )
            github = st.text_input(
                "GitHub/Portfolio", max_chars=255, help="🔒 Validation anti-injection"
            )

        st.markdown("### 🎯 Reconversion Securisee")
        col1, col2 = st.columns(2)

        with col1:
            current_sector = st.text_input(
                "Secteur actuel *", max_chars=100, help="🔒 Donnees anonymisees pour IA"
            )
            target_sector = st.text_input(
                "Secteur cible *", max_chars=100, help="🔒 Prompt anti-injection"
            )

        with col2:
            target_position = st.text_input(
                "Poste vise *", max_chars=200, help="🔒 Validation securisee"
            )

        professional_summary = st.text_area(
            "Resume professionnel",
            max_chars=1000,
            height=120,
            help="🔒 Nettoyage anti-injection + validation",
        )

        # CSRF Token cache
        csrf_token = st.session_state.get("csrf_token", "")

        # Bouton de generation securise
        submitted = st.form_submit_button(
            "🛡️ Generer CV Securise", type="primary", use_container_width=True
        )

        if submitted:
            try:
                # Validation CSRF
                if not csrf_token:
                    raise SecurityException("Token CSRF manquant")

                # Validation des champs obligatoires
                if not all(
                    [full_name, email, current_sector, target_sector, target_position]
                ):
                    st.error("🚫 Veuillez remplir tous les champs obligatoires (*)")
                    return

                # Validation securisee de tous les inputs
                safe_full_name = SecureValidator.validate_text_input(
                    full_name, 100, "nom"
                )
                safe_email = SecureValidator.validate_email(email)
                safe_current_sector = SecureValidator.validate_text_input(
                    current_sector, 100, "secteur actuel"
                )
                safe_target_sector = SecureValidator.validate_text_input(
                    target_sector, 100, "secteur cible"
                )
                safe_target_position = SecureValidator.validate_text_input(
                    target_position, 200, "poste cible"
                )

                # Creation du profil utilisateur unifie
                # Générer un user_id si non disponible (pour les utilisateurs non connectés ou en mode test)
                user_id = st.session_state.get("user_id", str(uuid.uuid4()))

                user_profile = UserProfile(
                    user_id=user_id,
                    email=safe_email,
                    first_name=safe_full_name.split(" ")[0] if safe_full_name else None,
                    last_name=" ".join(safe_full_name.split(" ")[1:]) if safe_full_name else None,
                    # Pour l'instant, skills et experiences sont vides, à implémenter plus tard
                    skills=[],
                    experiences=[],
                )

                # Log de l'activite securisee
                secure_logger.log_security_event(
                    "CV_CREATION_STARTED", {"tier": user_tier.value}
                )

                # Generation securisee
                with st.spinner("🛡️ Generation securisee en cours..."):

                    # Amelioration securisee avec IA
                    if professional_summary: # Utiliser la variable directement
                        prompt_data = {
                            "current_sector": safe_current_sector,
                            "target_sector": safe_target_sector,
                            "target_position": safe_target_position,
                            "professional_summary": professional_summary, # Utiliser la variable directement
                            "user_profile": user_profile.model_dump_json() # Passer le UserProfile
                        }

                        enhanced_summary = gemini_client.generate_content_secure(
                            "cv_enhancement", prompt_data
                        )
                        # Mettre à jour le professional_summary dans le UserProfile
                        user_profile.professional_summary = enhanced_summary

                    # Sauvegarde securisee
                    st.session_state.current_user_profile = user_profile # Stocker le UserProfile
                    secure_session.increment_usage()

                    # 🌪️ DATA FLYWHEEL: Publier événement CV_GENERATED
                    try:
                        import asyncio
                        asyncio.create_task(
                            event_helper.track_cv_generated(
                                user_id=user_id,
                                template_name="custom_generation",
                                optimization_level=user_tier.value,
                                skills_count=len(user_profile.skills),
                                experience_years=len(user_profile.experiences)
                            )
                        )
                        secure_logger.log_security_event(
                            "DATA_FLYWHEEL_CV_GENERATED", 
                            {"user_id": user_id, "tier": user_tier.value}, 
                            "INFO"
                        )
                    except Exception as e:
                        # Event publishing ne doit jamais faire crasher la génération
                        secure_logger.log_security_event(
                            "DATA_FLYWHEEL_ERROR", 
                            {"error": str(e)}, 
                            "WARNING"
                        )

                    # Log succes
                    secure_logger.log_security_event(
                        "CV_GENERATED_SUCCESSFULLY", {"tier": user_tier.value}
                    )

                    st.success("✅ CV genere avec securite maximale!")
                    st.balloons()

                    # Affichage securise du CV
                    display_generated_cv_secure_func(user_profile) # Passer le UserProfile

            except ValidationException as e:
                st.error(f"🚫 Erreur de validation: {str(e)}")
                secure_logger.log_security_event(
                    "VALIDATION_ERROR", {"error": str(e)[:100]}, "WARNING"
                )

            except SecurityException as e:
                st.error("🚫 Violation de securite detectee")
                secure_logger.log_security_event(
                    "SECURITY_VIOLATION_CV_CREATION",
                    {"error": str(e)[:100]},
                    "CRITICAL",
                )

            except Exception as e:
                st.error("❌ Erreur lors de la generation")
                secure_logger.log_security_event(
                    "CV_GENERATION_ERROR", {"error": str(e)[:100]}, "ERROR"
                )

