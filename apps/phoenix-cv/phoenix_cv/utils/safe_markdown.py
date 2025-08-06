
import streamlit as st
import bleach

# SECURITY: Define a strict set of allowed HTML tags and attributes
# This is the core of the XSS protection.
ALLOWED_TAGS = [
    'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'br', 
    'strong', 'em', 'b', 'i', 'u', 'ul', 'ol', 'li', 'a'
]

ALLOWED_ATTRIBUTES = {
    '*': ['style', 'class'],
    'a': ['href', 'title', 'target'],
}

def safe_markdown(content: str):
    """
    Renders markdown after sanitizing it to prevent XSS attacks.
    It allows a predefined set of safe HTML tags and attributes.
    
    Args:
        content: The markdown/HTML content to render.
    """
    # Sanitize the content first
    sanitized_content = bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True  # Remove disallowed tags instead of escaping them
    )
    
    # Render the sanitized content
    st.markdown(sanitized_content, unsafe_allow_html=True)
