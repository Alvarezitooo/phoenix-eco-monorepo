"""
🚀 Phoenix Letters - Launcher avec Patch Architectural Runtime
Solution finale Gemini Pro Oracle - Injection explicite du workspace dans sys.path
"""

import sys
from pathlib import Path

# --- DÉBUT DU PATCH ARCHITECTURAL DE RUNTIME ---
# Objectif : Forcer l'interpréteur Python à reconnaître la structure du monorepo.

# 1. On détermine le chemin absolu de la racine du monorepo.
#    Path(__file__) est le chemin de ce script (launch_letters.py).
#    .resolve() nettoie le chemin (gère les '..', etc.).
#    .parent est le dossier qui contient ce script, donc la racine.
ROOT_DIR = Path(__file__).resolve().parent

# 2. On définit les chemins absolus vers nos dossiers sources de paquets.
APPS_DIR = ROOT_DIR / "apps"
PACKAGES_DIR = ROOT_DIR / "packages"

# 3. On ajoute ces chemins au sys.path de Python.
#    Ceci est la clé. L'interpréteur saura maintenant que 'apps' et 'packages'
#    sont des endroits où il peut trouver des modules de haut niveau.
#    Il pourra donc trouver 'phoenix_letters' dans 'apps'.
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))
# --- FIN DU PATCH ARCHITECTURAL DE RUNTIME ---

# 4. Maintenant que le chemin est correctement configuré, on tente l'import.
#    Cette fois, il ne peut pas échouer.
try:
    # L'import n'est plus relatif, c'est un import absolu
    # car 'apps' est maintenant dans le path.
    from phoenix_letters.phoenix_letters.app import main
    
except ModuleNotFoundError as e:
    import streamlit as st
    st.error(f"""
        **ERREUR D'IMPORTATION FATALE**

        Le patch du `sys.path` n'a pas suffi. Cela indique une incohérence
        dans la structure des dossiers par rapport au script de lancement.

        **État du `sys.path` au moment de l'erreur :**
        ```
        {sys.path}
        ```

        **Erreur originale :**
        `{e}`
    """)
    sys.exit()

# 5. On lance l'application.
if __name__ == "__main__":
    print("🔥 Patch architectural runtime activé - sys.path injecté")
    print(f"✅ APPS_DIR ajouté: {APPS_DIR}")
    print(f"✅ PACKAGES_DIR ajouté: {PACKAGES_DIR}")
    main()