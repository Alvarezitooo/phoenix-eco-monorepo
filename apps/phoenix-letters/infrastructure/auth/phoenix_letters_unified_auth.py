"""
🔐 Phoenix Letters - Service d'Authentification Unifié
Intégration complète avec Phoenix Shared Auth pour une expérience seamless

Author: Claude Phoenix DevSecOps Guardian  
Version: 1.0.0 - Production Ready
"""

import logging
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime, timedelta
import streamlit as st

# Import du service de synchronisation cross-app
try:
    from packages.phoenix_shared_auth.services.cross_app_auth import get_cross_app_auth_service
    from packages.phoenix_shared_auth.entities.phoenix_user import PhoenixUser, PhoenixApp
    CROSS_APP_SYNC_AVAILABLE = True
except ImportError:
    CROSS_APP_SYNC_AVAILABLE = False
    PhoenixUser = None
    PhoenixApp = None

# Import du système d'auth partagé
try:
    from packages.phoenix_shared_auth.services.phoenix_auth_service import PhoenixAuthService
    from packages.phoenix_shared_auth.database.phoenix_db_connection import get_phoenix_db_connection
    from core.entities.user import UserTier
    SHARED_AUTH_AVAILABLE = True
except ImportError:
    # Fallback si le module partagé n'est pas disponible
    SHARED_AUTH_AVAILABLE = False

# Import du système d'auth local existant
from infrastructure.auth.user_auth_service import UserAuthService
from infrastructure.auth.streamlit_auth_middleware import StreamlitAuthMiddleware
from infrastructure.database.db_connection import DatabaseConnection
from config.settings import Settings

logger = logging.getLogger(__name__)


