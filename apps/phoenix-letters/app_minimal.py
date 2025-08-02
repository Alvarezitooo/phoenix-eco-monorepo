"""
🚀 Phoenix Letters - Version Ultra-Minimale pour Diagnostic
Point d'entrée le plus simple possible pour éliminer toute erreur d'import
"""

import streamlit as st
import os

def main():
    st.set_page_config(page_title="Phoenix Letters", page_icon="🚀")
    
    st.title("🚀 Phoenix Letters - Test de Déploiement")
    st.success("✅ Application déployée avec succès !")
    
    # Test variables d'environnement
    st.subheader("🔍 Variables d'environnement")
    
    env_vars = [
        "GOOGLE_API_KEY",
        "SUPABASE_URL", 
        "SUPABASE_KEY",
        "JWT_SECRET_KEY",
        "PHOENIX_MASTER_KEY"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            st.success(f"✅ {var}: Configuré ({'*' * 8})")
        else:
            st.error(f"❌ {var}: Non configuré")
    
    st.info("🎯 Si vous voyez ce message, le déploiement fonctionne parfaitement !")

if __name__ == "__main__":
    main()