import sys
from pathlib import Path

# 1. On détermine la racine du monorepo.
ROOT_DIR = Path(__file__).resolve().parent

# 2. On ajoute le dossier de l'application 'phoenix-cv' au chemin Python.
#    Ceci permet des imports absolus cohérents comme 'from phoenix_cv.services...'.
APP_ROOT = ROOT_DIR / "apps" / "phoenix-cv"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# 3. Ajout explicite du répertoire racine pour éviter les erreurs d'import
MONOREPO_ROOT = ROOT_DIR
if str(MONOREPO_ROOT) not in sys.path:
    sys.path.insert(0, str(MONOREPO_ROOT))

# 3. On importe et on exécute l'application.
try:
    # 🔥 SYMMETRY PERFECT - LAUNCH_CV.PY 03/08/2025 11:00
    from phoenix_cv.phoenix_cv_app import main
    
    if __name__ == "__main__":
        main()

except Exception as e:
    import streamlit as st
    st.error("Une erreur est survenue lors du chargement de Phoenix CV.")
    st.exception(e)