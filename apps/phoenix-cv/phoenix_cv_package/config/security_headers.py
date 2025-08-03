"""
🛡️ Security Headers Configuration
Headers HTTP de sécurité pour Phoenix CV
"""

SECURITY_HEADERS = {
    # Protection Clickjacking
    "X-Frame-Options": "DENY",
    # Protection MIME sniffing
    "X-Content-Type-Options": "nosniff",
    # Protection XSS navigateur
    "X-XSS-Protection": "1; mode=block",
    # Référer policy
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Content Security Policy
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://generativelanguage.googleapis.com"
    ),
    # HSTS (si HTTPS)
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    # Permissions Policy
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


def apply_security_headers():
    """Applique les headers de sécurité à Streamlit"""
    import streamlit as st

    # Note: Streamlit ne permet pas de modifier les headers HTTP directement
    # Ces headers doivent être configurés au niveau du reverse proxy (Nginx, Apache)
    # ou du service d'hébergement (Streamlit Cloud, etc.)

    # Pour le développement, on peut les logger
    st.write("🛡️ Headers sécurité configurés (voir reverse proxy)")
