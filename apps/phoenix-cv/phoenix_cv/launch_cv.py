#!/usr/bin/env python3
"""
🔄 REDIRECTION TEMPORAIRE - Phoenix CV Launch
Redirige vers main.py pour compatibilité cache Streamlit
"""

import sys
import os
from pathlib import Path

# Configuration du PYTHONPATH pour les imports Phoenix
if __name__ == "__main__":
    # Ajouter le répertoire parent (apps/phoenix-cv/) au PYTHONPATH
    current_dir = Path(__file__).parent  # phoenix_cv/
    app_dir = current_dir.parent  # apps/phoenix-cv/
    monorepo_root = app_dir.parent.parent  # racine monorepo
    
    # Ajouter les chemins nécessaires
    sys.path.insert(0, str(app_dir))
    sys.path.insert(0, str(monorepo_root / "packages"))
    
    # Import et exécution
    from phoenix_cv.main import main_modern
    main_modern()