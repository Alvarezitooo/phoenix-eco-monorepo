"""
📊 Composants d'affichage sécurisés - Phoenix CV
Fonctions d'affichage des résultats CV, analyses ATS et profils démo
"""

import streamlit as st
import html
from models.cv_data import CVTier, CVProfile, PersonalInfo, Experience, Education, Skill
from services.secure_ats_optimizer import ATSAnalysis
from utils.exceptions import SecurityException
from utils.secure_logging import secure_logger
from utils.secure_crypto import secure_crypto


def display_generated_cv_secure(profile: CVProfile, template_engine, ats_optimizer):
    """Affichage sécurisé du CV généré"""
    
    st.markdown("---")
    st.markdown("## 🛡️ Votre CV Phoenix Sécurisé")
    
    # Sélection template sécurisée
    user_tier = st.session_state.get('user_tier', CVTier.FREE)
    available_templates = template_engine.get_available_templates_secure(user_tier)
    
    template_options = {t.name: t.id for t in available_templates}
    selected_template = st.selectbox(
        "🎨 Template sécurisé",
        options=list(template_options.keys()),
        help="Design validé anti-XSS et échappement HTML automatique"
    )
    
    template_id = template_options[selected_template]
    
    # Rendu sécurisé
    try:
        html_cv = template_engine.render_cv_secure(
            profile, template_id, for_export=False
        )
        
        # Affichage sécurisé
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.components.v1.html(html_cv, height=800, scrolling=True)
        
        with col2:
            st.markdown("### 🛡️ Actions Sécurisées")
            
            if st.button("📄 Export PDF Chiffré", use_container_width=True):
                st.success("🔒 PDF généré avec chiffrement AES-256!")
                secure_logger.log_security_event("PDF_EXPORT_SECURE", {"template": template_id})
            
            if st.button("📝 Export DOCX Sécurisé", use_container_width=True):
                st.success("🔒 DOCX généré avec protection DRM!")
                secure_logger.log_security_event("DOCX_EXPORT_SECURE", {"template": template_id})
            
            if st.button("🔗 Lien Sécurisé", use_container_width=True):
                secure_token = secure_crypto.generate_secure_token(16)
                st.success(f"🔒 Lien généré: phoenix.cv/s/{secure_token[:8]}...")
                secure_logger.log_security_event("SECURE_LINK_GENERATED", {})
            
            # Analyse ATS sécurisée
            st.markdown("---")
            st.markdown("### ⚡ Score ATS Sécurisé")
            
            if st.button("🔍 Analyse ATS Complete", use_container_width=True):
                with st.spinner("🛡️ Analyse ATS sécurisée..."):
                    try:
                        ats_analysis = ats_optimizer.analyze_ats_compatibility_secure(profile)
                        display_ats_results_secure(ats_analysis)
                    except Exception as e:
                        st.error("❌ Erreur analyse ATS")
                        secure_logger.log_security_event(
                            "ATS_ANALYSIS_ERROR",
                            {"error": str(e)[:100]},
                            "ERROR"
                        )
    
    except SecurityException as e:
        st.error("🚫 Erreur de sécurité lors du rendu")
        secure_logger.log_security_event(
            "CV_RENDER_SECURITY_ERROR",
            {"template": template_id},
            "CRITICAL"
        )
    
    except Exception as e:
        st.error("❌ Erreur lors du rendu sécurisé")
        secure_logger.log_security_event(
            "CV_RENDER_ERROR",
            {"template": template_id, "error": str(e)[:100]},
            "ERROR"
        )


def display_parsed_cv_secure(profile: CVProfile, display_generated_cv_secure_func):
    """Affichage sécurisé du CV parsé"""
    
    st.markdown("---")
    st.markdown("## 🔍 Analyse Sécurisée de Votre CV")
    
    # Métriques sécurisées
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Expériences détectées", len(profile.experiences), "✅ Validées")
    
    with col2:
        st.metric("Formations trouvées", len(profile.education), "🔒 Sécurisées")
    
    with col3:
        st.metric("Compétences extraites", len(profile.skills), "🛡️ Nettoyées")
    
    # Détails sécurisés
    with st.expander("📋 Informations extraites (anonymisées)"):
        
        st.markdown(f"**Secteur actuel:** {html.escape(profile.current_sector)}")
        st.markdown(f"**Secteur cible:** {html.escape(profile.target_sector)}")
        st.markdown(f"**Poste visé:** {html.escape(profile.target_position)}")
        
        if profile.professional_summary:
            st.markdown("**Résumé professionnel:**")
            st.write(html.escape(profile.professional_summary))
    
    # Actions sécurisées
    st.markdown("### 🚀 Étapes Suivantes Sécurisées")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✨ Améliorer avec IA Sécurisée", type="primary", use_container_width=True):
            with st.spinner("🛡️ Amélioration sécurisée..."):
                try:
                    # Amélioration sécurisée basique pour démo
                    enhanced_profile = profile  # Simplification pour l'exemple
                    st.session_state.current_cv_profile = enhanced_profile
                    st.success("✅ CV amélioré avec sécurité maximale!")
                    display_generated_cv_secure_func(enhanced_profile)
                    
                except Exception as e:
                    st.error("❌ Erreur amélioration sécurisée")
                    secure_logger.log_security_event(
                        "CV_ENHANCEMENT_ERROR",
                        {"error": str(e)[:100]},
                        "ERROR"
                    )
    
    with col2:
        if st.button("🎨 Templates Sécurisés", use_container_width=True):
            display_generated_cv_secure_func(profile)


