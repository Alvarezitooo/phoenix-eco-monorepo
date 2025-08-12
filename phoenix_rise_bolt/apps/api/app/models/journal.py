from sqlalchemy import Column, String, Text, Integer, Enum, Boolean, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class MoodEnum(enum.IntEnum):
    VERY_BAD = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5

class PrivacyLevel(enum.Enum):
    PRIVATE = "private"
    TEAM_AI = "team_ai"

class JournalEntry(BaseModel):
    """Journal entry model"""
    
    __tablename__ = "journal_entries"
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Content
    title = Column(String(200))
    content = Column(Text, nullable=False)  # Markdown content
    content_encrypted = Column(Text)  # Encrypted content for sensitive entries
    
    # Metadata
    mood = Column(Enum(MoodEnum), nullable=True)
    tags = Column(ARRAY(String), default=[])
    word_count = Column(Integer, default=0)
    
    # AI processing
    ai_summary = Column(Text, nullable=True)
    ai_insights = Column(JSONB, nullable=True)
    ai_processed = Column(Boolean, default=False)
    
    # Privacy
    privacy_level = Column(Enum(PrivacyLevel), default=PrivacyLevel.PRIVATE)
    is_sensitive = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="journal_entries")
    
    def __repr__(self):
        return f"<JournalEntry {self.title or 'Untitled'}>"