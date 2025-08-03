import os
from pathlib import Path
import streamlit as st
import sys

# --- CONFIGURATION DU CONTEXTE ---
APP_ROOT = Path(__file__).resolve().parent / "apps" / "phoenix-cv" / "phoenix_cv"
os.chdir(APP_ROOT)

# --- BLOC DE DÉBOGAGE D'IMPORTATION ---
st.set_page_config(layout="wide")
st.title("🕵️ Oracle's Debug Mode - Phoenix CV")
st.write(f"**Working Directory:** `{os.getcwd()}`")
st.write(f"**Python Path:** `{sys.path}`")

try:
    st.info("Attempting to import `main` from `app.py`...")
    
    # On tente d'importer la fonction principale
    from app import main
    
    st.success("✅ `from app import main` SUCCESSFUL!")
    st.info("Now attempting to run `main()`...")
    
    # Si l'import réussit, on exécute l'application
    main()

except ImportError as e:
    st.error(f"❌ IMPORT FAILED: An `ImportError` occurred.")
    st.write("This is the most likely cause of the issue. A module imported by `app.py` is missing or cannot be found.")
    st.exception(e) # AFFICHE LA TRACEBACK COMPLÈTE DE L'ERREUR D'IMPORT

except Exception as e:
    st.error(f"❌ EXECUTION FAILED: A non-import error occurred inside `app.py`.")
    st.write("The application was imported but crashed during execution.")
    st.exception(e) # AFFICHE LA TRACEBACK COMPLÈTE DE L'ERREUR