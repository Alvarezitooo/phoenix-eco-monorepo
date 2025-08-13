"""
🌉 Phoenix Event Bridge - Types d'événements standardisés
Définition des types d'événements pour l'architecture Event-Sourcing Phoenix

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Strategic Vision Implementation
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

class PhoenixEventType(Enum):
    """Types d'événements standardisés pour l'écosystème Phoenix"""
    
    # 🔐 Authentification et utilisateur
    USER_REGISTERED = "user.registered"
    USER_SIGNED_IN = "user.signed_in" 
    USER_SIGNED_OUT = "user.signed_out"
    USER_TIER_UPDATED = "user.tier_updated"
    
    # 📄 Phoenix CV Events
    CV_UPLOADED = "cv.uploaded"
    CV_GENERATED = "cv.generated"
    TEMPLATE_SELECTED = "cv.template_selected"
    ATS_OPTIMIZATION_PERFORMED = "cv.ats_optimization_performed"
    MIRROR_MATCH_EXECUTED = "cv.mirror_match_executed"
    
    # ✉️ Phoenix Letters Events  
    LETTER_GENERATED = "letter.generated"
    JOB_OFFER_ANALYZED = "letter.job_offer_analyzed"
    LETTER_OPTIMIZED = "letter.optimized"
    LETTER_TEMPLATE_APPLIED = "letter.template_applied"
    
    # 🧘 Phoenix Rise Events
    JOURNAL_ENTRY_CREATED = "rise.journal_entry_created"
    MEDITATION_SESSION_COMPLETED = "rise.meditation_completed"
    COACHING_SESSION_STARTED = "rise.coaching_started"
    KAIZEN_GOAL_SET = "rise.kaizen_goal_set"
    
    # 💰 Billing et abonnements
    SUBSCRIPTION_ACTIVATED = "billing.subscription_activated"
    SUBSCRIPTION_CANCELLED = "billing.subscription_cancelled"
    PAYMENT_SUCCEEDED = "billing.payment_succeeded"
    PAYMENT_FAILED = "billing.payment_failed"
    CHECKOUT_SESSION_CREATED = "billing.checkout_created"
    
    # 🎯 Écosystème
    CROSS_APP_NAVIGATION = "ecosystem.cross_app_navigation"
    DATA_SYNC_REQUESTED = "ecosystem.data_sync_requested"
    INTEGRATION_EVENT = "ecosystem.integration"


@dataclass
class PhoenixEventData:
    """Structure standardisée des événements Phoenix"""
    
    # Identifiants
    event_id: str
    event_type: PhoenixEventType
    stream_id: str  # user_id qui devient stream_id
    
    # Métadonnées
    timestamp: datetime
    app_source: str  # 'cv', 'letters', 'rise', 'website', 'billing'
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    
    # Données de l'événement
    payload: Dict[str, Any] = None
    
    # Contexte technique
    version: str = "1.0"
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        """Génère automatiquement les IDs manquants"""
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        
        if not self.timestamp:
            self.timestamp = datetime.now()
        
        if not self.payload:
            self.payload = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'événement en dictionnaire pour sérialisation"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "stream_id": self.stream_id,
            "timestamp": self.timestamp.isoformat(),
            "app_source": self.app_source,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "payload": self.payload,
            "version": self.version,
            "correlation_id": self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhoenixEventData':
        """Recrée un événement depuis un dictionnaire"""
        return cls(
            event_id=data["event_id"],
            event_type=PhoenixEventType(data["event_type"]),
            stream_id=data["stream_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            app_source=data["app_source"],
            user_agent=data.get("user_agent"),
            session_id=data.get("session_id"),
            payload=data.get("payload", {}),
            version=data.get("version", "1.0"),
            correlation_id=data.get("correlation_id")
        )


@dataclass 
class PhoenixEventStream:
    """Flux d'événements pour un utilisateur (stream_id)"""
    
    stream_id: str  # user_id
    events: list[PhoenixEventData]
    created_at: datetime
    updated_at: datetime
    version: int = 1
    
    def add_event(self, event: PhoenixEventData):
        """Ajoute un événement au flux"""
        if event.stream_id != self.stream_id:
            raise ValueError(f"Event stream_id {event.stream_id} doesn't match stream {self.stream_id}")
        
        self.events.append(event)
        self.updated_at = datetime.now()
        self.version += 1
    
    def get_events_by_type(self, event_type: PhoenixEventType) -> list[PhoenixEventData]:
        """Filtre les événements par type"""
        return [event for event in self.events if event.event_type == event_type]
    
    def get_events_by_app(self, app_source: str) -> list[PhoenixEventData]:
        """Filtre les événements par application source"""
        return [event for event in self.events if event.app_source == app_source]


# Helpers pour création d'événements typés
class PhoenixEventFactory:
    """Factory pour créer des événements typés facilement"""
    
    @staticmethod
    def create_user_registered(user_id: str, email: str, app_source: str = "website") -> PhoenixEventData:
        """Crée un événement d'inscription utilisateur"""
        return PhoenixEventData(
            event_id=str(uuid.uuid4()),
            event_type=PhoenixEventType.USER_REGISTERED,
            stream_id=user_id,
            timestamp=datetime.now(),
            app_source=app_source,
            payload={
                "email": email,
                "registration_method": "email_password"
            }
        )
    
    @staticmethod
    def create_cv_generated(
        user_id: str, 
        template_name: str,
        ats_score: float,
        skills_count: int,
        experience_count: int
    ) -> PhoenixEventData:
        """Crée un événement de génération CV"""
        return PhoenixEventData(
            event_id=str(uuid.uuid4()),
            event_type=PhoenixEventType.CV_GENERATED,
            stream_id=user_id,
            timestamp=datetime.now(),
            app_source="cv",
            payload={
                "template_name": template_name,
                "ats_score": ats_score,
                "skills_count": skills_count,
                "experience_count": experience_count,
                "generation_duration_ms": None  # À remplir par l'app
            }
        )
    
    @staticmethod
    def create_letter_generated(
        user_id: str,
        job_title: str,
        company_name: str,
        optimization_level: str,
        ai_model_used: str = "gemini-1.5-flash"
    ) -> PhoenixEventData:
        """Crée un événement de génération lettre"""
        return PhoenixEventData(
            event_id=str(uuid.uuid4()),
            event_type=PhoenixEventType.LETTER_GENERATED,
            stream_id=user_id,
            timestamp=datetime.now(),
            app_source="letters",
            payload={
                "job_title": job_title,
                "company_name": company_name,
                "optimization_level": optimization_level,
                "ai_model_used": ai_model_used,
                "word_count": None  # À remplir par l'app
            }
        )
    
    @staticmethod
    def create_subscription_activated(
        user_id: str,
        subscription_tier: str,
        stripe_customer_id: str,
        stripe_subscription_id: str
    ) -> PhoenixEventData:
        """Crée un événement d'activation d'abonnement"""
        return PhoenixEventData(
            event_id=str(uuid.uuid4()),
            event_type=PhoenixEventType.SUBSCRIPTION_ACTIVATED,
            stream_id=user_id,
            timestamp=datetime.now(),
            app_source="billing",
            payload={
                "subscription_tier": subscription_tier,
                "stripe_customer_id": stripe_customer_id,
                "stripe_subscription_id": stripe_subscription_id,
                "previous_tier": "free"
            }
        )