"""
🔒 Phoenix Feature Access Control - Middleware de contrôle d'accès
Middleware pour faire respecter les restrictions Premium/Gratuit dans les applications

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import logging
import streamlit as st
from typing import Dict, Any, Callable, Optional, Tuple
from datetime import datetime
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Niveaux d'accès aux fonctionnalités"""
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"


class FeatureAccessControl:
    """
    Contrôleur d'accès aux fonctionnalités basé sur les abonnements
    Gère les restrictions et les paywalls dynamiques
    """
    
    def __init__(self, auth_service):
        self.auth_service = auth_service
        self.usage_tracker = {}
        
    def require_feature_access(self, feature: str, required_level: AccessLevel = AccessLevel.PREMIUM):
        """
        Décorateur pour contrôler l'accès aux fonctionnalités
        
        Args:
            feature: Nom de la fonctionnalité
            required_level: Niveau d'accès requis
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Vérifier authentification
                user_id = st.session_state.get("user_id")
                if not user_id:
                    self._show_login_required()
                    return None
                
                # Vérifier accès à la fonctionnalité
                has_access, message = self._check_feature_access(user_id, feature, required_level)
                
                if has_access:
                    # Incrémenter compteur d'utilisation
                    self._track_usage(user_id, feature)
                    return func(*args, **kwargs)
                else:
                    # Afficher paywall ou limitation
                    self._show_feature_restriction(feature, message, required_level)
                    return None
            
            return wrapper
        return decorator
    
    def check_monthly_limit(self, feature: str, limit: int):
        """
        Décorateur pour vérifier les limites mensuelles
        
        Args:
            feature: Nom de la fonctionnalité
            limit: Limite mensuelle (-1 pour illimité)
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user_id = st.session_state.get("user_id")
                if not user_id:
                    self._show_login_required()
                    return None
                
                # Vérifier limite mensuelle
                current_usage = self._get_monthly_usage(user_id, feature)
                
                if limit == -1 or current_usage < limit:
                    # Incrémenter usage
                    self._increment_usage(user_id, feature)
                    return func(*args, **kwargs)
                else:
                    # Limite atteinte
                    self._show_monthly_limit_reached(feature, limit)
                    return None
            
            return wrapper
        return decorator
    
    def _check_feature_access(self, user_id: str, feature: str, required_level: AccessLevel) -> Tuple[bool, str]:
        """Vérifie l'accès à une fonctionnalité"""
        try:
            # Récupérer informations d'abonnement
            if hasattr(self.auth_service, 'check_cv_feature_access'):
                # Service Phoenix CV
                return self.auth_service.check_cv_feature_access(user_id, feature)
            elif hasattr(self.auth_service, 'check_letters_feature_access'):
                # Service Phoenix Letters
                return self.auth_service.check_letters_feature_access(user_id, feature)
            else:
                # Fallback basique
                user_tier = st.session_state.get("user_tier", "free")
                if required_level == AccessLevel.FREE:
                    return True, "Accès gratuit"
                elif required_level == AccessLevel.PREMIUM and user_tier in ["premium", "pro"]:
                    return True, "Accès Premium"
                else:
                    return False, "Fonctionnalité Premium requise"
                    
        except Exception as e:
            logger.error(f"❌ Erreur vérification accès {feature}: {e}")
            return False, "Erreur technique"
    
    def _track_usage(self, user_id: str, feature: str):
        """Suit l'utilisation des fonctionnalités"""
        try:
            # Obtenir mois actuel
            current_month = datetime.now().strftime("%Y-%m")
            usage_key = f"{user_id}_{feature}_{current_month}"
            
            # Incrémenter compteur en session
            if usage_key not in st.session_state:
                st.session_state[usage_key] = 0
            st.session_state[usage_key] += 1
            
            # Logger usage
            logger.info(f"📊 Usage {feature} pour {user_id}: {st.session_state[usage_key]}")
            
        except Exception as e:
            logger.error(f"❌ Erreur suivi usage: {e}")
    
    def _get_monthly_usage(self, user_id: str, feature: str) -> int:
        """Récupère l'usage mensuel d'une fonctionnalité"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            usage_key = f"{user_id}_{feature}_{current_month}"
            return st.session_state.get(usage_key, 0)
        except:
            return 0
    
    def _increment_usage(self, user_id: str, feature: str):
        """Incrémente l'usage d'une fonctionnalité"""
        self._track_usage(user_id, feature)
    
    def _show_login_required(self):
        """Affiche le message de connexion requise"""
        st.error("🔐 **Connexion requise**")
        st.info("Veuillez vous connecter pour accéder à cette fonctionnalité.")
        
        if st.button("🔑 Se connecter", type="primary"):
            st.session_state.auth_flow = "login"
            st.rerun()
    
    def _show_feature_restriction(self, feature: str, message: str, required_level: AccessLevel):
        """Affiche la restriction d'accès à une fonctionnalité"""
        st.error(f"⭐ **Fonctionnalité Premium : {feature}**")
        st.info(message)
        
        # Suggestions selon le niveau requis
        if required_level == AccessLevel.PREMIUM:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🆓 Version Gratuite")
                st.markdown("- Fonctionnalités de base")
                st.markdown("- Support email")
                st.markdown("- Limites d'usage")
            
            with col2:
                st.markdown("### ⭐ Version Premium")
                st.markdown("- **Fonctionnalités avancées**")
                st.markdown("- **Usage illimité**")
                st.markdown("- **Support prioritaire**")
                
                if st.button("🚀 Passer Premium", type="primary", key=f"upgrade_{feature}"):
                    st.success("🔗 Redirection vers l'abonnement...")
                    # TODO: Intégrer avec Stripe
    
    def _show_monthly_limit_reached(self, feature: str, limit: int):
        """Affiche le message de limite mensuelle atteinte"""
        st.warning(f"⚠️ **Limite mensuelle atteinte : {feature}**")
        st.info(f"Vous avez utilisé vos {limit} utilisations gratuites ce mois-ci.")
        
        # Afficher les options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⏳ Attendre le mois prochain")
            next_reset = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            if next_reset.month == 12:
                next_reset = next_reset.replace(year=next_reset.year + 1, month=1)
            else:
                next_reset = next_reset.replace(month=next_reset.month + 1)
            
            days_until_reset = (next_reset - datetime.now()).days
            st.write(f"⏰ Remise à zéro dans {days_until_reset} jours")
        
        with col2:
            st.markdown("### ⭐ Passer Premium")
            st.write("✨ **Usage illimité immédiatement**")
            
            if st.button("🚀 Débloquer maintenant", type="primary", key=f"unlock_{feature}"):
                st.success("🔗 Redirection vers l'abonnement...")
    
    def render_subscription_status_widget(self):
        """Affiche le widget de statut d'abonnement"""
        user_id = st.session_state.get("user_id")
        if not user_id:
            return
        
        try:
            # Récupérer infos d'abonnement
            if hasattr(self.auth_service, 'get_subscription_info'):
                subscription_info = self.auth_service.get_subscription_info(user_id)
                display_info = subscription_info.get("subscription_display", {})
                
                # Widget de statut
                with st.container():
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col2:
                        st.markdown(
                            f"""
                            <div style="
                                background: {display_info.get('color', '#6b7280')}; 
                                padding: 0.75rem 1.5rem; 
                                border-radius: 25px; 
                                text-align: center; 
                                color: white;
                                margin-bottom: 1rem;
                            ">
                                <strong>{display_info.get('icon', '')} {display_info.get('badge', 'GRATUIT')}</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        if subscription_info.get("package_type") == "pack_cv_letters":
                            st.success("🔥 Pack CV + Letters actif !")
                        elif subscription_info.get("can_upgrade_to_pack"):
                            st.info("💡 Pack CV + Letters disponible")
                
        except Exception as e:
            logger.error(f"❌ Erreur widget abonnement: {e}")
    
    def get_feature_limits_display(self, app_name: str) -> Dict[str, Any]:
        """Récupère les limites de fonctionnalités pour affichage"""
        user_id = st.session_state.get("user_id")
        if not user_id:
            return {}
        
        try:
            # Récupérer features selon l'app
            if app_name == "cv" and hasattr(self.auth_service, 'get_cv_features'):
                features = self.auth_service.get_cv_features(user_id)
            elif app_name == "letters" and hasattr(self.auth_service, 'get_letters_features'):
                features = self.auth_service.get_letters_features(user_id)
            else:
                return {}
            
            # Traitement des limites pour affichage
            limits_display = {}
            
            for feature, value in features.items():
                if isinstance(value, int):
                    if value == -1:
                        limits_display[feature] = {"status": "unlimited", "text": "Illimité", "color": "green"}
                    elif value > 0:
                        current_usage = self._get_monthly_usage(user_id, feature)
                        remaining = max(0, value - current_usage)
                        percentage = (current_usage / value) * 100 if value > 0 else 0
                        
                        if percentage >= 100:
                            status, color = "exhausted", "red"
                        elif percentage >= 80:
                            status, color = "warning", "orange" 
                        else:
                            status, color = "ok", "green"
                            
                        limits_display[feature] = {
                            "status": status,
                            "text": f"{remaining}/{value}",
                            "percentage": percentage,
                            "color": color
                        }
                elif isinstance(value, bool):
                    limits_display[feature] = {
                        "status": "enabled" if value else "disabled",
                        "text": "Activé" if value else "Premium requis",
                        "color": "green" if value else "gray"
                    }
            
            return limits_display
            
        except Exception as e:
            logger.error(f"❌ Erreur limites display: {e}")
            return {}


# Instances spécialisées par application
cv_access_control = None
letters_access_control = None

def get_cv_access_control(auth_service) -> FeatureAccessControl:
    """Factory pour contrôleur d'accès Phoenix CV"""
    global cv_access_control
    if cv_access_control is None:
        cv_access_control = FeatureAccessControl(auth_service)
    return cv_access_control

def get_letters_access_control(auth_service) -> FeatureAccessControl:
    """Factory pour contrôleur d'accès Phoenix Letters"""
    global letters_access_control
    if letters_access_control is None:
        letters_access_control = FeatureAccessControl(auth_service)
    return letters_access_control