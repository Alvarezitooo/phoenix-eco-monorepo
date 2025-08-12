from sqlalchemy import Column, String, Text, Integer, Enum, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
from .journal import MoodEnum

class MoodLog(BaseModel):
    """Daily mood log model"""
    
    __tablename__ = "mood_logs"
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Mood data
    mood = Column(Enum(MoodEnum), nullable=False)
    note = Column(Text, nullable=True)
    date = Column(Date, nullable=False, index=True)
    
    # Context
    energy_level = Column(Integer, nullable=True)  # 1-5
    stress_level = Column(Integer, nullable=True)  # 1-5
    sleep_quality = Column(Integer, nullable=True)  # 1-5
    
    # Relationships
    user = relationship("User", back_populates="mood_logs")
    
    def __repr__(self):
        return f"<MoodLog {self.date} - {self.mood.name}>"
    
    class Config:
        # Unique constraint on user_id and date
        __table_args__ = (
            UniqueConstraint('user_id', 'date', name='unique_user_date_mood'),
        )