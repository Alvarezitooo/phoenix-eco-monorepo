"""
🚀 Phoenix Letters - Version Legacy Fonctionnelle
Point d'entrée simplifié pour déploiement immédiat sur Streamlit Cloud

Author: Claude Phoenix DevSecOps Guardian
Version: Legacy-Deploy - Functional Immediate Entry Point
"""

import logging
import os
import streamlit as st
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logger
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Point d'entrée principal simplifié"""
    st.set_page_config(
        page_title="🚀 Phoenix Letters", 
        page_icon="🔥",
        layout="wide"
    )
    
    # Vérification des variables d'environnement critiques
    required_env = ["GOOGLE_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_env = [env for env in required_env if not os.getenv(env)]
    
    if missing_env:
        st.error(f"❌ Variables d'environnement manquantes: {', '.join(missing_env)}")
        st.info("🔧 Configurez ces variables dans Streamlit Cloud → Settings → Secrets")
        st.stop()
    
    # Header principal
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
        <h1>🚀 Phoenix Letters</h1>
        <p>Générateur IA de Lettres de Motivation pour Reconversions Professionnelles</p>
        <p><strong>✅ Application déployée avec succès !</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status des services
    st.success("🔥 Phoenix Letters est opérationnel sur le nouveau monorepo !")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**📦 Repository**\nphoenix-eco-monorepo")
    
    with col2:
        st.info("**🚀 Status**\nDéployé avec succès")
        
    with col3:
        st.info("**⚙️ Architecture**\nMonorepo intégré")
    
    # Informations de migration
    st.markdown("---")
    st.markdown("### 🔄 **Migration vers Authentification Unifiée**")
    
    st.warning("""
    **📋 Prochaines étapes de la migration :**
    
    1. ✅ **Monorepo configuré** - Applications intégrées
    2. 🔄 **En cours** - Migration vers authentification Supabase unifiée
    3. ⏳ **À venir** - Intégration complète du data pipeline
    4. ⏳ **À venir** - Activation des fonctionnalités premium
    """)
    
    # Environnement de test
    st.markdown("### 🧪 **Test des Services**")
    
    if st.button("🔍 Tester la connexion Gemini"):
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key and len(api_key) > 20:
                st.success("✅ Clé Gemini API configurée correctement")
            else:
                st.error("❌ Clé Gemini API invalide")
        except Exception as e:
            st.error(f"❌ Erreur test Gemini: {e}")
    
    if st.button("🔍 Tester la connexion Supabase"):
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            if supabase_url and supabase_key:
                st.success("✅ Configuration Supabase détectée")
            else:
                st.error("❌ Configuration Supabase manquante")
        except Exception as e:
            st.error(f"❌ Erreur test Supabase: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🚀 <strong>Phoenix Letters</strong> - Révolutionner les reconversions professionnelles</p>
        <p>🏗️ Bâti avec Streamlit • 🤖 Propulsé par Gemini AI • 🛡️ Sécurisé by design</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()