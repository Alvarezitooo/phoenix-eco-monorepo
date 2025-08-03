"""
Module UI pour l'authentification des utilisateurs (connexion et inscription).

Ce module fournit les fonctions Streamlit pour afficher les formulaires
de connexion et d'inscription, et interagit avec le service d'authentification.
"""

import streamlit as st
from services.auth_service import AuthService


def render_auth_ui(auth_service: AuthService):
    """Affiche l'interface de connexion/inscription avec un style amélioré."""

    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 3.5rem; color: #333; margin-bottom: 0.5rem;">🦋 Phoenix Rise</h1>
            <p style="font-size: 1.2rem; color: #555;">Votre coach de carrière IA pour une reconversion réussie</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
            .stTabs [data-baseweb="tab-list"] {
                justify-content: center;
            }
            .stTabs [data-baseweb="tab"] {
                font-size: 1.1rem;
                font-weight: 600;
                color: #555;
            }
            .stTabs [aria-selected="true"] {
                color: #6a11cb;
            }
            .stForm {
                padding: 2rem;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.9);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                margin-top: 1.5rem;
            }
            .stForm h3 {
                color: #6a11cb;
                margin-bottom: 1.5rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    auth_tab, register_tab = st.tabs(["🔑 Se Connecter", "📝 S'inscrire"])

    with auth_tab:
        with st.form("login_form"):
            st.markdown("### Connectez-vous à votre compte")
            email = st.text_input("Email", placeholder="votre@email.com")
            password = st.text_input(
                "Mot de passe", type="password", placeholder="Votre mot de passe"
            )
            submitted = st.form_submit_button("Se Connecter", use_container_width=True)

            if submitted:
                success, error_message = auth_service.sign_in(email, password)
                if success:
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error(error_message)

    with register_tab:
        with st.form("register_form"):
            st.markdown("### Créez votre compte Phoenix Rise")
            email = st.text_input(
                "Email", key="reg_email", placeholder="votre@email.com"
            )
            password = st.text_input(
                "Mot de passe",
                type="password",
                key="reg_pass",
                placeholder="Minimum 6 caractères",
            )
            confirm_password = st.text_input(
                "Confirmer le mot de passe",
                type="password",
                placeholder="Confirmez votre mot de passe",
            )
            submitted = st.form_submit_button("S'inscrire", use_container_width=True)

            if submitted:
                if password != confirm_password:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    success, error_message = auth_service.sign_up(email, password)
                    if success:
                        st.success(
                            "Inscription réussie ! Vous pouvez maintenant vous connecter."
                        )
                    else:
                        st.error(error_message)
