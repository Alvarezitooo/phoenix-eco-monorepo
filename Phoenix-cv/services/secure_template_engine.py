from dataclasses import dataclass
from typing import Dict, List
import html

from models.cv_data import CVProfile, CVTier
from utils.secure_validator import SecureValidator
from utils.secure_logging import secure_logger
from utils.exceptions import SecurityException, ValidationException

@dataclass
class CVTemplate:
    """Template CV sécurisé"""
    id: str
    name: str
    category: str
    description: str
    is_premium: bool
    preview_image: str
    html_template: str
    css_styles: str
    
    def __post_init__(self):
        self.html_template = SecureValidator.sanitize_html_output(self.html_template)

class SecureTemplateEngine:
    """Moteur de templates sécurisé"""
    
    def __init__(self):
        self.templates = self._load_secure_templates()
    
    def _load_secure_templates(self) -> Dict[str, CVTemplate]:
        """Charge les templates sécurisés"""
        templates = {}
        
        templates['modern_free'] = CVTemplate(
            id='modern_free',
            name='Modern Épuré',
            category='Moderne',
            description='Template moderne et épuré, sécurisé pour tous secteurs',
            is_premium=False,
            preview_image='modern_preview.jpg',
            html_template=self._get_secure_modern_template(),
            css_styles=self._get_secure_modern_styles()
        )
        
        return templates
    
    def get_available_templates_secure(self, user_tier: CVTier) -> List[CVTemplate]:
        """Retourne les templates autorisés selon le tier"""
        available = []
        
        for template in self.templates.values():
            if not template.is_premium or user_tier in [CVTier.PRO, CVTier.ECOSYSTEM]:
                available.append(template)
        
        return available
    
    def render_cv_secure(self, profile: CVProfile, template_id: str, for_export: bool = False) -> str:
        """Rendu sécurisé de CV"""
        try:
            if template_id not in self.templates:
                raise ValidationException(f"Template non autorisé: {template_id}")
            
            template = self.templates[template_id]
            
            html_content = self._render_template_secure(template, profile, for_export)
            
            safe_html = SecureValidator.sanitize_html_output(html_content)
            
            secure_logger.log_security_event(
                "CV_RENDERED_SUCCESSFULLY",
                {"template_id": template_id, "html_length": len(safe_html)}
            )
            
            return safe_html
            
        except Exception as e:
            secure_logger.log_security_event(
                "CV_RENDER_ERROR",
                {"template_id": template_id, "error": str(e)[:100]},
                "ERROR"
            )
            raise SecurityException("Erreur lors du rendu du CV")
    
    def _render_template_secure(self, template: CVTemplate, profile: CVProfile, for_export: bool) -> str:
        """Rendu sécurisé avec échappement HTML"""
        html_content = template.html_template
        
        safe_replacements = {
            '{{FULL_NAME}}': html.escape(profile.personal_info.full_name),
            '{{EMAIL}}': html.escape(profile.personal_info.email),
            '{{PHONE}}': html.escape(profile.personal_info.phone),
            '{{ADDRESS}}': html.escape(profile.personal_info.address),
            '{{LINKEDIN}}': html.escape(profile.personal_info.linkedin),
            '{{PROFESSIONAL_SUMMARY}}': html.escape(profile.professional_summary),
            '{{TARGET_POSITION}}': html.escape(profile.target_position)
        }
        
        for placeholder, safe_value in safe_replacements.items():
            html_content = html_content.replace(placeholder, safe_value)
        
        experiences_html = self._render_experiences_secure(profile.experiences)
        html_content = html_content.replace('{{EXPERIENCES}}', experiences_html)
        
        education_html = self._render_education_secure(profile.education)
        html_content = html_content.replace('{{EDUCATION}}', education_html)
        
        skills_html = self._render_skills_secure(profile.skills)
        html_content = html_content.replace('{{SKILLS}}', skills_html)
        
        full_html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:;">
            <meta http-equiv="X-Frame-Options" content="DENY">
            <meta http-equiv="X-Content-Type-Options" content="nosniff">
            <title>CV Phoenix - {html.escape(profile.personal_info.full_name)}</title>
            <style>
                {template.css_styles}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return full_html
    
    def _render_experiences_secure(self, experiences: List[Experience]) -> str:
        """Rendu sécurisé des expériences"""
        if not experiences:
            return "<p>Aucune expérience renseignée</p>"
        
        html_parts = []
        for exp in experiences[:10]:
            end_date = "Présent" if exp.current else html.escape(exp.end_date)
            
            exp_html = f"""
            <div class="experience-item">
                <div class="experience-header">
                    <h3>{html.escape(exp.title)}</h3>
                    <span class="company">{html.escape(exp.company)} - {html.escape(exp.location)}</span>
                    <span class="period">{html.escape(exp.start_date)} - {end_date}</span>
                </div>
                <div class="experience-description">
                    <p>{html.escape(exp.description)}</p>
                </div>
            </div>
            """
            html_parts.append(exp_html)
        
        return "".join(html_parts)
    
    def _render_education_secure(self, education: List[Education]) -> str:
        """Rendu sécurisé de la formation"""
        if not education:
            return "<p>Aucune formation renseignée</p>"
        
        html_parts = []
        for edu in education[:5]:
            edu_html = f"""
            <div class="education-item">
                <h3>{html.escape(edu.degree)}</h3>
                <span class="institution">{html.escape(edu.institution)} - {html.escape(edu.location)}</span>
                <span class="year">{html.escape(edu.graduation_year)}</span>
            </div>
            """
            html_parts.append(edu_html)
        
        return "".join(html_parts)
    
    def _render_skills_secure(self, skills: List[Skill]) -> str:
        """Rendu sécurisé des compétences"""
        if not skills:
            return "<p>Aucune compétence renseignée</p>"
        
        categories = {}
        for skill in skills[:30]:
            category = html.escape(skill.category or "Autres")
            if category not in categories:
                categories[category] = []
            categories[category].append(skill)
        
        html_parts = []
        for category, category_skills in categories.items():
            skills_html_parts = []
            for skill in category_skills:
                skill_html = f"""
                <div class="skill-item">
                    <span class="skill-name">{html.escape(skill.name)}</span>
                    <span class="skill-level">{html.escape(skill.level)}</span>
                </div>
                """
                skills_html_parts.append(skill_html)
            
            category_html = f"""
            <div class="skill-category">
                <h4>{category}</h4>
                <div class="skills-list">
                    {" ".join(skills_html_parts)}
                </div>
            </div>
            """
            html_parts.append(category_html)
        
        return "".join(html_parts)
    
    def _get_secure_modern_template(self) -> str:
        """Template moderne sécurisé"""
        return """
        <div class="cv-container">
            <header class="cv-header">
                <h1>{{FULL_NAME}}</h1>
                <h2>{{TARGET_POSITION}}</h2>
                <div class="contact-info">
                    <span>{{EMAIL}}</span>
                    <span>{{PHONE}}</span>
                    <span>{{ADDRESS}}</span>
                </div>
            </header>
            
            <section class="summary-section">
                <h2>Profil Professionnel</h2>
                <p>{{PROFESSIONAL_SUMMARY}}</p>
            </section>
            
            <section class="experience-section">
                <h2>Expérience Professionnelle</h2>
                {{EXPERIENCES}}
            </section>
            
            <section class="education-section">
                <h2>Formation</h2>
                {{EDUCATION}}
            </section>
            
            <section class="skills-section">
                <h2>Compétences</h2>
                {{SKILLS}}
            </section>
        </div>
        """
    
    def _get_secure_modern_styles(self) -> str:
        """Styles CSS sécurisés"""
        return """
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Arial', 'Helvetica', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }
        
        .cv-container {
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            padding: 40px;
            border-radius: 8px;
        }
        
        .cv-header {
            text-align: center;
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .cv-header h1 {
            font-size: 2.5em;
            margin: 0;
            color: #007bff;
            word-break: break-word;
        }
        
        .cv-header h2 {
            font-size: 1.3em;
            margin: 10px 0;
            color: #666;
            font-weight: normal;
            word-break: break-word;
        }
        
        .contact-info {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        
        .contact-info span {
            color: #666;
            font-size: 0.9em;
            word-break: break-all;
        }
        
        section {
            margin: 30px 0;
        }
        
        section h2 {
            color: #007bff;
            font-size: 1.4em;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }
        
        .experience-item, .education-item {
            margin-bottom: 25px;
            padding: 15px;
            border-left: 3px solid #007bff;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .experience-header h3 {
            margin: 0 0 5px 0;
            color: #333;
            word-break: break-word;
        }
        
        .company, .institution {
            font-weight: bold;
            color: #666;
            word-break: break-word;
        }
        
        .period, .year {
            float: right;
            color: #007bff;
            font-size: 0.9em;
        }
        
        .skills-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .skill-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: #e9ecef;
            border-radius: 4px;
        }
        
        .skill-level {
            color: #007bff;
            font-weight: bold;
        }
        
        /* Sécurité CSS */
        * {
            max-width: 100%;
        }
        
        img {
            max-width: 100%;
            height: auto;
        }
        
        @media print {
            body { max-width: none; margin: 0; padding: 0; }
            .cv-container { box-shadow: none; padding: 20px; }
        }
        
        @media (max-width: 768px) {
            .contact-info { flex-direction: column; text-align: center; }
            .period, .year { float: none; display: block; }
        }
        """
