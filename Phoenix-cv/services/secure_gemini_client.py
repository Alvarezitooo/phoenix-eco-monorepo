import os
import re
import time
import threading
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from functools import wraps
import html

import google.generativeai as genai

from utils.secure_logging import secure_logger
from utils.exceptions import SecurityException
from utils.rate_limiter import rate_limit
from utils.secure_validator import SecureValidator

class SecureGeminiClient:
    """Client Gemini sécurisé avec protection injection"""
    
    def __init__(self):
        self._setup_secure_client()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._request_history = []
        self._lock = threading.Lock()
    
    def _setup_secure_client(self):
        """Configuration sécurisée du client Gemini"""
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise SecurityException("API key Gemini non configurée")
        
        if not re.match(r'^[A-Za-z0-9_-]{20,}$', api_key):
            raise SecurityException("Format de clé API invalide")
        
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={
                'max_output_tokens': 2048,
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40
            }
        )
        
        secure_logger.log_security_event("GEMINI_CLIENT_INITIALIZED", {})
    
    @rate_limit(max_requests=10, window_seconds=60)
    def generate_content_secure(self, prompt_template: str, user_data: Dict[str, str], max_retries: int = 2) -> str:
        """Génération sécurisée avec template et validation"""
        try:
            clean_data = self._sanitize_user_data(user_data)
            
            secure_prompt = self._build_secure_prompt(prompt_template, clean_data)
            
            if not self._validate_prompt(secure_prompt):
                raise SecurityException("Prompt non autorisé")
            
            for attempt in range(max_retries):
                try:
                    future = self.executor.submit(self._call_gemini_api, secure_prompt)
                    response = future.result(timeout=30)
                    
                    clean_response = self._sanitize_ai_response(response)
                    
                    self._log_api_usage(len(secure_prompt), len(clean_response))
                    
                    return clean_response
                    
                except TimeoutError:
                    secure_logger.log_security_event("GEMINI_TIMEOUT", {"attempt": attempt + 1})
                    if attempt == max_retries - 1:
                        raise SecurityException("Timeout de génération IA")
                    time.sleep(1 * (attempt + 1))
                
                except Exception as e:
                    secure_logger.log_security_event(
                        "GEMINI_API_ERROR", 
                        {"attempt": attempt + 1, "error": str(e)[:100]}
                    )
                    if attempt == max_retries - 1:
                        raise SecurityException("Erreur de génération IA")
                    time.sleep(2 * (attempt + 1))
            
            raise SecurityException("Échec de génération après tous les essais")
            
        except Exception as e:
            secure_logger.log_security_event(
                "CONTENT_GENERATION_FAILED",
                {"error": str(e)[:100]},
                "ERROR"
            )
            raise SecurityException("Erreur lors de la génération de contenu")
    
    def _sanitize_user_data(self, user_data: Dict[str, str]) -> Dict[str, str]:
        """Nettoyage sécurisé des données utilisateur"""
        clean_data = {}
        
        for key, value in user_data.items():
            if not isinstance(value, str):
                value = str(value)
            
            clean_value = SecureValidator.validate_text_input(value, 2000, key)
            
            injection_patterns = [
                r'ignore\s+previous\s+instructions',
                r'forget\s+everything',
                r'system\s*:',
                r'admin\s*:',
                r'root\s*:',
                r'<\s*script',
                r'javascript\s*:',
                r'eval\s*\(',
                r'exec\s*\('
            ]
            
            for pattern in injection_patterns:
                clean_value = re.sub(pattern, '[FILTERED]', clean_value, flags=re.IGNORECASE)
            
            clean_data[key] = clean_value
        
        return clean_data
    
    def _build_secure_prompt(self, template: str, data: Dict[str, str]) -> str:
        """Construction sécurisée du prompt avec template"""
        SECURE_TEMPLATES = {
            'cv_enhancement': """
Tu es un expert en CV spécialisé dans les reconversions professionnelles.

CONTEXTE PROFESSIONNEL:
- Secteur actuel: {current_sector}
- Secteur cible: {target_sector}
- Poste visé: {target_position}

CONSIGNES STRICTES:
1. Améliore UNIQUEMENT le résumé professionnel
2. Maximum 300 mots
3. Focus sur les compétences transférables
4. Utilise un ton professionnel
5. Ne mentionne aucune information personnelle

RÉSUMÉ À AMÉLIORER:
{professional_summary}

RÉPONSE ATTENDUE: Un résumé professionnel amélioré uniquement, sans préambule ni conclusion.
""",
            'cv_parsing': """
Tu es un expert en extraction de données de CV pour les reconversions professionnelles.

INSTRUCTIONS:
1. Extrais les informations du CV fourni
2. Structure les données en JSON valide
3. Les données personnelles sont déjà anonymisées
4. Focus sur les compétences transférables

CV À ANALYSER:
{cv_content}

RÉPONSE ATTENDUE: JSON structuré selon le schéma défini, sans texte supplémentaire.
""",
            'ats_analysis': """
Tu es un expert en optimisation ATS (Applicant Tracking Systems).

MISSION:
1. Analyse la compatibilité ATS du CV fourni
2. Donne un score de 0 à 100
3. Identifie les mots-clés manquants
4. Propose des améliorations concrètes

CV À ANALYSER:
{cv_content}

{job_description}

RÉPONSE ATTENDUE: JSON avec score, recommandations et mots-clés manquants uniquement.
"""
        }
        
        if template not in SECURE_TEMPLATES:
            raise SecurityException("Template de prompt non autorisé")
        
        secure_template = SECURE_TEMPLATES[template]
        
        try:
            secure_prompt = secure_template.format(**data)
            return secure_prompt
        except KeyError as e:
            raise SecurityException(f"Données manquantes pour le template: {e}")
    
    def _validate_prompt(self, prompt: str) -> bool:
        """Validation finale du prompt avant envoi"""
        if len(prompt) > 10000:
            return False
        
        suspicious_patterns = [
            r'ignore\s+above',
            r'disregard\s+previous',
            r'forget\s+instructions',
            r'roleplay\s+as',
            r'pretend\s+to\s+be'
        ]
        
        prompt_lower = prompt.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, prompt_lower):
                secure_logger.log_security_event(
                    "SUSPICIOUS_PROMPT_PATTERN",
                    {"pattern": pattern},
                    "WARNING"
                )
                return False
        
        return True
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Appel API Gemini avec gestion d'erreurs"""
        response = self.model.generate_content(prompt)
        return response.text
    
    def _sanitize_ai_response(self, response: str) -> str:
        """Nettoyage de la réponse IA"""
        if not response:
            return ""
        
        clean_response = response.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        
        if len(clean_response) > 5000:
            clean_response = clean_response[:5000] + "... [TRONQUÉ]"
        
        clean_response = html.escape(clean_response)
        
        return clean_response.strip()
    
    def _log_api_usage(self, prompt_length: int, response_length: int):
        """Log d'utilisation API"""
        with self._lock:
            usage_event = {
                'timestamp': datetime.utcnow().isoformat(),
                'prompt_length': prompt_length,
                'response_length': response_length
            }
            
            self._request_history.append(usage_event)
            
            if len(self._request_history) > 100:
                self._request_history = self._request_history[-50:]
            
            secure_logger.log_security_event("GEMINI_API_USAGE", usage_event)
