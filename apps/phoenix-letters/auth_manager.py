"""
🔐 Phoenix Letters Authentication Manager
Gestionnaire d'authentification centralisé et sécurisé
"""

import logging
import streamlit as st
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Imports directs depuis packages/ - Architecture Monorepo
from packages.phoenix_shared_auth.client import AuthManager as PhoenixAuthManager  
from packages.phoenix_shared_auth.stripe_manager import StripeManager
from core.entities.user import UserTier
from core.services.subscription_service import SubscriptionService
from utils.async_runner import AsyncServiceRunner


logger = logging.getLogger(__name__)


@dataclass
class AuthenticatedUser:
    """Représentation d'un utilisateur authentifié"""

    id: str
    email: str
    user_tier: UserTier
    access_token: Optional[str] = None
    subscription_status: Optional[str] = None
    customer_id: Optional[str] = None


class PhoenixLettersAuthManager:
    """Gestionnaire d'authentification pour Phoenix Letters"""

    def __init__(self):
        self.auth_manager = PhoenixAuthManager()
        self.logger = logging.getLogger(__name__)

    def render_login_page(
        self,
        subscription_service: Optional[SubscriptionService] = None,
        async_runner: Optional[AsyncServiceRunner] = None,
    ) -> None:
        """Affiche la page de connexion/inscription"""
        # Import local pour éviter circulaire
        from ui_components import PhoenixUIComponents

        # En-tête élégant
        PhoenixUIComponents.render_login_form_header()

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            self._render_login_container(subscription_service, async_runner)

        # Pied de page sécurité
        PhoenixUIComponents.render_security_footer()

    def _render_login_container(
        self,
        subscription_service: Optional[SubscriptionService],
        async_runner: Optional[AsyncServiceRunner],
    ) -> None:
        """Affiche le container de connexion"""
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
                ✨ Connectez-vous à votre espace
            </h3>
            <p style="color: #64748b; margin-top: 0.5rem; font-size: 0.95rem;">
                Prêt(e) à créer des lettres qui marquent les esprits ?
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        self._render_login_form(subscription_service, async_runner)

        # Séparateur
        st.markdown("---")

        # Section inscription
        self._render_signup_section()

        # Fermeture du container
        st.markdown("</div>", unsafe_allow_html=True)

    def _render_login_form(
        self,
        subscription_service: Optional[SubscriptionService],
        async_runner: Optional[AsyncServiceRunner],
    ) -> None:
        """Affiche le formulaire de connexion"""
        email = st.text_input(
            "📧 Adresse e-mail",
            key="login_email",
            placeholder="votre.email@exemple.com",
            help="Utilisez l'email de votre compte Phoenix",
        )
        password = st.text_input(
            "🔒 Mot de passe",
            type="password",
            key="login_password",
            placeholder="Votre mot de passe sécurisé",
            help="Votre mot de passe reste privé et sécurisé",
        )

        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button(
                "🚀 Se connecter à Phoenix",
                key="login_btn",
                type="primary",
                use_container_width=True,
            ):
                self._handle_login(email, password, subscription_service, async_runner)

    def _handle_login(
        self,
        email: str,
        password: str,
        subscription_service: Optional[SubscriptionService],
        async_runner: Optional[AsyncServiceRunner],
    ) -> None:
        """Gère la connexion utilisateur"""
        if not email or not password:
            st.error(
                "✋ Merci de remplir tous les champs pour continuer votre aventure Phoenix."
            )
            return

        try:
            success, message, user_id, access_token = self.auth_manager.sign_in(
                email, password
            )
            if success:
                self._store_user_session(user_id, email, access_token)
                self._load_user_subscription(
                    user_id, subscription_service, async_runner
                )
                st.success(
                    f"🎉 Bienvenue dans votre espace Phoenix, {email.split('@')[0]} ! Votre créativité n'attend plus que vous."
                )
                st.rerun()
            else:
                st.error(
                    f"😔 Connexion impossible : {message}. Vérifiez vos identifiants et réessayez."
                )
        except Exception as e:
            self.logger.error(f"Erreur connexion: {e}")
            st.error(
                f"😕 Une erreur inattendue est survenue. Notre équipe Phoenix travaille à la résoudre : {e}"
            )

    def _render_signup_section(self) -> None:
        """Affiche la section d'inscription"""
        st.markdown(
            """
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
        """,
            unsafe_allow_html=True,
        )

        new_email = st.text_input(
            "📧 Votre adresse e-mail",
            key="signup_email",
            placeholder="nom.prenom@exemple.com",
            help="Utilisez une adresse e-mail valide pour recevoir vos confirmations",
        )
        new_password = st.text_input(
            "🔐 Créez un mot de passe sécurisé",
            type="password",
            key="signup_password",
            placeholder="Minimum 8 caractères",
            help="Un bon mot de passe protège votre créativité",
        )

        col_signup1, col_signup2, col_signup3 = st.columns([1, 2, 1])
        with col_signup2:
            if st.button(
                "🌟 Créer mon compte Phoenix",
                key="signup_btn",
                use_container_width=True,
            ):
                self._handle_signup(new_email, new_password)

    def _handle_signup(self, email: str, password: str) -> None:
        """Gère l'inscription utilisateur"""
        if not email or not password:
            st.error(
                "🤔 Merci de remplir tous les champs pour créer votre compte Phoenix."
            )
            return

        try:
            success, message, user_id = self.auth_manager.sign_up(email, password)
            if success:
                st.session_state.user_id = user_id
                st.session_state.user_email = email
                st.session_state.is_authenticated = True
                st.session_state.user_tier = (
                    UserTier.FREE
                )  # Nouveau compte est Free par défaut
                st.success(
                    f"🎊 Fantastique ! Votre compte Phoenix est créé, {email.split('@')[0]}. Vous pouvez maintenant déployer vos ailes créatives !"
                )
                st.rerun()
            else:
                st.error(
                    f"🚫 Inscription impossible : {message}. Peut-être que ce compte existe déjà ?"
                )
        except Exception as e:
            self.logger.error(f"Erreur inscription: {e}")
            st.error(
                f"😓 Une erreur technique est survenue. Notre équipe Phoenix y travaille : {e}"
            )

    def _store_user_session(
        self, user_id: str, email: str, access_token: Optional[str]
    ) -> None:
        """Stocke les informations utilisateur en session"""
        st.session_state.user_id = user_id
        st.session_state.user_email = email
        st.session_state.access_token = access_token
        st.session_state.is_authenticated = True

    def _load_user_subscription(
        self,
        user_id: str,
        subscription_service: Optional[SubscriptionService],
        async_runner: Optional[AsyncServiceRunner],
    ) -> None:
        """Charge les informations d'abonnement utilisateur"""
        try:
            if async_runner and subscription_service:
                future = async_runner.run_coro_in_thread(
                    subscription_service.get_user_subscription(user_id)
                )
                subscription = future.result(timeout=10)
                if subscription:
                    st.session_state.user_tier = subscription.current_tier
                    self.logger.info(
                        f"Subscription trouvée - User ID: {user_id} - Tier: {subscription.current_tier.value}"
                    )
                else:
                    st.session_state.user_tier = UserTier.FREE
                    self.logger.warning(
                        f"Aucun abonnement trouvé pour user_id: {user_id} - Tier FREE attribué"
                    )
            else:
                st.session_state.user_tier = UserTier.FREE  # Fallback
                self.logger.warning(
                    "Services d'abonnement non disponibles - Tier FREE attribué"
                )
        except Exception as e:
            st.session_state.user_tier = UserTier.FREE
            self.logger.error(
                f"Erreur récupération subscription pour user_id {user_id}: {e}"
            )

    def get_current_user(self) -> Optional[AuthenticatedUser]:
        """Récupère l'utilisateur actuellement connecté"""
        if not st.session_state.get("is_authenticated", False):
            return None

        return AuthenticatedUser(
            id=st.session_state.get("user_id"),
            email=st.session_state.get("user_email"),
            user_tier=st.session_state.get("user_tier", UserTier.FREE),
            access_token=st.session_state.get("access_token"),
            subscription_status=st.session_state.get("subscription_status"),
            customer_id=st.session_state.get("customer_id"),
        )

    def logout(self) -> None:
        """Déconnecte l'utilisateur"""
        # Nettoyage de la session
        keys_to_clear = [
            "user_id",
            "user_email",
            "access_token",
            "is_authenticated",
            "user_tier",
            "subscription_status",
            "customer_id",
        ]

        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        st.success("👋 Vous êtes maintenant déconnecté. À bientôt sur Phoenix !")
        st.rerun()

    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié"""
        return st.session_state.get("is_authenticated", False)

    def is_premium_user(self) -> bool:
        """Vérifie si l'utilisateur est Premium"""
        return st.session_state.get("user_tier") == UserTier.PREMIUM

    def render_admin_debug_panel(self) -> None:
        """Affiche le panneau debug admin (temporaire)"""
        current_user = self.get_current_user()
        if not current_user:
            return

        with st.expander("🔧 Admin Debug (temporaire)", expanded=False):
            if st.button("🔧 [ADMIN] Forcer upgrade vers Premium", type="secondary"):
                try:
                    import os

                    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
                    if not service_role_key:
                        st.error("❌ SUPABASE_SERVICE_ROLE_KEY manquante")
                        return

                    from phoenix_shared_auth.client import get_supabase_client

                    admin_client = get_supabase_client()

                    admin_subscription = {
                        "user_id": current_user.id,
                        "current_tier": "premium",
                    }

                    response = (
                        admin_client.table("user_subscriptions")
                        .upsert(admin_subscription)
                        .execute()
                    )
                    st.success(f"✅ Upgrade Premium réussi ! Response: {response.data}")
                    st.info("🔄 Rechargez la page pour voir le changement.")

                except Exception as e:
                    st.error(f"❌ Erreur upgrade admin: {e}")
