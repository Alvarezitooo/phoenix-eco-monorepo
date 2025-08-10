"""
🔮 Phoenix Aube - Premier outil européen d'exploration métier + validation IA

Innovation différenciante : Transformer la peur de l'IA en superpouvoir professionnel
pour les reconversions professionnelles.

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - MVP Foundation
"""

__version__ = "1.0.0"
__author__ = "Claude Phoenix DevSecOps Guardian"
__email__ = "contact.phoenixletters@gmail.com"

# Configuration logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("🔮 Phoenix Aube - Exploration métier IA-proof initialisé")

__all__ = ["__version__", "__author__", "logger"]