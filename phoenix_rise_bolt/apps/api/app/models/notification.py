from sqlalchemy import Column, String, Text, Enum, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class NotificationType(enum.Enum):
    RITUAL_SUGGESTION = "ritual_suggestion"
    MOOD_REMINDER = "mood_reminder"
    JOURNAL_REMINDER = "journal_reminder"
    STREAK_MILESTONE = "streak_milestone"
    ONBOARDING = "onboarding"
    SYSTEM = "system"

class NotificationStatus(enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    READ = "read"
    DISMISSED = "dismissed"

class NotificationChannel(enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"

class Notification(BaseModel):
    """Notification model"""
    
    __tablename__ = "notifications"
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification content
    type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Delivery
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.IN_APP)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.QUEUED, index=True)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    payload = Column(JSONB, nullable=True)  # Additional data (ritual_id, etc.)
    priority = Column(String(10), default="normal")  # low, normal, high
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Actions
    action_url = Column(String(500), nullable=True)
    action_text = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.type.name} - {self.status.name}>"