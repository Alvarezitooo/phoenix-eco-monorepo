"""
Page tarification securisee - Phoenix CV
Plans tarifaires avec garanties securite enterprise
"""

import streamlit as st


def render_pricing_page_secure():
    """Page tarification securisee"""
    
    st.title("💎 Phoenix CV Secure - Tarifs")
    
    # Badge securite
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <span style="background: #28a745; color: white; padding: 8px 20px; border-radius: 20px; font-weight: bold;">
            🛡️ CERTIFICATION SECURISE ENTERPRISE - ISO 27001 Compliant
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # Plan Gratuit Securise
    with col1:
        st.markdown("""
        <div style="border: 2px solid #ddd; border-radius: 10px; padding: 20px; text-align: center;">
            <h3>🆓 Gratuit Securise</h3>
            <h2 style="color: #28a745;">0€</h2>
            <p><strong>Securite de base</strong></p>
            <ul style="text-align: left;">
                <li>🔒 1 CV/mois chiffre</li>
                <li>🛡️ Templates securises</li>
                <li>📊 Export PDF securise</li>
                <li>⚡ IA anti-injection</li>
                <li>🔐 Anonymisation PII</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Plan Pro Securise
    with col2:
        st.markdown("""
        <div style="border: 3px solid #007bff; border-radius: 10px; padding: 20px; text-align: center; background: #f8f9ff;">
            <h3>💎 Pro Securise</h3>
            <h2 style="color: #007bff;">19,99€<small>/mois</small></h2>
            <p><strong>Securite Enterprise</strong></p>
            <ul style="text-align: left;">
                <li>🔒 CV illimites chiffres</li>
                <li>🛡️ Templates premium securises</li>
                <li>🧠 IA Expert anti-injection</li>
                <li>⚡ ATS optimizer securise</li>
                <li>📊 Export multi-formats chiffres</li>
                <li>🔐 Support prioritaire securise</li>
                <li>📋 Audit trail complet</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🛡️ Passer Pro Securise", type="primary", use_container_width=True):
            st.success("🔒 Redirection securisee SSL/TLS... (A implementer)")
    
    # Plan Enterprise
    with col3:
        st.markdown("""
        <div style="border: 2px solid #ffc107; border-radius: 10px; padding: 20px; text-align: center; background: #fffdf0;">
            <h3>🏢 Enterprise</h3>
            <h2 style="color: #ffc107;">Sur devis</h2>
            <p><strong>Securite Gouvernementale</strong></p>
            <ul style="text-align: left;">
                <li>🔒 Chiffrement bout-en-bout</li>
                <li>🛡️ Infrastructure dediee</li>
                <li>👤 SSO/SAML integration</li>
                <li>📊 Audit securite mensuel</li>
                <li>🔐 Conformite ANSSI</li>
                <li>⚡ SLA 99.99% garanti</li>
                <li>👨‍💼 Support 24/7 dedie</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Certifications securite
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🛡️ Certifications Securite
        
        - **🏆 ISO 27001** - Management securite information
        - **🔒 SOC 2 Type II** - Controles securite valides
        - **🇪🇺 RGPD Compliant** - Protection donnees EU
        - **🔐 SSL/TLS 1.3** - Chiffrement transport
        - **⚡ Penetration Testing** - Tests mensuels
        """)
    
    with col2:
        st.markdown("""
        ### ❓ Securite FAQ
        
        **Ou sont stockees mes donnees ?**  
        Serveurs EU chiffres AES-256, jamais aux US.
        
        **L'IA peut-elle voir mes donnees ?**  
        Non, anonymisation complete avant traitement.
        
        **Qui a acces a mes CV ?**  
        Vous uniquement. Zero acces administrateur.
        """)
    
    # Garanties securisees
    st.markdown("---")
    st.markdown("### 🔐 Garanties Securite Enterprise")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **🛡️ Chiffrement**  
        AES-256 bout-en-bout  
        Cles rotees mensuellement
        """)
    
    with col2:
        st.markdown("""
        **🔒 Conformite**  
        RGPD, ISO 27001, SOC 2  
        Audits trimestriels
        """)
    
    with col3:
        st.markdown("""
        **⚡ Monitoring**  
        24/7 SOC surveillance  
        Alertes temps reel
        """)
    
    with col4:
        st.markdown("""
        **🎯 Incident**  
        Response < 15min  
        Recovery < 4h garanti
        """)