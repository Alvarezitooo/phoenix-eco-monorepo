"""Client Google Gemini optimisé avec batch processing et caching intelligent."""

import logging
import asyncio
import time
from typing import Any, Dict, Optional, List, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

import google.generativeai as genai
from config.settings import Settings
from core.entities.letter import UserTier
from core.services.solidarity_ecological_fund import phoenix_solidarity_fund
from infrastructure.monitoring.phoenix_green_metrics import phoenix_green_metrics
from shared.exceptions.specific_exceptions import AIServiceError, RateLimitError
from shared.interfaces.ai_interface import AIServiceInterface
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@dataclass
class BatchRequest:
    """Structure pour requête batch."""
    prompt: str
    user_tier: UserTier
    max_tokens: int = 1000
    temperature: float = 0.7
    feature_used: Optional[str] = None
    request_id: str = None

@dataclass
class CacheEntry:
    """Entrée de cache optimisée."""
    content: str
    timestamp: float
    user_tier: str
    ttl: int = 3600  # 1 heure par défaut


class GeminiClient(AIServiceInterface):
    """✅ Client optimisé pour Google Gemini AI avec batch processing."""

    def __init__(self, settings: Settings):
        """Initialise le client Gemini avec optimisations."""
        self.settings = settings
        self._cache: Dict[str, CacheEntry] = {}
        self._batch_queue: List[BatchRequest] = []
        self._max_batch_size = 5
        self._batch_timeout = 2.0  # secondes
        self._executor = ThreadPoolExecutor(max_workers=3)
        
        try:
            genai.configure(api_key=self.settings.google_api_key)
            self.model = genai.GenerativeModel("models/gemini-1.5-flash")
            logger.info("✅ Gemini client initialized with optimizations")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise AIServiceError(f"Impossible d'initialiser le client IA: {e}")

    def _get_cache_key(self, prompt: str, user_tier: UserTier, max_tokens: int, temperature: float) -> str:
        """Génère clé de cache optimisée."""
        prompt_hash = hash(f"{prompt}{user_tier.value}{max_tokens}{temperature}")
        return f"gemini_{prompt_hash}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """Récupère du cache intelligent."""
        if cache_key not in self._cache:
            return None
        
        entry = self._cache[cache_key]
        if time.time() - entry.timestamp > entry.ttl:
            del self._cache[cache_key]
            return None
        
        return entry.content
    
    def _set_cache(self, cache_key: str, content: str, user_tier: UserTier) -> None:
        """Met en cache avec TTL adaptatif."""
        # TTL plus long pour premium
        ttl = 7200 if user_tier == UserTier.PREMIUM else 3600
        
        self._cache[cache_key] = CacheEntry(
            content=content,
            timestamp=time.time(),
            user_tier=user_tier.value,
            ttl=ttl
        )
        
        # Nettoyer le cache si trop volumineux
        if len(self._cache) > 100:
            self._cleanup_cache()
    def _cleanup_cache(self) -> None:
        """Nettoie le cache des entrées expirées."""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now - entry.timestamp > entry.ttl
        ]
        for key in expired_keys:
            del self._cache[key]
    
    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_content(
        self,
        prompt: str,
        user_tier: UserTier,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        feature_used: Optional[str] = None,
    ) -> str:
        """
        Génère du contenu avec Gemini et tracking Green AI.

        Args:
            prompt: Prompt pour la génération
            user_tier: Niveau d'abonnement utilisateur
            max_tokens: Nombre maximum de tokens
            temperature: Température de génération
            feature_used: Fonctionnalité utilisée (pour tracking)

        Returns:
            str: Contenu généré

        Raises:
            AIServiceError: En cas d'erreur de génération
            RateLimitError: En cas de limite de débit atteinte
        """
        # 🌱 Démarrage du tracking Green AI
        with phoenix_green_metrics.track_gemini_call(
            user_tier.value, feature_used
        ) as tracker:
            retry_count = 0

            try:
                # Validation du prompt
                if not prompt or len(prompt) < 10:
                    raise AIServiceError("Prompt trop court ou vide")

                if len(prompt) > 100000:
                    raise AIServiceError("Prompt trop long (max 100k caractères)")

                # ✅ Cache optimisé
                cache_key = self._get_cache_key(prompt, user_tier, max_tokens, temperature)
                cached_content = self._get_from_cache(cache_key)
                
                if cached_content:
                    logger.info(f"✅ Cache hit for {user_tier.value} user")
                    tracker.record_request(prompt)
                    tracker.record_response(cached_content, from_cache=True)
                    return cached_content

                # Configuration selon le tier utilisateur
                generation_config = self._get_generation_config(
                    user_tier, max_tokens, temperature
                )

                # 🌱 Enregistrement de la requête
                tracker.record_request(prompt)

                # ✅ Génération optimisée avec timeout adaptatif
                timeout = 45 if user_tier == UserTier.PREMIUM else 30
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    request_options={"timeout": timeout},
                )

                if not response.text:
                    raise AIServiceError("Réponse vide du service IA")

                # Validation de la réponse
                if len(response.text) < 50:
                    raise AIServiceError("Réponse trop courte du service IA")

                # ✅ Mise en cache intelligent
                self._set_cache(cache_key, response.text, user_tier)

                # 🌱 Enregistrement de la réponse
                tracker.record_response(response.text, from_cache=False)

                # 💝🌱 Contribution au fonds solidaire-écologique
                phoenix_solidarity_fund.contribute_from_usage(
                    user_id=None,  # Anonyme pour RGPD
                    user_tier=user_tier.value,
                    trigger_event="letter_generation",
                )

                logger.info(
                    f"🌱💝 Content generated successfully for {user_tier.value} user - CO2 tracked + Fund contributed"
                )
                return response.text.strip()

            except genai.types.BlockedPromptException:
                logger.warning("Prompt blocked by safety filters")
                raise AIServiceError("Contenu bloqué par les filtres de sécurité")

            except genai.types.StopCandidateException:
                logger.warning("Generation stopped by safety filters")
                raise AIServiceError(
                    "Génération interrompue par les filtres de sécurité"
                )

            except Exception as e:
                # 🌱 Enregistrement des retries
                retry_count += 1
                tracker.record_retry()

                if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                    logger.error(f"Rate limit exceeded: {e}")
                    raise RateLimitError(
                        "Limite de débit API atteinte. Veuillez réessayer plus tard."
                    )

                logger.error(f"Unexpected error in content generation: {e}")
                raise AIServiceError(f"Erreur inattendue du service IA: {e}")
    
    def generate_batch(
        self, 
        requests: List[BatchRequest]
    ) -> List[Tuple[str, Optional[str]]]:
        """✅ Génération batch optimisée pour multiple prompts."""
        if not requests:
            return []
        
        results = []
        
        # Traiter par chunks pour éviter les timeouts
        chunk_size = min(self._max_batch_size, len(requests))
        
        for i in range(0, len(requests), chunk_size):
            chunk = requests[i:i + chunk_size]
            
            # Traitement parallèle du chunk
            chunk_futures = []
            for req in chunk:
                future = self._executor.submit(
                    self.generate_content,
                    req.prompt,
                    req.user_tier,
                    req.max_tokens,
                    req.temperature,
                    req.feature_used
                )
                chunk_futures.append((req.request_id or f"req_{i}", future))
            
            # Collecter les résultats
            for req_id, future in chunk_futures:
                try:
                    result = future.result(timeout=60)
                    results.append((req_id, result))
                except Exception as e:
                    logger.error(f"Batch request {req_id} failed: {e}")
                    results.append((req_id, None))
        
        logger.info(f"✅ Batch processing completed: {len(results)} requests")
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache."""
        now = time.time()
        valid_entries = sum(
            1 for entry in self._cache.values()
            if now - entry.timestamp <= entry.ttl
        )
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self._cache) - valid_entries,
            "cache_hit_potential": valid_entries / max(len(self._cache), 1)
        }

    def _get_generation_config(
        self, user_tier: UserTier, max_tokens: int, temperature: float
    ) -> Dict[str, Any]:
        """Configure la génération selon le tier utilisateur."""
        base_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }

        # Configuration spécifique par tier
        if user_tier == UserTier.PREMIUM:
            base_config.update({"temperature": 0.7, "top_p": 0.8, "top_k": 30})
        else:  # FREE
            base_config.update(
                {"temperature": 0.6, "top_p": 0.7, "top_k": 20}  # Plus conservateur
            )

        return base_config
    
    def __del__(self):
        """Nettoyage à la destruction."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)
