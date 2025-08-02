from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date

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