"""
📊 IRIS ANALYTICS - Monitoring et métriques pour Iris API
Collecte des métriques business et techniques pour optimisation

Author: Claude Phoenix DevSecOps Guardian
Version: 2.0.0 - Production Analytics
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

from supabase import Client

logger = logging.getLogger(__name__)

class EventType(Enum):
    CHAT_REQUEST = "chat_request"
    CHAT_RESPONSE = "chat_response"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    RATE_LIMIT_HIT = "rate_limit_hit"
    ERROR = "error"
    USER_UPGRADE = "user_upgrade"

@dataclass
class IrisAnalyticsEvent:
    """Événement analytics Iris"""
    event_type: EventType
    user_id: Optional[str]
    user_tier: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]
    session_id: Optional[str] = None
    ip_hash: Optional[str] = None
    user_agent_hash: Optional[str] = None

class IrisAnalytics:
    """
    Service d'analytics pour Iris API
    Collecte métriques business et techniques pour optimisation
    """
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.batch_events: List[IrisAnalyticsEvent] = []
        self.batch_size = int(os.getenv("ANALYTICS_BATCH_SIZE", "50"))
        self.flush_interval = int(os.getenv("ANALYTICS_FLUSH_INTERVAL", "60"))  # secondes
        self._setup_analytics_tables()
        
        # Démarrer le flush périodique
        asyncio.create_task(self._periodic_flush())
    
    def _setup_analytics_tables(self):
        """S'assure que les tables analytics existent"""
        try:
            # Table pour les événements
            self.supabase.table('iris_events').select('id').limit(1).execute()
        except:
            logger.warning("Table iris_events non trouvée, création recommendée")
            
        try:
            # Table pour les métriques agrégées
            self.supabase.table('iris_metrics_daily').select('id').limit(1).execute() 
        except:
            logger.warning("Table iris_metrics_daily non trouvée, création recommendée")
    
    async def track_event(self, event: IrisAnalyticsEvent):
        """Enregistre un événement analytics"""
        try:
            # Anonymisation des données sensibles
            anonymized_event = self._anonymize_event(event)
            
            # Ajouter au batch
            self.batch_events.append(anonymized_event)
            
            # Flush si batch plein
            if len(self.batch_events) >= self.batch_size:
                await self._flush_events()
                
        except Exception as e:
            logger.error(f"Erreur tracking event: {e}")
    
    def _anonymize_event(self, event: IrisAnalyticsEvent) -> IrisAnalyticsEvent:
        """Anonymise les données sensibles pour RGPD"""
        import hashlib
        
        # Hash de l'user_id
        anonymized_user_id = None
        if event.user_id:
            anonymized_user_id = hashlib.sha256(f"{event.user_id}_analytics".encode()).hexdigest()[:16]
        
        # Hash de l'IP 
        anonymized_ip = None
        if event.ip_hash:
            anonymized_ip = hashlib.sha256(event.ip_hash.encode()).hexdigest()[:8]
        
        # Nettoyer les métadonnées sensibles
        clean_metadata = {}
        for key, value in event.metadata.items():
            if key not in ['email', 'password', 'token', 'personal_info']:
                if isinstance(value, str) and len(value) > 100:
                    clean_metadata[key] = value[:100] + "..."
                else:
                    clean_metadata[key] = value
        
        return IrisAnalyticsEvent(
            event_type=event.event_type,
            user_id=anonymized_user_id,
            user_tier=event.user_tier,
            timestamp=event.timestamp,
            metadata=clean_metadata,
            session_id=event.session_id,
            ip_hash=anonymized_ip,
            user_agent_hash=event.user_agent_hash
        )
    
    async def _flush_events(self):
        """Envoie le batch d'événements à Supabase"""
        if not self.batch_events:
            return
            
        try:
            # Convertir en format Supabase
            events_data = [
                {
                    'event_type': event.event_type.value,
                    'user_hash': event.user_id,
                    'user_tier': event.user_tier,
                    'timestamp': event.timestamp.isoformat(),
                    'metadata': json.dumps(event.metadata),
                    'session_id': event.session_id,
                    'ip_hash': event.ip_hash,
                    'user_agent_hash': event.user_agent_hash
                }
                for event in self.batch_events
            ]
            
            # Insérer en batch
            result = self.supabase.table('iris_events').insert(events_data).execute()
            
            logger.info(f"Analytics: {len(self.batch_events)} événements envoyés")
            self.batch_events.clear()
            
        except Exception as e:
            logger.error(f"Erreur flush analytics: {e}")
            # Garder les événements pour retry
            if len(self.batch_events) > self.batch_size * 2:
                # Éviter l'accumulation excessive
                self.batch_events = self.batch_events[-self.batch_size:]
    
    async def _periodic_flush(self):
        """Flush périodique des événements"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_events()
            except Exception as e:
                logger.error(f"Erreur flush périodique: {e}")
    
    # === MÉTHODES DE TRACKING SPÉCIALISÉES ===
    
    async def track_chat_request(
        self, 
        user_id: str, 
        user_tier: str, 
        message_length: int,
        app_context: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Track une requête de chat"""
        await self.track_event(IrisAnalyticsEvent(
            event_type=EventType.CHAT_REQUEST,
            user_id=user_id,
            user_tier=user_tier,
            timestamp=datetime.now(),
            metadata={
                'message_length': message_length,
                'app_context': app_context,
            },
            session_id=session_id
        ))
    
    async def track_chat_response(
        self,
        user_id: str,
        user_tier: str, 
        response_length: int,
        processing_time_ms: int,
        model_used: str,
        confidence: float,
        session_id: Optional[str] = None
    ):
        """Track une réponse de chat"""
        await self.track_event(IrisAnalyticsEvent(
            event_type=EventType.CHAT_RESPONSE,
            user_id=user_id,
            user_tier=user_tier,
            timestamp=datetime.now(),
            metadata={
                'response_length': response_length,
                'processing_time_ms': processing_time_ms,
                'model_used': model_used,
                'confidence': confidence,
            },
            session_id=session_id
        ))
    
    async def track_auth_failure(self, reason: str, ip_hash: Optional[str] = None):
        """Track un échec d'authentification"""
        await self.track_event(IrisAnalyticsEvent(
            event_type=EventType.AUTH_FAILURE,
            user_id=None,
            user_tier=None,
            timestamp=datetime.now(),
            metadata={'reason': reason},
            ip_hash=ip_hash
        ))
    
    async def track_rate_limit_hit(self, user_id: str, user_tier: str):
        """Track un dépassement de limite"""
        await self.track_event(IrisAnalyticsEvent(
            event_type=EventType.RATE_LIMIT_HIT,
            user_id=user_id,
            user_tier=user_tier,
            timestamp=datetime.now(),
            metadata={'tier': user_tier}
        ))
    
    async def track_error(
        self, 
        error_type: str, 
        error_message: str,
        user_id: Optional[str] = None,
        user_tier: Optional[str] = None
    ):
        """Track une erreur système"""
        await self.track_event(IrisAnalyticsEvent(
            event_type=EventType.ERROR,
            user_id=user_id,
            user_tier=user_tier,
            timestamp=datetime.now(),
            metadata={
                'error_type': error_type,
                'error_message': error_message[:200]  # Limité pour la DB
            }
        ))
    
    # === MÉTRIQUES BUSINESS ===
    
    async def get_daily_metrics(self, date: datetime) -> Dict[str, Any]:
        """Récupère les métriques d'une journée"""
        try:
            date_str = date.strftime('%Y-%m-%d')
            
            result = self.supabase.table('iris_metrics_daily').select('*').eq('date', date_str).single().execute()
            
            if result.data:
                return result.data
            else:
                # Calculer à la volée si pas en cache
                return await self._calculate_daily_metrics(date)
                
        except Exception as e:
            logger.error(f"Erreur récupération métriques: {e}")
            return {}
    
    async def _calculate_daily_metrics(self, date: datetime) -> Dict[str, Any]:
        """Calcule les métriques d'une journée à partir des événements"""
        try:
            date_start = date.strftime('%Y-%m-%d 00:00:00')
            date_end = date.strftime('%Y-%m-%d 23:59:59')
            
            # Requête des événements de la journée
            events = self.supabase.table('iris_events').select('*').gte('timestamp', date_start).lte('timestamp', date_end).execute()
            
            if not events.data:
                return {}
            
            # Calculs
            total_requests = len([e for e in events.data if e['event_type'] == 'chat_request'])
            total_responses = len([e for e in events.data if e['event_type'] == 'chat_response'])
            unique_users = len(set([e['user_hash'] for e in events.data if e['user_hash']]))
            
            # Répartition par tier
            tier_breakdown = {}
            for event in events.data:
                if event['user_tier']:
                    tier = event['user_tier']
                    tier_breakdown[tier] = tier_breakdown.get(tier, 0) + 1
            
            # Temps de réponse moyen
            response_times = [
                json.loads(e['metadata']).get('processing_time_ms', 0)
                for e in events.data
                if e['event_type'] == 'chat_response' and e['metadata']
            ]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            metrics = {
                'date': date.strftime('%Y-%m-%d'),
                'total_requests': total_requests,
                'total_responses': total_responses,
                'unique_users': unique_users,
                'avg_response_time_ms': round(avg_response_time, 2),
                'tier_breakdown': tier_breakdown,
                'calculated_at': datetime.now().isoformat()
            }
            
            # Sauvegarder en cache
            self.supabase.table('iris_metrics_daily').upsert(metrics, on_conflict='date').execute()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur calcul métriques: {e}")
            return {}
    
    async def get_user_analytics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Récupère les analytics d'un utilisateur"""
        try:
            # Hash de l'user_id comme dans les événements
            import hashlib
            user_hash = hashlib.sha256(f"{user_id}_analytics".encode()).hexdigest()[:16]
            
            # Récupérer les événements des derniers jours
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            events = self.supabase.table('iris_events').select('*').eq('user_hash', user_hash).gte('timestamp', since_date).execute()
            
            if not events.data:
                return {'message_count': 0, 'days_active': 0}
            
            # Calculs
            message_count = len([e for e in events.data if e['event_type'] == 'chat_request'])
            
            # Jours actifs
            active_dates = set([
                datetime.fromisoformat(e['timestamp']).strftime('%Y-%m-%d')
                for e in events.data
            ])
            
            return {
                'message_count': message_count,
                'days_active': len(active_dates),
                'last_activity': max([e['timestamp'] for e in events.data]) if events.data else None,
                'total_events': len(events.data)
            }
            
        except Exception as e:
            logger.error(f"Erreur analytics utilisateur: {e}")
            return {'error': str(e)}

# Fonction pour créer l'instance analytics
def create_analytics(supabase_client: Client) -> IrisAnalytics:
    """Crée une instance d'analytics"""
    return IrisAnalytics(supabase_client)