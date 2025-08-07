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

# 4. Debug pour Streamlit Cloud - Vérifier les chemins
import os
print(f"DEBUG - Current working directory: {os.getcwd()}")
print(f"DEBUG - ROOT_DIR: {ROOT_DIR}")
print(f"DEBUG - APP_ROOT: {APP_ROOT}")
print(f"DEBUG - sys.path premiers éléments: {sys.path[:3]}")
print(f"DEBUG - Phoenix CV existe: {os.path.exists(APP_ROOT)}")
print(f"DEBUG - Models existe: {os.path.exists(APP_ROOT / 'phoenix_cv' / 'models')}")
print(f"DEBUG - user_profile.py existe: {os.path.exists(APP_ROOT / 'phoenix_cv' / 'models' / 'user_profile.py')}")
print(f"DEBUG - Contenu du répertoire phoenix_cv: {os.listdir(APP_ROOT / 'phoenix_cv') if os.path.exists(APP_ROOT / 'phoenix_cv') else 'N/A'}")
print(f"DEBUG - Contenu models: {os.listdir(APP_ROOT / 'phoenix_cv' / 'models') if os.path.exists(APP_ROOT / 'phoenix_cv' / 'models') else 'N/A'}")

# 3. On importe et on exécute l'application.
try:
    # 🔥 SYMMETRY PERFECT - LAUNCH_CV.PY 03/08/2025 11:00
    from phoenix_cv.main import main
    
    if __name__ == "__main__":
        main()

except Exception as e:
    import streamlit as st
    st.error("Une erreur est survenue lors du chargement de Phoenix CV.")
    st.exception(e)