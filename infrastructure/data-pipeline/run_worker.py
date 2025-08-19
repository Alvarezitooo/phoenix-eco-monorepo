#!/usr/bin/env python3
"""
🚀 Phoenix Event Bridge - Background Worker
Point d'entrée pour le service worker Render

Ce script lance l'Event Bridge en mode background worker
pour traiter les événements en continu.
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

# Configuration paths monorepo  
MONOREPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(MONOREPO_ROOT))

# Import depuis packages/ - Architecture Monorepo
from packages.phoenix_shared_auth.client import get_supabase_client

# Import du Event Bridge principal
from infrastructure.data-pipeline.phoenix_event_bridge import PhoenixEventBridge

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("phoenix.worker")

class WorkerManager:
    """Gestionnaire du worker Event Bridge"""
    
    def __init__(self):
        self.running = True
        self.event_bridge = None
        
    async def initialize(self):
        """Initialise l'Event Bridge"""
        try:
            # Vérification des variables d'environnement
            required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                raise EnvironmentError(f"Variables manquantes: {missing_vars}")
            
            # Initialisation Event Bridge
            supabase_client = get_supabase_client()
            self.event_bridge = PhoenixEventBridge(supabase_client)
            
            logger.info("🚀 Event Bridge initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Event Bridge: {e}")
            return False
    
    async def run(self):
        """Lance le worker en continu"""
        logger.info("🔄 Démarrage du worker Event Bridge...")
        
        if not await self.initialize():
            logger.error("💥 Échec initialisation - Arrêt du worker")
            return
        
        try:
            while self.running:
                # Traitement des événements en continu
                await self.event_bridge.process_pending_events()
                
                # Pause entre les cycles
                await asyncio.sleep(5)  # 5 secondes entre les cycles
                
        except asyncio.CancelledError:
            logger.info("🛑 Worker arrêté gracieusement")
        except Exception as e:
            logger.error(f"💥 Erreur critique dans le worker: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Nettoyage à l'arrêt"""
        logger.info("🧹 Nettoyage du worker...")
        if self.event_bridge:
            await self.event_bridge.cleanup()
    
    def stop(self):
        """Arrête le worker"""
        logger.info("🛑 Demande d'arrêt du worker...")
        self.running = False

# Gestionnaire de signaux pour arrêt gracieux
worker_manager = WorkerManager()

def signal_handler(signum, frame):
    """Gestionnaire pour SIGTERM/SIGINT"""
    logger.info(f"📡 Signal {signum} reçu - Arrêt gracieux...")
    worker_manager.stop()

def main():
    """Point d'entrée principal du worker"""
    logger.info("🔥 Phoenix Event Bridge Worker - Démarrage")
    
    # Configuration signaux
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Lance le worker async
        asyncio.run(worker_manager.run())
    except KeyboardInterrupt:
        logger.info("⌨️ Interruption clavier - Arrêt...")
    except Exception as e:
        logger.error(f"💥 Erreur fatale: {e}")
        sys.exit(1)
    
    logger.info("👋 Worker Event Bridge arrêté")

if __name__ == "__main__":
    main()