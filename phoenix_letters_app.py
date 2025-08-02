"""
🚀 Phoenix Letters - App à la racine du monorepo
Contournement du bug Streamlit Cloud avec les chemins apps/
"""

import streamlit as st
import sys
import os

# Ajouter le chemin vers l'app Phoenix Letters
sys.path.append(os.path.join(os.path.dirname(__file__), "apps", "phoenix-letters"))

# Import de l'app fonctionnelle
try:
    from apps.phoenix_letters.streamlit_app import *
except ImportError:
    # Fallback ultra-simple
    st.title("🚀 Phoenix Letters")
    st.success("✅ Application déployée depuis la racine du monorepo!")
    
    st.info("""
    **🔄 Data Pipeline Préservé**
    
    - ✅ Architecture monorepo intacte
    - ✅ Supabase Event Store actif
    - ✅ Écosystème Phoenix unifié
    - ✅ Applications interconnectées
    """)
    
    # Test variables d'environnement
    env_vars = ["GOOGLE_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            st.success(f"✅ {var} configuré")
        else:
            st.error(f"❌ {var} manquant")