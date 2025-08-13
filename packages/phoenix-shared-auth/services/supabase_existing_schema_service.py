"""
🗄️ Phoenix Supabase Integration - Schéma Existant
Service d'intégration avec votre schéma Supabase existant optimisé

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Production Ready with Existing Schema
"""

import logging
import os
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
import json

try:
    from supabase import Client, create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

logger = logging.getLogger(__name__)

# Configuration Supabase (depuis variables d'environnement)
SUPABASE_CONFIG = {
    "url": os.getenv("SUPABASE_URL", "https://bfnkgodxpkdarpabigbg.supabase.co"),
    "key": os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmbmtnb2R4cGtkYXJwYWJpZ2JnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM5ODA0OTIsImV4cCI6MjA2OTU1NjQ5Mn0.-Fjb6YiSDf55nR6Esi9bKkOmpJeCVWrHfMJBm0e4kK8")
}


class PhoenixSupabaseExistingService:
    """
    Service d'intégration avec votre schéma Supabase existant
    Utilise les tables: profiles, user_subscriptions, cv_generations, letter_generations, user_activity_metrics
    """
    
    def __init__(self):
        self.supabase_available = SUPABASE_AVAILABLE
        self.client: Optional[Client] = None
        
        if self.supabase_available:
            try:
                self.client = create_client(SUPABASE_CONFIG["url"], SUPABASE_CONFIG["key"])
                logger.info("✅ Supabase connecté au schéma Phoenix existant")
            except Exception as e:
                logger.error(f"❌ Erreur connexion Supabase: {e}")
                self.supabase_available = False
        
        if not self.supabase_available:
            logger.warning("⚠️ Supabase non disponible")
    
    def get_or_create_user_profile(self, user_id: str, email: str, full_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Récupère ou crée un profil utilisateur dans la table profiles existante
        
        Args:
            user_id: ID utilisateur (UUID)
            email: Email utilisateur
            full_name: Nom complet optionnel
            
        Returns:
            Dict contenant les données du profil ou None
        """
        if not self.supabase_available or not self.client:
            return None
        
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_response = self.client.table('profiles').select('*').eq('id', user_id).execute()
            
            if existing_response.data:
                logger.info(f"✅ Profil existant trouvé: {email}")
                return existing_response.data[0]
            
            # Créer nouveau profil
            new_profile = {
                'id': user_id,
                'email': email,
                'full_name': full_name or email.split('@')[0],
                'subscription_tier': 'free',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = self.client.table('profiles').insert(new_profile).execute()
            
            if response.data:
                logger.info(f"✅ Nouveau profil créé: {email}")
                return response.data[0]
                
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur get/create profil pour {email}: {e}")
            return None
    
    def update_user_subscription(
        self, 
        user_id: str, 
        stripe_customer_id: str, 
        stripe_subscription_id: str,
        subscription_tier: str,
        current_period_start: datetime,
        current_period_end: datetime
    ) -> bool:
        """
        Met à jour ou crée un abonnement utilisateur dans user_subscriptions
        """
        if not self.supabase_available or not self.client:
            return False
        
        try:
            # Mettre à jour le tier dans profiles
            profile_update = self.client.table('profiles').update({
                'subscription_tier': subscription_tier,
                'updated_at': datetime.now().isoformat()
            }).eq('id', user_id).execute()
            
            # Vérifier si abonnement existe
            existing_sub = self.client.table('user_subscriptions').select('*').eq('user_id', user_id).execute()
            
            subscription_data = {
                'user_id': user_id,
                'stripe_customer_id': stripe_customer_id,
                'stripe_subscription_id': stripe_subscription_id,
                'subscription_tier': subscription_tier,
                'status': 'active',
                'current_period_start': current_period_start.isoformat(),
                'current_period_end': current_period_end.isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            if existing_sub.data:
                # Mettre à jour abonnement existant
                response = self.client.table('user_subscriptions').update(subscription_data).eq('user_id', user_id).execute()
                logger.info(f"✅ Abonnement mis à jour pour {user_id}: {subscription_tier}")
            else:
                # Créer nouvel abonnement
                subscription_data['created_at'] = datetime.now().isoformat()
                response = self.client.table('user_subscriptions').insert(subscription_data).execute()
                logger.info(f"✅ Nouvel abonnement créé pour {user_id}: {subscription_tier}")
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour abonnement {user_id}: {e}")
            return False
    
    def get_user_features(self, user_id: str, app_type: str) -> Dict[str, Any]:
        """
        Récupère les fonctionnalités disponibles selon l'abonnement
        
        Args:
            user_id: ID utilisateur
            app_type: 'cv' ou 'letters'
            
        Returns:
            Dict contenant les limites et fonctionnalités
        """
        if not self.supabase_available or not self.client:
            return self._get_default_free_features(app_type)
        
        try:
            # Récupérer profil utilisateur
            profile_response = self.client.table('profiles').select('subscription_tier').eq('id', user_id).execute()
            
            if not profile_response.data:
                return self._get_default_free_features(app_type)
            
            tier = profile_response.data[0]['subscription_tier']
            
            # Récupérer usage actuel
            current_usage = self.get_monthly_usage(user_id, app_type)
            
            # Retourner features selon tier
            if tier in ['premium', 'pro']:
                return self._get_premium_features(app_type, current_usage)
            else:
                return self._get_free_features(app_type, current_usage)
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération features {app_type} pour {user_id}: {e}")
            return self._get_default_free_features(app_type)
    
    def get_monthly_usage(self, user_id: str, app_type: str) -> Dict[str, int]:
        """
        Récupère l'usage mensuel depuis les tables de génération existantes
        """
        if not self.supabase_available or not self.client:
            return {}
        
        try:
            current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            usage = {}
            
            if app_type == 'cv':
                # Compter CV générés ce mois-ci
                cv_response = self.client.table('cv_generations').select('id').eq('user_id', user_id).gte('created_at', current_month_start.isoformat()).execute()
                usage['cv_count_monthly'] = len(cv_response.data) if cv_response.data else 0
                
            elif app_type == 'letters':
                # Compter lettres générées ce mois-ci  
                letters_response = self.client.table('letter_generations').select('id').eq('user_id', user_id).gte('created_at', current_month_start.isoformat()).execute()
                usage['letters_count_monthly'] = len(letters_response.data) if letters_response.data else 0
            
            return usage
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération usage {app_type} pour {user_id}: {e}")
            return {}
    
    def track_generation(self, user_id: str, app_type: str, generation_data: Dict[str, Any]) -> bool:
        """
        Enregistre une génération (CV ou lettre) dans les tables existantes
        """
        if not self.supabase_available or not self.client:
            return False
        
        try:
            if app_type == 'cv':
                cv_data = {
                    'user_id': user_id,
                    'template_used': generation_data.get('template', 'default'),
                    'generation_status': 'completed',
                    'cv_data': json.dumps(generation_data),
                    'generated_html': generation_data.get('html_content', ''),
                    'created_at': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
                }
                
                response = self.client.table('cv_generations').insert(cv_data).execute()
                
            elif app_type == 'letters':
                letter_data = {
                    'user_id': user_id,
                    'job_offer_text': generation_data.get('job_offer', ''),
                    'generated_letter': generation_data.get('letter_content', ''),
                    'generation_type': generation_data.get('type', 'standard'),
                    'ai_optimization_level': generation_data.get('optimization', 'basic'),
                    'created_at': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
                }
                
                response = self.client.table('letter_generations').insert(letter_data).execute()
            
            # Tracker l'activité dans user_activity_metrics
            self.track_user_activity(user_id, app_type, f'{app_type}_generation', generation_data)
            
            return bool(response.data if 'response' in locals() else False)
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement génération {app_type} pour {user_id}: {e}")
            return False
    
    def track_user_activity(self, user_id: str, app_source: str, action_type: str, metadata: Dict[str, Any]) -> bool:
        """
        Enregistre une activité utilisateur dans user_activity_metrics
        """
        if not self.supabase_available or not self.client:
            return False
        
        try:
            activity_data = {
                'user_id': user_id,
                'app_source': app_source,
                'action_type': action_type,
                'session_id': metadata.get('session_id', f'session_{int(datetime.now().timestamp())}'),
                'metadata': json.dumps(metadata),
                'timestamp': datetime.now().isoformat()
            }
            
            response = self.client.table('user_activity_metrics').insert(activity_data).execute()
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"❌ Erreur tracking activité pour {user_id}: {e}")
            return False
    
    def _get_free_features(self, app_type: str, current_usage: Dict[str, int]) -> Dict[str, Any]:
        """Fonctionnalités version gratuite avec usage actuel"""
        if app_type == 'cv':
            return {
                "cv_count_monthly": 3,
                "current_cv_usage": current_usage.get('cv_count_monthly', 0),
                "templates_count": 5,
                "ats_optimization": False,
                "mirror_match": False,
                "premium_templates": False,
                "trajectory_builder": False,
                "smart_coach_advanced": False,
                "export_formats": ["PDF"],
                "support_level": "email",
                "subscription_tier": "free",
                "is_premium": False
            }
        elif app_type == 'letters':
            return {
                "letters_count_monthly": 5,
                "current_letters_usage": current_usage.get('letters_count_monthly', 0),
                "templates_count": 3,
                "ai_optimization": "basic",
                "job_analysis": False,
                "premium_prompts": False,
                "batch_generation": False,
                "export_formats": ["TXT"],
                "support_level": "email",
                "subscription_tier": "free",
                "is_premium": False
            }
    
    def _get_premium_features(self, app_type: str, current_usage: Dict[str, int]) -> Dict[str, Any]:
        """Fonctionnalités version Premium avec usage actuel"""
        if app_type == 'cv':
            return {
                "cv_count_monthly": -1,  # Illimité
                "current_cv_usage": current_usage.get('cv_count_monthly', 0),
                "templates_count": 20,
                "ats_optimization": True,
                "mirror_match": True,
                "premium_templates": True,
                "trajectory_builder": True,
                "smart_coach_advanced": True,
                "export_formats": ["PDF", "DOCX", "HTML"],
                "support_level": "priority",
                "subscription_tier": "premium",
                "is_premium": True
            }
        elif app_type == 'letters':
            return {
                "letters_count_monthly": -1,  # Illimité
                "current_letters_usage": current_usage.get('letters_count_monthly', 0),
                "templates_count": 15,
                "ai_optimization": "advanced",
                "job_analysis": True,
                "premium_prompts": True,
                "batch_generation": True,
                "export_formats": ["TXT", "PDF", "DOCX"],
                "support_level": "priority",
                "subscription_tier": "premium",
                "is_premium": True
            }
    
    def _get_default_free_features(self, app_type: str) -> Dict[str, Any]:
        """Fonctionnalités par défaut en cas d'erreur"""
        return self._get_free_features(app_type, {})


# Instance singleton
phoenix_supabase_service = None

def get_phoenix_supabase_service() -> PhoenixSupabaseExistingService:
    """Factory function pour service Supabase Phoenix"""
    global phoenix_supabase_service
    if phoenix_supabase_service is None:
        phoenix_supabase_service = PhoenixSupabaseExistingService()
    return phoenix_supabase_service