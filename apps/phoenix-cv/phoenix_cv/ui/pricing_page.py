"""
Page tarification securisee - Phoenix CV
Plans tarifaires avec garanties securite enterprise
"""

import streamlit as st
from phoenix_cv.utils.safe_markdown import safe_markdown, safe_redirect
from phoenix_cv.main import initiate_stripe_checkout





def render_pricing_page_secure():
    """Page tarification Phoenix complète avec tous les produits"""

    st.title("🔥 Phoenix Ecosystem - Solutions Reconversion")

    # Badge securite
    st.markdown(
        """
    <div style="text-align: center; margin-bottom: 30px;">
        <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 20px; border-radius: 20px; font-weight: bold;">
            🛡️ CERTIFICATION SECURISE ENTERPRISE - ISO 27001 Compliant
        </span>
    </div>
    """, 
        unsafe_allow_html=True
    )

    # CSS pour les cartes de pricing
    st.markdown("""
    <style>
    .pricing-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .pricing-card {
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        position: relative;
    }
    
    .pricing-card:hover {
        transform: translateY(-5px);
    }
    
    .card-gratuit { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    .card-letters { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    .card-cv { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    .card-bundle { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        color: white; 
        border: 3px solid #764ba2;
        transform: scale(1.02);
    }
    
    .price-tag {
        font-size: 2rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .features-list {
        text-align: left;
        margin: 1rem 0;
    }
    
    .features-list li {
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    
    .best-deal {
        position: absolute;
        top: -10px;
        right: -10px;
        background: gold;
        color: black;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .btn-phoenix {
        background: white;
        color: #333;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Grille de pricing pour les 4 plans
    col1, col2, col3, col4 = st.columns(4)

    # Plan Gratuit
    with col1:
        with st.container():
            st.markdown("### 🆓 Gratuit")
            st.markdown("**0€/mois**")
            st.markdown("""
            - 🔒 3 générations/mois
            - 🛡️ Templates sécurisés
            - 📊 Export PDF basic
            - ⚡ IA anti-injection
            - 🔐 Anonymisation PII
            """)
            st.success("🎯 Plan actuel gratuit")

    # Phoenix Letters
    with col2:
        with st.container():
            st.markdown("### 📝 Phoenix Letters")
            st.markdown("**9,99€/mois**")
            st.markdown("""
            - 🔒 Lettres illimitées
            - 🛡️ Analyses ATS avancées
            - 🧠 Mirror Match précis
            - ⚡ Smart Coach IA
            - 📊 Templates exclusifs
            - 🔐 Support prioritaire
            - 📋 Export PDF premium
            """)
            
            if st.button("🚀 S'abonner Letters", key="letters_btn", type="primary"):
                user_id = st.session_state.get("user_id", "guest_user")
                user_email = st.session_state.get("user_email", None)
                initiate_stripe_checkout(user_id, "letters_premium", user_email)

    # Phoenix CV
    with col3:
        with st.container():
            st.markdown("### 📄 Phoenix CV")
            st.markdown("**7,99€/mois**")
            st.markdown("""
            - 🔒 CV illimités
            - 🛡️ Templates premium
            - 🧠 ATS Optimizer avancé
            - ⚡ Mirror Match précis
            - 📊 Export multi-formats
            - 🔐 Support prioritaire
            - 📋 Analytics avancées
            """)
            
            if st.button("📄 S'abonner CV", key="cv_btn", type="primary"):
                user_id = st.session_state.get("user_id", "guest_user")
                user_email = st.session_state.get("user_email", None)
                initiate_stripe_checkout(user_id, "premium", user_email)

    # Phoenix Bundle  
    with col4:
        with st.container():
            st.markdown("### 🚀 Bundle Complet")
            st.markdown("**15,99€/mois**")
            st.info("🔥 BEST DEAL - Économie 1,99€")
            st.markdown("""
            - ✨ Phoenix Letters complet
            - ✨ Phoenix CV complet
            - 🎁 Smart Coach universel
            - 🎁 Mirror Match cross-platform
            - 🎁 Analytics avancées
            - 🎁 Support VIP prioritaire
            - 🎁 Accès bêta features
            """)
            
            if st.button("🔥 Bundle Deal", key="bundle_btn", type="primary"):
                user_id = st.session_state.get("user_id", "guest_user")
                user_email = st.session_state.get("user_email", None)
                initiate_stripe_checkout(user_id, "bundle_premium", user_email)

    # Message de comparaison
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
        <p><strong>💡 Recommandation Phoenix :</strong></p>
        <p>🎯 <strong>Letters seul</strong> : Spécialisé lettres de motivation reconversion</p>
        <p>📄 <strong>CV seul</strong> : Optimisation CV et profil LinkedIn exclusivement</p>
        <p>🚀 <strong>Bundle</strong> : Solution complète reconversion avec économie de 1,99€/mois !</p>
    </div>
    """, unsafe_allow_html=True)


    # Certifications securite
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        ### 🛡️ Certifications Securite
        
        - **🏆 ISO 27001** - Management securite information
        - **🔒 SOC 2 Type II** - Controles securite valides
        - **🇪🇺 RGPD Compliant** - Protection donnees EU
        - **🔐 SSL/TLS 1.3** - Chiffrement transport
        - **⚡ Penetration Testing** - Tests mensuels
        """
        )

    with col2:
        st.markdown(
            """
        ### ❓ Securite FAQ
        
        **Ou sont stockees mes donnees ?**  
        Serveurs EU chiffres AES-256, jamais aux US.
        
        **L'IA peut-elle voir mes donnees ?**  
        Non, anonymisation complete avant traitement.
        
        **Qui a acces a mes CV ?**  
        Vous uniquement. Zero acces administrateur.
        """
        )

    # Garanties securisees
    st.markdown("---")
    st.markdown("### 🔐 Garanties Securite Enterprise")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
        **🛡️ Chiffrement**  
        AES-256 bout-en-bout  
        Cles rotees mensuellement
        """
        )

    with col2:
        st.markdown(
            """
        **🔒 Conformite**  
        RGPD, ISO 27001, SOC 2  
        Audits trimestriels
        """
        )

    with col3:
        st.markdown(
            """
        **⚡ Monitoring**  
        24/7 SOC surveillance  
        Alertes temps reel
        """
        )

    with col4:
        st.markdown(
            """
        **🎯 Incident**  
        Response < 15min  
        Recovery < 4h garanti
        """
        )
