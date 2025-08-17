"""
🚀 Phoenix Streamlit Auth Middleware - Authentification Streamlit Unifiée
Middleware pour intégrer l'authentification Phoenix dans les apps Streamlit
"""

import json
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import streamlit as st

from phoenix_shared_authentities.phoenix_user import PhoenixApp, PhoenixUser
from phoenix_shared_authservices.phoenix_auth_service import PhoenixAuthService


class PhoenixStreamlitAuth:
    """
    Middleware d'authentification Phoenix pour applications Streamlit
    Gère la session, les formulaires et la navigation
    """

    def __init__(self, auth_service: PhoenixAuthService, app_name: PhoenixApp):
        """
        Initialise le middleware Streamlit

        Args:
            auth_service: Service d'authentification Phoenix
            app_name: Nom de l'application Phoenix (Letters, CV, Rise)
        """
        self.auth_service = auth_service
        self.app_name = app_name

        # Clés de session Streamlit
        self.SESSION_KEYS = {
            "user": f"phoenix_user_{app_name.value}",
            "authenticated": f"phoenix_authenticated_{app_name.value}",
            "access_token": f"phoenix_access_token_{app_name.value}",
            "refresh_token": f"phoenix_refresh_token_{app_name.value}",
            "auth_state": f"phoenix_auth_state_{app_name.value}",
        }

    def require_auth(self, page_func: Callable) -> Callable:
        """
        Décorateur pour protéger une page avec authentification

        Args:
            page_func: Fonction de page Streamlit à protéger

        Returns:
            Callable: Fonction protégée
        """

        def wrapper(*args, **kwargs):
            if self.is_authenticated():
                return page_func(*args, **kwargs)
            else:
                self.render_auth_page()

        return wrapper

    def is_authenticated(self) -> bool:
        """
        Vérifie si l'utilisateur est authentifié

        Returns:
            bool: True si authentifié
        """
        return st.session_state.get(self.SESSION_KEYS["authenticated"], False)

    def get_current_user(self) -> Optional[PhoenixUser]:
        """
        Récupère l'utilisateur courant de la session

        Returns:
            Optional[PhoenixUser]: Utilisateur ou None
        """
        if not self.is_authenticated():
            return None

        user_data = st.session_state.get(self.SESSION_KEYS["user"])
        if user_data:
            # L'utilisateur est stocké comme dict dans la session
            return self._deserialize_user(user_data)

        return None

    def login_user(self, email: str, password: str) -> bool:
        """
        Connecte un utilisateur

        Args:
            email: Email de l'utilisateur
            password: Mot de passe

        Returns:
            bool: True si connexion réussie
        """
        try:
            user, access_token, refresh_token = self.auth_service.authenticate_user(
                email=email, password=password, app=self.app_name
            )

            # Stocker dans la session Streamlit
            st.session_state[self.SESSION_KEYS["user"]] = self._serialize_user(user)
            st.session_state[self.SESSION_KEYS["authenticated"]] = True
            st.session_state[self.SESSION_KEYS["access_token"]] = access_token
            st.session_state[self.SESSION_KEYS["refresh_token"]] = refresh_token
            st.session_state[self.SESSION_KEYS["auth_state"]] = "logged_in"

            st.success(f"✅ Connexion réussie ! Bienvenue {user.display_name}")
            st.rerun()
            return True

        except Exception as e:
            st.error(f"❌ Erreur de connexion: {e}")
            return False

    def register_user(
        self,
        email: str,
        password: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        newsletter_opt_in: bool = False,
    ) -> bool:
        """
        Enregistre un nouvel utilisateur

        Args:
            email: Email de l'utilisateur
            password: Mot de passe
            username: Nom d'utilisateur optionnel
            first_name: Prénom optionnel
            last_name: Nom optionnel
            newsletter_opt_in: Consentement newsletter

        Returns:
            bool: True si inscription réussie
        """
        try:
            user = self.auth_service.register_user(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
                newsletter_opt_in=newsletter_opt_in,
                source_app=self.app_name,
            )

            st.success(f"✅ Inscription réussie ! Bienvenue {user.display_name}")

            # Connexion automatique après inscription
            return self.login_user(email, password)

        except Exception as e:
            st.error(f"❌ Erreur d'inscription: {e}")
            return False

    def logout_user(self) -> None:
        """
        Déconnecte l'utilisateur courant
        """
        # Nettoyer la session
        for key in self.SESSION_KEYS.values():
            if key in st.session_state:
                del st.session_state[key]

        st.session_state[self.SESSION_KEYS["auth_state"]] = "logged_out"
        st.success("✅ Déconnexion réussie !")
        st.rerun()

    def render_auth_page(self) -> None:
        """
        Affiche la page d'authentification (connexion/inscription)
        """
        st.title(f"🔐 Phoenix {self.app_name.value.title()} - Authentification")

        # Tabs pour connexion/inscription
        login_tab, register_tab = st.tabs(["🔑 Connexion", "📝 Inscription"])

        with login_tab:
            self._render_login_form()

        with register_tab:
            self._render_register_form()

    def _render_login_form(self) -> None:
        """Affiche le formulaire de connexion"""
        st.subheader("🔑 Connexion")

        with st.form("phoenix_login_form"):
            email = st.text_input("📧 Email", key="login_email")
            password = st.text_input(
                "🔒 Mot de passe", type="password", key="login_password"
            )

            col1, col2 = st.columns([1, 3])

            with col1:
                submit = st.form_submit_button("🚀 Se connecter", type="primary")

            with col2:
                if st.form_submit_button("🆔 Mode Invité"):
                    self._enable_guest_mode()

            if submit and email and password:
                self.login_user(email, password)

    def _render_register_form(self) -> None:
        """Affiche le formulaire d'inscription"""
        st.subheader("📝 Inscription")

        with st.form("phoenix_register_form"):
            col1, col2 = st.columns(2)

            with col1:
                first_name = st.text_input("👤 Prénom", key="reg_first_name")
                email = st.text_input("📧 Email", key="reg_email")

            with col2:
                last_name = st.text_input("👤 Nom", key="reg_last_name")
                username = st.text_input(
                    "🏷️ Nom d'utilisateur (optionnel)", key="reg_username"
                )

            password = st.text_input(
                "🔒 Mot de passe", type="password", key="reg_password"
            )
            password_confirm = st.text_input(
                "🔒 Confirmer mot de passe", type="password", key="reg_password_confirm"
            )

            newsletter_opt_in = st.checkbox(
                "📧 Recevoir la newsletter Phoenix", key="reg_newsletter"
            )

            submit = st.form_submit_button("✨ S'inscrire", type="primary")

            if submit:
                if not email or not password:
                    st.error("❌ Email et mot de passe requis")
                elif password != password_confirm:
                    st.error("❌ Les mots de passe ne correspondent pas")
                elif len(password) < 6:
                    st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
                else:
                    self.register_user(
                        email=email,
                        password=password,
                        username=username if username else None,
                        first_name=first_name if first_name else None,
                        last_name=last_name if last_name else None,
                        newsletter_opt_in=newsletter_opt_in,
                    )

    def _enable_guest_mode(self) -> None:
        """Active le mode invité"""
        # Créer un utilisateur invité temporaire
        guest_user_data = {
            "id": f'guest_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            "email": "guest@phoenix.local",
            "display_name": "Invité",
            "is_guest": True,
        }

        st.session_state[self.SESSION_KEYS["user"]] = guest_user_data
        st.session_state[self.SESSION_KEYS["authenticated"]] = True
        st.session_state[self.SESSION_KEYS["auth_state"]] = "guest_mode"

        st.success("🆔 Mode invité activé ! Fonctionnalités limitées.")
        st.rerun()

    def _serialize_user(self, user: PhoenixUser) -> Dict[str, Any]:
        """Sérialise un utilisateur pour la session Streamlit"""
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "display_name": user.display_name,
            "is_premium": user.is_premium,
            "current_tier": user.subscription.current_tier.value,
            "enabled_apps": [app.value for app in user.subscription.enabled_apps],
            "created_at": user.created_at.isoformat(),
            "is_guest": False,
        }

    def _deserialize_user(self, user_data: Dict[str, Any]) -> PhoenixUser:
        """Désérialise un utilisateur depuis la session Streamlit"""
        # Simplification pour la session - reconstruire depuis la DB si besoin complet
        from uuid import UUID

        from phoenix_shared_authentities.phoenix_user import PhoenixSubscription, UserTier

        # Si c'est un invité, créer un objet simple
        if user_data.get("is_guest"):
            return type(
                "GuestUser",
                (),
                {
                    "id": user_data["id"],
                    "email": user_data["email"],
                    "display_name": user_data["display_name"],
                    "is_guest": True,
                    "is_premium": False,
                },
            )()

        # Sinon reconstruire un PhoenixUser minimal
        subscription = PhoenixSubscription(
            current_tier=UserTier(user_data.get("current_tier", "free"))
        )

        user = PhoenixUser(
            id=UUID(user_data["id"]),
            email=user_data["email"],
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            subscription=subscription,
        )

        return user
