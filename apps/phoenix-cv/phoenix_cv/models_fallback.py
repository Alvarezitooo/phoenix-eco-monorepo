"""
Fallback models pour Phoenix CV - évite les problèmes d'import de sous-modules
Réexporte tous les modèles depuis les modules individuels
"""

# Import sécurisé des modèles
try:
    from phoenix_cv.models.user_profile import UserProfile, Skill, Experience, CV, Letter
    from phoenix_cv.models.phoenix_user import PhoenixUser, UserTier, PhoenixApp, AppPermission
    
    __all__ = [
        "UserProfile", 
        "Skill", 
        "Experience", 
        "CV", 
        "Letter",
        "PhoenixUser", 
        "UserTier", 
        "PhoenixApp", 
        "AppPermission"
    ]
    
except ImportError as e:
    # Fallback vers imports directs si nécessaire
    import sys
    import os
    
    # Ajout du chemin models si nécessaire
    models_path = os.path.join(os.path.dirname(__file__), 'models')
    if models_path not in sys.path:
        sys.path.append(models_path)
    
    try:
        from user_profile import UserProfile, Skill, Experience, CV, Letter
        from phoenix_user import PhoenixUser, UserTier, PhoenixApp, AppPermission
        
        __all__ = [
            "UserProfile", 
            "Skill", 
            "Experience", 
            "CV", 
            "Letter",
            "PhoenixUser", 
            "UserTier", 
            "PhoenixApp", 
            "AppPermission"
        ]
        
    except ImportError as inner_e:
        # Dernière ligne de défense - modèles locaux
        from dataclasses import dataclass, field
        from typing import List, Dict, Optional
        from datetime import date
        from enum import Enum
        
        @dataclass
        class Skill:
            name: str
            level: int # 1-5

        @dataclass
        class Experience:
            title: str
            company: str
            start_date: date
            end_date: Optional[date]
            description: str

        @dataclass
        class CV:
            cv_id: str
            content_hash: str
            ats_score: float
            keywords: List[str]

        @dataclass
        class Letter:
            letter_id: str
            job_title: str
            company: str
            content_hash: str

        @dataclass
        class UserProfile:
            user_id: str # UUID from Auth Service
            email: str
            first_name: Optional[str]
            last_name: Optional[str]
            
            skills: List[Skill] = field(default_factory=list)
            experiences: List[Experience] = field(default_factory=list)
            
            generated_cvs: List[CV] = field(default_factory=list)
            generated_letters: List[Letter] = field(default_factory=list)
            
            # Data from Phoenix Rise
            mood_history: List[Dict] = field(default_factory=list)
            coaching_sessions: int = 0

        class UserTier(Enum):
            FREE = "free"
            PREMIUM = "premium"
            ENTERPRISE = "enterprise"

        class PhoenixApp(Enum):
            LETTERS = "letters"
            CV = "cv"
            RISE = "rise"

        class AppPermission(Enum):
            READ = "read"
            WRITE = "write"
            ADMIN = "admin"

        @dataclass
        class PhoenixUser:
            user_id: str
            email: str
            tier: UserTier
            apps: List[PhoenixApp] = field(default_factory=list)
            permissions: Dict[PhoenixApp, List[AppPermission]] = field(default_factory=dict)
            
        __all__ = [
            "UserProfile", 
            "Skill", 
            "Experience", 
            "CV", 
            "Letter",
            "PhoenixUser", 
            "UserTier", 
            "PhoenixApp", 
            "AppPermission"
        ]