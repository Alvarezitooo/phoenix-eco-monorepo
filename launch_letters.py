import sys
from pathlib import Path

# 1. On détermine le chemin absolu vers le VRAI code source de l'application.
APP_ROOT = Path(__file__).resolve().parent / "apps" / "phoenix-letters"

# 2. On ajoute le répertoire au sys.path au lieu de changer le CWD
#    Ceci évite de perturber Streamlit qui a besoin de la référence au script original
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# 3. Maintenant on peut importer directement depuis le code de l'application
try:
    # On importe la fonction main depuis le fichier main.py
    from main import main

except ImportError as e:
    import streamlit as st
    st.error(f"""
        **ERREUR D'IMPORTATION**
        
        **Répertoire app ajouté au sys.path :**
        `{APP_ROOT}`

        **Erreur originale :**
        `{e}`
    """)
    sys.exit()

# 4. On exécute la fonction principale.
if __name__ == "__main__":
    main()