# infrastructure/data-pipeline/app.py
# 🏛️ PHOENIX DATA PIPELINE - Point d'entrée Worker
# Event Bridge + User Profile Service

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configuration paths
current_dir = Path(__file__).resolve().parent
monorepo_root = current_dir.parent.parent
packages_dir = monorepo_root / "packages"

# Ajout des packages au path
if str(packages_dir) not in sys.path:
    sys.path.insert(0, str(packages_dir))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Point d'entrée principal du pipeline de données"""
    service_type = os.getenv("WORKER_TYPE", "event_bridge")
    
    logger.info(f"🚀 Démarrage Phoenix Data Pipeline - Type: {service_type}")
    
    if service_type == "event_bridge":
        from phoenix_event_bridge import main as event_bridge_main
        await event_bridge_main()
    elif service_type == "user_profile":
        from phoenix_user_profile_service.main import main as profile_main
        await profile_main()
    else:
        logger.error(f"Type de service non reconnu: {service_type}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())