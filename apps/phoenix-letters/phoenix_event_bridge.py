"""
🌉 PHOENIX EVENT BRIDGE - Intégration Applications ↔ Event Store
Service d'intégration pour connecter Phoenix CV, Letters, Rise au Event Store Supabase
Simplifie l'Event-Sourcing pour les applications Streamlit existantes
"""

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)

# ========================================
# 📊 TYPES D'ÉVÉNEMENTS PHOENIX
# ========================================

class PhoenixEventType(Enum):
    """Types d'événements standardisés Phoenix"""
    # Événements utilisateur
    USER_REGISTERED = "UserRegistered"
    USER_LOGIN = "UserLogin"
    USER_LOGOUT = "UserLogout"
    USER_TIER_UPDATED = "UserTierUpdated"
    
    # Événements Phoenix CV
    CV_UPLOADED = "CVUploaded"
    CV_GENERATED = "CVGenerated"
    CV_OPTIMIZED = "CVOptimized"
    TEMPLATE_SELECTED = "TemplateSelected"
    ATS_SCORE_CALCULATED = "ATSScoreCalculated"
    
    # Événements Phoenix Letters
    LETTER_GENERATED = "LetterGenerated"
    JOB_OFFER_ANALYZED = "JobOfferAnalyzed"
    MIRROR_MATCH_PERFORMED = "MirrorMatchPerformed"
    PERSONALIZATION_APPLIED = "PersonalizationApplied"
    
    # Événements Phoenix Rise
    COACHING_SESSION_STARTED = "CoachingSessionStarted"
    COACHING_SESSION_COMPLETED = "CoachingSessionCompleted"
    MOOD_LOGGED = "MoodLogged"
    GOAL_SET = "GoalSet"
    PROGRESS_TRACKED = "ProgressTracked"
    
    # Événements système
    SKILL_ADDED = "SkillAdded"
    EXPERIENCE_ADDED = "ExperienceAdded"
    FEEDBACK_SUBMITTED = "FeedbackSubmitted"
    SUBSCRIPTION_ACTIVATED = "SubscriptionActivated"

@dataclass
class PhoenixEventData:
    """Structure données événement Phoenix"""
    event_type: PhoenixEventType
    user_id: str
    app_source: str  # cv, letters, rise
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

# ========================================
# 🌉 PHOENIX EVENT BRIDGE
# ========================================

