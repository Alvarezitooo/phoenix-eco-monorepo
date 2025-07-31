"""
Page templates securisee - Phoenix CV
Affichage et apercu securise des templates CV disponibles
"""

import streamlit as st
import html
from models.cv_data import CVTier


def render_templates_page_secure(template_engine, create_demo_profile_secure_func):
    """Page templates securisee"""
    
    st.title("🎨 Templates Securises Phoenix CV")
    
    user_tier = st.session_state.get('user_tier', CVTier.FREE)
    available_templates = template_engine.get_available_templates_secure(user_tier)
    
    st.markdown(f"**{len(available_templates)} templates securises** disponibles pour votre plan")
    
    # Indicateur de securite templates
    st.markdown("""
    <div style="background: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin-bottom: 20px;">
        <h5 style="color: #0c5460; margin: 0;">🛡️ Securite Templates</h5>
        <p style="color: #0c5460; margin: 5px 0 0 0; font-size: 0.9em;">
            • HTML echappe automatiquement • CSP headers integres • XSS prevention • Output sanitization
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Affichage securise des templates
    cols = st.columns(2)
    
    for i, template in enumerate(available_templates):
        with cols[i % 2]:
            
            st.markdown(f"### {html.escape(template.name)}")
            st.markdown(f"**Categorie:** {html.escape(template.category)}")
            st.markdown(f"**Description:** {html.escape(template.description)}")
            
            if template.is_premium and user_tier == CVTier.FREE:
                st.markdown("🔒 **Template Premium**")
                if st.button(f"🚀 Debloquer {template.name}", key=f"unlock_{template.id}"):
                    st.session_state.current_page = 'pricing'
                    st.rerun()
            else:
                if st.button(f"👁️ Apercu Securise", key=f"preview_{template.id}"):
                    # Profil demo securise
                    demo_profile = create_demo_profile_secure_func()
                    html_preview = template_engine.render_cv_secure(
                        demo_profile, template.id, for_export=False
                    )
                    
                    st.markdown("**Apercu securise du template:**")
                    st.components.v1.html(html_preview, height=600, scrolling=True)
            
            st.markdown("---")