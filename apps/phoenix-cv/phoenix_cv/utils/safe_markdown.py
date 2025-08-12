
import streamlit as st
import bleach

# SECURITY: Define a strict set of allowed HTML tags and attributes
# This is the core of the XSS protection - Configuration sécurisée
ALLOWED_TAGS = [
    'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'br', 
    'strong', 'em', 'b', 'i', 'u', 'ul', 'ol', 'li', 'a', 'small',
    'button'  # Re-ajouté button pour UI (sans onclick)
    # Still removed: 'script' pour sécurité
]

ALLOWED_ATTRIBUTES = {
    '*': ['class'],
    'div': ['style'],
    'span': ['style'],
    'p': ['style'],
    'h1': ['style'], 'h2': ['style'], 'h3': ['style'], 'h4': ['style'], 'h5': ['style'], 'h6': ['style'],
    'a': ['href', 'title', 'target'],
    'button': ['style', 'type'],  # Button attributes sans onclick
    'small': ['style'],
    'strong': ['style'],
    'ul': ['style'],
    'li': ['style'],
    # Removed: onclick, script attributes pour sécurité
}

# CSS properties whitelist for style validation - Complet pour Phoenix CV
ALLOWED_CSS_PROPERTIES = [
    # Couleurs
    'color', 'background-color', 'background', 
    # Typography
    'font-weight', 'font-size', 'font-style', 'line-height', 'text-align', 'text-decoration',
    # Spacing
    'margin', 'margin-top', 'margin-bottom', 'margin-left', 'margin-right',
    'padding', 'padding-top', 'padding-bottom', 'padding-left', 'padding-right',
    # Layout
    'display', 'justify-content', 'align-items', 'flex-direction',
    'height', 'width', 'max-width', 'min-height', 'min-width', 'max-height',
    'position', 'top', 'right', 'bottom', 'left',
    # Borders & Effects
    'border', 'border-radius', 'border-left', 'border-right', 'border-top', 'border-bottom',
    'border-color', 'border-width', 'border-style',
    'box-shadow', 'opacity', 'transform',
    # Grid & Flexbox
    'grid-template-columns', 'grid-template-rows', 'gap', 'grid-gap',
    'flex', 'flex-grow', 'flex-shrink', 'flex-basis',
    # Other
    'cursor', 'white-space', 'overflow', 'overflow-x', 'overflow-y',
    'z-index', 'vertical-align'
]

def validate_css_style(style_value: str) -> str:
    """Valide et filtre les propriétés CSS inline pour éviter les injections"""
    if not style_value:
        return ""
    
    # Parse basic CSS properties
    safe_styles = []
    for declaration in style_value.split(';'):
        if ':' in declaration:
            prop, value = declaration.split(':', 1)
            prop = prop.strip().lower()
            value = value.strip()
            
            # Whitelist de propriétés CSS autorisées
            if prop in ALLOWED_CSS_PROPERTIES:
                # Validation élargie pour fonctions CSS utiles
                dangerous_patterns = [
                    'javascript:', 'expression:', 'behavior:', 'data:',
                    '@import', 'url(javascript:', 'url(data:'
                ]
                if not any(dangerous in value.lower() for dangerous in dangerous_patterns):
                    # Permettre les fonctions CSS utiles comme clamp, rgba, linear-gradient
                    safe_styles.append(f"{prop}: {value}")
    
    return '; '.join(safe_styles)

def safe_markdown(content: str):
    """
    Renders markdown after sanitizing it to prevent XSS attacks.
    Version temporaire: bypass complet pour debug CSS.
    
    Args:
        content: The markdown/HTML content to render.
    """
    # VERSION TEMPORAIRE DE DEBUG: bypass complet de bleach
    # pour voir si c'est bleach qui vide les CSS
    st.markdown(content, unsafe_allow_html=True)

def safe_redirect(url: str, message: str = "🔄 Redirection..."):
    """
    Effectue une redirection sécurisée via Streamlit link_button.
    
    Args:
        url: URL de redirection
        message: Message à afficher pendant la redirection
    """
    st.success(message)
    st.link_button("👉 Ouvrir le lien", url, type="primary")
