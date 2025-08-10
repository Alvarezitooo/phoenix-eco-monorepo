/**
 * Hook API Dojo sécurisé avec validation côté client
 * Version optimisée du useDojoApi avec sécurité renforcée
 *
 * Author: Claude Phoenix DevSecOps Guardian
 * Version: 2.0.0 - Security Enhanced
 */

import { useState, useCallback, useRef } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_DOJO_API_URL || 'http://127.0.0.1:8000';

interface KaizenEntry {
  user_id: string;
  action: string;
  date: string;
  completed: boolean;
}

interface ZazenSession {
  user_id: string;
  timestamp: string;
  duration: number;
  triggered_by?: string;
}

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  status?: number;
}

interface SecurityValidationResult {
  isValid: boolean;
  error?: string;
}

export const useDojoApiSecure = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 🔒 Cache pour éviter les appels répétés
  const requestCacheRef = useRef<Map<string, { response: any; timestamp: number }>>(new Map());

  // 🔒 Rate limiting simple
  const lastRequestRef = useRef<Map<string, number>>(new Map());
  const RATE_LIMIT_MS = 1000; // 1 requête par seconde max

  // 🔒 Validation sécurité côté client
  const validateKaizenAction = useCallback((action: string): SecurityValidationResult => {
    // Validation basique côté client (complément du serveur)
    if (!action || typeof action !== 'string') {
      return { isValid: false, error: 'Action invalide' };
    }

    if (action.length > 500) {
      return { isValid: false, error: 'Action trop longue (max 500 caractères)' };
    }

    // Détection patterns suspects (basique)
    const suspiciousPatterns = [
      /<script[^>]*>/i,
      /javascript:/i,
      /vbscript:/i,
      /on\w+\s*=/i,
      /(union|select|insert|delete|update|drop)\b/i,
    ];

    for (const pattern of suspiciousPatterns) {
      if (pattern.test(action)) {
        return { isValid: false, error: 'Contenu non autorisé détecté' };
      }
    }

    return { isValid: true };
  }, []);

  const validateZazenDuration = useCallback((duration: number): SecurityValidationResult => {
    if (!Number.isInteger(duration) || duration < 30 || duration > 3600) {
      return { isValid: false, error: 'Durée invalide (30s-1h)' };
    }
    return { isValid: true };
  }, []);

  // 🔒 Vérification rate limiting
  const checkRateLimit = useCallback((endpoint: string): boolean => {
    const lastRequest = lastRequestRef.current.get(endpoint) || 0;
    const now = Date.now();

    if (now - lastRequest < RATE_LIMIT_MS) {
      return false; // Too fast
    }

    lastRequestRef.current.set(endpoint, now);
    return true;
  }, []);

  // 🔒 Génération clé cache
  const getCacheKey = useCallback((endpoint: string, data?: any): string => {
    return `${endpoint}_${data ? JSON.stringify(data) : ''}`;
  }, []);

  // 🔒 Vérification cache
  const checkCache = useCallback((key: string, ttlMs: number = 5000): any => {
    const cached = requestCacheRef.current.get(key);
    if (cached && Date.now() - cached.timestamp < ttlMs) {
      return cached.response;
    }
    return null;
  }, []);

  // 🔒 Mise en cache
  const setCache = useCallback((key: string, response: any) => {
    requestCacheRef.current.set(key, {
      response,
      timestamp: Date.now(),
    });

    // Nettoyer cache si trop volumineux
    if (requestCacheRef.current.size > 50) {
      const oldestKey = requestCacheRef.current.keys().next().value;
      requestCacheRef.current.delete(oldestKey);
    }
  }, []);

  const createKaizen = useCallback(
    async (kaizenData: KaizenEntry): Promise<ApiResponse> => {
      const endpoint = '/kaizen';

      // 🔒 Validation sécurité
      const validation = validateKaizenAction(kaizenData.action);
      if (!validation.isValid) {
        return {
          success: false,
          error: validation.error,
        };
      }

      // 🔒 Rate limiting
      if (!checkRateLimit(endpoint)) {
        return {
          success: false,
          error: 'Trop de requêtes. Attends un moment.',
        };
      }

      // 🔒 Vérifier cache (éviter double soumission)
      const cacheKey = getCacheKey(endpoint, kaizenData);
      const cached = checkCache(cacheKey, 2000); // 2s cache
      if (cached) {
        console.log('✅ Using cached Kaizen response');
        return cached;
      }

      setIsLoading(true);
      setError(null);

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(kaizenData),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          let errorMessage = `Erreur HTTP: ${response.status}`;

          try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
          } catch (e) {
            // Ignore JSON parse error
          }

          throw new Error(errorMessage);
        }

        const data = await response.json();
        console.log('✅ Kaizen created:', data);

        const result = {
          success: true,
          data,
          status: response.status,
        };

        // 🔒 Mettre en cache
        setCache(cacheKey, result);

        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Erreur inconnue';
        console.error('❌ Error creating Kaizen:', errorMessage);
        setError(errorMessage);

        return {
          success: false,
          error: errorMessage,
        };
      } finally {
        setIsLoading(false);
      }
    },
    [validateKaizenAction, checkRateLimit, getCacheKey, checkCache, setCache],
  );

  const createZazenSession = useCallback(
    async (sessionData: ZazenSession): Promise<ApiResponse> => {
      const endpoint = '/zazen-session';

      // 🔒 Validation sécurité
      const validation = validateZazenDuration(sessionData.duration);
      if (!validation.isValid) {
        return {
          success: false,
          error: validation.error,
        };
      }

      // 🔒 Rate limiting
      if (!checkRateLimit(endpoint)) {
        return {
          success: false,
          error: 'Trop de requêtes. Attends un moment.',
        };
      }

      setIsLoading(true);
      setError(null);

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(sessionData),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          let errorMessage = `Erreur HTTP: ${response.status}`;

          try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
          } catch (e) {
            // Ignore JSON parse error
          }

          throw new Error(errorMessage);
        }

        const data = await response.json();
        console.log('✅ Zazen session created:', data);

        return {
          success: true,
          data,
          status: response.status,
        };
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Erreur inconnue';
        console.error('❌ Error creating Zazen session:', errorMessage);
        setError(errorMessage);

        return {
          success: false,
          error: errorMessage,
        };
      } finally {
        setIsLoading(false);
      }
    },
    [validateZazenDuration, checkRateLimit],
  );

  const getUserKaizens = useCallback(
    async (userId: string, limit: number = 50): Promise<ApiResponse> => {
      const endpoint = `/kaizen/${userId}`;

      // 🔒 Rate limiting
      if (!checkRateLimit(endpoint)) {
        return {
          success: false,
          error: 'Trop de requêtes. Attends un moment.',
        };
      }

      // 🔒 Vérifier cache
      const cacheKey = getCacheKey(endpoint, { limit });
      const cached = checkCache(cacheKey, 10000); // 10s cache pour GET
      if (cached) {
        console.log('✅ Using cached Kaizens');
        return cached;
      }

      setIsLoading(true);
      setError(null);

      try {
        const url = new URL(`${API_BASE_URL}${endpoint}`);
        url.searchParams.set('limit', limit.toString());

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);

        const response = await fetch(url.toString(), {
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        console.log('✅ Kaizens retrieved:', data.length, 'entries');

        const result = {
          success: true,
          data,
          status: response.status,
        };

        // 🔒 Mettre en cache
        setCache(cacheKey, result);

        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Erreur inconnue';
        console.error('❌ Error retrieving Kaizens:', errorMessage);
        setError(errorMessage);

        return {
          success: false,
          error: errorMessage,
        };
      } finally {
        setIsLoading(false);
      }
    },
    [checkRateLimit, getCacheKey, checkCache, setCache],
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearCache = useCallback(() => {
    requestCacheRef.current.clear();
    lastRequestRef.current.clear();
  }, []);

  return {
    // Actions sécurisées
    createKaizen,
    createZazenSession,
    getUserKaizens,

    // Utils
    clearError,
    clearCache,

    // State
    isLoading,
    error,

    // Config
    apiBaseUrl: API_BASE_URL,

    // Stats
    cacheSize: requestCacheRef.current.size,
  };
};

export default useDojoApiSecure;
