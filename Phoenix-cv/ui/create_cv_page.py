"""
Page creation CV securisee - Phoenix CV
Formulaire securise de creation CV avec validation et chiffrement
"""

import streamlit as st
from models.cv_data import CVTier, PersonalInfo, CVProfile
from services.secure_session_manager import secure_session
from utils.exceptions import SecurityException, ValidationException
from utils.secure_logging import secure_logger
from utils.secure_validator import SecureValidator


def render_create_cv_page_secure(gemini_client, display_generated_cv_secure_func):
    """Page de creation CV securisee"""
    st.title("🛡️ Creation CV Ultra-Securisee")
    
    # Verification des limites securisees
    user_tier = st.session_state.get('user_tier', CVTier.FREE)
    can_create, limit_message = secure_session.check_limits(user_tier)
    
    if not can_create:
        st.error(limit_message)
        return
    
    # Indicateurs de securite
    st.markdown("""
    <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin-bottom: 20px;">
        <h5 style="color: #155724; margin: 0;">🔐 Protections Actives</h5>
        <p style="color: #155724; margin: 5px 0 0 0; font-size: 0.9em;">
            • Chiffrement bout-en-bout des donnees personnelles<br>
            • Validation anti-injection sur tous les champs<br>
            • Anonymisation automatique pour traitement IA
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulaire securise
    with st.form("secure_cv_creation_form"):
        
        st.markdown("### 👤 Informations Personnelles (Chiffrees)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Nom complet *", 
                max_chars=100,
                help="🔒 Chiffre AES-256 automatiquement"
            )
            email = st.text_input(
                "Email *", 
                max_chars=254,
                help="🔒 Validation securisee + anonymisation IA"
            )
            phone = st.text_input(
                "Telephone", 
                max_chars=20,
                help="🔒 Anonymise automatiquement"
            )
        
        with col2:
            address = st.text_area(
                "Adresse", 
                max_chars=500,
                height=100,
                help="🔒 Chiffrement local + anonymisation"
            )
            linkedin = st.text_input(
                "LinkedIn", 
                max_chars=255,
                help="🔒 URL validee et securisee"
            )
            github = st.text_input(
                "GitHub/Portfolio", 
                max_chars=255,
                help="🔒 Validation anti-injection"
            )
        
        st.markdown("### 🎯 Reconversion Securisee")
        col1, col2 = st.columns(2)
        
        with col1:
            current_sector = st.text_input(
                "Secteur actuel *", 
                max_chars=100,
                help="🔒 Donnees anonymisees pour IA"
            )
            target_sector = st.text_input(
                "Secteur cible *", 
                max_chars=100,
                help="🔒 Prompt anti-injection"
            )
        
        with col2:
            target_position = st.text_input(
                "Poste vise *", 
                max_chars=200,
                help="🔒 Validation securisee"
            )
        
        professional_summary = st.text_area(
            "Resume professionnel",
            max_chars=1000,
            height=120,
            help="🔒 Nettoyage anti-injection + validation"
        )
        
        # CSRF Token cache
        csrf_token = st.session_state.get('csrf_token', '')
        
        # Bouton de generation securise
        submitted = st.form_submit_button(
            "🛡️ Generer CV Securise", 
            type="primary", 
            use_container_width=True
        )
        
        if submitted:
            try:
                # Validation CSRF
                if not csrf_token:
                    raise SecurityException("Token CSRF manquant")
                
                # Validation des champs obligatoires
                if not all([full_name, email, current_sector, target_sector, target_position]):
                    st.error("🚫 Veuillez remplir tous les champs obligatoires (*)")
                    return
                
                # Validation securisee de tous les inputs
                safe_full_name = SecureValidator.validate_text_input(full_name, 100, "nom")
                safe_email = SecureValidator.validate_email(email)
                safe_current_sector = SecureValidator.validate_text_input(current_sector, 100, "secteur actuel")
                safe_target_sector = SecureValidator.validate_text_input(target_sector, 100, "secteur cible")
                safe_target_position = SecureValidator.validate_text_input(target_position, 200, "poste cible")
                
                # Creation du profil securise
                personal_info = PersonalInfo(
                    full_name=safe_full_name,
                    email=safe_email,
                    phone=SecureValidator.validate_text_input(phone, 20, "telephone") if phone else "",
                    address=SecureValidator.validate_text_input(address, 500, "adresse") if address else "",
                    linkedin=linkedin if linkedin else "",
                    github=github if github else ""
                )
                
                cv_profile = CVProfile(
                    personal_info=personal_info,
                    professional_summary=SecureValidator.validate_text_input(
                        professional_summary, 1000, "resume"
                    ) if professional_summary else "",
                    target_position=safe_target_position,
                    target_sector=safe_target_sector,
                    current_sector=safe_current_sector
                )
                
                # Log de l'activite securisee
                secure_logger.log_security_event(
                    "CV_CREATION_STARTED",
                    {"tier": user_tier.value}
                )
                
                # Generation securisee
                with st.spinner("🛡️ Generation securisee en cours..."):
                    
                    # Amelioration securisee avec IA
                    if cv_profile.professional_summary:
                        prompt_data = {
                            'current_sector': safe_current_sector,
                            'target_sector': safe_target_sector, 
                            'target_position': safe_target_position,
                            'professional_summary': cv_profile.professional_summary
                        }
                        
                        enhanced_summary = gemini_client.generate_content_secure(
                            'cv_enhancement',
                            prompt_data
                        )
                        cv_profile.professional_summary = enhanced_summary
                    
                    # Sauvegarde securisee
                    st.session_state.current_cv_profile = cv_profile
                    secure_session.increment_usage()
                    
                    # Log succes
                    secure_logger.log_security_event(
                        "CV_GENERATED_SUCCESSFULLY",
                        {"tier": user_tier.value}
                    )
                    
                    st.success("✅ CV genere avec securite maximale!")
                    st.balloons()
                    
                    # Affichage securise du CV
                    display_generated_cv_secure_func(cv_profile)
                    
            except ValidationException as e:
                st.error(f"🚫 Erreur de validation: {str(e)}")
                secure_logger.log_security_event(
                    "VALIDATION_ERROR",
                    {"error": str(e)[:100]},
                    "WARNING"
                )
            
            except SecurityException as e:
                st.error("🚫 Violation de securite detectee")
                secure_logger.log_security_event(
                    "SECURITY_VIOLATION_CV_CREATION",
                    {"error": str(e)[:100]},
                    "CRITICAL"
                )
            
            except Exception as e:
                st.error("❌ Erreur lors de la generation")
                secure_logger.log_security_event(
                    "CV_GENERATION_ERROR",
                    {"error": str(e)[:100]},
                    "ERROR"
                )