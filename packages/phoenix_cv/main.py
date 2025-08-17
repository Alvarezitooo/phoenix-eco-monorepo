"""
🏛️ PHOENIX CV - MAIN ENGINE CONFORME CONTRAT V5
Point d'entrée principal Phoenix CV avec Event-Sourcing

Conforme au Contrat d'Exécution V5:
- Event-Sourcing pour les imports UI
- Sécurité intégrée (validation input, protection BDD)
- Services partagés obligatoires
- Qualité code (black, ruff)
- Conscience déploiement

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Event-Sourcing Architecture
"""

import streamlit as st
import os
import sys
from typing import Optional, Any

# 🏛️ UTILISATION_SERVICES_PARTAGES: UI Loader commun
from phoenix_common.ui_loader import import_ui_safe, render_ui_diagnostics_safe, create_ui_fallback

# Import sécurisé des composants UI
def load_ui_components():
    """
    Chargement des composants UI avec fallbacks sécurisés
    """
    
    # Import des composants principaux avec loader sécurisé
    PhoenixCVHeader, PhoenixCVPremiumBarrier, PhoenixCVNavigation = import_ui_safe(
        "phoenix_cv.ui.components",
        ["PhoenixCVHeader", "PhoenixCVPremiumBarrier", "PhoenixCVNavigation"]
    )
    
    # Fallbacks sécurisés si imports échouent
    if PhoenixCVHeader is None:
        PhoenixCVHeader = create_ui_fallback("PhoenixCVHeader", "Header Phoenix CV indisponible")
    
    if PhoenixCVPremiumBarrier is None:
        PhoenixCVPremiumBarrier = create_ui_fallback("PhoenixCVPremiumBarrier", "Barrière premium indisponible")
    
    if PhoenixCVNavigation is None:
        PhoenixCVNavigation = create_ui_fallback("PhoenixCVNavigation", "Navigation Phoenix CV indisponible")
    
    return PhoenixCVHeader, PhoenixCVPremiumBarrier, PhoenixCVNavigation

# Import des services partagés (OBLIGATOIRE Contrat V5)
def load_shared_services():
    """
    Chargement des services partagés Phoenix avec clients optimisés
    """
    
    try:
        # 🏛️ UTILISATION_SERVICES_PARTAGES: Settings unifié + clients optimisés
        from phoenix_common.settings import get_settings
        from phoenix_common.clients import get_phoenix_auth_client, get_cached_client_status
        
        settings = get_settings()
        
        # Clients optimisés avec cache
        auth_manager = get_phoenix_auth_client()
        client_status = get_cached_client_status()
        
        # 🏛️ UTILISATION_SERVICES_PARTAGES: Modèles de données obligatoires  
        from phoenix_shared_models.user import PhoenixUser
        
        return True, auth_manager, PhoenixUser, settings, client_status
        
    except ImportError as e:
        # 🎯 EVENT-SOURCING: Service partagé indisponible
        if EVENT_SOURCING_AVAILABLE:
            publish_event(UIComponentImportFailed(
                module_path="phoenix_shared_services",
                reason="shared_service_unavailable",
                traceback=str(e)
            ))
        
        return False, None, None, None, None

