"""
🔐 Phoenix CV Authentication Manager
Gestionnaire d'authentification centralisé et sécurisé pour Phoenix CV
"""

import logging
import streamlit as st
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Imports directs depuis packages/ - Architecture Monorepo
from packages.phoenix_shared_auth.client import AuthManager as PhoenixAuthManager
from packages.phoenix_shared_auth.stripe_manager import StripeManager


logger = logging.getLogger(__name__)


@dataclass
class CVAuthenticatedUser:
    """Représentation d'un utilisateur authentifié Phoenix CV"""

    id: str
    email: str
    user_tier: str = "FREE"  # FREE, PREMIUM
    access_token: Optional[str] = None
    subscription_status: Optional[str] = None
    customer_id: Optional[str] = None


class PhoenixCVAuthManager:
    """Gestionnaire d'authentification pour Phoenix CV"""

    def __init__(self):
        self.auth_manager = PhoenixAuthManager()
        self.logger = logging.getLogger(__name__)

    def render_login_page(self) -> None:
        """Affiche la page de connexion/inscription CV"""
        # Import local pour éviter circulaire
        from ui_components import PhoenixCVUIComponents

        # En-tête élégant
        PhoenixCVUIComponents.render_login_form_header()

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            self._render_login_container()

        # Pied de page sécurité
        PhoenixCVUIComponents.render_security_footer()

    def _render_login_container(self) -> None:
        """Affiche le container de connexion CV"""
        st.markdown(
            """
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
            backdrop-filter: blur(10px);
        ">
        """,
            unsafe_allow_html=True,
        )

        # Section connexion
        st.markdown(
            """
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h3 style="color: #1e293b; margin: 0; font-weight: 600;">
                ✨ Accédez à votre espace CV
            </h3>
            <p style="color: #64748b; margin-top: 0.5rem; font-size: 0.95rem;">
                Créez et gérez vos CV professionnels
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        self._render_login_form()

        # Séparateur
        st.markdown("---")

        # Section inscription
        self._render_signup_section()

        # Fermeture du container
        st.markdown("</div>", unsafe_allow_html=True)

    def _render_login_form(self) -> None:
        """Affiche le formulaire de connexion"""
        email = st.text_input(
            "📧 Adresse e-mail",
            key="cv_login_email",
            placeholder="votre.email@exemple.com",
            help="Utilisez l'email de votre compte Phoenix",
        )
        password = st.text_input(
            "🔒 Mot de passe",
            type="password",
            key="cv_login_password",
            placeholder="Votre mot de passe sécurisé",
            help="Votre mot de passe reste privé et sécurisé",
        )

        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button(
                "🚀 Se connecter à Phoenix CV",
                key="cv_login_btn",
                type="primary",
                use_container_width=True,
            ):
                self._handle_login(email, password)

    def _handle_login(self, email: str, password: str) -> None:
        """Gère la connexion utilisateur"""
        if not email or not password:
            st.error(
                "✋ Merci de remplir tous les champs pour accéder à votre espace CV."
            )
            return

        try:
            success, message, user_id, access_token = self.auth_manager.sign_in(
                email, password
            )
            if success:
                self._store_user_session(user_id, email, access_token)
                st.success(
                    f"🎉 Bienvenue dans Phoenix CV, {email.split('@')[0]} ! Créons votre CV parfait."
                )
                st.rerun()
            else:
                st.error(
                    f"😔 Connexion impossible : {message}. Vérifiez vos identifiants."
                )
        except Exception as e:
            self.logger.error(f"Erreur connexion CV: {e}")
            st.error(
                f"😕 Une erreur technique est survenue. Réessayez dans quelques instants."
            )

    def _render_signup_section(self) -> None:
        """Affiche la section d'inscription"""
        st.markdown(
            """
        <div style="text-align: center; margin: 2rem 0; padding: 1.5rem; 
                   background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
                   border-radius: 15px; border-left: 4px solid #3b82f6;">
            <h4 style="color: #1e40af; margin: 0 0 0.5rem 0;">
                ✨ Nouveau sur Phoenix CV ?
            </h4>
            <p style="color: #1e3a8a; margin: 0; font-size: 0.95rem;">
                Créez votre compte et boostez votre carrière
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        new_email = st.text_input(
            "📧 Votre adresse e-mail",
            key="cv_signup_email",
            placeholder="nom.prenom@exemple.com",
            help="Utilisez une adresse e-mail valide",
        )
        new_password = st.text_input(
            "🔐 Créez un mot de passe sécurisé",
            type="password",
            key="cv_signup_password",
            placeholder="Minimum 8 caractères",
            help="Un mot de passe fort protège vos CV",
        )

        col_signup1, col_signup2, col_signup3 = st.columns([1, 2, 1])
        with col_signup2:
            if st.button(
                "🌟 Créer mon compte Phoenix CV",
                key="cv_signup_btn",
                use_container_width=True,
            ):
                self._handle_signup(new_email, new_password)

    def _handle_signup(self, email: str, password: str) -> None:
        """Gère l'inscription utilisateur"""
        if not email or not password:
            st.error(
                "🤔 Merci de remplir tous les champs pour créer votre compte Phoenix CV."
            )
            return

        try:
            success, message, user_id = self.auth_manager.sign_up(email, password)
            if success:
                st.session_state.cv_user_id = user_id
                st.session_state.cv_user_email = email
                st.session_state.cv_is_authenticated = True
                st.session_state.cv_user_tier = "FREE"
                st.success(
                    f"🎊 Excellent ! Votre compte Phoenix CV est créé, {email.split('@')[0]}. Créons votre premier CV !"
                )
                st.rerun()
            else:
                st.error(f"🚫 Inscription impossible : {message}")
        except Exception as e:
            self.logger.error(f"Erreur inscription CV: {e}")
            st.error(
                f"😓 Une erreur technique est survenue. Réessayez plus tard."
            )

    def _store_user_session(
        self, user_id: str, email: str, access_token: Optional[str]
    ) -> None:
        """Stocke les informations utilisateur en session"""
        st.session_state.cv_user_id = user_id
        st.session_state.cv_user_email = email
        st.session_state.cv_access_token = access_token
        st.session_state.cv_is_authenticated = True
        st.session_state.cv_user_tier = "FREE"  # Par défaut

    def get_current_user(self) -> Optional[CVAuthenticatedUser]:
        """Récupère l'utilisateur actuellement connecté"""
        if not st.session_state.get("cv_is_authenticated", False):
            return None

        return CVAuthenticatedUser(
            id=st.session_state.get("cv_user_id"),
            email=st.session_state.get("cv_user_email"),
            user_tier=st.session_state.get("cv_user_tier", "FREE"),
            access_token=st.session_state.get("cv_access_token"),
            subscription_status=st.session_state.get("cv_subscription_status"),
            customer_id=st.session_state.get("cv_customer_id"),
        )

    def logout(self) -> None:
        """Déconnecte l'utilisateur"""
        # Nettoyage de la session CV
        keys_to_clear = [
            "cv_user_id",
            "cv_user_email",
            "cv_access_token",
            "cv_is_authenticated",
            "cv_user_tier",
            "cv_subscription_status",
            "cv_customer_id",
        ]

        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        st.success("👋 Vous êtes maintenant déconnecté de Phoenix CV. À bientôt !")
        st.rerun()

    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié"""
        return st.session_state.get("cv_is_authenticated", False)

    def is_premium_user(self) -> bool:
        """Vérifie si l'utilisateur est Premium"""
        return st.session_state.get("cv_user_tier") == "PREMIUM"