import os
import google.generativeai as genai
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Phoenix Rise - Coach IA Reconversion",
    page_icon="🦋",
    layout="wide",
)

# Configuration de l'API Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Erreur: La variable d'environnement GEMINI_API_KEY n'est pas configurée.")
    st.stop()
genai.configure(api_key=api_key)


def render_research_action_banner():
    """🔬 Bannière de sensibilisation à la recherche-action Phoenix"""
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <p style="margin: 0; font-size: 0.95rem; font-weight: 500;">
                🎓 <strong>Participez à une recherche-action sur l'impact de l'IA dans la reconversion professionnelle.</strong>
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.9; line-height: 1.4;">
                En utilisant Phoenix, vous contribuez anonymement à une étude sur l'IA éthique et la réinvention de soi. 
                Vos données (jamais nominatives) aideront à construire des outils plus justes et plus humains.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    """Point d'entrée principal de l'application."""
    
    # 🚀 PHOENIX RISE - VERSION MINIMALE POUR TESTS DÉPLOIEMENT
    st.title("🦋 Phoenix Rise")
    st.subheader("Coach IA pour Reconversion Professionnelle")
    
    # 🔬 BANNIÈRE RECHERCHE-ACTION PHOENIX
    render_research_action_banner()
    
    # Message de statut
    st.success("✅ **Phoenix Rise démarré avec succès !**")
    st.info("🚧 **Version de test déploiement** - Fonctionnalités complètes en cours de développement")
    
    # Fonctionnalités prévues
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 **Fonctionnalités à venir**")
        st.markdown("- 📔 **Journal de bord interactif**")  
        st.markdown("- 🎯 **Dashboard de progression**")
        st.markdown("- 🤖 **Coach IA personnalisé**")
        st.markdown("- 🔮 **Protocole Renaissance**")
    
    with col2:
        st.markdown("### 🛠️ **Technologies**")
        st.markdown("- ⚡ **Streamlit** - Interface utilisateur")
        st.markdown("- 🤖 **Gemini AI** - Intelligence artificielle") 
        st.markdown("- 🗄️ **Supabase** - Base de données")
        st.markdown("- 📊 **Plotly** - Visualisation données")
    
    # Test basique de l'API Gemini
    st.markdown("---")
    st.markdown("### 🧪 **Test API Gemini**")
    
    if st.button("🚀 Tester la connexion IA"):
        try:
            with st.spinner("Test connexion Gemini..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content("Dis bonjour de la part de Phoenix Rise!")
                st.success("✅ **Connexion Gemini opérationnelle !**")
                st.write(f"**Réponse IA :** {response.text}")
        except Exception as e:
            st.error(f"❌ Erreur connexion Gemini: {e}")
    
    # Info développement
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 10px;">
            <p style="margin: 0; color: #666; font-size: 0.9rem;">
                💻 **Développé par Claude Phoenix DevSecOps Guardian** | 🔒 **Sécurité & RGPD by design**
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()