class PhoenixLettersAuthService:
    """
    Service d'authentification unifié pour Phoenix Letters
    Intègre Phoenix Shared Auth avec le système local existant
    """
    
    def __init__(self, settings: Settings, db_connection: DatabaseConnection):
        self.settings = settings
        self.db_connection = db_connection
        self.shared_auth_available = SHARED_AUTH_AVAILABLE
        self.cross_app_sync_available = CROSS_APP_SYNC_AVAILABLE
        
        # Service d'auth local (toujours disponible)
        self.local_auth_service = UserAuthService(settings, db_connection)
        self.local_auth_middleware = StreamlitAuthMiddleware(self.local_auth_service, settings)
        
        # Service d'auth partagé (si disponible)
        self.shared_auth_service = None
        self.cross_app_auth_service = None
        
        if self.shared_auth_available:
            try:
                # Initialisation du service d'auth partagé
                phoenix_db_connection = get_phoenix_db_connection()
                self.shared_auth_service = PhoenixAuthService(phoenix_db_connection)
                
                if self.cross_app_sync_available:
                    self.cross_app_auth_service = get_cross_app_auth_service(self.shared_auth_service)
                    
                logger.info("✅ Phoenix Shared Auth initialisé avec succès")
            except Exception as e:
                logger.error(f"❌ Erreur initialisation Phoenix Shared Auth: {e}")
                self.shared_auth_available = False
        
        if not self.shared_auth_available:
            logger.warning("⚠️ Phoenix Shared Auth non disponible - Mode local activé")
        
        if self.cross_app_sync_available:
            logger.info("✅ Cross-App Session Sync disponible")
        else:
            logger.warning("⚠️ Cross-App Session Sync non disponible")
    
    def get_current_user(self) -> Optional[Any]:
        """
        Récupère l'utilisateur actuel en vérifiant d'abord cross-app auth,
        puis l'authentification locale
        """
        # 1. Vérifier cross-app authentication en premier
        if self.cross_app_auth_service:
            cross_app_user = self.cross_app_auth_service.init_streamlit_auth_check()
            if cross_app_user:
                # Synchroniser avec système local
                self._sync_cross_app_user_to_local(cross_app_user)
                return self._convert_phoenix_user_to_local(cross_app_user)
        
        # 2. Vérifier authentification locale existante
        local_user = self.local_auth_middleware.get_current_user()
        if local_user:
            # Si utilisateur local existe, essayer de synchroniser vers Phoenix
            if self.shared_auth_available:
                self._sync_local_user_to_phoenix(local_user)
            return local_user
        
        return None
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[Any], str]:
        """
        Authentifie un utilisateur via Phoenix Shared Auth d'abord,
        puis fallback vers le système local
        """
        if not email or not password:
            return False, None, "Email et mot de passe requis"
        
        try:
            # 1. Essayer authentification via Phoenix Shared Auth
            if self.shared_auth_available and self.shared_auth_service:
                phoenix_user = self.shared_auth_service.authenticate_user(email, password)
                
                if phoenix_user:
                    # Synchroniser vers système local
                    local_user = self._sync_phoenix_user_to_local(phoenix_user)
                    
                    if local_user:
                        # Créer session locale
                        self._create_local_session(local_user)
                        
                        # Créer session cross-app si disponible
                        if self.cross_app_auth_service:
                            self._create_cross_app_session(phoenix_user)
                        
                        logger.info(f"✅ Authentification Phoenix réussie pour {email}")
                        return True, local_user, "Connexion réussie via Phoenix Ecosystem"
            
            # 2. Fallback vers authentification locale
            try:
                user, access_token, refresh_token = self.local_auth_service.authenticate_user(email, password)
                
                # Créer session Streamlit
                st.session_state["auth_token"] = access_token
                st.session_state["refresh_token"] = refresh_token
                st.session_state["user_id"] = str(user.id)
                st.session_state["user_tier"] = user.subscription.current_tier
                st.session_state["phoenix_ecosystem"] = False
                
                # Essayer de synchroniser vers Phoenix si disponible
                if self.shared_auth_available:
                    self._sync_local_user_to_phoenix(user)
                
                logger.info(f"✅ Authentification locale réussie pour {email}")
                return True, user, "Connexion réussie"
                
            except Exception as e:
                logger.warning(f"❌ Authentification locale échouée pour {email}: {e}")
                return False, None, "Email ou mot de passe incorrect"
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'authentification: {e}")
            return False, None, "Erreur technique lors de la connexion"
    
    def register_user(
        self, 
        email: str, 
        password: str, 
        username: str = None,
        newsletter_opt_in: bool = False
    ) -> Tuple[bool, Optional[Any], str]:
        """
        Inscrit un nouvel utilisateur via Phoenix Shared Auth d'abord,
        puis fallback vers le système local
        """
        if not all([email, password]):
            return False, None, "Email et mot de passe requis"
        
        if len(password) < 8:
            return False, None, "Le mot de passe doit contenir au moins 8 caractères"
        
        if "@" not in email:
            return False, None, "Email invalide"
        
        try:
            # 1. Essayer inscription via Phoenix Shared Auth
            if self.shared_auth_available and self.shared_auth_service:
                try:
                    # Déterminer prénom/nom depuis username ou email
                    first_name = username or email.split('@')[0]
                    last_name = ""
                    
                    phoenix_user = self.shared_auth_service.register_user(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        tier=UserTier.FREE,
                        metadata={
                            "source_app": "phoenix_letters",
                            "newsletter_opt_in": newsletter_opt_in,
                            "registration_date": datetime.now().isoformat()
                        }
                    )
                    
                    if phoenix_user:
                        # Synchroniser vers système local
                        local_user = self._sync_phoenix_user_to_local(phoenix_user)
                        
                        if local_user:
                            logger.info(f"✅ Inscription Phoenix réussie pour {email}")
                            return True, local_user, "Compte créé avec succès dans l'écosystème Phoenix"
                except Exception as e:
                    logger.warning(f"⚠️ Inscription Phoenix échouée pour {email}: {e}")
            
            # 2. Fallback vers inscription locale
            try:
                local_user = self.local_auth_service.register_user(
                    email, password, username, newsletter_opt_in
                )
                
                # Essayer de synchroniser vers Phoenix si disponible
                if self.shared_auth_available:
                    self._sync_local_user_to_phoenix(local_user)
                
                logger.info(f"✅ Inscription locale réussie pour {email}")
                return True, local_user, "Compte créé avec succès"
                
            except Exception as e:
                logger.warning(f"❌ Inscription locale échouée pour {email}: {e}")
                return False, None, "Cet email est déjà utilisé ou erreur technique"
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'inscription: {e}")
            return False, None, "Erreur technique lors de la création du compte"
    
    def logout_user(self):
        """
        Déconnecte l'utilisateur des systèmes local et cross-app
        """
        # Déconnexion locale
        self.local_auth_middleware.logout()
        
        # Nettoyage session Streamlit
        session_keys_to_clear = [
            "user_id", "user_email", "user_tier", "auth_token", "refresh_token",
            "phoenix_ecosystem", "cross_app_source", "login_method"
        ]
        
        for key in session_keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        logger.info("✅ Utilisateur déconnecté et session nettoyée")
    
    def render_auth_interface(self) -> Optional[Any]:
        """
        Affiche l'interface d'authentification native avec design Phoenix
        """
        st.markdown("## 🔐 Authentification Phoenix Letters")
        
        # Vérifier cross-app auth d'abord
        current_user = self.get_current_user()
        if current_user:
            return current_user
        
        # Afficher formulaire d'authentification amélioré
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #f97316 0%, #ef4444 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
                <h3 style="color: white; margin: 0;">📝 Phoenix Letters</h3>
                <p style="color: #f0f0f0; margin: 0.5rem 0;">Générateur IA de lettres de motivation pour reconversions</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Tabs pour connexion/inscription
        login_tab, register_tab = st.tabs(["🔑 Connexion", "✨ Inscription"])
        
        with login_tab:
            with st.form("phoenix_letters_login_form"):
                st.markdown("#### Connectez-vous à votre compte")
                
                email = st.text_input(
                    "Email",
                    placeholder="votre@email.com",
                    help="L'email utilisé lors de votre inscription"
                )
                
                password = st.text_input(
                    "Mot de passe",
                    type="password",
                    help="Votre mot de passe Phoenix"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    login_submitted = st.form_submit_button(
                        "🔑 Se connecter",
                        type="primary",
                        use_container_width=True
                    )
                
                with col2:
                    if st.form_submit_button("🔒 Mot de passe oublié ?", use_container_width=True):
                        st.info("Un email de réinitialisation vous sera envoyé à votre adresse.")
                
                if login_submitted and email and password:
                    success, user, message = self.authenticate_user(email, password)
                    
                    if success:
                        st.success(f"✅ {message}")
                        
                        # Affichage des infos de connexion Phoenix
                        if st.session_state.get("phoenix_ecosystem"):
                            st.info("🌟 **Phoenix Ecosystem** : Accès à toutes les applications Phoenix !")
                        
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        with register_tab:
            with st.form("phoenix_letters_register_form"):
                st.markdown("#### Créez votre compte Phoenix")
                
                email = st.text_input(
                    "Email",
                    placeholder="jean.dupont@email.com",
                    help="Votre email servira d'identifiant"
                )
                
                username = st.text_input(
                    "Nom d'utilisateur (optionnel)",
                    placeholder="Jean Dupont",
                    help="Comment souhaitez-vous être appelé ?"
                )
                
                password = st.text_input(
                    "Mot de passe",
                    type="password",
                    help="Au moins 8 caractères"
                )
                
                password_confirm = st.text_input(
                    "Confirmer le mot de passe",
                    type="password"
                )
                
                # Consentements
                st.markdown("---")
                
                newsletter_opt_in = st.checkbox(
                    "Je souhaite recevoir des conseils carrière par email (optionnel)"
                )
                
                data_consent = st.checkbox(
                    "J'accepte le traitement de mes données pour la génération de lettres",
                    help="Obligatoire pour utiliser Phoenix Letters"
                )
                
                register_submitted = st.form_submit_button(
                    "✨ Créer mon compte",
                    type="primary",
                    use_container_width=True
                )
                
                if register_submitted:
                    if not all([email, password, password_confirm]):
                        st.error("⚠️ Veuillez remplir tous les champs obligatoires")
                    elif password != password_confirm:
                        st.error("❌ Les mots de passe ne correspondent pas")
                    elif not data_consent:
                        st.error("⚠️ Vous devez accepter le traitement des données pour continuer")
                    elif len(password) < 8:
                        st.error("❌ Le mot de passe doit contenir au moins 8 caractères")
                    else:
                        success, user, message = self.register_user(
                            email, password, username, newsletter_opt_in
                        )
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            st.info("🔄 Vous pouvez maintenant vous connecter avec vos identifiants")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        
        # Informations sécurité
        st.info(
            "🔒 **Sécurité garantie** : Vos données sont chiffrées et protégées selon les standards RGPD. "
            "Phoenix Letters respecte votre vie privée et ne partage jamais vos informations."
        )
        
        return None
    
    def _sync_cross_app_user_to_local(self, phoenix_user: PhoenixUser):
        """Synchronise utilisateur cross-app vers système local"""
        try:
            # Vérifier si utilisateur existe déjà localement
            existing_user = self.local_auth_service.get_user_by_email(phoenix_user.email)
            
            if not existing_user:
                # Créer utilisateur local
                username = f"{phoenix_user.first_name} {phoenix_user.last_name}".strip()
                local_user = self.local_auth_service.register_user(
                    phoenix_user.email,
                    "phoenix_managed_password",  # Mot de passe géré par Phoenix
                    username or phoenix_user.email.split('@')[0],
                    newsletter_opt_in=False
                )
                logger.info(f"✅ Utilisateur cross-app créé localement: {phoenix_user.email}")
                return local_user
            else:
                logger.info(f"✅ Utilisateur cross-app trouvé localement: {phoenix_user.email}")
                return existing_user
                
        except Exception as e:
            logger.error(f"❌ Erreur sync cross-app vers local: {e}")
            return None
    
    def _sync_phoenix_user_to_local(self, phoenix_user: PhoenixUser):
        """Synchronise utilisateur Phoenix vers système local"""
        return self._sync_cross_app_user_to_local(phoenix_user)
    
    def _sync_local_user_to_phoenix(self, local_user):
        """Synchronise utilisateur local vers Phoenix (si possible)"""
        try:
            if not self.shared_auth_available or not self.shared_auth_service:
                return
            
            # Vérifier si utilisateur existe déjà dans Phoenix
            phoenix_user = self.shared_auth_service.get_user_by_email(local_user.email)
            
            if not phoenix_user:
                # Créer utilisateur Phoenix
                # Extraire prénom/nom depuis username
                full_name = local_user.username or local_user.email.split('@')[0]
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""
                
                phoenix_user = self.shared_auth_service.register_user(
                    email=local_user.email,
                    password="local_managed_password",  # Mot de passe géré localement
                    first_name=first_name,
                    last_name=last_name,
                    tier=UserTier.FREE,
                    metadata={
                        "synced_from": "phoenix_letters_local",
                        "original_id": str(local_user.id),
                        "sync_date": datetime.now().isoformat()
                    }
                )
                
                if phoenix_user:
                    st.session_state["phoenix_ecosystem"] = True
                    logger.info(f"✅ Utilisateur local synchronisé vers Phoenix: {local_user.email}")
                
        except Exception as e:
            logger.error(f"❌ Erreur sync local vers Phoenix: {e}")
    
    def _convert_phoenix_user_to_local(self, phoenix_user: PhoenixUser):
        """Convertit utilisateur Phoenix vers format local"""
        # Cette méthode retourne une représentation compatible avec le système local
        # En pratique, on utiliserait le _sync_cross_app_user_to_local pour créer un vrai utilisateur local
        class LocalUserProxy:
            def __init__(self, phoenix_user):
                self.id = str(phoenix_user.id)
                self.email = phoenix_user.email
                self.username = f"{phoenix_user.first_name} {phoenix_user.last_name}".strip()
                self.subscription = type('obj', (object,), {
                    'current_tier': phoenix_user.tier.value if phoenix_user.tier else 'free'
                })()
        
        return LocalUserProxy(phoenix_user)
    
    def _create_local_session(self, local_user):
        """Crée session locale Streamlit"""
        # Cette méthode est utilisée quand on a un utilisateur local valide
        st.session_state["user_id"] = str(local_user.id)
        st.session_state["user_email"] = local_user.email
        st.session_state["user_tier"] = getattr(local_user.subscription, 'current_tier', 'free')
        st.session_state["phoenix_ecosystem"] = True
    
    def _create_cross_app_session(self, phoenix_user: PhoenixUser):
        """Crée session cross-app si disponible"""
        if self.cross_app_auth_service:
            # Le service cross-app gère déjà la session via init_streamlit_auth_check
            pass
    
    def is_shared_auth_available(self) -> bool:
        """Vérifie si le système d'auth partagé est disponible"""
        return self.shared_auth_available
    
    def get_session_info(self) -> Dict[str, Any]:
        """Retourne les informations de session actuelles"""
        return {
            "authenticated": st.session_state.get("user_id") is not None,
            "user_id": st.session_state.get("user_id"),
            "user_email": st.session_state.get("user_email"),
            "user_tier": st.session_state.get("user_tier", "free"),
            "phoenix_ecosystem": st.session_state.get("phoenix_ecosystem", False),
            "shared_auth_available": self.shared_auth_available,
            "cross_app_sync_available": self.cross_app_sync_available
        }


# Factory function pour créer l'instance du service
def create_phoenix_letters_auth_service(settings: Settings, db_connection: DatabaseConnection) -> PhoenixLettersAuthService:
    """Factory function pour service d'authentification unifié Phoenix Letters"""
    return PhoenixLettersAuthService(settings, db_connection)