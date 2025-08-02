"""
🚀 Phoenix Letters - Launcher pour Application Originale
Point d'entrée à la racine pour contourner les limitations monorepo

Solution Gemini Pro Oracle - Utilise l'application Phoenix Letters complète
Redirection vers l'application originale avancée avec toutes ses fonctionnalités
"""

import os
import sys

# Ajouter le chemin de l'application au sys.path pour permettre les imports
app_path = os.path.join(os.path.dirname(__file__), 'apps', 'phoenix-letters')
sys.path.insert(0, app_path)

# Point d'entrée principal avec fallback intelligent vers l'app originale
if __name__ == "__main__":
    try:
        # Essayer d'importer l'application Phoenix Letters complète
        from app import main
        main()
    except ImportError as e:
        # Si problème d'import, essayer l'app legacy
        try:
            from app_legacy import main
            main()
        except ImportError:
            # Fallback final - version ultra-simple
            import streamlit as st
            
            st.set_page_config(
                page_title="🚀 Phoenix Letters",
                page_icon="🔥",
                layout="wide"
            )
            
            st.error("❌ Impossible de charger l'application Phoenix Letters")
            st.info("🔧 Problème d'import détecté - Vérifiez la configuration")
            st.code(f"Erreur: {str(e)}")
            
            st.markdown("""
            ### 🚀 Phoenix Letters - Launcher Actif
            
            Le launcher fonctionne mais l'application complète n'a pas pu être chargée.
            
            **Architecture monorepo avec pattern Gemini Pro Oracle ✅**
            """)

def main():
    """Point d'entrée depuis les imports directs"""
    # Cette fonction sera surchargée par l'import de l'app originale
    pass