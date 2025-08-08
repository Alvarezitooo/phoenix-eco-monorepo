"""
Optimiseur de cache avancé pour appels Gemini.
Cache intelligent avec compression, TTL adaptatif et stratégies d'éviction.

Author: Claude Phoenix DevSecOps Guardian
Version: 1.0.0 - Performance Optimization
"""

import hashlib
import json
import logging
import time
import zlib
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class CachePriority(Enum):
    """Priorités de cache pour stratégie d'éviction."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class CacheEntry:
    """Entrée de cache optimisée."""
    content: str
    compressed_content: Optional[bytes] = None
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    ttl_seconds: int = 3600  # 1h par défaut
    priority: CachePriority = CachePriority.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Compression automatique si contenu volumineux."""
        if len(self.content) > 1000:  # Compresser si >1KB
            self.compressed_content = zlib.compress(self.content.encode('utf-8'))
    
    @property
    def decompressed_content(self) -> str:
        """Récupère le contenu (décompressé si nécessaire)."""
        if self.compressed_content:
            return zlib.decompress(self.compressed_content).decode('utf-8')
        return self.content
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée."""
        return time.time() - self.created_at > self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """Age de l'entrée en secondes."""
        return time.time() - self.created_at
    
    def access(self) -> str:
        """Marque l'accès et retourne le contenu."""
        self.last_accessed = time.time()
        self.access_count += 1
        return self.decompressed_content
    
    @property
    def size_bytes(self) -> int:
        """Taille en mémoire de l'entrée."""
        return len(self.compressed_content) if self.compressed_content else len(self.content.encode('utf-8'))

