import sys
from pathlib import Path

# 1. On détermine la racine du monorepo.
ROOT_DIR = Path(__file__).resolve().parent

# 2. On ajoute le dossier 'apps' au chemin de Python.
#    Ceci permet à Python de trouver le paquet 'phoenix_cv'.
APPS_DIR = ROOT_DIR / "apps"
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

# 3. On importe et on exécute l'application.
try:
    # 🚀 ULTIMATE CACHE BUST - STREAMLIT_APP.PY 03/08/2025 10:30
    from phoenix_cv.phoenix_cv_app import main
    
    if __name__ == "__main__":
        main()

except Exception as e:
    import streamlit as st
    st.error("Une erreur est survenue lors du chargement de Phoenix CV.")
    st.exception(e)