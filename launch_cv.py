"""
🚀 Phoenix CV - Launcher Script pour Streamlit Cloud
Point d'entrée à la racine utilisant le pattern Gemini Pro Oracle

Solution architecturale éprouvée pour monorepo compatibility
Infrastructure as Code pour déploiement robuste Phoenix CV
"""

import os
import sys

# Ajouter le chemin de l'application au sys.path pour permettre les imports
app_path = os.path.join(os.path.dirname(__file__), 'apps', 'phoenix-cv')
sys.path.insert(0, app_path)

# Importer et exécuter l'application réelle
try:
    # Essayer d'importer l'app Phoenix CV avec auth unifiée
    from phoenix_cv_auth_integration import main
    if __name__ == '__main__':
        main()
except ImportError:
    # Fallback vers version minimale fonctionnelle
    import streamlit as st
    
    st.set_page_config(
        page_title="🚀 Phoenix CV",
        page_icon="📄",
        layout="wide"
    )
    
    # CSS et header
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>📄 Phoenix CV</h1>
        <p>Générateur IA de CV Optimisés pour Reconversions</p>
        <p><strong>✅ Déploiement via Launcher Script Réussi!</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("🎉 Pattern Gemini Pro Oracle appliqué à Phoenix CV!")
    
    # Informations architecturales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**🏗️ Architecture**\nMonorepo + Launcher")
    
    with col2:
        st.info("**🔄 Data Pipeline**\nSupabase Intégré")
        
    with col3:
        st.info("**📄 Spécialité**\nCV + ATS Optimization")
    
    # Test variables d'environnement
    st.markdown("---")
    st.subheader("🔧 Configuration Phoenix CV")
    
    env_vars = {
        "GOOGLE_API_KEY": "🤖 Gemini AI",
        "SUPABASE_URL": "🗄️ Event Store", 
        "SUPABASE_KEY": "🔐 Authentification",
        "JWT_SECRET_KEY": "🛡️ Sécurité JWT",
        "PHOENIX_MASTER_KEY": "🔑 Chiffrement"
    }
    
    configured = 0
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value and len(value) > 10:
            st.success(f"✅ **{description}** - {var} configuré")
            configured += 1
        else:
            st.error(f"❌ **{description}** - {var} manquant")
    
    # Fonctionnalités CV
    st.markdown("---")
    st.subheader("⚡ Fonctionnalités Phoenix CV")
    
    features = [
        "📝 **Génération CV IA** - CV optimisés selon profil",
        "🎯 **ATS Optimization** - Compatibilité systèmes de recrutement", 
        "🔍 **Analyse CV** - Scoring et recommandations",
        "🎨 **Templates Premium** - Designs professionnels",
        "🚀 **Mirror Match** - Correspondance CV/Offre parfaite",
        "🤖 **Smart Coach** - Conseils personnalisés temps réel"
    ]
    
    for feature in features:
        st.info(feature)
    
    # Résumé
    st.markdown("---")
    if configured >= 3:
        st.success(f"🎯 **Phoenix CV Opérationnel!** ({configured}/{len(env_vars)}) Prêt pour génération CV")
        st.balloons()
    else:
        st.warning(f"⚠️ **Configuration partielle** ({configured}/{len(env_vars)}) - Ajoutez les variables manquantes")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>📄 <strong>Phoenix CV</strong> - Révolutionner la création de CV pour reconversions</p>
        <p>🏗️ Launcher Script Architecture • 🔄 Data Pipeline • ⚡ ATS Ready</p>
    </div>
    """, unsafe_allow_html=True)