"""
🔐 Phoenix CV - Service d'Authentification Unifié
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
    from packages.phoenix_shared_auth.services.cross_app_session_sync import session_sync_service, PhoenixApp
    CROSS_APP_SYNC_AVAILABLE = True
except ImportError:
    CROSS_APP_SYNC_AVAILABLE = False
    session_sync_service = None
    PhoenixApp = None

# Import du service d'abonnements granulaires
try:
    from packages.phoenix_shared_auth.services.phoenix_subscription_service import get_phoenix_subscription_service
    from packages.phoenix_shared_auth.entities.phoenix_subscription import SubscriptionTier, PhoenixApp as SubsPhoenixApp
    SUBSCRIPTION_SERVICE_AVAILABLE = True
except ImportError:
    SUBSCRIPTION_SERVICE_AVAILABLE = False
    get_phoenix_subscription_service = None

# Import du système d'auth partagé
try:
    from packages.phoenix_shared_auth.services.phoenix_auth_service import PhoenixAuthService
    from phoenix_cv.models.phoenix_user import PhoenixUser, UserTier
    from packages.phoenix_shared_auth.database.phoenix_db_connection import get_phoenix_db_connection
    SHARED_AUTH_AVAILABLE = True
except ImportError:
    # Fallback si le module partagé n'est pas disponible
    SHARED_AUTH_AVAILABLE = False
    PhoenixUser = None
    UserTier = None

logger = logging.getLogger(__name__)


class PhoenixCVAuthService:
    """
    Service d'authentification unifié pour Phoenix CV
    Intègre Phoenix Shared Auth avec gestion de fallback
    """
    
    def __init__(self):
        self.shared_auth_available = SHARED_AUTH_AVAILABLE
        self.cross_app_sync_available = CROSS_APP_SYNC_AVAILABLE
        self.subscription_service_available = SUBSCRIPTION_SERVICE_AVAILABLE
        self.auth_service = None
        self.subscription_service = None
        
        if self.shared_auth_available:
            try:
                # Initialisation du service d'auth partagé
                db_connection = get_phoenix_db_connection()
                self.auth_service = PhoenixAuthService(db_connection)
                
                # Initialisation du service d'abonnements
                if self.subscription_service_available:
                    self.subscription_service = get_phoenix_subscription_service(db_connection)
                
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
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Authentifie un utilisateur via Phoenix Shared Auth
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe
            
        Returns:
            Tuple[bool, Optional[user_data], str]: (success, user_data, message)
        """
        if not email or not password:
            return False, None, "Email et mot de passe requis"
        
        try:
            if self.shared_auth_available and self.auth_service:
                # Authentification via Shared Auth
                user = self.auth_service.authenticate_user(email, password)
                
                if user:
                    user_data = {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "tier": user.tier.value if user.tier else "free",
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "phoenix_ecosystem": True
                    }
                    
                    # Mise à jour de la session Streamlit
                    self._update_streamlit_session(user_data)
                    
                    # Création session cross-app si disponible
                    if self.cross_app_sync_available and session_sync_service:
                        session_id = session_sync_service.create_unified_session(
                            user_data, PhoenixApp.CV
                        )
                        st.session_state["phoenix_session_id"] = session_id
                    
                    logger.info(f"✅ Authentification réussie pour {email}")
                    return True, user_data, "Connexion réussie"
                else:
                    logger.warning(f"❌ Authentification échouée pour {email}")
                    return False, None, "Email ou mot de passe incorrect"
            
            else:
                # Mode fallback local (démonstration)
                return self._authenticate_local(email, password)
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'authentification: {e}")
            return False, None, "Erreur technique lors de la connexion"
    
    def register_user(
        self, 
        email: str, 
        password: str, 
        first_name: str, 
        last_name: str,
        marketing_consent: bool = False
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Inscrit un nouvel utilisateur via Phoenix Shared Auth
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe
            first_name: Prénom
            last_name: Nom
            marketing_consent: Consentement marketing
            
        Returns:
            Tuple[bool, Optional[user_data], str]: (success, user_data, message)
        """
        if not all([email, password, first_name, last_name]):
            return False, None, "Tous les champs sont requis"
        
        if len(password) < 8:
            return False, None, "Le mot de passe doit contenir au moins 8 caractères"
        
        if "@" not in email:
            return False, None, "Email invalide"
        
        try:
            if self.shared_auth_available and self.auth_service:
                # Inscription via Shared Auth
                user = self.auth_service.register_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    tier=UserTier.FREE,
                    metadata={
                        "source_app": "phoenix_cv",
                        "marketing_consent": marketing_consent,
                        "registration_date": datetime.now().isoformat()
                    }
                )
                
                if user:
                    user_data = {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "tier": user.tier.value,
                        "is_active": user.is_active,
                        "phoenix_ecosystem": True
                    }
                    
                    logger.info(f"✅ Inscription réussie pour {email}")
                    return True, user_data, "Compte créé avec succès"
                else:
                    logger.warning(f"❌ Inscription échouée pour {email}")
                    return False, None, "Cet email est déjà utilisé"
            
            else:
                # Mode fallback local
                return self._register_local(email, password, first_name, last_name, marketing_consent)
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'inscription: {e}")
            return False, None, "Erreur technique lors de la création du compte"
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un utilisateur par son ID
        """
        try:
            if self.shared_auth_available and self.auth_service:
                user = self.auth_service.get_user_by_id(user_id)
                
                if user:
                    return {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "tier": user.tier.value if user.tier else "free",
                        "is_active": user.is_active,
                        "phoenix_ecosystem": True
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération utilisateur {user_id}: {e}")
            return None
    
    def update_user_tier(self, user_id: str, new_tier: str) -> bool:
        """
        Met à jour le tier d'un utilisateur
        """
        try:
            if self.shared_auth_available and self.auth_service:
                tier_enum = UserTier.PREMIUM if new_tier.lower() in ["premium", "pro"] else UserTier.FREE
                success = self.auth_service.update_user_tier(user_id, tier_enum)
                
                if success:
                    # Mise à jour session Streamlit si c'est l'utilisateur actuel
                    if st.session_state.get("user_id") == user_id:
                        st.session_state["user_tier"] = new_tier
                    
                    logger.info(f"✅ Tier mis à jour pour utilisateur {user_id}: {new_tier}")
                    return True
                
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour tier utilisateur {user_id}: {e}")
            return False
    
    def create_guest_session(self) -> Dict[str, Any]:
        """
        Crée une session invité pour utilisation sans compte
        """
        guest_id = f"guest_cv_{int(datetime.now().timestamp())}"
        
        guest_data = {
            "id": guest_id,
            "email": None,
            "first_name": "Invité",
            "last_name": "",
            "tier": "free",
            "is_guest": True,
            "session_expires": (datetime.now() + timedelta(hours=24)).isoformat(),
            "phoenix_ecosystem": False
        }
        
        self._update_streamlit_session(guest_data)
        
        logger.info(f"✅ Session invité créée: {guest_id}")
        return guest_data
    
    def logout_user(self):
        """
        Déconnecte l'utilisateur et nettoie la session
        """
        # Nettoyage de la session Streamlit
        session_keys_to_clear = [
            "user_id", "user_email", "user_first_name", "user_last_name",
            "user_tier", "is_guest", "authenticated", "auth_flow",
            "cv_count_monthly", "phoenix_ecosystem"
        ]
        
        for key in session_keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        logger.info("✅ Utilisateur déconnecté et session nettoyée")
    
    def _update_streamlit_session(self, user_data: Dict[str, Any]):
        """
        Met à jour la session Streamlit avec les données utilisateur
        """
        st.session_state.update({
            "user_id": user_data["id"],
            "user_email": user_data.get("email"),
            "user_first_name": user_data.get("first_name", ""),
            "user_last_name": user_data.get("last_name", ""),
            "user_tier": user_data.get("tier", "free"),
            "is_guest": user_data.get("is_guest", False),
            "authenticated": True,
            "auth_flow": "authenticated",
            "phoenix_ecosystem": user_data.get("phoenix_ecosystem", False)
        })
    
    def _authenticate_local(self, email: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Authentification locale de fallback (démonstration)
        """
        # Comptes de démonstration
        demo_users = {
            "demo@phoenix.com": {
                "password": "demo123",
                "data": {
                    "id": "demo_user_1",
                    "email": "demo@phoenix.com",
                    "first_name": "Demo",
                    "last_name": "User",
                    "tier": "premium",
                    "is_active": True,
                    "phoenix_ecosystem": False
                }
            },
            "test@phoenix.com": {
                "password": "test123",
                "data": {
                    "id": "test_user_1",
                    "email": "test@phoenix.com",
                    "first_name": "Test",
                    "last_name": "Phoenix",
                    "tier": "free",
                    "is_active": True,
                    "phoenix_ecosystem": False
                }
            }
        }
        
        if email in demo_users and demo_users[email]["password"] == password:
            user_data = demo_users[email]["data"]
            self._update_streamlit_session(user_data)
            return True, user_data, "Connexion réussie (mode démonstration)"
        
        return False, None, "Email ou mot de passe incorrect"
    
    def _register_local(
        self, 
        email: str, 
        password: str, 
        first_name: str, 
        last_name: str,
        marketing_consent: bool
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Inscription locale de fallback (démonstration)
        """
        # Simulation d'une base locale
        if not hasattr(st.session_state, "local_users"):
            st.session_state.local_users = {}
        
        if email in st.session_state.local_users:
            return False, None, "Cet email est déjà utilisé"
        
        user_data = {
            "id": f"local_user_{len(st.session_state.local_users) + 1}",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tier": "free",
            "is_active": True,
            "phoenix_ecosystem": False,
            "created_at": datetime.now().isoformat()
        }
        
        # Sauvegarde locale
        st.session_state.local_users[email] = {
            "password": password,  # En prod, serait hashé
            "data": user_data
        }
        
        return True, user_data, "Compte créé avec succès (mode local)"
    
    def is_shared_auth_available(self) -> bool:
        """
        Vérifie si le système d'auth partagé est disponible
        """
        return self.shared_auth_available
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Retourne les informations de session actuelles
        """
        session_info = {
            "authenticated": st.session_state.get("authenticated", False),
            "user_id": st.session_state.get("user_id"),
            "user_email": st.session_state.get("user_email"),
            "user_tier": st.session_state.get("user_tier", "free"),
            "is_guest": st.session_state.get("is_guest", False),
            "phoenix_ecosystem": st.session_state.get("phoenix_ecosystem", False),
            "shared_auth_available": self.shared_auth_available,
            "cross_app_sync_available": self.cross_app_sync_available,
            "subscription_service_available": self.subscription_service_available,
            "phoenix_session_id": st.session_state.get("phoenix_session_id")
        }
        
        # Ajouter informations d'abonnement CV spécifiques
        if session_info["authenticated"] and session_info["user_id"]:
            cv_features = self.get_cv_features(session_info["user_id"])
            session_info["cv_features"] = cv_features
        
        return session_info
    
    def get_cross_app_recommendations(self) -> List[Dict[str, Any]]:
        """
        Récupère les recommandations d'applications basées sur l'activité
        """
        if not self.cross_app_sync_available or not session_sync_service:
            return []
        
        session_id = st.session_state.get("phoenix_session_id")
        if not session_id:
            return []
        
        try:
            activity = session_sync_service.get_user_apps_activity(session_id)
            return activity.get("recommendations", [])
        except Exception as e:
            logger.error(f"❌ Erreur récupération recommandations: {e}")
            return []
    
    def get_cross_app_url(self, target_app: str, path: str = "") -> Optional[str]:
        """
        Génère une URL cross-app avec session
        """
        if not self.cross_app_sync_available or not session_sync_service:
            return None
        
        session_id = st.session_state.get("phoenix_session_id")
        if not session_id:
            return None
        
        try:
            app_enum = None
            if target_app.lower() == "letters":
                app_enum = PhoenixApp.LETTERS
            elif target_app.lower() == "website":
                app_enum = PhoenixApp.WEBSITE
            
            if app_enum:
                return session_sync_service.generate_cross_app_url(
                    session_id, app_enum, path
                )
            
            return None
        except Exception as e:
            logger.error(f"❌ Erreur génération URL cross-app: {e}")
            return None
    
    def update_cv_activity(self, cv_created: bool = False):
        """
        Met à jour l'activité CV dans la session cross-app
        """
        if not self.cross_app_sync_available or not session_sync_service:
            return
        
        session_id = st.session_state.get("phoenix_session_id")
        if not session_id:
            return
        
        try:
            updates = {
                "cross_app_data": {
                    "cv_count": st.session_state.get("cv_count", 0) + (1 if cv_created else 0),
                    "last_cv_activity": datetime.now().isoformat()
                }
            }
            
            session_sync_service.update_session_data(session_id, updates)
            logger.info("✅ Activité CV mise à jour dans session cross-app")
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour activité CV: {e}")
    
    def get_cv_features(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère les fonctionnalités CV disponibles pour un utilisateur
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            Dict contenant les fonctionnalités CV disponibles
        """
        if not self.subscription_service_available or not self.subscription_service:
            # Retour par défaut - fonctionnalités gratuites
            return {
                "cv_count_monthly": 3,
                "templates_count": 5,
                "ats_optimization": False,
                "mirror_match": False,
                "premium_templates": False,
                "trajectory_builder": False,
                "smart_coach_advanced": False,
                "export_formats": ["PDF"],
                "support_level": "email",
                "subscription_tier": "free",
                "is_premium": False
            }
        
        try:
            features = self.subscription_service.get_app_features(user_id, SubsPhoenixApp.CV)
            return features
        except Exception as e:
            logger.error(f"❌ Erreur récupération fonctionnalités CV: {e}")
            # Retour par défaut en cas d'erreur
            return {
                "cv_count_monthly": 3,
                "templates_count": 5,
                "ats_optimization": False,
                "is_premium": False,
                "error": str(e)
            }
    
    def check_cv_feature_access(self, user_id: str, feature: str) -> Tuple[bool, str]:
        """
        Vérifie l'accès à une fonctionnalité CV spécifique
        
        Args:
            user_id: ID utilisateur
            feature: Nom de la fonctionnalité (ex: "ats_optimization", "mirror_match")
            
        Returns:
            Tuple[bool, str]: (accès autorisé, message)
        """
        if not self.subscription_service_available or not self.subscription_service:
            return False, "Service d'abonnements non disponible"
        
        try:
            return self.subscription_service.check_feature_access(user_id, SubsPhoenixApp.CV, feature)
        except Exception as e:
            logger.error(f"❌ Erreur vérification accès feature {feature}: {e}")
            return False, f"Erreur: {str(e)}"
    
    def get_subscription_info(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère les informations d'abonnement détaillées pour l'utilisateur
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            Dict contenant les informations d'abonnement
        """
        if not self.subscription_service_available or not self.subscription_service:
            return {
                "package_type": "free",
                "has_pack_cv_letters": False,
                "subscription_display": {
                    "title": "Phoenix Gratuit",
                    "badge": "GRATUIT",
                    "icon": "🆓"
                }
            }
        
        try:
            user_subscription = self.subscription_service.get_user_subscription(user_id)
            summary = user_subscription.get_subscription_summary()
            
            return {
                "user_id": user_id,
                "package_type": summary.get("package_type", "single_app"),
                "has_pack_cv_letters": summary.get("has_pack_cv_letters", False),
                "premium_apps": summary.get("premium_apps", []),
                "subscription_display": summary.get("subscription_display", {}),
                "cv_is_premium": user_subscription.is_app_premium(SubsPhoenixApp.CV),
                "letters_is_premium": user_subscription.is_app_premium(SubsPhoenixApp.LETTERS),
                "can_upgrade_to_pack": self._can_upgrade_to_pack(user_subscription)
            }
        except Exception as e:
            logger.error(f"❌ Erreur récupération info abonnement: {e}")
            return {"error": str(e)}
    
    def _can_upgrade_to_pack(self, user_subscription) -> bool:
        """Détermine si l'utilisateur peut upgrader vers le pack CV + Letters"""
        try:
            cv_premium = user_subscription.is_app_premium(SubsPhoenixApp.CV)
            letters_premium = user_subscription.is_app_premium(SubsPhoenixApp.LETTERS)
            has_pack = user_subscription.has_pack_cv_letters()
            
            # Peut upgrader si :
            # - Aucun abonnement premium
            # - Un seul abonnement premium (CV ou Letters) mais pas de pack
            # - Deux abonnements séparés qu'on peut consolider en pack
            return not has_pack and (
                (not cv_premium and not letters_premium) or  # Aucun premium
                (cv_premium and not letters_premium) or      # Seulement CV
                (not cv_premium and letters_premium) or      # Seulement Letters
                (cv_premium and letters_premium and not user_subscription.has_pack_cv_letters())  # Deux séparés
            )
        except:
            return True  # Par défaut, permettre l'upgrade


# Instance globale du service d'authentification
phoenix_cv_auth = PhoenixCVAuthService()