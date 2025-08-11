#!/usr/bin/env python3
"""
🌅 Phoenix Aube - Point d'entrée principal
Exploration carrière européenne avec IA validation
"""

import sys
import os

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Point d'entrée principal Phoenix Aube"""
    from phoenix_aube.ui.main import main as aube_main
    aube_main()

if __name__ == "__main__":
    main()