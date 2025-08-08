import sys
from pathlib import Path

# 1. On détermine la racine du monorepo.
ROOT_DIR = Path(__file__).resolve().parent

# 2. On ajoute le dossier phoenix-rise au chemin de Python.
#    Ceci permet à Python de trouver le paquet 'phoenix_rise'.
PHOENIX_RISE_DIR = ROOT_DIR / "apps" / "phoenix-rise"
if str(PHOENIX_RISE_DIR) not in sys.path:
    sys.path.insert(0, str(PHOENIX_RISE_DIR))

# 3. On importe et on exécute l'application.
try:
    # 🚀 PHOENIX RISE LAUNCHER - 03/08/2025
    from phoenix_rise.main import main
    
    if __name__ == "__main__":
        main()

except Exception as e:
    import streamlit as st
    st.error("Une erreur est survenue lors du chargement de Phoenix Rise.")
    st.exception(e)