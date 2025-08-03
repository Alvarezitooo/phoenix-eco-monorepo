import os
from pathlib import Path
import streamlit.web.bootstrap

# --- L'ULTIME PATCH ARCHITECTURAL ---

# 1. On détermine le chemin absolu vers le VRAI code source de l'application.
#    C'est la destination finale que nous voulons atteindre.
APP_ROOT = Path(__file__).resolve().parent / "apps" / "phoenix-letters" / "phoenix_letters"

# 2. On définit le fichier principal à lancer.
APP_FILE = APP_ROOT / "app.py"

# 3. LE DÉCRET FINAL : On change le répertoire de travail actuel de Python
#    pour qu'il soit à la racine du code de notre application.
#    À partir de maintenant, pour Python, tout se passe comme si nous étions
#    à l'intérieur de /apps/phoenix-letters/phoenix_letters/
os.chdir(APP_ROOT)

# 4. On utilise le mécanisme interne de Streamlit pour lancer l'application.
#    Ceci est plus robuste qu'un simple import. On donne un chemin absolu
#    et on s'assure qu'il n'y a aucune ambiguïté.
#    La commande `streamlit run app.py` sera exécutée, mais avec le
#    répertoire de travail que NOUS avons choisi.
streamlit.web.bootstrap.run(str(APP_FILE), command_line="", args=[], flag_options={})