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
    """Header moderne style Phoenix Letters en Streamlit natif"""
    
    # Container pour l'effet gradient (background uniquement)
    with st.container():
        # Titre principal
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <h1 style="
                color: #1e3a8a; 
                font-size: 2.5rem; 
                font-weight: 700; 
                margin: 0;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                📄 Phoenix CV Creator
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Sous-titre
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <p style="
                color: #3b82f6; 
                font-size: 1.2rem; 
                font-weight: 500;
                margin: 0;
            ">
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
        
        # Sections Premium
        user_tier = st.session_state.get("user_tier", UserTier.FREE)
        
        # 💼 Expériences professionnelles (Premium)
        if user_tier == UserTier.PREMIUM:
            with st.expander("💼 Expériences professionnelles détaillées", expanded=False):
                st.markdown("**🌟 PREMIUM** - Ajoutez jusqu'à 5 expériences détaillées")
                
                experiences = []
                for i in range(3):  # 3 expériences max pour commencer
                    st.markdown(f"**Expérience #{i+1}**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        exp_title = st.text_input(f"Poste", key=f"exp_title_{i}")
                        exp_company = st.text_input(f"Entreprise", key=f"exp_company_{i}")
                    
                    with col2:
                        exp_duration = st.text_input(f"Durée", placeholder="2020-2023", key=f"exp_duration_{i}")
                        exp_location = st.text_input(f"Lieu", key=f"exp_location_{i}")
                    
                    exp_description = st.text_area(
                        f"Description des missions", 
                        height=100, 
                        key=f"exp_desc_{i}",
                        help="Décrivez vos principales responsabilités et réalisations"
                    )
                    
                    if exp_title and exp_company:
                        experiences.append({
                            "title": exp_title,
                            "company": exp_company,
                            "duration": exp_duration,
                            "location": exp_location,
                            "description": exp_description
                        })
                    
                    st.markdown("---")
        else:
            # Version gratuite - 1 expérience simple
            with st.expander("💼 Expérience principale", expanded=False):
                experience_description = st.text_area(
                    "Décrivez votre expérience principale",
                    height=120,
                    help="💡 Passez à PREMIUM pour ajouter plusieurs expériences détaillées"
                )
                
                # Call-to-action Premium
                st.markdown("""
                <div style="background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); 
                           padding: 1rem; border-radius: 10px; margin-top: 1rem; text-align: center;">
                    <h4 style="margin: 0; color: #333;">🌟 Débloquez le potentiel PREMIUM</h4>
                    <p style="margin: 0.5rem 0; color: #555; font-size: 0.9rem;">
                        ✨ Expériences multiples détaillées<br>
                        🎯 Descriptions par poste et réalisations<br>
                        📈 Optimisation ATS avancée
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # 🎓 Formations (Premium)
        if user_tier == UserTier.PREMIUM:
            with st.expander("🎓 Formations et certifications", expanded=False):
                st.markdown("**🌟 PREMIUM** - Formations illimitées avec détails")
                
                educations = []
                for i in range(3):
                    st.markdown(f"**Formation #{i+1}**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edu_degree = st.text_input(f"Diplôme/Certification", key=f"edu_degree_{i}")
                        edu_school = st.text_input(f"École/Organisme", key=f"edu_school_{i}")
                    
                    with col2:
                        edu_year = st.text_input(f"Année", key=f"edu_year_{i}")
                        edu_location = st.text_input(f"Lieu", key=f"edu_location_{i}")
                    
                    if edu_degree and edu_school:
                        educations.append({
                            "degree": edu_degree,
                            "school": edu_school,
                            "year": edu_year,
                            "location": edu_location
                        })
                    
                    st.markdown("---")
        else:
            # Version gratuite - formation simple
            with st.expander("🎓 Formation principale", expanded=False):
                education_level = st.selectbox(
                    "Niveau d'études",
                    ["Bac", "Bac+2", "Bac+3", "Bac+5", "Doctorat", "Autre"]
                )
                education_field = st.text_input("Domaine d'études", placeholder="Ex: Informatique")
        
        # 🔧 Compétences (Premium détaillé, Free simple)
        with st.expander("🔧 Compétences", expanded=False):
            if user_tier == UserTier.PREMIUM:
                st.markdown("**🌟 PREMIUM** - Compétences par catégories avec niveaux")
                
                # Compétences techniques
                st.markdown("**💻 Compétences techniques**")
                technical_skills = st.text_area(
                    "Technologies, langages, outils...",
                    height=60,
                    placeholder="Python, JavaScript, React, Docker, AWS..."
                )
                
                # Compétences métier
                st.markdown("**🏢 Compétences métier**")
                business_skills = st.text_area(
                    "Compétences sectorielles...",
                    height=60,
                    placeholder="Gestion de projet, Analyse financière, Marketing digital..."
                )
                
                # Soft skills
                st.markdown("**🤝 Soft skills**")
                soft_skills = st.text_area(
                    "Qualités humaines et relationnelles...",
                    height=60,
                    placeholder="Leadership, Communication, Adaptabilité, Esprit d'équipe..."
                )
                
                # Langues
                st.markdown("**🌍 Langues**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    lang1 = st.text_input("Langue 1", placeholder="Français")
                    level1 = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé", "Natif"], key="level1")
                with col2:
                    lang2 = st.text_input("Langue 2", placeholder="Anglais")
                    level2 = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé", "Natif"], key="level2")
                with col3:
                    lang3 = st.text_input("Langue 3", placeholder="Espagnol")
                    level3 = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé", "Natif"], key="level3")
                    
            else:
                st.markdown("💡 **Version gratuite** - Compétences principales")
                main_skills = st.text_area(
                    "Vos principales compétences",
                    height=80,
                    placeholder="Ex: Python, Gestion de projet, Communication..."
                )
                st.info("🌟 Passez à PREMIUM pour organiser vos compétences par catégories et ajouter les niveaux")
        
        # 🏆 Réalisations & Projets (Premium uniquement)
        if user_tier == UserTier.PREMIUM:
            with st.expander("🏆 Réalisations & Projets", expanded=False):
                st.markdown("**🌟 PREMIUM** - Mettez en avant vos succès")
                
                achievements = st.text_area(
                    "Réalisations marquantes",
                    height=100,
                    placeholder="• Augmentation du CA de 25%\n• Management d'une équipe de 10 personnes\n• Développement d'une app utilisée par 10k+ users"
                )
                
                projects = st.text_area(
                    "Projets personnels/professionnels",
                    height=100,
                    placeholder="• Développement d'un chatbot IA\n• Organisation d'événements tech\n• Contributions open source"
                )
        
        # Récapitulatif des fonctionnalités selon le tier
        if user_tier == UserTier.FREE:
            st.markdown("### 📋 Votre CV FREE")
            st.info("""
            **Inclus dans votre CV :**
            • ✅ Informations personnelles
            • ✅ Objectif professionnel  
            • ✅ 1 expérience principale
            • ✅ Formation principale
            • ✅ Compétences de base
            • ✅ 3 générations par mois
            
            **🌟 Passez à PREMIUM pour débloquer :**
            • 🚀 Expériences multiples détaillées
            • 🎓 Formations et certifications illimitées
            • 🔧 Compétences par catégories + niveaux
            • 🌍 Langues avec niveaux
            • 🏆 Réalisations et projets
            • 📊 Templates premium + ATS avancé
            • ♾️ Générations illimitées
            """)
        else:
            st.markdown("### 🌟 Votre CV PREMIUM")
            st.success("""
            **Toutes les fonctionnalités débloquées :**
            • ✅ Expériences professionnelles détaillées (3+)
            • ✅ Formations et certifications complètes
            • ✅ Compétences organisées par catégories
            • ✅ Langues avec niveaux de maîtrise
            • ✅ Réalisations et projets marquants
            • ✅ Templates premium et optimisation ATS
            • ✅ Générations illimitées
            """)
        
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
                    
                    # Construire les données CV complètes
                    cv_data = {
                        # Informations de base
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
                        "template": st.session_state.get("selected_template", "modern"),
                        "user_tier": user_tier.value
                    }
                    
                    # Données Premium ou Free selon le tier
                    if user_tier == UserTier.PREMIUM:
                        # Expériences détaillées
                        cv_data["experiences"] = experiences if 'experiences' in locals() else []
                        
                        # Formations détaillées
                        cv_data["educations"] = educations if 'educations' in locals() else []
                        
                        # Compétences par catégories
                        cv_data["skills"] = {
                            "technical": technical_skills if 'technical_skills' in locals() else "",
                            "business": business_skills if 'business_skills' in locals() else "",
                            "soft": soft_skills if 'soft_skills' in locals() else ""
                        }
                        
                        # Langues avec niveaux
                        cv_data["languages"] = []
                        if 'lang1' in locals() and lang1:
                            cv_data["languages"].append({"language": lang1, "level": level1})
                        if 'lang2' in locals() and lang2:
                            cv_data["languages"].append({"language": lang2, "level": level2})
                        if 'lang3' in locals() and lang3:
                            cv_data["languages"].append({"language": lang3, "level": level3})
                        
                        # Réalisations et projets
                        cv_data["achievements"] = achievements if 'achievements' in locals() else ""
                        cv_data["projects"] = projects if 'projects' in locals() else ""
                        
                    else:
                        # Version gratuite - données simples
                        cv_data["experience_description"] = experience_description if 'experience_description' in locals() else ""
                        cv_data["education_level"] = education_level if 'education_level' in locals() else ""
                        cv_data["education_field"] = education_field if 'education_field' in locals() else ""
                        cv_data["main_skills"] = main_skills if 'main_skills' in locals() else ""
                    
                    # Génération avec progress
                    generate_cv_with_progress(cv_data, gemini_client, display_generated_cv_secure_func, event_helper)
                    
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


def render_template_selector():
    """Sélecteur de templates CV avec preview"""
    
    templates = [
        {"name": "🎨 Moderne", "desc": "Design épuré, parfait pour Tech/Startup"},
        {"name": "📋 Classique", "desc": "Format traditionnel, idéal pour entreprises"},
        {"name": "🎯 ATS-Optimisé", "desc": "Maximise le passage des filtres automatiques"}
    ]
    
    cols = st.columns(len(templates))
    
    for i, template in enumerate(templates):
        with cols[i]:
            if st.button(
                f"{template['name']}\n{template['desc']}", 
                key=f"template_{i}",
                use_container_width=True
            ):
                st.session_state.selected_template = template['name']
                st.success(f"✅ Template {template['name']} sélectionné")


def generate_cv_with_progress(cv_data: Dict[str, Any], gemini_client, display_func, event_helper):
    """Génération CV avec barre de progression"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Étape 1: Validation
        status_text.text("🔍 Validation des données...")
        progress_bar.progress(25)
        time.sleep(0.5)
        
        # Étape 2: Génération IA
        status_text.text("🤖 Génération IA en cours...")
        progress_bar.progress(50)
        
        if gemini_client:
            enhanced_content = gemini_client.generate_content_secure("cv_enhancement", cv_data)
            cv_data["enhanced_summary"] = enhanced_content
        
        progress_bar.progress(75)
        
        # Étape 3: Finalisation
        status_text.text("✨ Finalisation du CV...")
        progress_bar.progress(100)
        
        # Sauvegarde
        st.session_state.current_cv_data = cv_data
        
        status_text.text("✅ CV généré avec succès!")
        time.sleep(1)
        
        # Nettoyage UI
        progress_bar.empty()
        status_text.empty()
        
        st.success("🎉 Votre CV est prêt!")
        st.balloons()
        
        # Affichage
        display_func(cv_data)
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Erreur lors de la génération: {str(e)}")


def render_cv_preview(cv_data: Dict[str, Any]):
    """Preview du CV généré"""
    
    st.markdown("### 👀 Aperçu de votre CV")
    
    with st.container():
        st.markdown(f"**{cv_data.get('full_name', 'Nom')}**")
        st.markdown(f"📧 {cv_data.get('email', 'email@example.com')}")
        st.markdown(f"🎯 **Objectif:** {cv_data.get('target_job', 'Poste visé')}")
        
        if cv_data.get('enhanced_summary'):
            st.markdown("**Profil professionnel:**")
            st.markdown(cv_data['enhanced_summary'])


def render_template_gallery():
    """Galerie de templates CV"""
    
    st.markdown("### 🎨 Galerie de Templates")
    st.info("💡 Choisissez un template adapté à votre secteur d'activité")
    
    st.write("Templates disponibles prochainement...")


def render_cv_history():
    """Historique des CV créés"""
    
    st.markdown("### 📊 Mes CV")
    st.info("💼 Retrouvez tous vos CV générés")
    
    st.write("Historique disponible prochainement...")


def get_remaining_generations(user_tier) -> int:
    """Calcule les générations restantes selon le tier"""
    from phoenix_cv.models.phoenix_user import UserTier
    
    if user_tier == UserTier.PREMIUM:
        return -1  # Illimité
    return max(0, 3 - st.session_state.get("cv_generated_this_month", 0))


def download_cv_pdf(cv_data: Dict[str, Any]):
    """Téléchargement CV en PDF"""
    
    st.download_button(
        label="📥 Télécharger en PDF",
        data="CV content placeholder",
        file_name=f"CV_{cv_data.get('full_name', 'Phoenix')}.pdf",
        mime="application/pdf"
    )


def analyze_ats_score(cv_data: Dict[str, Any]) -> int:
    """Analyse du score ATS"""
    
    # Score basique basé sur les champs remplis
    score = 0
    required_fields = ['full_name', 'email', 'target_job']
    
    for field in required_fields:
        if cv_data.get(field):
            score += 25
    
    return min(score, 100)
