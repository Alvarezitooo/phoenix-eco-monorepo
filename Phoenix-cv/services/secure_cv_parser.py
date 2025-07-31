import io
import re
from typing import Dict

import PyPDF2

import docx

from models.cv_data import CVProfile, PersonalInfo, Experience, Education, Skill
from services.secure_gemini_client import SecureGeminiClient
from utils.secure_validator import SecureValidator
from utils.secure_logging import secure_logger
from utils.exceptions import SecurityException, ValidationException
from utils.rate_limiter import rate_limit

class SecureCVParser:
    """Parser de CV sécurisé"""
    
    def __init__(self, gemini_client: SecureGeminiClient):
        self.gemini = gemini_client
    
    @rate_limit(max_requests=5, window_seconds=300)
    def extract_text_from_pdf_secure(self, file_content: bytes) -> str:
        """Extraction sécurisée de texte PDF"""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            page_count = 0
            
            for page in reader.pages:
                if page_count >= 20:
                    break
                
                page_text = page.extract_text()
                if len(text + page_text) > 50000:
                    break
                
                text += page_text + "\n"
                page_count += 1
            
            clean_text = SecureValidator.validate_text_input(text, 50000, "contenu PDF")
            
            secure_logger.log_security_event(
                "PDF_TEXT_EXTRACTED",
                {"pages": page_count, "text_length": len(clean_text)}
            )
            
            return clean_text
            
        except Exception as e:
            secure_logger.log_security_event(
                "PDF_EXTRACTION_ERROR",
                {"error": str(e)[:100]},
                "ERROR"
            )
            raise SecurityException("Erreur lors de l'extraction du PDF")
    
    def extract_text_from_docx_secure(self, file_content: bytes) -> str:
        """Extraction sécurisée de texte DOCX"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            
            for paragraph in doc.paragraphs:
                para_text = paragraph.text
                if len(text + para_text) > 50000:
                    break
                text += para_text + "\n"
            
            clean_text = SecureValidator.validate_text_input(text, 50000, "contenu DOCX")
            
            secure_logger.log_security_event(
                "DOCX_TEXT_EXTRACTED",
                {"text_length": len(clean_text)}
            )
            
            return clean_text
            
        except Exception as e:
            secure_logger.log_security_event(
                "DOCX_EXTRACTION_ERROR", 
                {"error": str(e)[:100]},
                "ERROR"
            )
            raise SecurityException("Erreur lors de l'extraction du DOCX")
    
    def parse_cv_with_ai_secure(self, cv_text: str) -> CVProfile:
        """Parsing sécurisé de CV avec IA"""
        try:
            clean_cv_text = SecureValidator.validate_text_input(cv_text, 50000, "texte CV")
            
            anonymized_text = self._anonymize_text_for_ai(clean_cv_text)
            
            prompt_data = {
                'cv_content': anonymized_text
            }
            
            response = self.gemini.generate_content_secure(
                'cv_parsing',
                prompt_data
            )
            
            parsed_data = self._parse_json_response_secure(response)
            
            profile = self._build_cv_profile_secure(parsed_data)
            
            secure_logger.log_security_event(
                "CV_PARSED_SUCCESSFULLY",
                {"experiences_count": len(profile.experiences), "skills_count": len(profile.skills)}
            )
            
            return profile
            
        except Exception as e:
            secure_logger.log_security_event(
                "CV_PARSING_FAILED",
                {"error": str(e)[:100]},
                "ERROR"
            )
            raise SecurityException("Erreur lors de l'analyse du CV")
    
    def _anonymize_text_for_ai(self, text: str) -> str:
        """Anonymisation avancée pour traitement IA"""
        anonymized = text
        
        patterns = [
            (r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', '[EMAIL]'),
            (r'\b(?:\+33|0)[1-9](?:[0-9]{8})\b', '[TELEPHONE]'),
            (r'\b\d{1,5}\s+(?:rue|avenue|boulevard|place|chemin)\s+[^,\n]{1,50}', '[ADRESSE]'),
            (r'\b(?:linkedin\.com/in/|github\.com/)[a-zA-Z0-9\-_.]+', '[PROFIL_SOCIAL]')
        ]
        
        for pattern, replacement in patterns:
            anonymized = re.sub(pattern, replacement, anonymized, flags=re.IGNORECASE)
        
        return anonymized
    
    def _parse_json_response_secure(self, response: str) -> Dict:
        """Parsing sécurisé de la réponse JSON"""
        try:
            if len(response) > 10000:
                raise ValidationException("Réponse IA trop volumineuse")
            
            parsed = json.loads(response)
            
            if not isinstance(parsed, dict):
                raise ValidationException("Format de réponse invalide")
            
            required_fields = {
                'professional_summary': 1000,
                'target_position': 200,
                'target_sector': 100,
                'current_sector': 100,
                'experiences': None,
                'education': None,
                'skills': None
            }
            
            for field, max_length in required_fields.items():
                if field not in parsed:
                    parsed[field] = "" if max_length else []
                elif max_length and isinstance(parsed[field], str):
                    if len(parsed[field]) > max_length:
                        parsed[field] = parsed[field][:max_length]
            
            return parsed
            
        except json.JSONDecodeError:
            raise ValidationException("Réponse JSON invalide")
    
    def _build_cv_profile_secure(self, data: Dict) -> CVProfile:
        """Construction sécurisée du profil CV"""
        try:
            personal_info = PersonalInfo().anonymize()
            
            experiences = []
            for exp_data in data.get('experiences', [])[:10]:
                if isinstance(exp_data, dict):
                    exp = Experience(
                        title=SecureValidator.validate_text_input(
                            exp_data.get('title', ''), 200, 'titre expérience'
                        ),
                        company=SecureValidator.validate_text_input(
                            exp_data.get('company', ''), 200, 'entreprise'
                        ),
                        location=SecureValidator.validate_text_input(
                            exp_data.get('location', ''), 100, 'lieu'
                        ),
                        start_date=exp_data.get('start_date', ''),
                        end_date=exp_data.get('end_date', ''),
                        current=bool(exp_data.get('current', False)),
                        description=SecureValidator.validate_text_input(
                            exp_data.get('description', ''), 2000, 'description'
                        ),
                        skills_used=exp_data.get('skills_used', [])[:20],
                        achievements=exp_data.get('achievements', [])[:10]
                    )
                    experiences.append(exp)
            
            education = []
            for edu_data in data.get('education', [])[:5]:
                if isinstance(edu_data, dict):
                    edu = Education(
                        degree=SecureValidator.validate_text_input(
                            edu_data.get('degree', ''), 200, 'diplôme'
                        ),
                        institution=SecureValidator.validate_text_input(
                            edu_data.get('institution', ''), 200, 'institution'
                        ),
                        location=edu_data.get('location', ''),
                        graduation_year=edu_data.get('graduation_year', ''),
                        relevant_courses=edu_data.get('relevant_courses', [])[:10]
                    )
                    education.append(edu)
            
            skills = []
            for skill_data in data.get('skills', [])[:50]:
                if isinstance(skill_data, dict):
                    skill = Skill(
                        name=SecureValidator.validate_text_input(
                            skill_data.get('name', ''), 100, 'nom compétence'
                        ),
                        level=skill_data.get('level', ''),
                        category=skill_data.get('category', '')
                    )
                    skills.append(skill)
            
            profile = CVProfile(
                personal_info=personal_info,
                professional_summary=SecureValidator.validate_text_input(
                    data.get('professional_summary', ''), 1000, 'résumé professionnel'
                ),
                target_position=SecureValidator.validate_text_input(
                    data.get('target_position', ''), 200, 'poste cible'
                ),
                target_sector=SecureValidator.validate_text_input(
                    data.get('target_sector', ''), 100, 'secteur cible'
                ),
                current_sector=SecureValidator.validate_text_input(
                    data.get('current_sector', ''), 100, 'secteur actuel'
                ),
                experiences=experiences,
                education=education,
                skills=skills,
                certifications=data.get('certifications', [])[:20],
                languages=data.get('languages', [])[:10]
            )
            
            return profile
            
        except Exception as e:
            secure_logger.log_security_event(
                "CV_PROFILE_BUILD_ERROR",
                {"error": str(e)[:100]},
                "ERROR"
            )
            raise SecurityException("Erreur lors de la construction du profil")