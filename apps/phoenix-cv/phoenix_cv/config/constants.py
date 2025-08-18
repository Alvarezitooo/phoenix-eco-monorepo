"""
Constantes pour Phoenix CV
"""

from enum import Enum

class CVTier(Enum):
    """Niveaux de qualité des CV"""
    BASIC = "basic"
    PROFESSIONAL = "professional"  
    PREMIUM = "premium"
    EXECUTIVE = "executive"

class CVTemplateType(Enum):
    """Types de templates de CV disponibles"""
    MODERN = "modern"
    CLASSIC = "classic"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    ATS_FRIENDLY = "ats_friendly"

class ATSLevel(Enum):
    """Niveaux d'optimisation ATS"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXCELLENT = "excellent"