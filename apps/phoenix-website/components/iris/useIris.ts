// 🤖 IRIS REACT HOOK - Hook personnalisé pour intégrer Iris dans Phoenix Website
'use client';

import { useState, useCallback, useEffect } from 'react';
import { IrisMessage, IrisResponse, IrisConfig } from './IrisTypes';

export const useIris = (config: IrisConfig) => {
  const [messages, setMessages] = useState<IrisMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (
      message: string,
      authToken: string,
      additionalContext?: Record<string, any>,
    ): Promise<IrisResponse | null> => {
      setIsLoading(true);
      setError(null);

      try {
        // Construction du message contextuel
        const contextualMessage = buildContextualMessage(message, config.appContext);

        const response = await fetch(config.apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authToken}`,
          },
          body: JSON.stringify({
            message: contextualMessage,
            context: {
              app: config.appContext,
              additional: additionalContext || {},
            },
          }),
          signal: AbortSignal.timeout(config.timeout),
        });

        if (!response.ok) {
          const errorResponse = await handleErrorResponse(response);
          return errorResponse;
        }

        const data = await response.json();
        const irisResponse: IrisResponse = {
          reply: data.reply,
          status: 'success',
          app_context: config.appContext,
          rate_limit_remaining: parseInt(response.headers.get('X-RateLimit-Remaining') || '0'),
        };

        // Ajouter les messages à l'historique
        setMessages((prev) => [
          ...prev,
          { role: 'user', content: message, timestamp: new Date(), app_context: config.appContext },
          {
            role: 'assistant',
            content: data.reply,
            timestamp: new Date(),
            app_context: config.appContext,
          },
        ]);

        return irisResponse;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Erreur inattendue';
        setError(errorMessage);
        return {
          reply: "😢 Une erreur s'est produite. Réessayez plus tard.",
          status: 'error',
        };
      } finally {
        setIsLoading(false);
      }
    },
    [config],
  );

  const clearHistory = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearHistory,
  };
};

// Fonctions utilitaires
const buildContextualMessage = (message: string, appContext: string): string => {
  const contextPrefixes = {
    'phoenix-letters': 'Dans le contexte de génération de lettres de motivation: ',
    'phoenix-cv': "Dans le contexte d'optimisation de CV: ",
    'phoenix-rise': 'Dans le contexte de développement personnel et journal: ',
    'phoenix-website': 'Dans le contexte général Phoenix: ',
  };

  const prefix = contextPrefixes[appContext as keyof typeof contextPrefixes] || '';
  return `${prefix}${message}`;
};

const handleErrorResponse = async (response: Response): Promise<IrisResponse> => {
  switch (response.status) {
    case 401:
      return {
        reply: '🔒 Session expirée. Reconnectez-vous pour continuer.',
        status: 'auth_error',
      };
    case 402:
      return {
        reply: '📊 Limite quotidienne atteinte. Passez à PREMIUM pour un accès illimité.',
        status: 'quota_exceeded',
      };
    case 429:
      return {
        reply: '⏳ Trop de requêtes. Patientez quelques instants.',
        status: 'rate_limited',
      };
    case 403:
      return {
        reply: '💫 Accès refusé. Vérifiez votre email ou contactez le support.',
        status: 'access_denied',
      };
    default:
      return {
        reply: '😢 Iris est temporairement indisponible.',
        status: 'service_unavailable',
      };
  }
};
