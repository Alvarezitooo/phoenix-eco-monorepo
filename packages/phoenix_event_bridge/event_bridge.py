"""
🌉 Phoenix Event Bridge - Architecture Event-Sourcing
Pont d'événements pour l'écosystème Phoenix selon la vision stratégique

Author: Claude Phoenix DevSecOps Guardian  
Version: 1.0.0 - Strategic Vision Implementation
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import asyncio

from .phoenix_event_types import PhoenixEventData, PhoenixEventType, PhoenixEventStream

logger = logging.getLogger(__name__)

class PhoenixEventBridge:
    """
    Pont d'événements principal pour l'architecture Event-Sourcing Phoenix
    
    Responsabilités:
    - Publication d'événements vers Event Store
    - Routage vers consumers appropriés  
    - Persistance dans Supabase
    - Gestion des retry et erreurs
    """
    
    def __init__(self, supabase_client=None):
        """Initialise le bridge avec client Supabase optionnel"""
        self.supabase_client = supabase_client
        self.event_handlers: Dict[PhoenixEventType, List[Callable]] = {}
        self.streams: Dict[str, PhoenixEventStream] = {}
        
        # Configuration depuis environment
        self.enable_persistence = os.getenv("PHOENIX_EVENT_PERSISTENCE", "true").lower() == "true"
        self.enable_logging = os.getenv("PHOENIX_EVENT_LOGGING", "true").lower() == "true"
        
        if self.enable_logging:
            logger.info("✅ PhoenixEventBridge initialized")
    
    async def publish_event(self, event: PhoenixEventData) -> bool:
        """
        Publie un événement dans l'écosystème
        
        Args:
            event: Événement à publier
            
        Returns:
            bool: Succès de la publication
        """
        try:
            # 1. Validation de l'événement
            if not self._validate_event(event):
                logger.error(f"❌ Invalid event: {event.event_id}")
                return False
            
            # 2. Logging de l'événement
            if self.enable_logging:
                logger.info(f"📤 Publishing event: {event.event_type.value} for {event.stream_id}")
            
            # 3. Ajouter à l'Event Stream local
            self._add_to_stream(event)
            
            # 4. Persistance en base si configurée
            if self.enable_persistence and self.supabase_client:
                success = await self._persist_to_supabase(event)
                if not success:
                    logger.warning(f"⚠️ Failed to persist event {event.event_id} to Supabase")
            
            # 5. Notification des handlers
            await self._notify_handlers(event)
            
            # 6. Log de succès
            if self.enable_logging:
                logger.info(f"✅ Event published: {event.event_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error publishing event {event.event_id}: {e}")
            return False
    
    async def _persist_to_supabase(self, event: PhoenixEventData) -> bool:
        """Persiste un événement dans Supabase"""
        try:
            if not self.supabase_client:
                return False
            
            event_record = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "stream_id": event.stream_id,
                "timestamp": event.timestamp.isoformat(),
                "app_source": event.app_source,
                "payload": event.payload,
                "version": event.version,
                "correlation_id": event.correlation_id,
                "created_at": datetime.now().isoformat()
            }
            
            # Insérer dans table phoenix_events
            response = self.supabase_client.table('phoenix_events').insert(event_record).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"❌ Supabase persistence error: {e}")
            return False
    
    def _validate_event(self, event: PhoenixEventData) -> bool:
        """Valide la structure d'un événement"""
        required_fields = ['event_id', 'event_type', 'stream_id', 'timestamp', 'app_source']
        
        for field in required_fields:
            if not hasattr(event, field) or getattr(event, field) is None:
                logger.error(f"❌ Missing required field: {field}")
                return False
        
        return True
    
    def _add_to_stream(self, event: PhoenixEventData):
        """Ajoute un événement au stream local"""
        stream_id = event.stream_id
        
        if stream_id not in self.streams:
            self.streams[stream_id] = PhoenixEventStream(
                stream_id=stream_id,
                events=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        self.streams[stream_id].add_event(event)
    
    async def _notify_handlers(self, event: PhoenixEventData):
        """Notifie les handlers d'événements"""
        event_type = event.event_type
        
        if event_type in self.event_handlers:
            handlers = self.event_handlers[event_type]
            
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"❌ Event handler error: {e}")
    
    def subscribe(self, event_type: PhoenixEventType, handler: Callable):
        """
        Abonne un handler à un type d'événement
        
        Args:
            event_type: Type d'événement à écouter
            handler: Fonction appelée lors de l'événement
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"✅ Handler subscribed to {event_type.value}")
    
    def get_stream(self, stream_id: str) -> Optional[PhoenixEventStream]:
        """Récupère un stream d'événements"""
        return self.streams.get(stream_id)
    
    def get_events_by_type(self, event_type: PhoenixEventType, stream_id: Optional[str] = None) -> List[PhoenixEventData]:
        """Récupère tous les événements d'un type donné"""
        events = []
        
        for stream in self.streams.values():
            if stream_id is None or stream.stream_id == stream_id:
                events.extend(stream.get_events_by_type(event_type))
        
        return events
    
    def get_user_journey(self, user_id: str) -> List[PhoenixEventData]:
        """Récupère le parcours complet d'un utilisateur"""
        stream = self.get_stream(user_id)
        return stream.events if stream else []


