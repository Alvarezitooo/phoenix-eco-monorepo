"""
🏛️ Phoenix Letters - Stripe Price Manager
Gestionnaire centralisé des prix Stripe pour Letters
Conforme Contrat d'Exécution V5
"""

import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class LettersStripePriceManager:
    """Gestionnaire des prix Stripe spécifiques à Phoenix Letters"""
    
    def __init__(self):
        self._price_cache: Optional[Dict[str, str]] = None
    
    def get_price_ids(self) -> Dict[str, str]:
        """
        Récupère les price IDs Letters depuis le système centralisé Phoenix
        
        Returns:
            Dict avec les clés: letters_premium, bundle, cv_premium (pour cross-sell)
        """
        if self._price_cache is not None:
            return self._price_cache
        
        try:
            # Import du système centralisé
            from phoenix_shared_auth.entities.phoenix_subscription import (
                STRIPE_PRICE_IDS, BUNDLE_PRICE_IDS, PhoenixApp, SubscriptionTier
            )
            
            price_ids = {
                # Prix principal Letters
                "letters_premium": STRIPE_PRICE_IDS[PhoenixApp.LETTERS][SubscriptionTier.PREMIUM],
                
                # Bundle Letters + CV (offre principale)
                "bundle": BUNDLE_PRICE_IDS["phoenix_pack_cv_letters"],
                
                # CV Premium pour cross-sell
                "cv_premium": STRIPE_PRICE_IDS[PhoenixApp.CV][SubscriptionTier.PREMIUM],
            }
            
            # Cache pour éviter les re-imports
            self._price_cache = price_ids
            
            logger.info(f"✅ Prix Stripe Letters chargés: {list(price_ids.keys())}")
            return price_ids
            
        except ImportError as e:
            logger.error(f"❌ Import système centralisé échoué: {e}")
            # Fallback avec prix hardcodés (sécurité)
            return self._get_fallback_prices()
        
        except Exception as e:
            logger.error(f"❌ Erreur chargement prix Stripe: {e}")
            return self._get_fallback_prices()
    
    def _get_fallback_prices(self) -> Dict[str, str]:
        """
        Prix de fallback si le système centralisé est indisponible
        
        Returns:
            Prix hardcodés depuis les variables d'environnement ou constantes
        """
        logger.warning("🔄 Utilisation des prix de fallback")
        
        # Priorité: Variables d'environnement spécifiques
        fallback_prices = {
            "letters_premium": os.getenv("STRIPE_PRICE_LETTERS_PREMIUM", "price_1RraAcDcM3VIYgvyEBNFXfbR"),
            "bundle": os.getenv("STRIPE_PRICE_BUNDLE", "price_1RraWhDcM3VIYgvyGykPghCc"), 
            "cv_premium": os.getenv("STRIPE_PRICE_CV_PREMIUM", "price_1RraUoDcM3VIYgvy0NXiKmKV"),
        }
        
        return fallback_prices
    
    def get_price_id_for_product(self, product_type: str) -> Optional[str]:
        """
        Récupère un price ID spécifique
        
        Args:
            product_type: 'letters_premium', 'bundle', ou 'cv_premium'
            
        Returns:
            Price ID Stripe ou None si non trouvé
        """
        prices = self.get_price_ids()
        return prices.get(product_type)
    
    def validate_price_ids(self) -> Dict[str, bool]:
        """
        Valide que tous les price IDs sont présents et correctement formatés
        
        Returns:
            Dict avec le statut de validation pour chaque prix
        """
        prices = self.get_price_ids()
        validation = {}
        
        required_products = ["letters_premium", "bundle", "cv_premium"]
        
        for product in required_products:
            price_id = prices.get(product)
            is_valid = (
                price_id is not None and 
                isinstance(price_id, str) and
                price_id.startswith("price_") and
                len(price_id) > 10
            )
            validation[product] = is_valid
            
            if not is_valid:
                logger.error(f"❌ Price ID invalide pour {product}: {price_id}")
            else:
                logger.debug(f"✅ Price ID valide pour {product}")
        
        return validation
    
    def is_ready_for_production(self) -> bool:
        """
        Vérifie si les prix sont prêts pour la production
        
        Returns:
            True si tous les prix sont valides et présents
        """
        validation = self.validate_price_ids()
        all_valid = all(validation.values())
        
        if all_valid:
            logger.info("🚀 Prix Stripe Letters prêts pour production")
        else:
            invalid_products = [k for k, v in validation.items() if not v]
            logger.warning(f"⚠️ Prix invalides: {invalid_products}")
        
        return all_valid

# Instance globale pour l'application
letters_stripe_prices = LettersStripePriceManager()

def get_letters_stripe_prices() -> Dict[str, str]:
    """Helper function pour récupérer les prix Letters"""
    return letters_stripe_prices.get_price_ids()

def get_letters_price_id(product_type: str) -> Optional[str]:
    """Helper function pour récupérer un prix spécifique"""
    return letters_stripe_prices.get_price_id_for_product(product_type)