#!/usr/bin/env python3
"""
🚀 IRIS AGENT STARTUP SCRIPT - Démarrage sécurisé de l'agent Iris
Script de démarrage avec vérifications de sécurité et configuration.
"""

import os
import sys
import logging
from pathlib import Path

def setup_logging():
    """Configure le système de logging sécurisé."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('iris_agent.log', mode='a')
        ]
    )
    return logging.getLogger(__name__)

def validate_environment():
    """Valide la configuration d'environnement."""
    logger = logging.getLogger(__name__)
    
    required_vars = [
        'GEMINI_API_KEY',
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Variables d'environnement manquantes: {missing_vars}")
        logger.info("Copiez .env.example vers .env et configurez les variables requises")
        return False
    
    # Validation de la clé Gemini
    gemini_key = os.getenv('GEMINI_API_KEY')
    if len(gemini_key) < 30:
        logger.error("GEMINI_API_KEY semble invalide (trop courte)")
        return False
    
    logger.info("✅ Configuration d'environnement valide")
    return True

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées."""
    logger = logging.getLogger(__name__)
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'google.generativeai',
        'jwt',
        'bcrypt'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Packages manquants: {missing_packages}")
        logger.info("Installez avec: poetry install")
        return False
    
    logger.info("✅ Toutes les dépendances sont disponibles")
    return True

def load_env_file():
    """Charge le fichier .env si présent."""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)

def start_iris_agent():
    """Lance l'agent Iris avec uvicorn."""
    import uvicorn
    
    # Configuration uvicorn sécurisée
    config = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": 8003,
        "log_level": os.getenv('IRIS_LOG_LEVEL', 'info').lower(),
        "reload": os.getenv('IRIS_ENV', 'production') == 'development',
        "access_log": True,
    }
    
    # En production, désactiver le reload et certaines features debug
    if os.getenv('IRIS_ENV', 'production') == 'production':
        config.update({
            "reload": False,
            "debug": False,
        })
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Démarrage d'Iris Agent...")
    logger.info(f"Configuration: {config}")
    
    uvicorn.run(**config)

if __name__ == "__main__":
    # Setup initial logging
    logger = setup_logging()
    
    logger.info("🤖 IRIS AGENT - Démarrage du système")
    
    # Load environment file
    load_env_file()
    
    # Validations pre-flight
    if not validate_environment():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # All checks passed, start the agent
    try:
        start_iris_agent()
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt d'Iris Agent par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur critique lors du démarrage: {e}")
        sys.exit(1)