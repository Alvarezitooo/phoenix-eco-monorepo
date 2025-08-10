"""
🧠 DATA FLYWHEEL - INTÉGRATION EVENT-SOURCING SUPABASE
Agent IA d'apprentissage continu connecté au Event Store Phoenix
Architecture hybride: IA locale + Event Store cloud
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

# Import Supabase
from supabase import Client, create_client

# Import direct du module local
from .data_flywheel_agent import DataFlywheelAgent, InteractionData, LearningPattern

logger = logging.getLogger(__name__)

# ========================================
# 📊 STRUCTURES EVENT-SOURCING
# ========================================

@dataclass
class PhoenixEvent:
    """Événement Phoenix standardisé"""
    event_id: str
    stream_id: str  # user_id
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    app_source: str  # cv, letters, rise
    version: int = 1
    metadata: Dict[str, Any] = None

@dataclass
class UserJourneyAnalysis:
    """Analyse du parcours utilisateur"""
    user_id: str
    total_events: int
    apps_used: List[str]
    reconversion_signals: List[str]
    success_indicators: List[str]
    recommendations: List[str]
    confidence_score: float
    last_activity: datetime

# ========================================
# 🧠 DATA FLYWHEEL EVENT CONSUMER
# ========================================

class DataFlywheelSupabaseConsumer:
    """
    Agent IA qui consomme les événements Supabase pour apprentissage continu
    Combine Event-Sourcing avec Intelligence Artificielle locale
    """

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialise le Data Flywheel avec connexion Supabase
        
        Args:
            supabase_url: URL Supabase (env SUPABASE_URL si None)
            supabase_key: Clé Supabase (env SUPABASE_KEY si None)
        """
        # Connexion Supabase
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL et SUPABASE_KEY requis")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Agent IA local pour analyse
        self.ai_agent = DataFlywheelAgent()
        
        # Cache des analyses récentes
        self.analysis_cache = {}
        self.cache_duration = timedelta(minutes=30)
        
        logger.info("✅ DataFlywheelSupabaseConsumer initialisé")

    async def consume_user_events(self, user_id: str, limit: int = 100) -> List[PhoenixEvent]:
        """
        Récupère les événements d'un utilisateur depuis Supabase
        
        Args:
            user_id: ID utilisateur
            limit: Nombre max d'événements
            
        Returns:
            List[PhoenixEvent]: Événements de l'utilisateur
        """
        try:
            response = self.supabase.table('events')\
                .select('*')\
                .eq('stream_id', user_id)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            events = []
            for event_data in response.data:
                event = PhoenixEvent(
                    event_id=event_data['event_id'],
                    stream_id=event_data['stream_id'],
                    event_type=event_data['event_type'],
                    payload=event_data['payload'],
                    timestamp=datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00')),
                    app_source=event_data['app_source'],
                    version=event_data.get('version', 1),
                    metadata=event_data.get('metadata', {})
                )
                events.append(event)
            
            logger.info(f"📥 Récupéré {len(events)} événements pour user {user_id}")
            return events
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération events: {e}")
            return []

    async def analyze_user_journey(self, user_id: str) -> UserJourneyAnalysis:
        """
        Analyse le parcours complet d'un utilisateur via Event-Sourcing
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            UserJourneyAnalysis: Analyse complète du parcours
        """
        # Vérifier cache
        cache_key = f"journey_{user_id}"
        if cache_key in self.analysis_cache:
            cached_analysis, cached_time = self.analysis_cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_analysis
        
        try:
            # Récupérer tous les événements
            events = await self.consume_user_events(user_id, limit=500)
            
            if not events:
                return UserJourneyAnalysis(
                    user_id=user_id,
                    total_events=0,
                    apps_used=[],
                    reconversion_signals=[],
                    success_indicators=[],
                    recommendations=["Commencez par créer un CV sur Phoenix CV"],
                    confidence_score=0.0,
                    last_activity=datetime.now()
                )
            
            # Analyser avec IA locale
            analysis = await self._analyze_events_with_ai(events)
            
            # Mettre en cache
            self.analysis_cache[cache_key] = (analysis, datetime.now())
            
            logger.info(f"🎯 Analyse parcours user {user_id} - Score: {analysis.confidence_score}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse parcours: {e}")
            return UserJourneyAnalysis(
                user_id=user_id,
                total_events=0,
                apps_used=[],
                reconversion_signals=[],
                success_indicators=[],
                recommendations=["Erreur d'analyse - Réessayez plus tard"],
                confidence_score=0.0,
                last_activity=datetime.now()
            )

    async def _analyze_events_with_ai(self, events: List[PhoenixEvent]) -> UserJourneyAnalysis:
        """
        Analyse les événements avec l'IA locale
        """
        user_id = events[0].stream_id
        apps_used = list(set(event.app_source for event in events))
        
        # Signaux de reconversion détectés
        reconversion_signals = []
        success_indicators = []
        
        # Analyse par type d'événement
        for event in events:
            if event.event_type == "CVGenerated":
                reconversion_signals.append("Création CV active")
                if event.payload.get("ats_score", 0) > 80:
                    success_indicators.append("CV haute qualité ATS")
            
            elif event.event_type == "LetterGenerated":
                reconversion_signals.append("Candidature active")
                if event.payload.get("personalization_score", 0) > 85:
                    success_indicators.append("Lettre hautement personnalisée")
            
            elif event.event_type == "CoachingSessionCompleted":
                success_indicators.append("Engagement coaching")
            
            elif event.event_type == "SkillAdded":
                reconversion_signals.append("Développement compétences")
        
        # Recommandations intelligentes
        recommendations = await self._generate_smart_recommendations(events, apps_used)
        
        # Score de confiance basé sur l'activité et la qualité
        confidence_score = self._calculate_confidence_score(events, success_indicators)
        
        return UserJourneyAnalysis(
            user_id=user_id,
            total_events=len(events),
            apps_used=apps_used,
            reconversion_signals=reconversion_signals,
            success_indicators=success_indicators,
            recommendations=recommendations,
            confidence_score=confidence_score,
            last_activity=events[0].timestamp if events else datetime.now()
        )

    async def _generate_smart_recommendations(self, events: List[PhoenixEvent], apps_used: List[str]) -> List[str]:
        """
        Génère des recommandations intelligentes basées sur le parcours
        """
        recommendations = []
        
        # Analyse de la séquence d'utilisation
        if "cv" in apps_used and "letters" not in apps_used:
            recommendations.append("💌 Créez une lettre de motivation avec Phoenix Letters")
        
        if "letters" in apps_used and "rise" not in apps_used:
            recommendations.append("🚀 Boostez votre motivation avec Phoenix Rise")
        
        if len(apps_used) >= 2:
            recommendations.append("🎯 Excellent! Vous utilisez l'écosystème Phoenix")
        
        # Analyse de la fréquence d'utilisation
        recent_events = [e for e in events if e.timestamp > datetime.now() - timedelta(days=7)]
        if len(recent_events) < 3:
            recommendations.append("⚡ Restez actif - 3 actions par semaine optimisent vos chances")
        
        # Recommandations basées sur la qualité
        low_quality_events = [e for e in events 
                            if e.payload.get("quality_score", 100) < 70]
        if len(low_quality_events) > 2:
            recommendations.append("📈 Améliorez la qualité avec nos templates premium")
        
        return recommendations or ["🌟 Continuez votre excellent travail!"]

    def _calculate_confidence_score(self, events: List[PhoenixEvent], success_indicators: List[str]) -> float:
        """
        Calcule un score de confiance pour la réussite de la reconversion
        """
        if not events:
            return 0.0
        
        # Score de base sur l'activité
        activity_score = min(len(events) / 10, 1.0) * 30  # Max 30 points
        
        # Score qualité des actions
        quality_score = len(success_indicators) * 15  # 15 points par indicateur
        
        # Score régularité (activité récente)
        recent_events = [e for e in events if e.timestamp > datetime.now() - timedelta(days=30)]
        regularity_score = min(len(recent_events) / 5, 1.0) * 25  # Max 25 points
        
        # Score diversité des apps
        apps_used = len(set(event.app_source for event in events))
        diversity_score = min(apps_used / 3, 1.0) * 10  # Max 10 points
        
        total_score = activity_score + quality_score + regularity_score + diversity_score
        return min(total_score, 100.0)

    async def store_ai_insights(self, user_id: str, insights: Dict[str, Any]) -> bool:
        """
        Stocke les insights IA générés comme événements
        
        Args:
            user_id: ID utilisateur
            insights: Insights générés par l'IA
            
        Returns:
            bool: Succès du stockage
        """
        try:
            event_data = {
                "stream_id": user_id,
                "event_type": "AIInsightsGenerated", 
                "payload": insights,
                "app_source": "flywheel",
                "metadata": {
                    "ai_version": "data_flywheel_v2",
                    "generation_timestamp": datetime.now().isoformat()
                }
            }
            
            response = self.supabase.table('events').insert(event_data).execute()
            
            logger.info(f"💾 Insights IA stockés pour user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage insights: {e}")
            return False

    async def get_ecosystem_analytics(self) -> Dict[str, Any]:
        """
        Génère des analytics globales de l'écosystème Phoenix
        
        Returns:
            Dict: Analytics de l'écosystème
        """
        try:
            # Stats globales sur 30 derniers jours
            cutoff_date = datetime.now() - timedelta(days=30)
            
            response = self.supabase.table('events')\
                .select('app_source, event_type, stream_id')\
                .gte('timestamp', cutoff_date.isoformat())\
                .execute()
            
            events = response.data
            
            # Calculs analytics
            total_events = len(events)
            unique_users = len(set(event['stream_id'] for event in events))
            app_usage = {}
            
            for event in events:
                app = event['app_source']
                app_usage[app] = app_usage.get(app, 0) + 1
            
            # Events populaires
            event_types = [event['event_type'] for event in events]
            popular_events = dict(sorted(
                {event: event_types.count(event) for event in set(event_types)}.items(),
                key=lambda x: x[1], reverse=True
            )[:5])
            
            analytics = {
                "period": "30_days",
                "total_events": total_events,
                "unique_users": unique_users,
                "app_usage": app_usage,
                "popular_events": popular_events,
                "avg_events_per_user": round(total_events / max(unique_users, 1), 2),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"📊 Analytics écosystème: {unique_users} utilisateurs, {total_events} événements")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Erreur analytics écosystème: {e}")
            return {}

