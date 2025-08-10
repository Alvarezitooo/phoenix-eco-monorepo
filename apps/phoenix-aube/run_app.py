#!/usr/bin/env python3
"""
🔮 Phoenix Aube - Script de démarrage
Lanceur pour développement et production Phoenix Aube
"""

import sys
import os
import subprocess
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
app_root = Path(__file__).parent
sys.path.insert(0, str(app_root))

def run_streamlit():
    """Lance l'interface Streamlit Phoenix Aube"""
    print("🔮 Phoenix Aube - Démarrage interface Streamlit...")
    
    # Commande Streamlit avec configuration Phoenix Aube
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "phoenix_aube/ui/main.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--theme.primaryColor=#667eea",
        "--theme.backgroundColor=#ffffff",
        "--theme.secondaryBackgroundColor=#f0f2f6"
    ]
    
    try:
        subprocess.run(cmd, cwd=app_root, check=True)
    except KeyboardInterrupt:
        print("\n🔮 Phoenix Aube - Arrêt demandé par utilisateur")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du démarrage Streamlit: {e}")
        sys.exit(1)

def run_api():
    """Lance l'API FastAPI Phoenix Aube"""
    print("🔮 Phoenix Aube - Démarrage API FastAPI...")
    
    # Importer et lancer FastAPI avec Uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "phoenix_aube.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ Uvicorn non installé. Installez avec: pip install uvicorn")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🔮 Phoenix Aube - API arrêtée par utilisateur")

def run_both():
    """Lance API et Streamlit en parallèle (développement)"""
    import threading
    
    print("🔮 Phoenix Aube - Démarrage API + Interface...")
    
    # Thread pour l'API
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Attendre un peu que l'API démarre
    import time
    time.sleep(2)
    
    # Démarrer Streamlit dans le thread principal
    run_streamlit()

def show_help():
    """Affiche l'aide d'utilisation"""
    print("""
🔮 Phoenix Aube - Script de démarrage

Usage:
    python run_app.py [command]

Commands:
    streamlit    Lance uniquement l'interface Streamlit Trust by Design (défaut)
    api          Lance uniquement l'API FastAPI
    both         Lance API + Streamlit en parallèle (dev)
    trust        Lance interface Trust by Design directement
    help         Affiche cette aide

Exemples:
    python run_app.py                    # Interface Streamlit Trust by Design
    python run_app.py streamlit          # Interface Streamlit avec choix
    python run_app.py trust              # Trust by Design direct
    python run_app.py api               # API FastAPI
    python run_app.py both              # API + Interface

URLs par défaut:
    - Interface Streamlit: http://localhost:8501
    - API FastAPI: http://localhost:8000
    - Documentation API: http://localhost:8000/docs

Fonctionnalités Phoenix Aube:
    ✅ Exploration métier scientifique (Big Five + RIASEC)
    ✅ Validation IA future-proof (innovation européenne)  
    ✅ Transparency Engine (Trust by Design)
    ✅ Event Store Integration (écosystème Phoenix)
    ✅ Interface Trust by Design (UX transparente)
    """)

def check_dependencies():
    """Vérifie les dépendances essentielles"""
    required_packages = [
        "streamlit", "fastapi", "pydantic", "plotly", 
        "pandas", "uvicorn"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Packages manquants: {', '.join(missing)}")
        print("Installez avec: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Point d'entrée principal"""
    
    # Vérifier dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Analyser arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "streamlit"
    
    if command in ["help", "--help", "-h"]:
        show_help()
    elif command == "streamlit":
        run_streamlit()
    elif command == "api":
        run_api()
    elif command == "both":
        run_both()
    elif command == "trust":
        run_trust_interface()
    else:
        print(f"❌ Commande inconnue: {command}")
        print("Utilisez 'python run_app.py help' pour voir les options")
        sys.exit(1)

def run_trust_interface():
    """Lance directement l'interface Trust by Design"""
    print("🔮 Phoenix Aube - Interface Trust by Design...")
    
    # Commande Streamlit spécialement configurée pour Trust by Design
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "phoenix_aube/ui/trust_by_design_app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--theme.primaryColor=#1e3c72",
        "--theme.backgroundColor=#ffffff",
        "--theme.secondaryBackgroundColor=#f0f9ff"
    ]
    
    try:
        subprocess.run(cmd, cwd=app_root, check=True)
    except KeyboardInterrupt:
        print("\n🔮 Interface Trust by Design arrêtée")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur Trust by Design: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()