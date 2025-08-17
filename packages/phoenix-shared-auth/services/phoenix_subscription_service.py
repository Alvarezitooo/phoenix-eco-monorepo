"""
💰 Phoenix Subscription Service - Gestion Abonnements Granulaires
Service de gestion des abonnements différenciés par application

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json

try:
    from supabase import Client
    from phoenix_shared_authentities.phoenix_subscription import (
        PhoenixUserSubscription, AppSubscriptionDetails, 
        SubscriptionTier, SubscriptionStatus, PhoenixApp,
        STRIPE_PRICE_IDS, BUNDLE_PRICE_IDS
    )
    from phoenix_shared_authdatabase.phoenix_db_connection import get_phoenix_db_connection
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

logger = logging.getLogger(__name__)


class PhoenixSubscriptionService:
    """
    Service de gestion des abonnements Phoenix
    Gère les abonnements granulaires par application avec synchronisation
    """
    
    def __init__(self, db_connection=None):
        self.supabase_available = SUPABASE_AVAILABLE
        self.db_client: Optional[Client] = None
        
        if self.supabase_available:
            try:
                if db_connection:
                    self.db_client = db_connection.client
                else:
                    db_conn = get_phoenix_db_connection()
                    self.db_client = db_conn.client
                logger.info("✅ PhoenixSubscriptionService initialisé avec Supabase")
            except Exception as e:
                logger.error(f"❌ Erreur initialisation Supabase: {e}")
                self.supabase_available = False
        
        if not self.supabase_available:
            logger.warning("⚠️ PhoenixSubscriptionService en mode dégradé")
    
    def get_user_subscription(self, user_id: str) -> PhoenixUserSubscription:
        """
        Récupère l'abonnement complet d'un utilisateur
        
        Args:
            user_id: ID utilisateur Phoenix
            
        Returns:
            PhoenixUserSubscription: Abonnement utilisateur
        """
        if not self.supabase_available or not self.db_client:
            # Mode dégradé - abonnement gratuit par défaut
            return PhoenixUserSubscription(user_id=user_id)
        
        try:
            # Récupérer abonnements depuis Supabase
            response = self.db_client.table('phoenix_subscriptions').select('*').eq('user_id', user_id).single().execute()
            
            if response.data:
                return PhoenixUserSubscription.from_dict(response.data)
            else:
                # Créer abonnement gratuit par défaut
                return self._create_default_subscription(user_id)
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération abonnement {user_id}: {e}")
            return PhoenixUserSubscription(user_id=user_id)
    
    def update_app_subscription(
        self, 
        user_id: str, 
        app: PhoenixApp, 
        tier: SubscriptionTier,
        stripe_subscription_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Met à jour l'abonnement pour une application spécifique
        
        Args:
            user_id: ID utilisateur Phoenix
            app: Application concernée
            tier: Nouveau tier d'abonnement
            stripe_subscription_id: ID abonnement Stripe
            metadata: Métadonnées additionnelles
            
        Returns:
            bool: Succès de la mise à jour
        """
        try:
            # Récupérer abonnement utilisateur
            user_subscription = self.get_user_subscription(user_id)
            
            # Déterminer statut selon tier
            status = SubscriptionStatus.ACTIVE if tier != SubscriptionTier.FREE else SubscriptionStatus.ACTIVE
            
            # Préparer données de mise à jour
            update_data = {
                "stripe_subscription_id": stripe_subscription_id,
                "stripe_price_id": STRIPE_PRICE_IDS.get(app, {}).get(tier),
                "current_period_start": datetime.now(),
                "current_period_end": datetime.now() + timedelta(days=30) if tier != SubscriptionTier.FREE else None
            }
            
            if metadata:
                update_data.update(metadata)
            
            # Mettre à jour abonnement
            success = user_subscription.update_app_subscription(
                app=app,
                tier=tier,
                status=status,
                **update_data
            )
            
            if success and self.supabase_available:
                # Sauvegarder en base
                self._save_subscription_to_db(user_subscription)
                
                # Synchroniser vers les applications
                self._sync_subscription_to_apps(user_id, app, tier)
            
            logger.info(f"✅ Abonnement {app.value} mis à jour pour {user_id}: {tier.value}")
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour abonnement {app.value} pour {user_id}: {e}")
            return False
    
    def subscribe_to_pack_cv_letters(
        self,
        user_id: str,
        stripe_subscription_id: str,
        payment_method_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Souscrit un utilisateur au pack CV + Letters
        
        Args:
            user_id: ID utilisateur Phoenix
            stripe_subscription_id: ID abonnement Stripe du pack
            payment_method_id: ID méthode de paiement
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        try:
            # Récupérer abonnement utilisateur
            user_subscription = self.get_user_subscription(user_id)
            
            # Activer le pack
            success = user_subscription.activate_pack_cv_letters(
                stripe_subscription_id=stripe_subscription_id,
                current_period_start=datetime.now(),
                current_period_end=datetime.now() + timedelta(days=30),
                payment_method_id=payment_method_id
            )
            
            if success and self.supabase_available:
                # Sauvegarder en base
                self._save_subscription_to_db(user_subscription)
                
                # Synchroniser vers les applications
                self._sync_subscription_to_apps(user_id, PhoenixApp.CV, SubscriptionTier.PREMIUM)
                self._sync_subscription_to_apps(user_id, PhoenixApp.LETTERS, SubscriptionTier.PREMIUM)
                
                # Enregistrer événement
                self._log_subscription_event(
                    user_id, PhoenixApp.WEBSITE, "pack_subscription_created", 
                    f"Pack CV + Letters activé (ID: {stripe_subscription_id})"
                )
            
            message = "Pack Phoenix CV + Letters activé avec succès ! 🔥" if success else "Erreur lors de l'activation du pack"
            return success, message
            
        except Exception as e:
            logger.error(f"❌ Erreur souscription pack CV + Letters pour {user_id}: {e}")
            return False, f"Erreur technique: {str(e)}"
    
    def subscribe_to_app(
        self, 
        user_id: str, 
        app: PhoenixApp, 
        tier: SubscriptionTier,
        stripe_subscription_id: str,
        payment_method_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Souscrit un utilisateur à une application
        
        Args:
            user_id: ID utilisateur Phoenix
            app: Application à souscrire
            tier: Tier d'abonnement
            stripe_subscription_id: ID abonnement Stripe
            payment_method_id: ID méthode de paiement
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        try:
            # Vérifier si déjà abonné
            current_subscription = self.get_user_subscription(user_id)
            current_app_sub = current_subscription.get_app_subscription(app)
            
            if current_app_sub.is_premium():
                return False, f"Utilisateur déjà abonné {tier.value} à {app.value}"
            
            # Mettre à jour abonnement
            success = self.update_app_subscription(
                user_id=user_id,
                app=app,
                tier=tier,
                stripe_subscription_id=stripe_subscription_id,
                metadata={
                    "payment_method_id": payment_method_id,
                    "subscription_source": "direct_app_purchase"
                }
            )
            
            if success:
                # Enregistrer événement
                self._log_subscription_event(
                    user_id, app, "subscription_created", 
                    f"Abonnement {tier.value} créé pour {app.value}"
                )
                
                return True, f"Abonnement {tier.value} activé pour {app.value}"
            else:
                return False, "Erreur lors de l'activation de l'abonnement"
                
        except Exception as e:
            logger.error(f"❌ Erreur souscription {app.value} pour {user_id}: {e}")
            return False, f"Erreur technique: {str(e)}"
    
    def cancel_app_subscription(
        self, 
        user_id: str, 
        app: PhoenixApp,
        cancel_immediately: bool = False
    ) -> Tuple[bool, str]:
        """
        Annule l'abonnement pour une application
        
        Args:
            user_id: ID utilisateur Phoenix
            app: Application concernée
            cancel_immediately: Annulation immédiate ou en fin de période
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        try:
            current_subscription = self.get_user_subscription(user_id)
            app_subscription = current_subscription.get_app_subscription(app)
            
            if not app_subscription.is_premium():
                return False, f"Aucun abonnement Premium actif pour {app.value}"
            
            if cancel_immediately:
                # Annulation immédiate - retour au gratuit
                success = self.update_app_subscription(
                    user_id=user_id,
                    app=app,
                    tier=SubscriptionTier.FREE,
                    metadata={"cancelled_at": datetime.now().isoformat()}
                )
                message = f"Abonnement {app.value} annulé immédiatement"
            else:
                # Annulation en fin de période
                current_subscription.update_app_subscription(
                    app=app,
                    tier=app_subscription.tier,
                    status=app_subscription.status,
                    cancel_at_period_end=True
                )
                
                if self.supabase_available:
                    self._save_subscription_to_db(current_subscription)
                
                success = True
                message = f"Abonnement {app.value} sera annulé en fin de période"
            
            if success:
                self._log_subscription_event(
                    user_id, app, "subscription_cancelled", message
                )
            
            return success, message
            
        except Exception as e:
            logger.error(f"❌ Erreur annulation abonnement {app.value} pour {user_id}: {e}")
            return False, f"Erreur technique: {str(e)}"
    
    def get_app_features(self, user_id: str, app: PhoenixApp) -> Dict[str, Any]:
        """
        Récupère les fonctionnalités disponibles pour un utilisateur sur une app
        
        Args:
            user_id: ID utilisateur Phoenix
            app: Application concernée
            
        Returns:
            Dict contenant les fonctionnalités disponibles
        """
        try:
            user_subscription = self.get_user_subscription(user_id)
            return user_subscription.get_app_features(app)
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération fonctionnalités {app.value} pour {user_id}: {e}")
            # Retour par défaut - fonctionnalités gratuites
            return {
                "subscription_tier": "free",
                "subscription_status": "active",
                "is_active": True,
                "is_premium": False,
                "error": str(e)
            }
    
    def check_feature_access(
        self, 
        user_id: str, 
        app: PhoenixApp, 
        feature: str
    ) -> Tuple[bool, str]:
        """
        Vérifie si un utilisateur a accès à une fonctionnalité
        
        Args:
            user_id: ID utilisateur Phoenix
            app: Application concernée
            feature: Nom de la fonctionnalité
            
        Returns:
            Tuple[bool, str]: (accès autorisé, message)
        """
        try:
            features = self.get_app_features(user_id, app)
            
            if feature in features:
                feature_value = features[feature]
                
                # Gestion des limites numériques
                if isinstance(feature_value, int):
                    if feature_value == -1:  # Illimité
                        return True, "Accès illimité"
                    elif feature_value > 0:
                        return True, f"Limite: {feature_value}"
                    else:
                        return False, "Limite atteinte"
                
                # Gestion des booléens
                elif isinstance(feature_value, bool):
                    return feature_value, "Fonctionnalité disponible" if feature_value else "Fonctionnalité Premium requise"
                
                # Gestion des chaînes
                else:
                    return True, f"Mode: {feature_value}"
            
            return False, "Fonctionnalité non trouvée"
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification accès {feature} pour {user_id}: {e}")
            return False, f"Erreur: {str(e)}"
    
    def get_subscription_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        Génère des recommandations d'abonnement personnalisées
        
        Args:
            user_id: ID utilisateur Phoenix
            
        Returns:
            Dict contenant les recommandations
        """
        try:
            user_subscription = self.get_user_subscription(user_id)
            summary = user_subscription.get_subscription_summary()
            
            recommendations = {
                "user_id": user_id,
                "current_status": summary,
                "recommendations": [],
                "potential_savings": 0,
                "upgrade_benefits": {}
            }
            
            premium_apps = summary["premium_apps"]
            free_apps = [
                app for app in ["cv", "letters", "rise"] 
                if app not in premium_apps
            ]
            
            # Recommandations selon le profil
            if len(premium_apps) == 0:
                # Utilisateur entièrement gratuit
                recommendations["recommendations"].append({
                    "type": "first_premium",
                    "title": "Découvrez Phoenix Premium",
                    "description": "Déverrouillez toutes les fonctionnalités avancées",
                    "suggested_app": "cv",  # App la plus populaire
                    "price": "9.99€/mois",
                    "benefits": ["CV illimités", "Templates premium", "Support prioritaire"]
                })
            
            elif len(premium_apps) == 1:
                # Un seul abonnement - proposer bundle
                other_app = "letters" if premium_apps[0] == "cv" else "cv"
                recommendations["recommendations"].append({
                    "type": "bundle_upgrade",
                    "title": f"Bundle CV + Letters",
                    "description": "Économisez 30% avec le bundle complet",
                    "current_cost": "9.99€/mois",
                    "bundle_cost": "14.99€/mois",
                    "savings": "4.99€/mois",
                    "benefits": ["Toutes les fonctionnalités", "Synchronisation avancée", "Support prioritaire"]
                })
                recommendations["potential_savings"] = 4.99
            
            # Recommandations par app non souscrite
            for app in free_apps:
                app_enum = PhoenixApp(app)
                features = user_subscription.get_app_features(app_enum)
                
                recommendations["upgrade_benefits"][app] = {
                    "current_limitations": self._get_free_limitations(app_enum),
                    "premium_benefits": self._get_premium_benefits(app_enum),
                    "upgrade_cost": "9.99€/mois"
                }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Erreur recommandations pour {user_id}: {e}")
            return {"error": str(e)}
    
    def _create_default_subscription(self, user_id: str) -> PhoenixUserSubscription:
        """Crée un abonnement gratuit par défaut"""
        subscription = PhoenixUserSubscription(user_id=user_id)
        
        if self.supabase_available:
            self._save_subscription_to_db(subscription)
        
        return subscription
    
    def _save_subscription_to_db(self, subscription: PhoenixUserSubscription) -> bool:
        """Sauvegarde l'abonnement en base de données"""
        try:
            if not self.db_client:
                return False
            
            data = subscription.to_dict()
            
            # Upsert (insert ou update)
            response = self.db_client.table('phoenix_subscriptions').upsert(data).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde abonnement: {e}")
            return False
    
    def _sync_subscription_to_apps(
        self, 
        user_id: str, 
        app: PhoenixApp, 
        tier: SubscriptionTier
    ):
        """Synchronise l'abonnement vers les applications"""
        try:
            # Créer event de synchronisation pour l'app
            if self.db_client:
                sync_data = {
                    "user_id": user_id,
                    "app": app.value,
                    "tier": tier.value,
                    "sync_timestamp": datetime.now().isoformat(),
                    "sync_type": "subscription_update"
                }
                
                self.db_client.table('phoenix_app_syncs').insert(sync_data).execute()
                
        except Exception as e:
            logger.error(f"❌ Erreur sync abonnement vers {app.value}: {e}")
    
    def _log_subscription_event(
        self, 
        user_id: str, 
        app: PhoenixApp, 
        event_type: str, 
        description: str
    ):
        """Enregistre un événement d'abonnement"""
        try:
            if self.db_client:
                event_data = {
                    "user_id": user_id,
                    "app": app.value,
                    "event_type": event_type,
                    "description": description,
                    "created_at": datetime.now().isoformat()
                }
                
                self.db_client.table('phoenix_subscription_events').insert(event_data).execute()
                
        except Exception as e:
            logger.error(f"❌ Erreur log événement abonnement: {e}")
    
    def _get_free_limitations(self, app: PhoenixApp) -> List[str]:
        """Récupère les limitations de la version gratuite"""
        limitations = {
            PhoenixApp.CV: [
                "Seulement 3 CV par mois",
                "5 templates de base",
                "Pas d'optimisation ATS",
                "Support email uniquement"
            ],
            PhoenixApp.LETTERS: [
                "Seulement 5 lettres par mois",
                "3 templates de base", 
                "IA basique",
                "Support email uniquement"
            ],
            PhoenixApp.RISE: [
                "2 sessions coaching par mois",
                "10 méditations",
                "Contenu limité",
                "Support email uniquement"
            ]
        }
        
        return limitations.get(app, [])
    
    def _get_premium_benefits(self, app: PhoenixApp) -> List[str]:
        """Récupère les avantages de la version Premium"""
        benefits = {
            PhoenixApp.CV: [
                "CV illimités",
                "20+ templates premium",
                "Optimisation ATS avancée",
                "Mirror Match algorithme",
                "Trajectory Builder",
                "Support prioritaire"
            ],
            PhoenixApp.LETTERS: [
                "Lettres illimitées",
                "15+ templates premium",
                "IA avancée Gemini",
                "Analyse d'offres d'emploi",
                "Génération batch",
                "Support prioritaire"
            ],
            PhoenixApp.RISE: [
                "Sessions coaching illimitées",
                "Méditations illimitées",
                "Contenu premium complet",
                "Roadmap personnalisée",
                "Communauté complète",
                "Support prioritaire"
            ]
        }
        
        return benefits.get(app, [])


# Instance singleton pour import facile
phoenix_subscription_service = None

def get_phoenix_subscription_service(db_connection=None) -> PhoenixSubscriptionService:
    """Factory function pour service d'abonnements Phoenix"""
    global phoenix_subscription_service
    if phoenix_subscription_service is None:
        phoenix_subscription_service = PhoenixSubscriptionService(db_connection)
    return phoenix_subscription_service