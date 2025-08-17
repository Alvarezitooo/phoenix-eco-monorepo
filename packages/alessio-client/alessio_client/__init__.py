"""
🤖 ALESSIO CLIENT - Client partagé pour l'agent Alessio Phoenix
Package partagé pour intégrer Alessio dans toutes les applications Phoenix.
"""

from .streamlit_client import AlessioStreamlitClient, render_alessio_chat, render_alessio_status
from .react_client import AlessioReactClient
from .base_client import AlessioBaseClient

__version__ = "0.1.0"
__all__ = [
    "AlessioStreamlitClient",
    "AlessioReactClient", 
    "AlessioBaseClient",
    "render_alessio_chat",
    "render_alessio_status"
]