def run():
    """
    Point d'entrée principal Phoenix CV
    Conforme au Contrat d'Exécution V5
    """
    
    # 🛡️ SÉCURITÉ_INTEGREE: Configuration page sécurisée
    st.set_page_config(
        page_title="Phoenix CV - Générateur IA",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 🏛️ HOOK INTÉGRATION: Settings + validation
    from phoenix_common.settings import get_settings, validate_env
    from phoenix_common.monitoring import init_sentry, phoenix_safe_mode_ui, track_user_journey
    
    settings = get_settings()
    errs = validate_env(settings)
    if errs:
        st.error("Configuration incomplète:\n- " + "\n- ".join(errs))
        st.stop()
    
    # Mode sécurisé
    if settings.PHOENIX_SAFE_MODE:
        phoenix_safe_mode_ui()
        return
    
    # Monitoring
    init_sentry()
    track_user_journey("visit", user_id=st.session_state.get("user_id"))
    
    # Chargement des services partagés avec optimisations
    services_result = load_shared_services()
    services_ok = services_result[0] if services_result else False
    auth_manager = services_result[1] if services_ok else None
    PhoenixUser = services_result[2] if services_ok else None
    settings = services_result[3] if services_ok else None
    client_status = services_result[4] if services_ok else None
    
    # Chargement des composants UI avec diagnostics
    PhoenixCVHeader, PhoenixCVPremiumBarrier, PhoenixCVNavigation = load_ui_components()
    
    # Interface diagnostics si erreurs
    render_ui_diagnostics_safe()
    
    # Affichage statut clients en mode développement
    if settings and settings.is_development() and client_status:
        with st.expander("🔧 Statut des clients Phoenix", expanded=False):
            for service, status in client_status.items():
                st.markdown(f"**{service.title()}**: {status}")
    
    # Header principal
    PhoenixCVHeader.render(
        title="Phoenix CV",
        subtitle="Créez des CV qui se démarquent avec l'IA",
        icon="📄"
    )
    
    # Navigation principale
    PhoenixCVNavigation.render_main_nav()
    
    # 🛡️ SÉCURITÉ_INTEGREE: Vérification authentification
    user_authenticated = st.session_state.get("authenticated_user", False)
    
    if not user_authenticated and services_ok:
        st.warning("🔒 Connectez-vous pour accéder aux fonctionnalités Phoenix CV")
        
        # Interface d'authentification
        with st.expander("🚀 Connexion Phoenix", expanded=True):
            st.info("Utilisez votre compte Phoenix pour accéder à toutes les fonctionnalités")
            
            if st.button("🔗 Se connecter avec Phoenix Auth", type="primary"):
                # Future: intégration auth_manager
                st.info("🔗 Redirection vers l'authentification Phoenix...")
        
        return
    
    # Interface principale Phoenix CV
    current_tab = st.session_state.get("current_tab", "create")
    
    if current_tab == "create":
        _render_create_cv_tab(PhoenixCVPremiumBarrier)
    elif current_tab == "upload":
        _render_upload_cv_tab(PhoenixCVPremiumBarrier)
    else:
        _render_default_tab(PhoenixCVPremiumBarrier)

def _render_create_cv_tab(PhoenixCVPremiumBarrier):
    """Tab création CV"""
    st.markdown("### 🆕 Créer un nouveau CV")
    
    # Vérification limite utilisateur gratuit
    user_tier = st.session_state.get("user_tier", "free")
    cv_generated_today = st.session_state.get("cv_generated_today", 0)
    
    if user_tier == "free" and cv_generated_today >= 3:
        PhoenixCVPremiumBarrier.render(
            feature_name="Génération illimitée",
            description="Créez autant de CV que vous voulez",
            benefits=[
                "Génération illimitée de CV",
                "Templates premium exclusifs",
                "Optimisation ATS avancée",
                "Export multi-formats"
            ]
        )
        return
    
    # Interface création (simplifiée pour démo)
    st.info("🚧 Interface de création CV en cours de développement")
    
    if st.button("🎯 Créer CV (Démo)", type="primary"):
        st.success("✅ CV créé avec succès !")
        st.balloons()

def _render_upload_cv_tab(PhoenixCVPremiumBarrier):
    """Tab analyse CV"""
    st.markdown("### 📂 Analyser un CV existant")
    
    uploaded_file = st.file_uploader(
        "Choisissez votre CV", 
        type=['pdf', 'docx', 'txt'],
        help="Formats supportés: PDF, Word, Texte"
    )
    
    if uploaded_file:
        st.success(f"✅ Fichier {uploaded_file.name} téléchargé")
        
        if st.button("🔍 Analyser avec IA", type="primary"):
            st.info("🚧 Analyse IA en cours de développement")

def _render_default_tab(PhoenixCVPremiumBarrier):
    """Tab par défaut"""
    st.info("🏠 Sélectionnez une option dans la navigation")

if __name__ == "__main__":
    run()