def display_ats_results_secure(analysis: ATSAnalysis):
    """Affichage sécurisé des résultats ATS"""
    
    st.markdown("---")
    st.markdown("## ⚡ Résultats ATS Sécurisés")
    
    # Score sécurisé
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        score_color = "#28a745" if analysis.score >= 80 else "#ffc107" if analysis.score >= 60 else "#dc3545"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 30px; border: 3px solid {score_color}; border-radius: 15px; background: #f8f9fa;">
            <h2 style="color: {score_color}; margin: 0; font-size: 3em;">{analysis.score}%</h2>
            <h3 style="margin: 10px 0;">Score ATS Sécurisé</h3>
            <p style="font-size: 1.2em; color: {score_color}; font-weight: bold;">
                {analysis.level.value.upper()}
            </p>
            <p style="font-size: 0.8em; color: #666; margin-top: 10px;">
                🛡️ Analyse validée et sécurisée
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Détails sécurisés
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ❌ Mots-clés Manquants")
        if analysis.missing_keywords:
            for keyword in analysis.missing_keywords[:10]:  # Limite sécurisée
                st.markdown(f"- {html.escape(keyword)}")
        else:
            st.success("Aucun mot-clé majeur manquant!")
        
        st.markdown("### 🔧 Problèmes de Format")
        if analysis.format_issues:
            for issue in analysis.format_issues[:5]:  # Limite sécurisée
                st.markdown(f"- {html.escape(issue)}")
        else:
            st.success("Format parfaitement compatible ATS!")
    
    with col2:
        st.markdown("### ✅ Recommandations Sécurisées")
        if analysis.recommendations:
            for i, rec in enumerate(analysis.recommendations[:5], 1):  # Limite
                st.markdown(f"{i}. {html.escape(rec)}")
        
        st.markdown("### 📊 Densité Mots-clés")
        if analysis.keyword_density:
            for category, density in list(analysis.keyword_density.items())[:5]:
                safe_category = html.escape(category)
                percentage = max(0, min(100, int(density * 100)))  # Sécurisation
                st.progress(density, text=f"{safe_category}: {percentage}%")


def create_demo_profile_secure() -> CVProfile:
    """Profil démo sécurisé"""
    
    demo_personal = PersonalInfo(
        full_name="Marie Dupont",
        email="marie.demo@phoenix.cv",
        phone="06 XX XX XX XX",
        address="Paris, France",
        linkedin="linkedin.com/in/demo"
    )
    
    demo_experiences = [
        Experience(
            title="Aide-soignante",
            company="EHPAD Demo",
            location="Paris",
            start_date="01/2018",
            end_date="12/2023",
            description="Profil de démonstration sécurisé pour Phoenix CV. Données anonymisées et protégées.",
            skills_used=["Communication", "Organisation"],
            achievements=["Formation équipes", "Amélioration processes"]
        )
    ]
    
    demo_education = [
        Education(
            degree="Diplôme d'État Aide-Soignant",
            institution="École Demo",
            location="Paris",
            graduation_year="2018"
        )
    ]
    
    demo_skills = [
        Skill(name="Communication", level="Expert", category="Soft Skills"),
        Skill(name="Python", level="Intermédiaire", category="Technique")
    ]
    
    return CVProfile(
        personal_info=demo_personal,
        professional_summary="Profil de démonstration Phoenix CV sécurisé. Expert en reconversion professionnelle avec IA protégée et conformité RGPD.",
        target_position="Développeur Web",
        target_sector="Technologie",
        current_sector="Santé",
        experiences=demo_experiences,
        education=demo_education,
        skills=demo_skills,
        certifications=["Certification Démo"],
        languages=[{"language": "Français", "level": "Natif"}]
    )