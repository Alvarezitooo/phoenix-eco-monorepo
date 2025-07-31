"""
Page upload CV securisee - Phoenix CV
Import et analyse securisee de CV existants avec validation et scanning
"""

import streamlit as st
from config.security_config import SecurityConfig
from services.secure_file_handler import SecureFileHandler
from utils.exceptions import SecurityException
from utils.secure_logging import secure_logger
from utils.secure_validator import SecureValidator
from utils.rate_limiter import rate_limiter


def render_upload_cv_page_secure(cv_parser, display_parsed_cv_secure_func):
    """Page d'import CV ultra-securisee"""
    
    st.title("📁 Import CV Ultra-Securise")
    
    # Avertissements de securite
    st.markdown("""
    <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin-bottom: 20px;">
        <h5 style="color: #856404; margin: 0;">🛡️ Protections Upload Actives</h5>
        <p style="color: #856404; margin: 5px 0 0 0; font-size: 0.9em;">
            • Scan malware automatique • Validation type MIME • Anonymisation PII • Limite taille 10MB
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    Uploadez votre CV pour une analyse securisee et une optimisation professionnelle.
    
    **Formats autorises:** PDF, DOCX, TXT uniquement  
    **Taille maximum:** 10MB (validation stricte)  
    **Securite:** Scan automatique + anonymisation
    """)
    
    # Rate limiting affiche
    remaining = rate_limiter.get_remaining_requests(
        st.session_state.get('secure_session_id', 'anon'),
        SecurityConfig.FILE_UPLOADS_PER_HOUR, 
        3600
    )
    
    st.info(f"🚦 Uploads restants: {remaining}/{SecurityConfig.FILE_UPLOADS_PER_HOUR} par heure")
    
    uploaded_file = st.file_uploader(
        "🔒 Choisissez votre CV (Upload Securise)",
        type=['pdf', 'docx', 'txt'],
        help="Fichier analyse automatiquement par notre systeme de securite",
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        
        # Lecture securisee
        try:
            file_content = uploaded_file.read()
            
            # Validation securisee complete
            is_valid, message = SecureFileHandler.validate_file_secure(
                file_content, uploaded_file.name
            )
            
            if not is_valid:
                st.error(f"🚫 {message}")
                secure_logger.log_security_event(
                    "FILE_UPLOAD_REJECTED",
                    {"filename": uploaded_file.name[:50], "reason": message},
                    "WARNING"
                )
                return
            
            st.success(f"✅ Fichier valide et securise: {uploaded_file.name}")
            
            # Analyse securisee
            if st.button("🔍 Analyser Mon CV (Securise)", type="primary"):
                
                with st.spinner("🛡️ Analyse securisee en cours..."):
                    try:
                        # Extraction securisee du texte
                        if uploaded_file.name.endswith('.pdf'):
                            cv_text = cv_parser.extract_text_from_pdf_secure(file_content)
                        elif uploaded_file.name.endswith('.docx'):
                            cv_text = cv_parser.extract_text_from_docx_secure(file_content)
                        else:  # txt
                            cv_text = SecureValidator.validate_text_input(
                                file_content.decode('utf-8'), 50000, "contenu fichier TXT"
                            )
                        
                        # Parsing securise avec IA
                        parsed_profile = cv_parser.parse_cv_with_ai_secure(cv_text)
                        
                        st.session_state.current_cv_profile = parsed_profile
                        
                        st.success("✅ CV analyse avec securite maximale!")
                        
                        # Affichage des resultats securises
                        display_parsed_cv_secure_func(parsed_profile)
                        
                    except SecurityException as e:
                        st.error("🚫 Violation de securite lors de l'analyse")
                        secure_logger.log_security_event(
                            "CV_ANALYSIS_SECURITY_VIOLATION",
                            {"filename": uploaded_file.name[:50]},
                            "CRITICAL"
                        )
                    
                    except Exception as e:
                        st.error("❌ Erreur lors de l'analyse securisee")
                        secure_logger.log_security_event(
                            "CV_ANALYSIS_ERROR",
                            {"filename": uploaded_file.name[:50], "error": str(e)[:100]},
                            "ERROR"
                        )
        
        except Exception as e:
            st.error("🚫 Erreur lors de la lecture du fichier")
            secure_logger.log_security_event(
                "FILE_READ_ERROR",
                {"filename": uploaded_file.name[:50], "error": str(e)[:100]},
                "ERROR"
            )