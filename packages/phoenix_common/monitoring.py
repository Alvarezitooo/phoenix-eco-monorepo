# packages/phoenix_common/monitoring.py
# Observabilité et monitoring Phoenix
# Conforme Directive V3 (observabilité intégrée)

import os
import time
from typing import Dict, Any, Optional
from phoenix_common.settings import get_settings

def init_sentry() -> bool:
    """
    Initialise Sentry pour monitoring erreurs production.
    
    Returns:
        True si initialisé avec succès
    """
    settings = get_settings()
    
    if not settings.SENTRY_DSN:
        return False
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.streamlit import StreamlitIntegration
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENV,
            integrations=[StreamlitIntegration()],
            traces_sample_rate=0.1,  # 10% des transactions
            profiles_sample_rate=0.1
        )
        
        return True
        
    except ImportError:
        print("⚠️ Sentry SDK non installé")
        return False

def init_posthog() -> bool:
    """
    Initialise PostHog pour analytics utilisateur.
    
    Returns:
        True si initialisé avec succès  
    """
    settings = get_settings()
    
    if not settings.POSTHOG_KEY:
        return False
    
    try:
        import posthog
        
        posthog.api_key = settings.POSTHOG_KEY
        posthog.host = settings.POSTHOG_HOST
        
        return True
        
    except ImportError:
        print("⚠️ PostHog SDK non installé")
        return False

def track_event(
    event_name: str,
    user_id: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
):
    """
    Track événement utilisateur (PostHog).
    
    Args:
        event_name: Nom de l'événement
        user_id: ID utilisateur (optionnel)
        properties: Propriétés additionnelles
    """
    try:
        import posthog
        
        posthog.capture(
            distinct_id=user_id or "anonymous",
            event=event_name,
            properties=properties or {}
        )
        
    except Exception:
        # Fail silencieux pour ne pas casser l'UX
        pass

def health_check() -> Dict[str, Any]:
    """
    Healthcheck complet du système Phoenix.
    
    Returns:
        Statut de santé des composants
    """
    settings = get_settings()
    health = {
        "timestamp": time.time(),
        "env": settings.ENV,
        "safe_mode": settings.PHOENIX_SAFE_MODE,
        "services": {}
    }
    
    # Check Supabase
    try:
        from phoenix_common.clients import get_supabase_client
        client = get_supabase_client()
        # Test simple de connectivité
        result = client.table('profiles').select('id').limit(1).execute()
        health["services"]["supabase"] = "✅ OK"
    except Exception as e:
        health["services"]["supabase"] = f"❌ {str(e)[:50]}"
    
    # Check Stripe
    try:
        from phoenix_common.stripe_utils import get_stripe_client
        stripe = get_stripe_client()
        stripe.Account.retrieve()
        health["services"]["stripe"] = "✅ OK"
    except Exception as e:
        health["services"]["stripe"] = f"❌ {str(e)[:50]}"
    
    # Check Gemini
    try:
        from phoenix_common.clients import get_gemini_client
        client = get_gemini_client()
        health["services"]["gemini"] = "✅ OK"
    except Exception as e:
        health["services"]["gemini"] = f"❌ {str(e)[:50]}"
    
    return health

def phoenix_safe_mode_ui():
    """
    Interface utilisateur pour mode sécurisé Phoenix.
    """
    import streamlit as st
    
    st.warning("🛡️ **Mode Sécurisé Phoenix Activé**")
    st.info("""
    **Fonctionnalités limitées pour votre sécurité :**
    - Génération IA désactivée
    - Paiements désactivés  
    - Mode lecture seule
    
    **Pour désactiver :** Définir `PHOENIX_SAFE_MODE=0` dans l'environnement
    """)
    
    # Métriques dégradées
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🛡️ Sécurité", "Maximum")
    with col2:
        st.metric("⚡ Performance", "Limitée")
    with col3:
        st.metric("🔧 Fonctionnalités", "Dégradées")

def track_user_journey(step: str, user_id: Optional[str] = None, metadata: Optional[Dict] = None):
    """
    Track du parcours utilisateur pour optimisation conversion.
    
    Args:
        step: Étape du parcours (visit, generate, export, checkout)
        user_id: ID utilisateur
        metadata: Métadonnées contextuelles
    """
    properties = {"step": step}
    if metadata:
        properties.update(metadata)
    
    track_event(f"user_journey_{step}", user_id, properties)

def monitor_performance(func_name: str):
    """
    Décorateur pour monitorer les performances des fonctions.
    
    Args:
        func_name: Nom de la fonction à monitorer
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Track performance
                track_event("performance_metric", properties={
                    "function": func_name,
                    "duration_ms": duration * 1000,
                    "status": "success"
                })
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Track erreur
                track_event("performance_metric", properties={
                    "function": func_name,
                    "duration_ms": duration * 1000,
                    "status": "error",
                    "error": str(e)[:100]
                })
                
                raise
                
        return wrapper
    return decorator