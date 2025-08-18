#!/usr/bin/env python3
"""
🏛️ Phoenix CV - Launcher Robuste pour Streamlit Cloud
Garantit le démarrage de Phoenix CV indépendamment de la structure de dossiers
"""

import sys
import os
from pathlib import Path
import importlib.util
import runpy

def find_phoenix_cv_app():
    """
    Trouve et retourne le chemin vers l'application Phoenix CV
    Utilise plusieurs stratégies de résolution pour garantir le succès
    """
    current_dir = Path(__file__).resolve().parent
    
    # Stratégie 1: Structure monorepo standard
    cv_app_path = current_dir / "apps" / "phoenix-cv" / "app.py"
    if cv_app_path.exists():
        return cv_app_path
    
    # Stratégie 2: Recherche récursive depuis la racine
    for pattern in ["**/phoenix-cv/app.py", "**/phoenix_cv/app.py", "**/cv/app.py"]:
        matches = list(current_dir.rglob(pattern))
        if matches:
            return matches[0]
    
    # Stratégie 3: Variables d'environnement
    if env_path := os.getenv("PHOENIX_CV_APP_PATH"):
        env_app_path = Path(env_path)
        if env_app_path.exists():
            return env_app_path
    
    # Stratégie 4: Chemins relatifs depuis différents points
    relative_paths = [
        "./apps/phoenix-cv/app.py",
        "../apps/phoenix-cv/app.py", 
        "./phoenix-cv/app.py",
        "./cv/app.py"
    ]
    
    for rel_path in relative_paths:
        abs_path = (current_dir / rel_path).resolve()
        if abs_path.exists():
            return abs_path
    
    return None

def setup_python_path(app_path: Path):
    """
    Configure le PYTHONPATH pour que tous les imports fonctionnent
    """
    # Ajouter la racine du monorepo
    monorepo_root = app_path.parent.parent.parent
    if str(monorepo_root) not in sys.path:
        sys.path.insert(0, str(monorepo_root))
    
    # Ajouter le dossier packages pour les imports phoenix_*
    packages_dir = monorepo_root / "packages"
    if packages_dir.exists() and str(packages_dir) not in sys.path:
        sys.path.insert(0, str(packages_dir))
    
    # Ajouter le dossier de l'app elle-même
    app_dir = app_path.parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

def launch_phoenix_cv():
    """
    Lance Phoenix CV avec gestion d'erreurs robuste
    """
    print("🚀 Démarrage Phoenix CV...")
    
    # Étape 1: Localiser l'application
    app_path = find_phoenix_cv_app()
    if not app_path:
        print("❌ ERREUR: Impossible de localiser Phoenix CV app.py")
        print("Vérifiez que le fichier existe dans apps/phoenix-cv/app.py")
        sys.exit(1)
    
    print(f"✅ Phoenix CV trouvé: {app_path}")
    
    # Étape 2: Configuration des chemins
    setup_python_path(app_path)
    print(f"✅ PYTHONPATH configuré")
    
    # Étape 3: Variables d'environnement pour Phoenix CV
    os.environ.setdefault("PHOENIX_APP", "cv")
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    
    # Étape 4: Lancement avec gestion d'erreurs
    try:
        # Méthode 1: runpy (préférée pour Streamlit)
        print("🎯 Lancement via runpy...")
        os.chdir(app_path.parent)
        runpy.run_path(str(app_path), run_name="__main__")
        
    except Exception as e1:
        print(f"⚠️ Méthode runpy échouée: {e1}")
        
        try:
            # Méthode 2: Import dynamique
            print("🔄 Tentative import dynamique...")
            spec = importlib.util.spec_from_file_location("phoenix_cv_app", app_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                raise ImportError("Impossible de créer le spec du module")
                
        except Exception as e2:
            print(f"❌ ÉCHEC CRITIQUE: {e2}")
            print(f"App path: {app_path}")
            print(f"Working dir: {os.getcwd()}")
            print(f"Python path: {sys.path[:3]}...")
            sys.exit(1)

if __name__ == "__main__":
    launch_phoenix_cv()