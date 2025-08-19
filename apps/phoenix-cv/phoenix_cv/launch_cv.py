#!/usr/bin/env python3
"""
🔄 REDIRECTION TEMPORAIRE - Phoenix CV Launch
Redirige vers main.py pour compatibilité cache Streamlit
"""

# Import et exécution directe du main
if __name__ == "__main__":
    # Import relatif car on est dans le même package
    from .main import main_modern
    main_modern()