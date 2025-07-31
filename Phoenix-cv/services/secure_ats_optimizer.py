from dataclasses import dataclass
from typing import List, Dict

from models.cv_data import ATSScore, CVProfile
from services.secure_gemini_client import SecureGeminiClient
from utils.secure_validator import SecureValidator
from utils.secure_logging import secure_logger
from utils.exceptions import SecurityException
from utils.rate_limiter import rate_limit

@dataclass
class ATSAnalysis:
    """Résultat d'analyse ATS sécurisé"""
    score: int
    level: ATSScore
    missing_keywords: List[str]
    recommendations: List[str]
    format_issues: List[str]
    keyword_density: Dict[str, float]

class SecureATSOptimizer:
    """Optimiseur ATS sécurisé"""
    
    def __init__(self, gemini_client: SecureGeminiClient):
        self.gemini = gemini_client
    
    @rate_limit(max_requests=3, window_seconds=300)
    def analyze_ats_compatibility_secure(self, cv_profile: CVProfile, job_description: str = "") -> ATSAnalysis:
        """Analyse ATS sécurisée"""
        try:
            clean_job_desc = ""
            if job_description:
                clean_job_desc = SecureValidator.validate_text_input(
                    job_description, 5000, "description poste"
                )
            
            cv_content = self._build_cv_content_for_analysis(cv_profile)
            
            prompt_data = {
                'cv_content': cv_content,
                'job_description': f"Offre d'emploi cible: {clean_job_desc}" if clean_job_desc else ""
            }
            
            response = self.gemini.generate_content_secure(
                'ats_analysis',
                prompt_data
            )
            
            analysis_data = self._parse_ats_response_secure(response)
            
            analysis = self._build_ats_analysis_secure(analysis_data)
            
            secure_logger.log_security_event(
                "ATS_ANALYSIS_COMPLETED",
                {"score": analysis.score, "level": analysis.level.value}
            )
            
            return analysis
            
        except Exception as e:
            secure_logger.log_security_event(
                "ATS_ANALYSIS_ERROR",
                {"error": str(e)[:100]},
                "ERROR"
            )
            return ATSAnalysis(
                score=50,
                level=ATSScore.FAIR,
                missing_keywords=[],
                recommendations=["Erreur lors de l'analyse. Veuillez réessayer."],
                format_issues=[],
                keyword_density={}
            )
    
    def _build_cv_content_for_analysis(self, cv_profile: CVProfile) -> str:
        """Construction sécurisée du contenu CV pour analyse"""
        content_parts = []
        
        if cv_profile.professional_summary:
            content_parts.append(f"Résumé: {cv_profile.professional_summary}")
        
        if cv_profile.target_position:
            content_parts.append(f"Poste visé: {cv_profile.target_position}")
        
        if cv_profile.experiences:
            exp_texts = []
            for exp in cv_profile.experiences[:5]:
                exp_text = f"{exp.title} chez {exp.company}"
                if exp.description:
                    exp_text += f": {exp.description[:500]}"
                exp_texts.append(exp_text)
            content_parts.append("Expériences:\n" + "\n".join(exp_texts))
        
        if cv_profile.skills:
            skills_text = ", ".join([skill.name for skill in cv_profile.skills[:20]])
            content_parts.append(f"Compétences: {skills_text}")
        
        return "\n\n".join(content_parts)[:5000]
    
    def _parse_ats_response_secure(self, response: str) -> Dict:
        """Parsing sécurisé de la réponse ATS"""
        try:
            import json
            parsed = json.loads(response)
            
            required_fields = {
                'score': 50,
                'level': 'fair',
                'missing_keywords': [],
                'recommendations': [],
                'format_issues': [],
                'keyword_density': {}
            }
            
            for field, default in required_fields.items():
                if field not in parsed:
                    parsed[field] = default
            
            score = parsed.get('score', 50)
            if not isinstance(score, int) or score < 0 or score > 100:
                parsed['score'] = 50
            
            if len(parsed.get('missing_keywords', [])) > 20:
                parsed['missing_keywords'] = parsed['missing_keywords'][:20]
            
            if len(parsed.get('recommendations', [])) > 10:
                parsed['recommendations'] = parsed['recommendations'][:10]
            
            return parsed
            
        except (json.JSONDecodeError, TypeError):
            return {
                'score': 50,
                'level': 'fair', 
                'missing_keywords': [],
                'recommendations': ["Erreur d'analyse. Données par défaut."],
                'format_issues': [],
                'keyword_density': {}
            }
    
    def _build_ats_analysis_secure(self, data: Dict) -> ATSAnalysis:
        """Construction sécurisée de l'analyse ATS"""
        score = data.get('score', 50)
        
        if score >= 85:
            level = ATSScore.EXCELLENT
        elif score >= 70:
            level = ATSScore.GOOD
        elif score >= 50:
            level = ATSScore.FAIR
        else:
            level = ATSScore.POOR
        
        return ATSAnalysis(
            score=score,
            level=level,
            missing_keywords=data.get('missing_keywords', []),
            recommendations=data.get('recommendations', []),
            format_issues=data.get('format_issues', []),
            keyword_density=data.get('keyword_density', {})
        )