"""
⭐ Phoenix CV - Décorateurs de fonctionnalités Premium
Contrôle d'accès et restrictions pour les fonctionnalités Phoenix CV

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import streamlit as st
from functools import wraps
from typing import Callable, Any
import logging

# Import du service d'authentification
from phoenix_cv.services.phoenix_unified_auth import phoenix_cv_auth

# Import du contrôleur d'accès
try:
    from packages.phoenix_shared_auth.middleware.feature_access_control import (
        get_cv_access_control, AccessLevel
    )
    ACCESS_CONTROL_AVAILABLE = True
except ImportError:
    ACCESS_CONTROL_AVAILABLE = False

logger = logging.getLogger(__name__)


def require_cv_premium(feature_name: str):
    """
    Décorateur pour fonctionnalités Premium Phoenix CV
    
    Args:
        feature_name: Nom de la fonctionnalité
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = st.session_state.get("user_id")
            
            if not user_id:
                _show_login_required_cv()
                return None
            
            # Vérifier accès Premium
            has_access, message = phoenix_cv_auth.check_cv_feature_access(user_id, feature_name)
            
            if has_access:
                return func(*args, **kwargs)
            else:
                _show_premium_required_cv(feature_name, message)
                return None
        
        return wrapper
    return decorator


def check_cv_monthly_limit(limit_type: str):
    """
    Décorateur pour vérifier les limites mensuelles CV
    
    Args:
        limit_type: Type de limite ("cv_count_monthly", etc.)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = st.session_state.get("user_id")
            
            if not user_id:
                _show_login_required_cv()
                return None
            
            # Récupérer limites utilisateur
            cv_features = phoenix_cv_auth.get_cv_features(user_id)
            limit = cv_features.get(limit_type, 0)
            
            if limit == -1:
                # Illimité (Premium)
                return func(*args, **kwargs)
            elif limit > 0:
                # Vérifier usage actuel
                current_usage = _get_current_usage(user_id, limit_type)
                
                if current_usage < limit:
                    # Incrémenter usage
                    _increment_usage(user_id, limit_type)
                    return func(*args, **kwargs)
                else:
                    # Limite atteinte
                    _show_limit_reached_cv(limit_type, limit, current_usage)
                    return None
            else:
                # Fonctionnalité non disponible
                _show_premium_required_cv(limit_type, "Fonctionnalité Premium requise")
                return None
        
        return wrapper
    return decorator


def require_ats_optimization():
    """Décorateur pour l'optimisation ATS"""
    return require_cv_premium("ats_optimization")


def require_mirror_match():
    """Décorateur pour Mirror Match"""
    return require_cv_premium("mirror_match")


def require_premium_templates():
    """Décorateur pour les templates Premium"""
    return require_cv_premium("premium_templates")


def require_trajectory_builder():
    """Décorateur pour Trajectory Builder"""
    return require_cv_premium("trajectory_builder")


def require_smart_coach_advanced():
    """Décorateur pour Smart Coach avancé"""
    return require_cv_premium("smart_coach_advanced")


def limit_cv_creation():
    """Décorateur pour limiter la création de CV"""
    return check_cv_monthly_limit("cv_count_monthly")


# Fonctions d'affichage des restrictions

def _show_login_required_cv():
    """Affiche le message de connexion requise pour CV"""
    st.error("🔐 **Connexion requise pour Phoenix CV**")
    st.info("Connectez-vous pour créer des CV et accéder aux fonctionnalités avancées.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Se connecter", type="primary", key="login_required_cv"):
            st.session_state.auth_flow = "login"
            st.rerun()
    
    with col2:
        if st.button("🆓 Mode invité", key="guest_mode_cv"):
            st.session_state.auth_flow = "guest"
            st.rerun()


def _show_premium_required_cv(feature_name: str, message: str):
    """Affiche la restriction Premium pour une fonctionnalité CV"""
    feature_names = {
        "ats_optimization": "Optimisation ATS",
        "mirror_match": "Mirror Match Algorithme",
        "premium_templates": "Templates Premium",
        "trajectory_builder": "Trajectory Builder",
        "smart_coach_advanced": "Smart Coach Avancé"
    }
    
    display_name = feature_names.get(feature_name, feature_name)
    
    st.error(f"⭐ **Fonctionnalité Premium : {display_name}**")
    st.info(message)
    
    # Comparaison Gratuit vs Premium
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🆓 Phoenix CV Gratuit")
        st.markdown("- ✅ 3 CV par mois")
        st.markdown("- ✅ 5 templates de base")
        st.markdown("- ✅ Export PDF")
        st.markdown("- ✅ Support email")
    
    with col2:
        st.markdown("### ⭐ Phoenix CV Premium")
        st.markdown("- 🔥 **CV illimités**")
        st.markdown("- 🔥 **20+ templates premium**")
        st.markdown("- 🔥 **Optimisation ATS**")
        st.markdown("- 🔥 **Mirror Match**")
        st.markdown("- 🔥 **Trajectory Builder**")
        st.markdown("- 🔥 **Smart Coach avancé**")
        st.markdown("- 🔥 **Support prioritaire**")
    
    # Boutons d'action
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Phoenix CV Premium", type="primary", key=f"upgrade_cv_{feature_name}"):
            st.success("🔗 Redirection vers Phoenix CV Premium...")
            # TODO: Intégrer Stripe
    
    with col2:
        if st.button("🔥 Pack CV + Letters", key=f"pack_{feature_name}"):
            st.success("🔗 Redirection vers le Pack Phoenix...")
            # TODO: Intégrer Stripe Pack
    
    with col3:
        if st.button("ℹ️ En savoir plus", key=f"info_{feature_name}"):
            st.info("📄 Consultez notre page tarifs pour plus d'informations")


