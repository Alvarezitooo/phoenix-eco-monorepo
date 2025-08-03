import sys
from pathlib import Path

# --- CONFIGURATION DU CONTEXTE ---
APP_ROOT = Path(__file__).resolve().parent / "apps" / "phoenix-cv" / "phoenix_cv"

if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# --- IMPORT ET EXÉCUTION ---
from app import main

if __name__ == "__main__":
    main()