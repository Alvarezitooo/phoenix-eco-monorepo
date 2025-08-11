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
        # Import et lancement de Phoenix Aube main
        from phoenix_aube.ui.main import main as aube_main
        aube_main()
    except ImportError as e:
        import streamlit as st
        st.error(f"""
        ❌ **Erreur d'import Phoenix Aube**: {str(e)}
        
        **Solutions possibles:**
        1. Vérifiez que tous les packages sont installés
        2. Vérifiez la structure des dossiers
        3. Contactez le support Phoenix
        
        **Debug info:**
        - Répertoire actuel: {current_dir}
        - Répertoire Phoenix Aube: {aube_dir}
        - Python path: {sys.path[:3]}
        """)
        raise e

if __name__ == "__main__":
    main()