class PhoenixCVEventHelper:
    """Helper spécialisé pour les événements Phoenix CV"""
    
    def __init__(self, event_bridge: PhoenixEventBridge):
        self.bridge = event_bridge
    
    async def track_cv_uploaded(self, user_id: str, cv_filename: str, cv_size: int) -> str:
        """Publie un événement de upload CV"""
        event = PhoenixEventData(
            event_id="",  # Auto-généré
            event_type=PhoenixEventType.CV_UPLOADED,
            stream_id=user_id,
            timestamp=datetime.now(),
            app_source="cv",
            payload={
                "filename": cv_filename,
                "file_size": cv_size,
                "upload_method": "streamlit_file_uploader"
            }
        )
        
        success = await self.bridge.publish_event(event)
        return event.event_id if success else None
    
    async def track_cv_generated(
        self, 
        user_id: str, 
        template_name: str,
        ats_score: float,
        skills_count: int,
        experience_count: int
    ) -> str:
        """Publie un événement de génération CV"""
        event = PhoenixEventData(
            event_id="",
            event_type=PhoenixEventType.CV_GENERATED,
            stream_id=user_id,
            timestamp=datetime.now(),
            app_source="cv",
            payload={
                "template_name": template_name,
                "ats_score": ats_score,
                "skills_count": skills_count,
                "experience_count": experience_count
            }
        )
        
        success = await self.bridge.publish_event(event)
        return event.event_id if success else None
    
    async def track_template_selected(self, user_id: str, template_name: str, template_category: str) -> str:
        """Publie un événement de sélection template"""
        event = PhoenixEventData(
            event_id="",
            event_type=PhoenixEventType.TEMPLATE_SELECTED,
            stream_id=user_id,
            timestamp=datetime.now(),
            app_source="cv",
            payload={
                "template_name": template_name,
                "template_category": template_category
            }
        )
        
        success = await self.bridge.publish_event(event)
        return event.event_id if success else None


class PhoenixLettersEventHelper:
    """Helper spécialisé pour les événements Phoenix Letters"""
    
    def __init__(self, event_bridge: PhoenixEventBridge):
        self.bridge = event_bridge
    
    async def track_letter_generated(
        self,
        user_id: str,
        job_title: str,
        company_name: str,
        optimization_level: str
    ) -> str:
        """Publie un événement de génération lettre"""
        event = PhoenixEventData(
            event_id="",
            event_type=PhoenixEventType.LETTER_GENERATED,
            stream_id=user_id,
            timestamp=datetime.now(),
            app_source="letters",
            payload={
                "job_title": job_title,
                "company_name": company_name,
                "optimization_level": optimization_level
            }
        )
        
        success = await self.bridge.publish_event(event)
        return event.event_id if success else None


# Factory pour créer les instances
class PhoenixEventFactory:
    """Factory pour créer les services d'événements"""
    
    _bridge_instance = None
    
    @classmethod
    def create_bridge(cls, supabase_client=None) -> PhoenixEventBridge:
        """Crée ou récupère l'instance du bridge principal"""
        if cls._bridge_instance is None:
            cls._bridge_instance = PhoenixEventBridge(supabase_client)
        
        return cls._bridge_instance
    
    @classmethod  
    def create_cv_helper(cls, bridge: PhoenixEventBridge = None) -> PhoenixCVEventHelper:
        """Crée un helper pour Phoenix CV"""
        if bridge is None:
            bridge = cls.create_bridge()
        
        return PhoenixCVEventHelper(bridge)
    
    @classmethod
    def create_letters_helper(cls, bridge: PhoenixEventBridge = None) -> PhoenixLettersEventHelper:
        """Crée un helper pour Phoenix Letters"""
        if bridge is None:
            bridge = cls.create_bridge()
        
        return PhoenixLettersEventHelper(bridge)