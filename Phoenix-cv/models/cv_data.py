from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from marshmallow import Schema, fields, validate, ValidationError, post_load

from utils.secure_validator import SecureValidator
from utils.secure_crypto import secure_crypto

class CVTier(Enum):
    """Niveaux d'abonnement Phoenix CV"""
    FREE = "free"
    PRO = "pro"
    ECOSYSTEM = "ecosystem"

class ATSScore(Enum):
    """Niveaux d'optimisation ATS"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"

# Schémas de validation Marshmallow sécurisés
class PersonalInfoSchema(Schema):
    full_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=254))
    phone = fields.Str(validate=validate.Length(max=20), missing="")
    address = fields.Str(validate=validate.Length(max=500), missing="")
    linkedin = fields.Url(validate=validate.Length(max=255), missing="")
    github = fields.Url(validate=validate.Length(max=255), missing="")
    portfolio = fields.Url(validate=validate.Length(max=255), missing="")

class ExperienceSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    company = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    location = fields.Str(validate=validate.Length(max=100), missing="")
    start_date = fields.Str(validate=validate.Length(max=20), missing="")
    end_date = fields.Str(validate=validate.Length(max=20), missing="")
    current = fields.Bool(missing=False)
    description = fields.Str(validate=validate.Length(max=2000), missing="")
    skills_used = fields.List(fields.Str(validate=validate.Length(max=50)), missing=[])
    achievements = fields.List(fields.Str(validate=validate.Length(max=200)), missing=[])

@dataclass
class PersonalInfo:
    """Informations personnelles sécurisées"""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    
    def __post_init__(self):
        if self.full_name:
            self.full_name = SecureValidator.validate_text_input(self.full_name, 100, "nom")
        if self.email:
            self.email = SecureValidator.validate_email(self.email)
    
    def anonymize(self) -> 'PersonalInfo':
        """Anonymise les données PII pour traitement IA"""
        return PersonalInfo(
            full_name="[NOM_COMPLET]",
            email="[EMAIL]",
            phone="[TELEPHONE]", 
            address="[ADRESSE]",
            linkedin="[LINKEDIN]",
            github="[GITHUB]",
            portfolio="[PORTFOLIO]"
        )
    
    def encrypt_sensitive_data(self) -> Dict[str, str]:
        """Chiffre les données sensibles"""
        return {
            'full_name': secure_crypto.encrypt_data(self.full_name),
            'email': secure_crypto.encrypt_data(self.email),
            'phone': secure_crypto.encrypt_data(self.phone),
            'address': secure_crypto.encrypt_data(self.address)
        }

@dataclass
class Experience:
    """Expérience professionnelle sécurisée"""
    title: str = ""
    company: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    current: bool = False
    description: str = ""
    skills_used: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.title:
            self.title = SecureValidator.validate_text_input(self.title, 200, "titre poste")
        if self.description:
            self.description = SecureValidator.validate_text_input(self.description, 2000, "description")

@dataclass
class Education:
    """Formation sécurisée"""
    degree: str = ""
    institution: str = ""
    location: str = ""
    graduation_year: str = ""
    gpa: str = ""
    relevant_courses: List[str] = field(default_factory=list)

@dataclass
class Skill:
    """Compétence sécurisée"""
    name: str = ""
    level: str = ""
    category: str = ""
    
    def __post_init__(self):
        if self.name:
            self.name = SecureValidator.validate_text_input(self.name, 100, "nom compétence")

@dataclass
class CVProfile:
    """Profil CV complet sécurisé"""
    personal_info: PersonalInfo
    professional_summary: str = ""
    target_position: str = ""
    target_sector: str = ""
    current_sector: str = ""
    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[Dict[str, str]] = field(default_factory=list)
    projects: List[Dict[str, str]] = field(default_factory=list)
    volunteer_work: List[Dict[str, str]] = field(default_factory=list)