# ========================================
# 🚀 INTERFACE API FLYWHEEL
# ========================================

class DataFlywheelAPI:
    """
    API REST pour le Data Flywheel avec Event-Sourcing
    """
    
    def __init__(self):
        self.consumer = DataFlywheelSupabaseConsumer()
    
    async def analyze_user(self, user_id: str) -> Dict[str, Any]:
        """Endpoint: Analyse d'un utilisateur"""
        analysis = await self.consumer.analyze_user_journey(user_id)
        return asdict(analysis)
    
    async def get_recommendations(self, user_id: str) -> List[str]:
        """Endpoint: Recommandations pour un utilisateur"""
        analysis = await self.consumer.analyze_user_journey(user_id)
        return analysis.recommendations
    
    async def get_ecosystem_stats(self) -> Dict[str, Any]:
        """Endpoint: Statistiques globales écosystème"""
        return await self.consumer.get_ecosystem_analytics()

# ========================================
# 🧪 TESTS & EXEMPLES
# ========================================

async def test_flywheel_integration():
    """Test de l'intégration Event-Sourcing"""
    try:
        consumer = DataFlywheelSupabaseConsumer()
        
        # Test avec un user fictif
        test_user_id = "test-user-123"
        
        # Analyser le parcours
        analysis = await consumer.analyze_user_journey(test_user_id)
        print(f"✅ Analyse: {analysis.total_events} événements")
        print(f"📱 Apps utilisées: {analysis.apps_used}")
        print(f"🎯 Score confiance: {analysis.confidence_score}%")
        print(f"💡 Recommandations: {analysis.recommendations}")
        
        # Analytics globales
        ecosystem_stats = await consumer.get_ecosystem_analytics()
        print(f"📊 Stats écosystème: {ecosystem_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test échoué: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration
    asyncio.run(test_flywheel_integration())