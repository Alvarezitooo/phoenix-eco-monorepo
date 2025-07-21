from pydantic import BaseModel

class LetterResponse(BaseModel):
    lettre_generee: str