def _show_limit_reached_cv(limit_type: str, limit: int, current_usage: int):
    """Affiche le message de limite atteinte pour CV"""
    limit_names = {
        "cv_count_monthly": "création de CV"
    }
    
    limit_name = limit_names.get(limit_type, limit_type)
    
    st.warning(f"⚠️ **Limite mensuelle atteinte : {limit_name}**")
    st.info(f"Vous avez créé {current_usage}/{limit} CV ce mois-ci.")
    
    # Afficher les options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏳ Attendre le mois prochain")
        from datetime import datetime
        current_date = datetime.now()
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1, day=1)
        
        days_remaining = (next_month - current_date).days
        st.write(f"⏰ Remise à zéro dans {days_remaining} jours")
        
        if st.button("📅 Me rappeler", key="remind_reset"):
            st.success("📧 Nous vous enverrons un rappel !")
    
    with col2:
        st.markdown("### ⭐ Passer Premium")
        st.write("✨ **CV illimités immédiatement**")
        st.write("🎯 **+ Toutes les fonctionnalités Premium**")
        
        if st.button("🚀 Débloquer maintenant", type="primary", key=f"unlock_{limit_type}"):
            st.success("🔗 Redirection vers l'abonnement Premium...")
    
    # Option Pack
    st.markdown("---")
    st.markdown("### 🔥 **Offre spéciale : Pack CV + Letters**")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("🎯 CV illimités + Lettres illimitées")
        st.write("💰 **Économisez 30%** par rapport aux abonnements séparés")
    
    with col2:
        if st.button("🔥 Découvrir le Pack", key="discover_pack"):
            st.success("🔗 Redirection vers le Pack Phoenix...")


def _get_current_usage(user_id: str, usage_type: str) -> int:
    """Récupère l'usage actuel d'un type donné"""
    from datetime import datetime
    current_month = datetime.now().strftime("%Y-%m")
    usage_key = f"cv_usage_{user_id}_{usage_type}_{current_month}"
    return st.session_state.get(usage_key, 0)


def _increment_usage(user_id: str, usage_type: str):
    """Incrémente l'usage d'un type donné"""
    from datetime import datetime
    current_month = datetime.now().strftime("%Y-%m")
    usage_key = f"cv_usage_{user_id}_{usage_type}_{current_month}"
    
    if usage_key not in st.session_state:
        st.session_state[usage_key] = 0
    st.session_state[usage_key] += 1
    
    logger.info(f"📊 Usage CV {usage_type} pour {user_id}: {st.session_state[usage_key]}")


def render_cv_subscription_widget():
    """Rend le widget d'abonnement CV dans la sidebar"""
    user_id = st.session_state.get("user_id")
    if not user_id:
        return
    
    try:
        # Récupérer infos d'abonnement
        subscription_info = phoenix_cv_auth.get_subscription_info(user_id)
        display_info = subscription_info.get("subscription_display", {})
        cv_features = phoenix_cv_auth.get_cv_features(user_id)
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 📄 Abonnement CV")
            
            # Badge de statut
            st.markdown(
                f"""
                <div style="
                    background: {display_info.get('color', '#6b7280')}; 
                    padding: 0.5rem 1rem; 
                    border-radius: 20px; 
                    text-align: center; 
                    color: white;
                    margin-bottom: 1rem;
                    font-size: 0.9rem;
                ">
                    <strong>{display_info.get('icon', '')} {display_info.get('badge', 'GRATUIT')}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Limites d'usage
            if cv_features.get("cv_count_monthly", 0) != -1:
                current_usage = _get_current_usage(user_id, "cv_count_monthly")
                limit = cv_features.get("cv_count_monthly", 3)
                remaining = max(0, limit - current_usage)
                
                st.markdown(f"**CV ce mois-ci:** {current_usage}/{limit}")
                progress = min(1.0, current_usage / limit) if limit > 0 else 0
                st.progress(progress)
                
                if remaining <= 1:
                    st.warning(f"⚠️ Plus que {remaining} CV restant")
                elif remaining <= 0:
                    st.error("❌ Limite mensuelle atteinte")
            else:
                st.success("✅ **CV illimités**")
            
            # Fonctionnalités Premium
            premium_features = [
                ("ats_optimization", "Optimisation ATS", cv_features.get("ats_optimization", False)),
                ("mirror_match", "Mirror Match", cv_features.get("mirror_match", False)),
                ("trajectory_builder", "Trajectory Builder", cv_features.get("trajectory_builder", False))
            ]
            
            st.markdown("**Fonctionnalités Premium:**")
            for feature_key, feature_name, enabled in premium_features:
                icon = "✅" if enabled else "❌"
                st.markdown(f"{icon} {feature_name}")
            
            # Bouton d'upgrade si pas Premium
            if not cv_features.get("is_premium", False):
                st.markdown("---")
                if st.button("🚀 Passer Premium", type="primary", key="sidebar_upgrade"):
                    st.success("🔗 Redirection vers Premium...")
                    
                if subscription_info.get("can_upgrade_to_pack"):
                    if st.button("🔥 Pack CV + Letters", key="sidebar_pack"):
                        st.success("🔗 Redirection vers Pack...")
    
    except Exception as e:
        logger.error(f"❌ Erreur widget abonnement CV: {e}")


# Alias pour compatibilité
premium_required = require_cv_premium
monthly_limit = check_cv_monthly_limit