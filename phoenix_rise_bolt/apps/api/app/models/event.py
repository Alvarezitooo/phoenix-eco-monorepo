from sqlalchemy import Column, String, Integer, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel

class Event(BaseModel):
    """Event sourcing model"""
    
    __tablename__ = "events"
    
    # Stream identification
    stream_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Usually user_id
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Event metadata
    event_type = Column(String(100), nullable=False, index=True)
    event_version = Column(Integer, default=1, nullable=False)
    app_source = Column(String(50), default="rise", nullable=False)
    
    # Event payload
    payload = Column(JSONB, nullable=False)
    
    # Metadata
    correlation_id = Column(UUID(as_uuid=True), nullable=True)
    causation_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="events")
    
    def __repr__(self):
        return f"<Event {self.event_type} - {self.timestamp}>"

# Indexes for performance
Index('idx_events_stream_timestamp', Event.stream_id, Event.timestamp)
Index('idx_events_type_timestamp', Event.event_type, Event.timestamp)