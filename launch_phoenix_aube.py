#!/usr/bin/env python3
"""
🌅 Phoenix Aube - Lanceur depuis la racine du monorepo
Compatible Streamlit Cloud avec structure monorepo
"""

import sys
import os

# Ajouter les chemins nécessaires au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
aube_dir = os.path.join(current_dir, 'apps', 'phoenix-aube')
sys.path.insert(0, aube_dir)
sys.path.insert(0, current_dir)

def main():
    """Point d'entrée Phoenix Aube depuis la racine monorepo"""
    try:
        # Import direct - plus simple et compatible Streamlit Cloud
        sys.path.insert(0, os.path.join(aube_dir))
        
        # Import direct du module principal
        from streamlit_main import main as aube_main
        aube_main()
        
    except ImportError as e:
        import streamlit as st
        st.error(f"""
        ❌ **Erreur d'import Phoenix Aube**: {str(e)}
        
        **Debug info:**
        - Répertoire actuel: {current_dir}
        - Répertoire Phoenix Aube: {aube_dir}
        - Python path: {sys.path[:3]}
        - Fichier streamlit_main.py: {os.path.exists(os.path.join(aube_dir, 'streamlit_main.py'))}
        
        **Solutions:**
        1. Utilisez apps/phoenix-aube/streamlit_app.py comme main file
        2. Contactez le support Phoenix
        """)
        raise e
    except Exception as e:
        import streamlit as st
        st.error(f"❌ **Erreur Phoenix Aube**: {str(e)}")
        raise e

if __name__ == "__main__":
    main()