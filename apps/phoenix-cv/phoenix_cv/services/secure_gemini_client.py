import html
import os
import re
import threading
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from functools import wraps
from typing import Any, Dict

import google.generativeai as genai
from phoenix_cv.utils.exceptions import SecurityException
from phoenix_cv.utils.rate_limiter import rate_limit
from phoenix_cv.utils.secure_logging import secure_logger
from phoenix_cv.utils.secure_validator import SecureValidator

# ✅ Import optimiseur cache Gemini depuis packages partagés
try:
    from phoenix_shared_ai.services import get_cache_optimizer, CachePriority
except ImportError:
    # Stub pour développement sans packages partagés
    class DummyCacheOptimizer:
        def get(self, *args, **kwargs): return None
        def set(self, *args, **kwargs): return True
        def get_stats(self): return {"cache_disabled": True}
    
    def get_cache_optimizer(): return DummyCacheOptimizer()
    
    class CachePriority:
        LOW, MEDIUM, HIGH, CRITICAL = 1, 2, 3, 4


class SecureGeminiClient:
    """🛡️ Client Gemini sécurisé avec protection injection et cache intelligent optimisé."""

    def __init__(self):
        self._setup_secure_client()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._request_history = []
        self._lock = threading.Lock()
        
        # ✅ Initialiser cache optimisé Gemini
        self._cache_optimizer = get_cache_optimizer(max_size_mb=30)  # 30MB pour CV processing
        secure_logger.log_security_event("GEMINI_CACHE_INITIALIZED", 
            {"cache_size_mb": 30, "cache_available": True})

    def _setup_secure_client(self):
        """Configuration sécurisée du client Gemini"""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise SecurityException("API key Gemini non configurée")

        if not re.match(r"^[A-Za-z0-9_-]{20,}$", api_key):
            raise SecurityException("Format de clé API invalide")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config={
                "max_output_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
            },
        )

        secure_logger.log_security_event("GEMINI_CLIENT_INITIALIZED", {})

    @rate_limit(max_requests=10, window_seconds=60)
    def generate_content_secure(
        self, prompt_template: str, user_data: Dict[str, str], max_retries: int = 2
    ) -> str:
        """🚀 Génération sécurisée avec template, validation et cache intelligent."""
        try:
            clean_data = self._sanitize_user_data(user_data)
            secure_prompt = self._build_secure_prompt(prompt_template, clean_data)

            if not self._validate_prompt(secure_prompt):
                raise SecurityException("Prompt non autorisé")
            
            # ✅ Vérifier cache avant appel API
            model_config = self._get_model_config()
            cached_response = self._cache_optimizer.get(secure_prompt, clean_data, model_config)
            
            if cached_response:
                secure_logger.log_security_event("GEMINI_CACHE_HIT", 
                    {"template": prompt_template, "response_length": len(cached_response)})
                return cached_response
            
            # ✅ Cache miss - appel API avec retry
            for attempt in range(max_retries):
                try:
                    future = self.executor.submit(self._call_gemini_api, secure_prompt)
                    response = future.result(timeout=30)

                    clean_response = self._sanitize_ai_response(response)
                    
                    # ✅ Mettre en cache la réponse selon priorité template
                    cache_priority = self._determine_cache_priority(prompt_template)
                    cache_ttl = self._calculate_cache_ttl(prompt_template, clean_data)
                    
                    self._cache_optimizer.set(
                        secure_prompt, clean_data, clean_response, 
                        model_config, ttl=cache_ttl, priority=cache_priority
                    )
                    
                    secure_logger.log_security_event("GEMINI_CACHE_SET", 
                        {"template": prompt_template, "cache_ttl": cache_ttl, 
                         "priority": cache_priority.name if hasattr(cache_priority, 'name') else cache_priority})

                    self._log_api_usage(len(secure_prompt), len(clean_response))
                    return clean_response

                except TimeoutError:
                    secure_logger.log_security_event(
                        "GEMINI_TIMEOUT", {"attempt": attempt + 1}
                    )
                    if attempt == max_retries - 1:
                        raise SecurityException("Timeout de génération IA")
                    time.sleep(1 * (attempt + 1))

                except Exception as e:
                    secure_logger.log_security_event(
                        "GEMINI_API_ERROR",
                        {"attempt": attempt + 1, "error": str(e)[:100]},
                    )
                    if attempt == max_retries - 1:
                        raise SecurityException("Erreur de génération IA")
                    time.sleep(2 * (attempt + 1))

            raise SecurityException("Échec de génération après tous les essais")

        except Exception as e:
            secure_logger.log_security_event(
                "CONTENT_GENERATION_FAILED", {"error": str(e)[:100]}, "ERROR"
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
                r"ignore\s+previous\s+instructions",
                r"forget\s+everything",
                r"system\s*:",
                r"admin\s*:",
                r"root\s*:",
                r"<\s*script",
                r"javascript\s*:",
                r"eval\s*\(",
                r"exec\s*\(",
            ]

            for pattern in injection_patterns:
                clean_value = re.sub(
                    pattern, "[FILTERED]", clean_value, flags=re.IGNORECASE
                )

            clean_data[key] = clean_value

        return clean_data

    def _build_secure_prompt(self, template: str, data: Dict[str, str]) -> str:
        """Construction sécurisée du prompt avec template"""
        SECURE_TEMPLATES = {
            "cv_enhancement": """
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
            "cv_parsing": """
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
            "ats_analysis": """
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
""",
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
            r"ignore\s+above",
            r"disregard\s+previous",
            r"forget\s+instructions",
            r"roleplay\s+as",
            r"pretend\s+to\s+be",
        ]

        prompt_lower = prompt.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, prompt_lower):
                secure_logger.log_security_event(
                    "SUSPICIOUS_PROMPT_PATTERN", {"pattern": pattern}, "WARNING"
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
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]

        if len(clean_response) > 5000:
            clean_response = clean_response[:5000] + "... [TRONQUÉ]"

        clean_response = html.escape(clean_response)

        return clean_response.strip()

    def _log_api_usage(self, prompt_length: int, response_length: int):
        """Log d'utilisation API avec tracking coût"""
        with self._lock:
            # Estimation coût Gemini 1.5 Flash (prix approximatifs)
            estimated_input_tokens = prompt_length // 4  # ~4 chars par token
            estimated_output_tokens = response_length // 4
            
            # Prix estimés USD (à ajuster selon tarifs réels)
            cost_per_million_input = 0.075  # $0.075 per 1M input tokens
            cost_per_million_output = 0.30   # $0.30 per 1M output tokens
            
            estimated_cost = (
                (estimated_input_tokens * cost_per_million_input / 1_000_000) +
                (estimated_output_tokens * cost_per_million_output / 1_000_000)
            )
            
            usage_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "prompt_length": prompt_length,
                "response_length": response_length,
                "estimated_input_tokens": estimated_input_tokens,
                "estimated_output_tokens": estimated_output_tokens,
                "estimated_cost_usd": round(estimated_cost, 6),
                "total_tokens": estimated_input_tokens + estimated_output_tokens,
            }

            self._request_history.append(usage_event)

            if len(self._request_history) > 100:
                self._request_history = self._request_history[-50:]

            secure_logger.log_security_event("GEMINI_API_USAGE", usage_event)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'usage et coût"""
        with self._lock:
            if not self._request_history:
                return {"total_requests": 0, "total_cost_usd": 0.0}
            
            total_cost = sum(event.get("estimated_cost_usd", 0) for event in self._request_history)
            total_tokens = sum(event.get("total_tokens", 0) for event in self._request_history)
            
            return {
                "total_requests": len(self._request_history),
                "total_cost_usd": round(total_cost, 6),
                "total_tokens": total_tokens,
                "avg_cost_per_request": round(total_cost / len(self._request_history), 6) if self._request_history else 0,
                "last_24h_requests": len([
                    event for event in self._request_history 
                    if datetime.fromisoformat(event["timestamp"]) > datetime.utcnow() - timedelta(days=1)
                ]),
                "cache_stats": self._cache_optimizer.get_stats()
            }
    
    def _get_model_config(self) -> Dict[str, Any]:
        """Retourne la configuration actuelle du modèle pour le cache."""
        return {
            "model_name": "gemini-1.5-flash",
            "max_output_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40
        }
    
    def _determine_cache_priority(self, template: str) -> Any:
        """Détermine la priorité de cache selon le template."""
        # Templates fréquents = priorité élevée
        high_priority_templates = ["cv_parsing", "cv_enhancement"]
        medium_priority_templates = ["ats_analysis"]
        
        if template in high_priority_templates:
            return CachePriority.HIGH
        elif template in medium_priority_templates:
            return CachePriority.MEDIUM
        else:
            return CachePriority.LOW
    
    def _calculate_cache_ttl(self, template: str, user_data: Dict[str, str]) -> int:
        """Calcule le TTL de cache selon le contexte."""
        base_ttl = 3600  # 1h par défaut
        
        # Templates analytiques = TTL plus long (moins volatil)
        if template in ["cv_parsing", "ats_analysis"]:
            base_ttl = 7200  # 2h
        
        # Templates génératifs = TTL plus court (plus créatif)
        if template == "cv_enhancement":
            base_ttl = 1800  # 30min
        
        # Données très personnalisées = TTL réduit
        personal_indicators = ['nom', 'email', 'telephone']
        if any(indicator in key.lower() for key in user_data.keys() for indicator in personal_indicators):
            base_ttl //= 2
        
        return base_ttl
    
    def clear_cache(self) -> int:
        """Vide le cache Gemini et retourne le nombre d'entrées supprimées."""
        cleared_count = self._cache_optimizer.clear()
        secure_logger.log_security_event("GEMINI_CACHE_CLEARED", 
            {"cleared_entries": cleared_count})
        return cleared_count
