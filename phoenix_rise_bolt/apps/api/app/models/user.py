from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class UserStatus(enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class User(BaseModel):
    """User model"""
    
    __tablename__ = "users"
    
    # Supabase auth ID (UUID from auth.users)
    auth_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    
    # Profile
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Status
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    
    # Privacy settings
    data_retention_days = Column(Integer, default=365)
    analytics_enabled = Column(Boolean, default=True)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
    mood_logs = relationship("MoodLog", back_populates="user", cascade="all, delete-orphan")
    zazen_sessions = relationship("ZazenSession", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"