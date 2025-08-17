"""
🏛️ PHOENIX COMMON - Clients Optimisés avec Cache
Clients lazy-loaded avec @st.cache_resource pour performance
Conforme au Contrat d'Exécution V5

Author: Claude Phoenix DevSecOps Guardian  
Version: 4.1.0 - Performance Optimized
"""

import streamlit as st
from typing import Any, Optional
from .settings import get_settings

# 🤖 GEMINI CLIENT OPTIMISÉ
@st.cache_resource(show_spinner=False)
def get_gemini_client():
    """
    Client Gemini optimisé avec cache Streamlit
    
    Returns:
        Client Gemini configuré
        
    Raises:
        RuntimeError: Si GEMINI_API_KEY manquante
    """
    settings = get_settings()
    
    if not settings.has_gemini():
        raise RuntimeError("GEMINI_API_KEY manquante dans la configuration")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Configuration sécurisée
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
                candidate_count=1,
            )
        )
        
        return model
        
    except ImportError:
        raise RuntimeError("google-generativeai package non installé")
    except Exception as e:
        raise RuntimeError(f"Erreur initialisation Gemini: {e}")

# 🗄️ SUPABASE CLIENT OPTIMISÉ
@st.cache_resource(show_spinner=False)
def get_supabase_client():
    """
    Client Supabase optimisé avec cache Streamlit
    
    Returns:
        Client Supabase configuré
        
    Raises:
        RuntimeError: Si configuration Supabase manquante
    """
    settings = get_settings()
    
    if not settings.has_supabase():
        raise RuntimeError("Configuration Supabase manquante (URL + ANON_KEY)")
    
    try:
        from supabase import create_client, Client
        
        client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        
        return client
        
    except ImportError:
        raise RuntimeError("supabase package non installé")
    except Exception as e:
        raise RuntimeError(f"Erreur initialisation Supabase: {e}")

# 💳 STRIPE CLIENT OPTIMISÉ
@st.cache_resource(show_spinner=False)
def get_stripe_client():
    """
    Client Stripe optimisé avec cache Streamlit
    
    Returns:
        Module stripe configuré
        
    Raises:
        RuntimeError: Si STRIPE_SK manquante
    """
    settings = get_settings()
    
    if not settings.has_stripe():
        raise RuntimeError("Configuration Stripe manquante")
    
    try:
        import stripe
        
        stripe.api_key = settings.STRIPE_SK
        
        # Test de connexion rapide
        stripe.Account.retrieve()
        
        return stripe
        
    except ImportError:
        raise RuntimeError("stripe package non installé")
    except Exception as e:
        raise RuntimeError(f"Erreur initialisation Stripe: {e}")

# 🏛️ PHOENIX AUTH CLIENT OPTIMISÉ
@st.cache_resource(show_spinner=False)
def get_phoenix_auth_client():
    """
    Client authentification Phoenix optimisé
    
    Returns:
        AuthManager Phoenix configuré
    """
    try:
        from phoenix_shared_auth.client import get_auth_manager
        return get_auth_manager()
    except ImportError:
        raise RuntimeError("phoenix_shared_auth non disponible")

# 🔧 UTILITAIRES CACHE
def clear_all_caches():
    """
    Vide tous les caches clients Phoenix
    Utile pour refresh en cas de changement config
    """
    st.cache_resource.clear()
    st.success("✅ Caches clients Phoenix vidés")

def get_cached_client_status() -> dict:
    """
    Statut des clients mis en cache
    
    Returns:
        Dict avec statut de chaque client
    """
    settings = get_settings()
    
    status = {
        "gemini": "✅ Configuré" if settings.has_gemini() else "❌ Non configuré",
        "supabase": "✅ Configuré" if settings.has_supabase() else "❌ Non configuré", 
        "stripe": "✅ Configuré" if settings.has_stripe() else "❌ Non configuré",
        "phoenix_auth": "✅ Disponible",
        "safe_mode": "🛡️ Activé" if settings.PHOENIX_SAFE_MODE else "🚀 Désactivé"
    }
    
    return status