// 🤖 IRIS SECTION - Section dédiée Iris pour les pages Phoenix Website
'use client';

import React from 'react';
import { IrisChat } from './IrisChat';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Bot, Sparkles, MessageCircle, Zap, Shield, Users } from 'lucide-react';

interface IrisSectionProps {
  title?: string;
  description?: string;
  authToken?: string | null;
  showFeatures?: boolean;
  className?: string;
}

export const IrisSection: React.FC<IrisSectionProps> = ({
  title = "Rencontrez Iris, votre Guide IA Phoenix",
  description = "L'intelligence artificielle qui vous accompagne dans votre transformation professionnelle",
  authToken,
  showFeatures = true,
  className
}) => {
  const irisConfig = {
    apiUrl: process.env.NEXT_PUBLIC_IRIS_API_URL || 'http://localhost:8003/api/v1/chat',
    appContext: 'phoenix-website' as const,
    timeout: 60000
  };

  const features = [
    {
      icon: <MessageCircle className="w-6 h-6" />,
      title: "Conseils Personnalisés",
      description: "Iris adapte ses recommandations à votre profil et vos objectifs uniques"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Réponses Instantanées", 
      description: "Obtenez des conseils experts 24h/24, 7j/7 pour accélérer votre reconversion"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "100% Sécurisé",
      description: "Vos données sont protégées par un chiffrement de niveau entreprise"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Multi-Applications", 
      description: "Iris vous accompagne sur Letters, CV, Rise et toutes les apps Phoenix"
    }
  ];

  return (
    <section className={`py-16 px-4 ${className}`}>
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <Badge variant="secondary" className="bg-purple-100 text-purple-700 px-4 py-2">
              <Bot className="w-4 h-4 mr-2" />
              Intelligence Artificielle Phoenix
            </Badge>
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-6">
            {title}
          </h2>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            {description}
          </p>

          {!authToken && (
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-xl p-6 max-w-2xl mx-auto">
              <Sparkles className="w-8 h-8 text-purple-500 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-purple-800 mb-2">
                Connectez-vous pour débloquer Iris
              </h3>
              <p className="text-purple-700 mb-4">
                Accédez à votre assistant IA personnalisé et commencez votre transformation professionnelle
              </p>
              <Button className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600">
                Se connecter gratuitement
              </Button>
            </div>
          )}
        </div>

        {/* Features Grid */}
        {showFeatures && (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {features.map((feature, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white mx-auto mb-4">
                    {feature.icon}
                  </div>
                  <h3 className="font-semibold text-gray-800 mb-2">{feature.title}</h3>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Chat Interface */}
        <div className="flex justify-center">
          <div className="w-full max-w-4xl">
            <Card className="shadow-2xl border-0 bg-gradient-to-br from-white to-gray-50">
              <CardHeader className="bg-gradient-to-r from-purple-500 to-blue-500 text-white">
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Bot className="w-6 h-6" />
                  Essayez Iris maintenant
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <IrisChat
                  config={irisConfig}
                  authToken={authToken}
                  className="border-0 shadow-none"
                />
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Call to Action */}
        {authToken && (
          <div className="text-center mt-12">
            <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200 max-w-2xl mx-auto">
              <CardContent className="pt-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">
                  Prêt à aller plus loin avec Iris ?
                </h3>
                <p className="text-gray-600 mb-4">
                  Découvrez comment Iris peut vous accompagner dans chaque application Phoenix
                </p>
                <div className="flex flex-wrap justify-center gap-3">
                  <Button variant="outline" className="border-purple-300 hover:bg-purple-50">
                    Iris Letters - Lettres de motivation
                  </Button>
                  <Button variant="outline" className="border-blue-300 hover:bg-blue-50">
                    Iris CV - Optimisation carrière
                  </Button>
                  <Button variant="outline" className="border-green-300 hover:bg-green-50">
                    Iris Coach - Développement personnel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </section>
  );
};