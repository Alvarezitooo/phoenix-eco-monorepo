from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, ClassVar

@dataclass
class BaseEvent:
    event_id: str
    stream_id: str  # Typically the aggregate ID (e.g., user_id)
    timestamp: datetime
    payload: Dict[str, Any]
    version: int = 1
    # event_type will be defined in subclasses as a ClassVar

@dataclass
class UserProfileCreatedEvent(BaseEvent):
    event_type: ClassVar[str] = "UserProfileCreated"

@dataclass
class UserProfileUpdatedEvent(BaseEvent):
    event_type: ClassVar[str] = "UserProfileUpdated"