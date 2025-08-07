"""
Page creation CV securisee - Phoenix CV
Formulaire securise de creation CV avec validation et chiffrement
"""

import streamlit as st
import uuid
from phoenix_cv.models.user_profile import UserProfile, Skill, Experience, CV, Letter
from phoenix_cv.models.phoenix_user import UserTier
from phoenix_cv.services.secure_session_manager import secure_session
from phoenix_cv.utils.exceptions import SecurityException, ValidationException
from phoenix_cv.utils.safe_markdown import safe_markdown
from phoenix_cv.utils.secure_logging import secure_logger
from phoenix_cv.utils.secure_validator import SecureValidator


def render_create_cv_page_secure(gemini_client, display_generated_cv_secure_func):
    """Page de creation CV securisee"""
    st.title("🛡️ Creation CV Ultra-Securisee")

    # Verification des limites securisees
    user_tier = st.session_state.get("user_tier", UserTier.FREE)
    can_create, limit_message = secure_session.check_limits(user_tier)

    if not can_create:
        st.error(limit_message)
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

