import os
import sys
from pathlib import Path

# 1. On détermine le chemin absolu vers le VRAI code source de l'application.
APP_ROOT = Path(__file__).resolve().parent / "apps" / "phoenix-letters" / "phoenix_letters"

# 2. On change le répertoire de travail. C'EST LA CLÉ QUI A TOUT RÉSOLU.
os.chdir(APP_ROOT)

# 3. Maintenant que le contexte est parfait, on peut utiliser un import standard et stable.
#    Cette méthode est plus robuste que de dépendre d'une fonction interne de Streamlit.
try:
    # On importe la fonction main depuis le fichier app.py
    from app import main

except ImportError as e:
    import streamlit as st
    st.error(f"""
        **ERREUR D'IMPORTATION**
        Si vous voyez ceci, cela signifie que le fichier 'app.py' n'a pas été trouvé
        dans le répertoire de travail, ou que le fichier lui-même a une erreur d'import.

        **Répertoire de travail actuel (CWD) :**
        `{os.getcwd()}`

        **Erreur originale :**
        `{e}`
    """)
    sys.exit()

# 4. On exécute la fonction principale.
if __name__ == "__main__":
    main()