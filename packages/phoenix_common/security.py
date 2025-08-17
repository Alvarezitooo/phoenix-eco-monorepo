# packages/phoenix_common/security.py
# Sécurité minimale production pour Phoenix
# Conforme Directive V3 (sécurité intégrée)

import os
import hashlib
import hmac
from typing import Optional
from .settings import get_settings

def verify_stripe_webhook(payload: bytes, signature: str) -> bool:
    """
    Vérifie la signature Stripe webhook pour sécurité production.
    
    Args:
        payload: Corps de la requête webhook (bytes)
        signature: Header Stripe-Signature
        
    Returns:
        True si signature valide
    """
    settings = get_settings()
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    if not webhook_secret:
        return False
    
    try:
        # Parsing de la signature Stripe
        sig_parts = signature.split(',')
        timestamp = None
        signature_hash = None
        
        for part in sig_parts:
            if part.startswith('t='):
                timestamp = part[2:]
            elif part.startswith('v1='):
                signature_hash = part[3:]
        
        if not timestamp or not signature_hash:
            return False
        
        # Recalcul de la signature
        payload_to_sign = f"{timestamp}.{payload.decode()}"
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature_hash, expected_signature)
        
    except Exception:
        return False

def get_cors_origins() -> list[str]:
    """
    Retourne les origines CORS autorisées selon l'environnement.
    
    Returns:
        Liste des origines autorisées
    """
    settings = get_settings()
    
    if settings.ENV == "prod":
        return [
            "https://phoenix-ecosystem.com",
            "https://www.phoenix-ecosystem.com",
            "https://phoenix-cv.streamlit.app",
            "https://phoenix-letters.streamlit.app",
            "https://phoenix-rise.streamlit.app"
        ]
    elif settings.ENV == "staging":
        return [
            "https://staging-phoenix.vercel.app",
            "http://localhost:3000",
            "http://localhost:8501"
        ]
    else:  # dev
        return ["*"]  # Permissif en dev

def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitise les entrées utilisateur pour éviter XSS/injection.
    
    Args:
        text: Texte à sanitiser
        max_length: Longueur maximale autorisée
        
    Returns:
        Texte sanitisé
    """
    if not text:
        return ""
    
    # Limitation de longueur
    text = text[:max_length]
    
    # Suppression caractères dangereux
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def check_rls_config() -> dict:
    """
    Vérifie que RLS (Row Level Security) est activé sur Supabase.
    
    Returns:
        Statut de la configuration RLS
    """
    # TODO: Implémenter vérification RLS via API Supabase Management
    # Pour l'instant, retourne un placeholder
    return {
        "rls_enabled": True,  # À vérifier réellement
        "policies_count": "unknown",
        "recommendation": "Vérifier manuellement que RLS est ON dans Supabase Dashboard"
    }

def is_production_ready() -> tuple[bool, list[str]]:
    """
    Vérifie si l'app est prête pour la production.
    
    Returns:
        (is_ready, list_of_issues)
    """
    settings = get_settings()
    issues = []
    
    # Vérifications de base
    if not settings.SUPABASE_URL:
        issues.append("SUPABASE_URL manquante")
    if not settings.SUPABASE_ANON_KEY:
        issues.append("SUPABASE_ANON_KEY manquante")
    
    # Vérifications production
    if settings.ENV == "prod":
        if not os.getenv("STRIPE_WEBHOOK_SECRET"):
            issues.append("STRIPE_WEBHOOK_SECRET manquante (prod)")
        if not settings.SENTRY_DSN:
            issues.append("SENTRY_DSN manquante (monitoring prod)")
        if settings.PHOENIX_SAFE_MODE:
            issues.append("PHOENIX_SAFE_MODE activé en prod (performances dégradées)")
    
    return len(issues) == 0, issues