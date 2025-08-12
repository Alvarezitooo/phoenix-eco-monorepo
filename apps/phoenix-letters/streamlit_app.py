"""
🚀 Phoenix Letters - Point d'entrée Streamlit Cloud
Version simplifiée sans dépendances aux packages partagés

Author: Claude Phoenix DevSecOps Guardian  
Version: Streamlit Cloud Compatible
"""

import logging
import streamlit as st
import sys
import os

# Ajouter le répertoire de l'app au PYTHONPATH
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Point d'entrée principal pour Streamlit Cloud"""
    try:
        # Import de l'app Phoenix Letters locale
        from phoenix_letters.main import main as phoenix_main
        phoenix_main()
    except ImportError as e:
        logger.error(f"Erreur d'import Phoenix Letters: {e}")
        
        # Fallback vers une version simplifiée
        st.set_page_config(
            page_title="Phoenix Letters - IA de Motivation",
            page_icon="✍️",
            layout="wide"
        )
        
        st.title("🚀 Phoenix Letters")
        st.subheader("Générateur IA de Lettres de Motivation")
        
        st.error("""
        **Application en cours de maintenance**
        
        Phoenix Letters est temporairement indisponible en raison d'une mise à jour technique.
        
        **Alternatives disponibles :**
        - 🔍 [Phoenix CV](https://phoenix-cv.streamlit.app/) - Générateur de CV IA
        - 🎯 [Phoenix Rise](https://phoenix-rise.vercel.app/) - Coach carrière IA
        - 🌐 [Site Phoenix](https://phoenix-eco-monorepo.vercel.app/) - Découvrir l'écosystème
        """)
        
        st.info("💡 **Astuce** : Utilisez le site principal Phoenix pour accéder à toutes les applications")
        
        # Boutons de redirection
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Phoenix CV", use_container_width=True):
                st.markdown('[Rediriger vers Phoenix CV](https://phoenix-cv.streamlit.app/)')
                
        with col2:
            if st.button("🎯 Phoenix Rise", use_container_width=True):
                st.markdown('[Rediriger vers Phoenix Rise](https://phoenix-rise.vercel.app/)')
                
        with col3:
            if st.button("🌐 Site Phoenix", use_container_width=True):
                st.markdown('[Rediriger vers le site](https://phoenix-eco-monorepo.vercel.app/)')

if __name__ == "__main__":
    main()
