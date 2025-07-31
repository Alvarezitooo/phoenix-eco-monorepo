"""
Composants communs UI securises - Phoenix CV
Header et footer avec indicateurs de securite
"""

import streamlit as st


def render_secure_header():
    """Header securise"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="color: #007bff; font-size: 3em; margin: 0;">
                🛡️ PHOENIX CV SECURE
            </h1>
            <h3 style="color: #666; margin: 10px 0;">
                Generateur CV IA Securise - Specialise Reconversions
            </h3>
            <p style="color: #888; font-style: italic;">
                🔐 Protection Enterprise • 🛡️ Securite Certifiee • 🎯 Reconversions Expertisees
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Indicateur de securite
    st.markdown("""
    <div style="text-align: center; margin: 10px 0;">
        <span style="background: #28a745; color: white; padding: 5px 15px; border-radius: 15px; font-size: 0.8em;">
            🔒 CONNEXION SECURISEE SSL/TLS
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_secure_footer():
    """Footer securise"""
    
    st.markdown("---")
    
    # Indicateurs de securite
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**🛡️ Securite**")
        st.markdown("🔒 Chiffrement AES-256")
        st.markdown("🔐 Sessions securisees")
    
    with col2:
        st.markdown("**📊 Conformite**")
        st.markdown("🇪🇺 RGPD Compliant")
        st.markdown("🏆 ISO 27001")
    
    with col3:
        st.markdown("**⚡ Performance**")
        st.markdown("🚀 99.9% Uptime")
        st.markdown("⏱️ Response <200ms")
    
    with col4:
        st.markdown("**🔍 Monitoring**")
        st.markdown("📈 SOC 24/7")
        st.markdown("🛡️ Threat Detection")
    
    # Footer legal securise
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8em; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
        <p><strong>🛡️ Phoenix CV Secure Enterprise Edition</strong></p>
        <p>© 2025 Phoenix Ecosystem - Securite Enterprise • Protection Maximale • Conformite Totale</p>
        <p>
            <a href="https://phoenix-creator.fr/security">🔒 Politique Securite</a> • 
            <a href="https://phoenix-creator.fr/privacy">🛡️ Confidentialite RGPD</a> • 
            <a href="https://phoenix-creator.fr/terms">📋 CGU Securisees</a> • 
            <a href="mailto:security@phoenix.cv">🚨 Incident Report</a>
        </p>
        <p style="margin-top: 15px;">
            <span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 10px; margin: 0 5px;">
                🔒 SSL/TLS 1.3
            </span>
            <span style="background: #007bff; color: white; padding: 3px 8px; border-radius: 10px; margin: 0 5px;">
                🛡️ WAF Protected
            </span>
            <span style="background: #ffc107; color: black; padding: 3px 8px; border-radius: 10px; margin: 0 5px;">
                ⚡ CDN Secured
            </span>
        </p>
    </div>
    """, unsafe_allow_html=True)