"""
Modèle de données utilisateur pour Phoenix Rise.
Représente un utilisateur authentifié via Supabase.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """Modèle utilisateur simplifié."""
    id: str
    email: Optional[str] = None
    user_metadata: Optional[dict] = None
    
    def get_display_name(self) -> str:
        """Retourne le nom d'affichage (partie avant @ de l'email)."""
        if self.email:
            return self.email.split('@')[0]
        return "Utilisateur"
