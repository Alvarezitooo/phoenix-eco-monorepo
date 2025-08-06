// 🤖 IRIS CHAT COMPONENT - Composant React pour l'interface Iris Phoenix Website
'use client';

import React, { useState } from 'react';
import { useIris } from './useIris';
import { IrisConfig } from './IrisTypes';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Send, User, Bot } from 'lucide-react';

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
        'Comment améliorer mon CV pour l\'ATS ?',
        'Quelles compétences mettre en avant ?',
        'Comment structurer mes expériences ?'
      ],
      'phoenix-rise': [
        'Comment progresser dans ma reconversion ?',
        'Quels objectifs me fixer cette semaine ?',
        'Comment gérer mes émotions ?'
      ],
      'phoenix-website': [
        'Présente-moi l\'écosystème Phoenix',
        'Quels sont les avantages de chaque app ?',
        'Comment Phoenix peut-il m\'aider ?'
      ]
    };
    return suggestions[config.appContext as keyof typeof suggestions] || [];
  };

  if (!authToken) {
    return (
      <Card className={`iris-auth-prompt ${className}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-yellow-800">
            🔒 Connectez-vous pour accéder à Iris
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-yellow-700">
            Iris vous aide à optimiser votre stratégie avec des conseils personnalisés.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">💡 Aperçu des capacités d&apos;Iris :</h4>
            <ul className="text-blue-700 space-y-1">
              {getSuggestions().slice(0, 3).map((suggestion, index) => (
                <li key={index}>• {suggestion}</li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`iris-chat ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>{getAppTitle()}</span>
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            🎆 Version PREMIUM
          </Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="iris-messages max-h-96 overflow-y-auto space-y-3 border rounded-lg p-4 bg-gray-50">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <Bot className="w-12 h-12 mx-auto mb-2 text-gray-400" />
              <p>Bonjour ! Je suis Iris, votre assistant IA Phoenix.</p>
              <p className="text-sm">Posez-moi vos questions sur l&apos;écosystème Phoenix !</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-2 max-w-xs lg:max-w-md ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.role === 'user' ? 'bg-blue-500' : 'bg-purple-500'
                  }`}>
                    {message.role === 'user' ? (
                      <User className="w-4 h-4 text-white" />
                    ) : (
                      <Bot className="w-4 h-4 text-white" />
                    )}
                  </div>
                  <div
                    className={`px-4 py-2 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-white border shadow-sm text-gray-800'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <span className="text-xs opacity-75 block mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-red-700 text-sm">❌ {error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="iris-input-form">
          <div className="flex space-x-2">
            <Input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Posez votre question à Iris..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              size="sm"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
        </form>

        <div className="iris-suggestions">
          <p className="text-sm text-gray-600 mb-2">💡 Suggestions :</p>
          <div className="flex flex-wrap gap-2">
            {getSuggestions().slice(0, 3).map((suggestion, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => setInputMessage(suggestion)}
                className="text-xs h-8"
              >
                {suggestion}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};