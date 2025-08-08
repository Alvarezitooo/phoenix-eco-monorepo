"""
Adapters pour découplage des services Phoenix
"""

from .session_adapter import (
    SessionManager, 
    BaseSessionAdapter,
    StreamlitSessionAdapter,
    MemorySessionAdapter, 
    FlaskSessionAdapter,
    session_manager
)

__all__ = [
    "SessionManager",
    "BaseSessionAdapter", 
    "StreamlitSessionAdapter",
    "MemorySessionAdapter",
    "FlaskSessionAdapter", 
    "session_manager"
]