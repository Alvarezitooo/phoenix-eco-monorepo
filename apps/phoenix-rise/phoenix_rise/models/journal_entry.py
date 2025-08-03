from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JournalEntry(BaseModel):
    """Modèle de données pour une entrée de journal."""

    id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    mood: int = Field(..., ge=1, le=10)  # Humeur sur une échelle de 1 à 10
    confidence: int = Field(..., ge=1, le=10)  # Confiance sur une échelle de 1 à 10
    notes: Optional[str] = None
