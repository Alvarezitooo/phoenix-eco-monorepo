from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ZazenSession(BaseModel):
    """Zazen meditation session model"""
    
    __tablename__ = "zazen_sessions"
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Session metadata
    ritual_id = Column(String(100), nullable=False)  # e.g., "legitimacy", "clarity", "courage"
    topic = Column(String(200), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Session tracking
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False)
    
    # Breathing pattern tracking
    breath_pattern = Column(JSONB, nullable=True)  # Array of inhale-hold-exhale timings
    interruptions = Column(Integer, default=0)
    
    # Session feedback
    focus_rating = Column(Integer, nullable=True)  # 1-5
    post_session_mood = Column(Integer, nullable=True)  # 1-5
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="zazen_sessions")
    
    def __repr__(self):
        status = "completed" if self.is_completed else "in_progress"
        return f"<ZazenSession {self.topic} - {status}>"