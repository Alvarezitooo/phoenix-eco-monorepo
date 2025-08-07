// 🤖 IRIS WIDGET - Widget flottant Iris pour Phoenix Website
'use client';

import React, { useState } from 'react';
import { IrisChat } from './IrisChat';
import { Button } from '@/components/ui/button';
import { Bot, X, Minimize2, Maximize2 } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface IrisWidgetProps {
  authToken?: string | null;
  className?: string;
}

export const IrisWidget: React.FC<IrisWidgetProps> = ({ authToken, className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);

  const irisConfig = {
    apiUrl: process.env.NEXT_PUBLIC_IRIS_API_URL || 'http://localhost:8003/api/v1/chat',
    appContext: 'phoenix-website' as const,
    timeout: 60000,
  };

  const toggleWidget = () => {
    setIsOpen(!isOpen);
    setIsMinimized(false);
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  return (
    <div className={`fixed bottom-4 right-4 z-50 ${className}`}>
      {/* Bouton d'ouverture du widget */}
      {!isOpen && (
        <Button
          onClick={toggleWidget}
          className="w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
        >
          <Bot className="w-8 h-8 text-white" />
        </Button>
      )}

      {/* Widget Iris ouvert */}
      {isOpen && (
        <Card className="w-96 h-[600px] shadow-2xl border-0 bg-white rounded-lg overflow-hidden">
          {/* Header du widget */}
          <div className="bg-gradient-to-r from-purple-500 to-blue-500 text-white p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="w-6 h-6" />
              <span className="font-semibold">Iris Assistant</span>
            </div>
            <div className="flex items-center gap-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={toggleMinimize}
                className="text-white hover:bg-white/20 p-1 h-8 w-8"
              >
                {isMinimized ? (
                  <Maximize2 className="w-4 h-4" />
                ) : (
                  <Minimize2 className="w-4 h-4" />
                )}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={toggleWidget}
                className="text-white hover:bg-white/20 p-1 h-8 w-8"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Contenu du widget */}
          {!isMinimized && (
            <div className="h-[540px] overflow-hidden">
              <IrisChat
                config={irisConfig}
                authToken={authToken}
                className="h-full border-0 shadow-none"
              />
            </div>
          )}

          {/* Widget minimisé */}
          {isMinimized && (
            <div className="p-4 text-center">
              <Bot className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-600">Iris est prêt à vous aider !</p>
              <Button
                size="sm"
                onClick={toggleMinimize}
                className="mt-2 bg-gradient-to-r from-purple-500 to-blue-500"
              >
                Reprendre la conversation
              </Button>
            </div>
          )}
        </Card>
      )}

      {/* Indicateur de notification (optionnel) */}
      {!isOpen && authToken && (
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
          <span className="text-white text-xs font-bold">!</span>
        </div>
      )}
    </div>
  );
};

export default IrisWidget;