class PhoenixEventBridge:
    """
    Pont entre les applications Phoenix et le Event Store Supabase
    Simplifie la publication et consommation d'événements
    """

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialise le bridge avec connexion Supabase
        
        Args:
            supabase_url: URL Supabase (env SUPABASE_URL si None)
            supabase_key: Clé Supabase (env SUPABASE_ANON_KEY si None)
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_ANON_KEY")
        
        # Mode dégradé si configuration manquante
        self.degraded_mode = False
        if not self.supabase_url or not self.supabase_key:
            self.degraded_mode = True
            logger.warning("⚠️ EventBridge en mode dégradé - Configuration Supabase manquante")
            # Configuration mock pour éviter les crashes
            self.supabase_url = "mock://localhost"
            self.supabase_key = "mock_key"
            self.supabase = None
        else:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        logger.info("✅ PhoenixEventBridge initialisé" + (" (mode dégradé)" if self.degraded_mode else ""))

    async def publish_event(self, event_data: PhoenixEventData) -> str:
        """
        Publie un événement dans le Event Store
        
        Args:
            event_data: Données de l'événement
            
        Returns:
            str: ID de l'événement créé
        """
        # Mode dégradé : log local uniquement
        if self.degraded_mode:
            mock_id = f"mock_{uuid.uuid4().hex[:8]}"
            logger.debug(f"🔄 Mode dégradé - Événement {event_data.event_type.value} logé localement (ID: {mock_id})")
            return mock_id
            
        try:
            # Préparer les données pour Supabase
            supabase_event = {
                "stream_id": event_data.user_id,
                "event_type": event_data.event_type.value,
                "payload": event_data.payload,
                "app_source": event_data.app_source,
                "timestamp": event_data.timestamp.isoformat(),
                "metadata": {
                    **event_data.metadata,
                    "bridge_version": "v1.0",
                    "published_at": datetime.now().isoformat()
                }
            }
            
            # Insérer dans Supabase
            response = self.supabase.table('events').insert(supabase_event).execute()
            
            if response.data:
                event_id = response.data[0]['event_id']
                logger.info(f"📤 Événement publié: {event_data.event_type.value} - {event_id}")
                return event_id
            else:
                raise Exception("Aucune donnée retournée par Supabase")
            
        except Exception as e:
            logger.error(f"❌ Erreur publication événement: {e}")
            raise

    async def get_user_events(self, user_id: str, app_source: str = None, 
                            event_types: List[PhoenixEventType] = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les événements d'un utilisateur
        
        Args:
            user_id: ID utilisateur
            app_source: Filtrer par application (optionnel)
            event_types: Filtrer par types d'événements (optionnel)
            limit: Nombre max d'événements
            
        Returns:
            List[Dict]: Liste des événements
        """
        try:
            query = self.supabase.table('events').select('*').eq('stream_id', user_id)
            
            if app_source:
                query = query.eq('app_source', app_source)
            
            if event_types:
                event_type_values = [et.value for et in event_types]
                query = query.in_('event_type', event_type_values)
            
            response = query.order('timestamp', desc=True).limit(limit).execute()
            
            logger.info(f"📥 Récupéré {len(response.data)} événements pour user {user_id}")
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération événements: {e}")
            return []

    async def get_ecosystem_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Génère des statistiques de l'écosystème Phoenix
        
        Args:
            days: Nombre de jours à analyser
            
        Returns:
            Dict: Statistiques globales
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            response = self.supabase.table('events')\
                .select('app_source, event_type, stream_id')\
                .gte('timestamp', cutoff_date.isoformat())\
                .execute()
            
            events = response.data
            
            # Calculs statistiques
            total_events = len(events)
            unique_users = len(set(event['stream_id'] for event in events))
            
            # Répartition par app
            app_stats = {}
            for event in events:
                app = event['app_source']
                if app not in app_stats:
                    app_stats[app] = {"events": 0, "users": set()}
                app_stats[app]["events"] += 1
                app_stats[app]["users"].add(event['stream_id'])
            
            # Convertir sets en counts
            for app in app_stats:
                app_stats[app]["unique_users"] = len(app_stats[app]["users"])
                del app_stats[app]["users"]
            
            # Top événements
            event_counts = {}
            for event in events:
                event_type = event['event_type']
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            top_events = dict(sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            stats = {
                "period_days": days,
                "total_events": total_events,
                "unique_users": unique_users,
                "avg_events_per_user": round(total_events / max(unique_users, 1), 2),
                "app_statistics": app_stats,
                "top_events": top_events,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"📊 Stats écosystème: {unique_users} utilisateurs, {total_events} événements")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur génération stats: {e}")
            return {}

# ========================================
# 🎯 HELPERS POUR APPLICATIONS PHOENIX
# ========================================

class PhoenixCVEventHelper:
    """Helper pour événements Phoenix CV"""
    
    def __init__(self, event_bridge: PhoenixEventBridge):
        self.bridge = event_bridge
    
    async def track_cv_uploaded(self, user_id: str, cv_filename: str, cv_size: int):
        """Trace le téléchargement d'un CV"""
        event = PhoenixEventData(
            event_type=PhoenixEventType.CV_UPLOADED,
            user_id=user_id,
            app_source="cv",
            payload={
                "filename": cv_filename,
                "size_bytes": cv_size,
                "upload_timestamp": datetime.now().isoformat()
            }
        )
        return await self.bridge.publish_event(event)
    
    async def track_cv_generated(self, user_id: str, template_name: str, ats_score: float, 
                               skills_count: int, experience_count: int):
        """Trace la génération d'un CV"""
        event = PhoenixEventData(
            event_type=PhoenixEventType.CV_GENERATED,
            user_id=user_id,
            app_source="cv",
            payload={
                "template_name": template_name,
                "ats_score": ats_score,
                "skills_count": skills_count,
                "experience_count": experience_count,
                "generation_timestamp": datetime.now().isoformat()
            }
        )
        return await self.bridge.publish_event(event)
    
    async def track_template_selected(self, user_id: str, template_id: str, template_category: str):
        """Trace la sélection d'un template"""
        event = PhoenixEventData(
            event_type=PhoenixEventType.TEMPLATE_SELECTED,
            user_id=user_id,
            app_source="cv",
            payload={
                "template_id": template_id,
                "template_category": template_category,
                "selection_timestamp": datetime.now().isoformat()
            }
        )
        return await self.bridge.publish_event(event)

class PhoenixLettersEventHelper:
    """Helper pour événements Phoenix Letters"""
    
    def __init__(self, event_bridge: PhoenixEventBridge):
        self.bridge = event_bridge
    
    async def track_letter_generated(self, user_id: str, job_title: str, company: str, 
                                   personalization_score: float, generation_time: float):
        """Trace la génération d'une lettre"""
        event = PhoenixEventData(
            event_type=PhoenixEventType.LETTER_GENERATED,
            user_id=user_id,
            app_source="letters",
            payload={
                "job_title": job_title,
                "company": company,
                "personalization_score": personalization_score,
                "generation_time_seconds": generation_time,
                "generation_timestamp": datetime.now().isoformat()
            }
        )
        return await self.bridge.publish_event(event)
    
    async def track_job_offer_analyzed(self, user_id: str, job_url: str, keywords_extracted: List[str],
                                     match_score: float):
        """Trace l'analyse d'une offre d'emploi"""
        event = PhoenixEventData(
            event_type=PhoenixEventType.JOB_OFFER_ANALYZED,
            user_id=user_id,
            app_source="letters",
            payload={
                "job_url": job_url,
                "keywords_extracted": keywords_extracted,
                "match_score": match_score,
                "analysis_timestamp": datetime.now().isoformat()
            }
        )
        return await self.bridge.publish_event(event)

class PhoenixRiseEventHelper:
    """Helper pour événements Phoenix Rise"""
    
    def __init__(self, event_bridge: PhoenixEventBridge):
        self.bridge = event_bridge
    
    async def track_coaching_session(self, user_id: str, session_type: str, duration_minutes: int,
                                   mood_before: int, mood_after: int):
        """Trace une session de coaching"""
        event = PhoenixEventData(
            event_type=PhoenixEventType.COACHING_SESSION_COMPLETED,
            user_id=user_id,
            app_source="rise",
            payload={
                "session_type": session_type,
                "duration_minutes": duration_minutes,
                "mood_before": mood_before,
                "mood_after": mood_after,
                "mood_improvement": mood_after - mood_before,
                "session_timestamp": datetime.now().isoformat()
            }
        )
        return await self.bridge.publish_event(event)
    
    async def track_mood_logged(self, user_id: str, mood_score: int, mood_tags: List[str],
                              notes: str = ""):
        """Trace l'enregistrement d'humeur"""
        event = PhoenixEventData(
            event_type=PhoenixEventType.MOOD_LOGGED,
            user_id=user_id,
            app_source="rise",
            payload={
                "mood_score": mood_score,
                "mood_tags": mood_tags,
                "notes": notes,
                "log_timestamp": datetime.now().isoformat()
            }
        )
        return await self.bridge.publish_event(event)

# ========================================
# 🚀 FACTORY POUR APPLICATIONS
# ========================================

class PhoenixEventFactory:
    """
    Factory pour créer facilement les helpers d'événements
    Simplifie l'intégration pour chaque application Phoenix
    """
    
    @staticmethod
    def create_bridge(supabase_url: str = None, supabase_key: str = None) -> PhoenixEventBridge:
        """Crée un Event Bridge"""
        return PhoenixEventBridge(supabase_url, supabase_key)
    
    @staticmethod
    def create_cv_helper(bridge: PhoenixEventBridge = None) -> PhoenixCVEventHelper:
        """Crée un helper pour Phoenix CV"""
        if bridge is None:
            bridge = PhoenixEventBridge()
        return PhoenixCVEventHelper(bridge)
    
    @staticmethod
    def create_letters_helper(bridge: PhoenixEventBridge = None) -> PhoenixLettersEventHelper:
        """Crée un helper pour Phoenix Letters"""
        if bridge is None:
            bridge = PhoenixEventBridge()
        return PhoenixLettersEventHelper(bridge)
    
    @staticmethod
    def create_rise_helper(bridge: PhoenixEventBridge = None) -> PhoenixRiseEventHelper:
        """Crée un helper pour Phoenix Rise"""
        if bridge is None:
            bridge = PhoenixEventBridge()
        return PhoenixRiseEventHelper(bridge)

# ========================================
# 🧪 EXEMPLES D'UTILISATION
# ========================================

async def example_phoenix_cv_integration():
    """Exemple d'intégration pour Phoenix CV"""
    # Créer les helpers
    cv_helper = PhoenixEventFactory.create_cv_helper()
    
    # Simuler des événements CV
    user_id = "user-example-cv"
    
    # 1. Upload CV
    await cv_helper.track_cv_uploaded(user_id, "mon_cv.pdf", 256000)
    
    # 2. Sélection template
    await cv_helper.track_template_selected(user_id, "template_modern", "professional")
    
    # 3. Génération CV
    await cv_helper.track_cv_generated(user_id, "Modern Pro", 87.5, 12, 3)
    
    logger.info("✅ Événements Phoenix CV publiés")

async def example_phoenix_letters_integration():
    """Exemple d'intégration pour Phoenix Letters"""
    letters_helper = PhoenixEventFactory.create_letters_helper()
    
    user_id = "user-example-letters"
    
    # 1. Analyse offre d'emploi
    await letters_helper.track_job_offer_analyzed(
        user_id, 
        "https://example-job.com/offer", 
        ["Python", "IA", "Streamlit"], 
        92.3
    )
    
    # 2. Génération lettre
    await letters_helper.track_letter_generated(
        user_id, 
        "Développeur IA", 
        "TechCorp", 
        89.7, 
        12.5
    )
    
    logger.info("✅ Événements Phoenix Letters publiés")

async def example_analytics():
    """Exemple d'analytics écosystème"""
    bridge = PhoenixEventFactory.create_bridge()
    
    # Stats globales
    stats = await bridge.get_ecosystem_stats(30)
    logger.info(f"📊 Stats écosystème: {stats}")
    
    # Événements utilisateur spécifique
    events = await bridge.get_user_events("user-example-cv", limit=10)
    logger.info(f"📥 Événements utilisateur: {len(events)}")

if __name__ == "__main__":
    # Tests des intégrations
    asyncio.run(example_phoenix_cv_integration())
    asyncio.run(example_phoenix_letters_integration())
    asyncio.run(example_analytics())