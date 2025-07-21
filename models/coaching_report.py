from pydantic import BaseModel
from typing import List, Dict

class CoachingReport(BaseModel):
    score: float
    suggestions: List[str]
    rationale: Dict[str, str]
