
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

# CSS properties whitelist for style validation - Plus permissive pour UI
ALLOWED_CSS_PROPERTIES = [
    'color', 'background-color', 'background', 'font-weight', 'font-size',
    'text-align', 'margin', 'padding', 'border-radius', 'border',
    'display', 'justify-content', 'align-items', 'flex-direction',
    'height', 'width', 'max-width', 'min-height', 'box-shadow',
    'grid-template-columns', 'gap', 'position', 'top', 'right',
    'font-style', 'line-height', 'margin-bottom', 'margin-top',
    'padding-left', 'padding-right', 'padding-top', 'padding-bottom',
    'border-left', 'border-right', 'border-top', 'border-bottom',
    'cursor', 'white-space', 'overflow', 'text-decoration'
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
    Configuration sécurisée avec validation CSS inline.
    
    Args:
        content: The markdown/HTML content to render.
    """
    # Pre-process CSS validation
    import re
    def validate_style_attribute(match):
        style_content = match.group(1)
        validated_style = validate_css_style(style_content)
        return f'style="{validated_style}"'
    
    # Validate CSS before bleach processing
    pre_validated = re.sub(r'style="([^"]*)"', validate_style_attribute, content)
    
    # Sanitize the content with validated CSS
    sanitized_content = bleach.clean(
        pre_validated,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=False  # Escape disallowed tags instead of removing
    )
    
    # Render the sanitized content
    st.markdown(sanitized_content, unsafe_allow_html=True)

def safe_redirect(url: str, message: str = "🔄 Redirection..."):
    """
    Effectue une redirection sécurisée via Streamlit link_button.
    
    Args:
        url: URL de redirection
        message: Message à afficher pendant la redirection
    """
    st.success(message)
    st.link_button("👉 Ouvrir le lien", url, type="primary")
