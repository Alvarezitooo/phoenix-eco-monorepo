import secrets
import streamlit as st
from typing import Any, Optional
from core.entities.user import User

class SecureSessionManager:
    """
    Manages user sessions with cryptographically secure session IDs.
    
    This class is designed to abstract session management away from Streamlit's
    native session_state to prepare for a future migration to a persistent,
    server-side storage solution (e.g., Redis, Supabase table).
    """

    def __init__(self, settings):
        self.settings = settings

    def get_session_id(self) -> str:
        """
        Retrieves the current session ID or creates a new secure one.
        
        SECURITY: Ensures every session, including guests, has a
        cryptographically strong, non-predictable identifier.
        """
        if 'session_id' not in st.session_state:
            # SECURITY FIX: Use secrets.token_hex for unpredictable session IDs
            # instead of timestamp-based IDs. 32 bytes = 64 hex characters.
            st.session_state.session_id = secrets.token_hex(32)
        return st.session_state.session_id

    def get(self, key: str) -> Any:
        """Gets a value from the session."""
        session_id = self.get_session_id()
        # In a future implementation, this would use the session_id 
        # to query a persistent store like Redis.
        return st.session_state.get(f"{session_id}_{key}")

    def set(self, key: str, value: Any):
        """Sets a value in the session."""
        session_id = self.get_session_id()
        # In a future implementation, this would use the session_id 
        # to write to a persistent store.
        st.session_state[f"{session_id}_{key}"] = value

    def clear(self):
        """Clears the entire session state."""
        # This would clear the persistent session record.
        # For now, it clears the Streamlit session state.
        st.session_state.clear()

    def get_current_user(self) -> Optional[User]:
        """Retrieves the currently logged-in user from the session."""
        return self.get('current_user')

    def set_current_user(self, user: User):
        """Stores the user object in the session."""
        self.set('current_user', user)