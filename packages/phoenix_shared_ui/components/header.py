
import streamlit as st

def render_header(app_name: str, app_icon: str):
    """
    Affiche un header standardisé pour une application de l'écosystème Phoenix.

    Args:
        app_name: Le nom de l'application (ex: "Phoenix Letters").
        app_icon: L'emoji icône de l'application (ex: "✉️").
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border-left: 6px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
    ">
        <h2 style="margin: 0; color: #2c3e50; font-weight: 600;">
            {app_icon} {app_name}
        </h2>
        <p style="margin: 0.3rem 0 0 0; color: #57647c; font-size: 0.9rem;">
            Fait partie de l'écosystème 🦋 Phoenix
        </p>
    </div>
    """, unsafe_allow_html=True)