class GeminiCacheOptimizer:
    """🚀 Cache optimisé pour appels Gemini avec compression et éviction intelligente."""
    
    def __init__(self, 
                 max_size_mb: int = 50,
                 default_ttl: int = 3600,
                 cleanup_interval: int = 300):
        """
        Initialise l'optimiseur de cache.
        
        Args:
            max_size_mb: Taille max cache en MB
            default_ttl: TTL par défaut en secondes
            cleanup_interval: Intervalle nettoyage en secondes
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        
        self._cache: Dict[str, CacheEntry] = {}
        self._last_cleanup = time.time()
        
        # Statistiques
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'cleanups': 0,
            'bytes_saved': 0
        }
        
        logger.info(f"✅ GeminiCacheOptimizer initialized (max_size={max_size_mb}MB, ttl={default_ttl}s)")
    
    def _generate_cache_key(self, 
                          prompt: str, 
                          user_data: Dict[str, Any], 
                          model_config: Dict[str, Any] = None) -> str:
        """
        Génère une clé de cache unique et déterministe.
        
        Args:
            prompt: Template de prompt
            user_data: Données utilisateur
            model_config: Configuration modèle
            
        Returns:
            Clé de cache hashée
        """
        # Normaliser et sérialiser les données
        cache_data = {
            'prompt': prompt.strip(),
            'user_data': {k: str(v).strip() for k, v in user_data.items()},
            'model_config': model_config or {}
        }
        
        # Créer hash SHA-256 pour clé unique
        cache_string = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(cache_string.encode('utf-8')).hexdigest()
    
    def get(self, 
            prompt: str, 
            user_data: Dict[str, Any], 
            model_config: Dict[str, Any] = None) -> Optional[str]:
        """
        Récupère du cache si disponible.
        
        Args:
            prompt: Template de prompt
            user_data: Données utilisateur  
            model_config: Configuration modèle
            
        Returns:
            Contenu en cache ou None
        """
        cache_key = self._generate_cache_key(prompt, user_data, model_config)
        
        # Nettoyage périodique
        self._maybe_cleanup()
        
        if cache_key not in self._cache:
            self._stats['misses'] += 1
            return None
        
        entry = self._cache[cache_key]
        
        # Vérifier expiration
        if entry.is_expired:
            del self._cache[cache_key]
            self._stats['misses'] += 1
            logger.debug(f"🗑️ Cache entry expired and removed: {cache_key[:8]}")
            return None
        
        # Hit de cache !
        content = entry.access()
        self._stats['hits'] += 1
        self._stats['bytes_saved'] += len(content.encode('utf-8'))
        
        logger.debug(f"✅ Cache hit: {cache_key[:8]} (age: {entry.age_seconds:.1f}s, accesses: {entry.access_count})")
        return content
    
    def set(self, 
            prompt: str, 
            user_data: Dict[str, Any], 
            content: str,
            model_config: Dict[str, Any] = None,
            ttl: Optional[int] = None,
            priority: CachePriority = CachePriority.MEDIUM) -> bool:
        """
        Met en cache un contenu généré.
        
        Args:
            prompt: Template de prompt
            user_data: Données utilisateur
            content: Contenu à cacher
            model_config: Configuration modèle
            ttl: TTL spécifique (optionnel)
            priority: Priorité pour éviction
            
        Returns:
            True si mis en cache, False sinon
        """
        if not content or len(content.strip()) == 0:
            return False
        
        cache_key = self._generate_cache_key(prompt, user_data, model_config)
        
        # Créer entrée avec TTL adaptatif
        effective_ttl = ttl or self._calculate_adaptive_ttl(prompt, user_data, content)
        
        entry = CacheEntry(
            content=content,
            ttl_seconds=effective_ttl,
            priority=priority,
            metadata={
                'prompt_length': len(prompt),
                'user_data_keys': list(user_data.keys()),
                'content_length': len(content),
                'model_config': model_config or {}
            }
        )
        
        # Vérifier si espace suffisant
        if not self._ensure_space_available(entry.size_bytes):
            logger.warning(f"⚠️ Cannot cache entry, insufficient space: {cache_key[:8]}")
            return False
        
        self._cache[cache_key] = entry
        
        logger.debug(f"💾 Cached entry: {cache_key[:8]} (size: {entry.size_bytes}B, ttl: {effective_ttl}s)")
        return True
    
    def _calculate_adaptive_ttl(self, 
                              prompt: str, 
                              user_data: Dict[str, Any], 
                              content: str) -> int:
        """
        Calcule un TTL adaptatif basé sur le contenu.
        
        Args:
            prompt: Template de prompt
            user_data: Données utilisateur
            content: Contenu généré
            
        Returns:
            TTL en secondes
        """
        base_ttl = self.default_ttl
        
        # TTL plus long pour contenu volumineux (plus coûteux à regénérer)
        if len(content) > 5000:
            base_ttl *= 2
        elif len(content) > 2000:
            base_ttl *= 1.5
        
        # TTL plus court pour données très spécifiques (moins réutilisable)
        personal_data_indicators = ['nom', 'email', 'telephone', 'adresse', 'date_naissance']
        if any(indicator in key.lower() for key in user_data.keys() for indicator in personal_data_indicators):
            base_ttl //= 2
        
        # TTL plus long pour prompts génériques (plus réutilisable)
        if 'template' in prompt.lower() or 'modèle' in prompt.lower():
            base_ttl *= 1.3
        
        return max(300, min(base_ttl, 7200))  # Entre 5min et 2h
    
    def _ensure_space_available(self, required_bytes: int) -> bool:
        """
        S'assure qu'il y a assez d'espace libre.
        
        Args:
            required_bytes: Espace requis en bytes
            
        Returns:
            True si espace disponible
        """
        current_size = self.get_cache_size_bytes()
        
        if current_size + required_bytes <= self.max_size_bytes:
            return True
        
        # Éviction intelligente nécessaire
        bytes_to_free = (current_size + required_bytes) - self.max_size_bytes + (self.max_size_bytes // 10)  # +10% marge
        
        return self._evict_entries(bytes_to_free)
    
    def _evict_entries(self, bytes_to_free: int) -> bool:
        """
        Éviction intelligente des entrées selon LRU + priorité.
        
        Args:
            bytes_to_free: Nombre de bytes à libérer
            
        Returns:
            True si suffisamment d'espace libéré
        """
        if not self._cache:
            return False
        
        # Trier par priorité (asc) puis par dernier accès (asc) puis par taille (desc)
        entries_to_evict = sorted(
            [(k, v) for k, v in self._cache.items()],
            key=lambda x: (x[1].priority.value, x[1].last_accessed, -x[1].size_bytes)
        )
        
        freed_bytes = 0
        evicted_count = 0
        
        for cache_key, entry in entries_to_evict:
            if freed_bytes >= bytes_to_free:
                break
            
            # Ne pas évincer les entrées critiques récentes
            if entry.priority == CachePriority.CRITICAL and entry.age_seconds < 300:
                continue
            
            freed_bytes += entry.size_bytes
            del self._cache[cache_key]
            evicted_count += 1
            
            logger.debug(f"🗑️ Evicted entry: {cache_key[:8]} (priority: {entry.priority.name}, size: {entry.size_bytes}B)")
        
        self._stats['evictions'] += evicted_count
        
        success = freed_bytes >= bytes_to_free
        logger.info(f"🧹 Cache eviction {'✅ successful' if success else '❌ insufficient'}: freed {freed_bytes}B, evicted {evicted_count} entries")
        
        return success
    
    def _maybe_cleanup(self) -> None:
        """Nettoyage périodique des entrées expirées."""
        if time.time() - self._last_cleanup < self.cleanup_interval:
            return
        
        expired_keys = []
        for cache_key, entry in self._cache.items():
            if entry.is_expired:
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"🧹 Cleanup: removed {len(expired_keys)} expired entries")
            self._stats['cleanups'] += 1
        
        self._last_cleanup = time.time()
    
    def get_cache_size_bytes(self) -> int:
        """Retourne la taille actuelle du cache en bytes."""
        return sum(entry.size_bytes for entry in self._cache.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache."""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / max(total_requests, 1)) * 100
        
        return {
            'cache_entries': len(self._cache),
            'cache_size_mb': self.get_cache_size_bytes() / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'hit_rate_percent': round(hit_rate, 2),
            'total_hits': self._stats['hits'],
            'total_misses': self._stats['misses'],
            'total_evictions': self._stats['evictions'],
            'total_cleanups': self._stats['cleanups'],
            'bytes_saved_mb': self._stats['bytes_saved'] / (1024 * 1024),
            'avg_entry_size_kb': (self.get_cache_size_bytes() / max(len(self._cache), 1)) / 1024
        }
    
    def clear(self) -> int:
        """Vide complètement le cache."""
        cleared_count = len(self._cache)
        self._cache.clear()
        logger.info(f"🗑️ Cache cleared: {cleared_count} entries removed")
        return cleared_count
    
    def get_entry_details(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retourne les détails d'une entrée de cache."""
        if cache_key not in self._cache:
            return None
        
        entry = self._cache[cache_key]
        return {
            'cache_key': cache_key,
            'content_length': len(entry.decompressed_content),
            'size_bytes': entry.size_bytes,
            'created_at': datetime.fromtimestamp(entry.created_at).isoformat(),
            'last_accessed': datetime.fromtimestamp(entry.last_accessed).isoformat(),
            'age_seconds': entry.age_seconds,
            'access_count': entry.access_count,
            'ttl_seconds': entry.ttl_seconds,
            'priority': entry.priority.name,
            'is_compressed': entry.compressed_content is not None,
            'is_expired': entry.is_expired,
            'metadata': entry.metadata
        }


# Instance globale pour utilisation dans les clients Gemini
_global_cache_optimizer: Optional[GeminiCacheOptimizer] = None

def get_cache_optimizer(max_size_mb: int = 50) -> GeminiCacheOptimizer:
    """Retourne l'instance globale du cache optimizer."""
    global _global_cache_optimizer
    if _global_cache_optimizer is None:
        _global_cache_optimizer = GeminiCacheOptimizer(max_size_mb=max_size_mb)
    return _global_cache_optimizer

def cache_gemini_call(cache_optimizer: GeminiCacheOptimizer = None):
    """
    Décorateur pour cache automatique des appels Gemini.
    
    Usage:
        @cache_gemini_call()
        def my_gemini_method(self, prompt, user_data, model_config):
            return actual_api_call()
    """
    def decorator(func):
        def wrapper(self, prompt: str, user_data: Dict[str, Any], model_config: Dict[str, Any] = None, **kwargs):
            nonlocal cache_optimizer
            if cache_optimizer is None:
                cache_optimizer = get_cache_optimizer()
            
            # Vérifier cache
            cached_content = cache_optimizer.get(prompt, user_data, model_config)
            if cached_content is not None:
                return cached_content
            
            # Cache miss - appel API réel
            result = func(self, prompt, user_data, model_config, **kwargs)
            
            # Mettre en cache le résultat
            if result:
                cache_optimizer.set(prompt, user_data, result, model_config)
            
            return result
        
        return wrapper
    return decorator