"""
🤖 IRIS CLIENT - Client partagé pour l'agent Iris Phoenix
Package partagé pour intégrer Iris dans toutes les applications Phoenix.
"""

from .streamlit_client import IrisStreamlitClient, render_iris_chat, render_iris_status
from .react_client import IrisReactClient
from .base_client import IrisBaseClient

__version__ = "0.1.0"
__all__ = [
    "IrisStreamlitClient",
    "IrisReactClient", 
    "IrisBaseClient",
    "render_iris_chat",
    "render_iris_status"
]