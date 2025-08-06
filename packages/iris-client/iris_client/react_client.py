"""
🤖 IRIS REACT CLIENT - Client Iris pour applications React/Next.js
Interface JavaScript/TypeScript pour l'agent Iris côté frontend.
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class IrisReactClient:
    """
    Client Iris pour applications React/Next.js.
    Génère le code TypeScript nécessaire pour l'intégration.
    """
    
    def __init__(self, app_context: str = "phoenix-website"):
        self.app_context = app_context
    
    def generate_typescript_interface(self) -> str:
        """Génère les interfaces TypeScript pour Iris"""
        return '''
// 🤖 IRIS REACT CLIENT - Interfaces TypeScript
export interface IrisMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  app_context?: string;
}

export interface IrisResponse {
  reply: string;
  status: 'success' | 'auth_error' | 'quota_exceeded' | 'rate_limited' | 'access_denied' | 'service_unavailable' | 'error';
  app_context?: string;
  suggestions?: string[];
  rate_limit_remaining?: number;
}

export interface IrisConfig {
  apiUrl: string;
  appContext: 'phoenix-letters' | 'phoenix-cv' | 'phoenix-rise' | 'phoenix-website';
  timeout: number;
}
'''
    
    def generate_react_hook(self) -> str:
        """Génère le hook React pour Iris"""
        return '''
// 🤖 IRIS REACT HOOK - Hook personnalisé pour intégrer Iris
import { useState, useCallback, useEffect } from 'react';
import { IrisMessage, IrisResponse, IrisConfig } from './iris-types';

export const useIris = (config: IrisConfig) => {
  const [messages, setMessages] = useState<IrisMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (
    message: string, 
    authToken: string,
    additionalContext?: Record<string, any>
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
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          message: contextualMessage,
          context: {
            app: config.appContext,
            additional: additionalContext || {}
          }
        }),
        signal: AbortSignal.timeout(config.timeout)
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
        rate_limit_remaining: parseInt(response.headers.get('X-RateLimit-Remaining') || '0')
      };

      // Ajouter les messages à l\\'historique
      setMessages(prev => [
        ...prev,
        { role: 'user', content: message, timestamp: new Date(), app_context: config.appContext },
        { role: 'assistant', content: data.reply, timestamp: new Date(), app_context: config.appContext }
      ]);

      return irisResponse;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur inattendue';
      setError(errorMessage);
      return {
        reply: '😢 Une erreur s\\'est produite. Réessayez plus tard.',
        status: 'error'
      };
    } finally {
      setIsLoading(false);
    }
  }, [config]);

  const clearHistory = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearHistory
  };
};

// Fonctions utilitaires
const buildContextualMessage = (message: string, appContext: string): string => {
  const contextPrefixes = {
    'phoenix-letters': 'Dans le contexte de génération de lettres de motivation: ',
    'phoenix-cv': 'Dans le contexte d\\'optimisation de CV: ',
    'phoenix-rise': 'Dans le contexte de développement personnel et journal: ',
    'phoenix-website': 'Dans le contexte général Phoenix: '
  };
  
  const prefix = contextPrefixes[appContext as keyof typeof contextPrefixes] || '';
  return `${prefix}${message}`;
};

const handleErrorResponse = async (response: Response): Promise<IrisResponse> => {
  switch (response.status) {
    case 401:
      return {
        reply: '🔒 Session expirée. Reconnectez-vous pour continuer.',
        status: 'auth_error'
      };
    case 402:
      return {
        reply: '📊 Limite quotidienne atteinte. Passez à PREMIUM pour un accès illimité.',
        status: 'quota_exceeded'
      };
    case 429:
      return {
        reply: '⏳ Trop de requêtes. Patientez quelques instants.',
        status: 'rate_limited'
      };
    case 403:
      return {
        reply: '💫 Accès refusé. Vérifiez votre email ou contactez le support.',
        status: 'access_denied'
      };
    default:
      return {
        reply: '😢 Iris est temporairement indisponible.',
        status: 'service_unavailable'
      };
  }
};
'''
    
    def generate_react_component(self) -> str:
        """Génère le composant React pour l'interface Iris"""
        return '''
// 🤖 IRIS CHAT COMPONENT - Composant React pour l\\'interface Iris
import React, { useState } from 'react';
import { useIris } from './useIris';
import { IrisConfig } from './iris-types';

interface IrisChatProps {
  config: IrisConfig;
  authToken: string | null;
  className?: string;
}

export const IrisChat: React.FC<IrisChatProps> = ({ config, authToken, className }) => {
  const { messages, isLoading, error, sendMessage } = useIris(config);
  const [inputMessage, setInputMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !authToken || isLoading) return;

    await sendMessage(inputMessage, authToken);
    setInputMessage('');
  };

  const getAppTitle = () => {
    const titles = {
      'phoenix-letters': '🤖 Iris Lettres - Expert Lettres de Motivation',
      'phoenix-cv': '🤖 Iris CV - Optimisation CV & Carrière',
      'phoenix-rise': '🤖 Iris Coach - Accompagnement Reconversion',
      'phoenix-website': '🤖 Iris Phoenix - Guide Écosystème'
    };
    return titles[config.appContext as keyof typeof titles] || '🤖 Iris Assistant';
  };

  const getSuggestions = () => {
    const suggestions = {
      'phoenix-letters': [
        'Comment personnaliser ma lettre pour ce poste ?',
        'Quels mots-clés ATS utiliser ?',
        'Comment structurer ma motivation ?'
      ],
      'phoenix-cv': [
        'Comment améliorer mon CV pour l\\'ATS ?',
        'Quelles compétences mettre en avant ?',
        'Comment structurer mes expériences ?'
      ],
      'phoenix-rise': [
        'Comment progresser dans ma reconversion ?',
        'Quels objectifs me fixer cette semaine ?',
        'Comment gérer mes émotions ?'
      ],
      'phoenix-website': [
        'Présente-moi l\\'écosystème Phoenix',
        'Quels sont les avantages de chaque app ?',
        'Comment Phoenix peut-il m\\'aider ?'
      ]
    };
    return suggestions[config.appContext as keyof typeof suggestions] || [];
  };

  if (!authToken) {
    return (
      <div className={`iris-auth-prompt ${className}`}>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">
            🔒 Connectez-vous pour accéder à Iris
          </h3>
          <p className="text-yellow-700">
            Iris vous aide à optimiser votre stratégie avec des conseils personnalisés.
          </p>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-800 mb-2">💡 Aperçu des capacités d\\'Iris :</h4>
          <ul className="text-blue-700 space-y-1">
            {getSuggestions().slice(0, 3).map((suggestion, index) => (
              <li key={index}>• {suggestion}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className={`iris-chat ${className}`}>
      <div className="iris-header mb-4">
        <h2 className="text-xl font-bold text-gray-800">{getAppTitle()}</h2>
        <div className="bg-green-50 border border-green-200 rounded-lg p-2 mt-2">
          <span className="text-green-700 text-sm">
            🎆 Version PREMIUM : Accès illimité à Iris
          </span>
        </div>
      </div>

      <div className="iris-messages max-h-96 overflow-y-auto mb-4 space-y-3">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <span className="text-xs opacity-75">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          <p className="text-red-700 text-sm">❌ {error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="iris-input-form">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Posez votre question à Iris..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputMessage.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </form>

      <div className="iris-suggestions mt-4">
        <p className="text-sm text-gray-600 mb-2">💡 Suggestions :</p>
        <div className="flex flex-wrap gap-2">
          {getSuggestions().slice(0, 2).map((suggestion, index) => (
            <button
              key={index}
              onClick={() => setInputMessage(suggestion)}
              className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded-full text-gray-700"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
'''

    def save_react_files(self, output_dir: str = "./iris-react-components"):
        """Sauvegarde tous les fichiers React/TypeScript nécessaires"""
        import os
        
        # Créer le dossier de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        # Sauvegarder les fichiers
        files = {
            "iris-types.ts": self.generate_typescript_interface(),
            "useIris.ts": self.generate_react_hook(),
            "IrisChat.tsx": self.generate_react_component(),
            "README-Integration.md": self._generate_integration_readme()
        }
        
        for filename, content in files.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Fichier généré: {filepath}")
        
        return output_dir
    
    def _generate_integration_readme(self) -> str:
        """Génère la documentation d'intégration React"""
        return '''
# 🤖 Intégration Iris dans Phoenix Website (Next.js)

## Installation

1. Copiez les fichiers dans votre projet Next.js :
   - `iris-types.ts` → `types/iris.ts`
   - `useIris.ts` → `hooks/useIris.ts`
   - `IrisChat.tsx` → `components/IrisChat.tsx`

2. Installez les dépendances nécessaires (déjà présentes dans Next.js)

## Usage de base

```tsx
import { IrisChat } from '@/components/IrisChat';

export default function HomePage() {
  const authToken = useAuthToken(); // Votre système d'auth
  
  const irisConfig = {
    apiUrl: 'http://localhost:8003/api/v1/chat',
    appContext: 'phoenix-website' as const,
    timeout: 60000
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <IrisChat 
        config={irisConfig}
        authToken={authToken}
        className="max-w-2xl mx-auto"
      />
    </div>
  );
}
```

## Intégration dans la navigation

```tsx
// components/Navigation.tsx
import { useState } from 'react';
import { IrisChat } from './IrisChat';

export const Navigation = () => {
  const [showIris, setShowIris] = useState(false);

  return (
    <>
      <nav className="...">
        <button 
          onClick={() => setShowIris(true)}
          className="iris-toggle-btn"
        >
          🤖 Iris
        </button>
      </nav>
      
      {showIris && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50">
          <div className="absolute right-4 top-4 bg-white rounded-lg p-4 w-96 max-h-[80vh] overflow-y-auto">
            <button 
              onClick={() => setShowIris(false)}
              className="float-right text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
            <IrisChat config={irisConfig} authToken={authToken} />
          </div>
        </div>
      )}
    </>
  );
};
```

## Configuration avancée

```tsx
// Contexte global pour Iris
import { createContext, useContext } from 'react';

const IrisContext = createContext({
  isAvailable: false,
  userTier: 'FREE',
  messagesRemaining: 5
});

export const IrisProvider = ({ children }) => {
  // Logique de gestion d'état Iris
  return (
    <IrisContext.Provider value={irisContextValue}>
      {children}
    </IrisContext.Provider>
  );
};
```

## Styles CSS (Tailwind)

Les composants utilisent Tailwind CSS. Ajoutez ces classes personnalisées si nécessaire :

```css
/* globals.css */
.iris-chat {
  @apply bg-white rounded-lg shadow-lg;
}

.iris-message-user {
  @apply bg-blue-500 text-white rounded-lg px-4 py-2 max-w-xs ml-auto;
}

.iris-message-assistant {
  @apply bg-gray-100 text-gray-800 rounded-lg px-4 py-2 max-w-xs;
}
```
'''