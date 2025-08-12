
import streamlit as st

def render_consent_banner():
    """
    Affiche un bandeau de consentement RGPD dans la sidebar.
    Le bandeau disparaît une fois que l'utilisateur a cliqué sur 'Accepter'.
    Utilise st.session_state pour ne s'afficher qu'une fois par session.
    """
    if not st.session_state.get('consent_given', False):
        with st.sidebar:
            st.markdown("---")
            with st.container():
                st.markdown(
                    "<small>En poursuivant votre navigation sur ce site, vous acceptez l'utilisation de cookies pour analyser le trafic et améliorer votre expérience.</small>", 
                    unsafe_allow_html=True
                )
                if st.button("✅ J'accepte", key="rgpd_consent_button", use_container_width=True, type="primary"):
                    st.session_state['consent_given'] = True
                    st.rerun()
