'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function ResearchActionSection() {
  const researchStats = [
    {
      metric: 'Utilisateurs contributeurs',
      value: '1,247',
      description: 'Profils anonymisés pour la recherche',
    },
    {
      metric: 'Insights générés',
      value: '23',
      description: "Découvertes sur l'IA et la reconversion",
    },
    {
      metric: 'Conformité RGPD',
      value: '100%',
      description: 'Protection totale des données personnelles',
    },
    {
      metric: 'Publications académiques',
      value: '3',
      description: "Articles publiés sur l'éthique IA",
    },
  ];

  const researchPrinciples = [
    {
      icon: '🛡️',
      title: 'Privacy by Design',
      description: 'Anonymisation SHA256 irréversible dès la conception',
    },
    {
      icon: '📊',
      title: 'Données Agrégées Uniquement',
      description: 'Aucune donnée individuelle, seulement des insights collectifs',
    },
    {
      icon: '✋',
      title: 'Consentement Explicite',
      description: 'Opt-in volontaire, révocable à tout moment',
    },
    {
      icon: '🎯',
      title: 'Finalité Claire',
      description: "Améliorer l'IA éthique pour les reconversions professionnelles",
    },
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
            🔬 Recherche-Action
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Construisons ensemble l'IA
            <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              {' '}
              éthique{' '}
            </span>
            de demain
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Phoenix mène une recherche-action pionnière sur l'impact de l'IA dans la reconversion
            professionnelle. Vos contributions anonymisées aident à développer des outils plus
            justes et plus humains.
          </p>
        </div>

        {/* Research Stats */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {researchStats.map((stat, index) => (
            <Card
              key={index}
              className="text-center p-6 hover:shadow-lg transition-all duration-300 border-0 bg-white/80 backdrop-blur-sm"
            >
              <CardContent className="p-0">
                <div className="text-3xl font-bold text-indigo-600 mb-2">{stat.value}</div>
                <div className="font-semibold text-gray-900 mb-2">{stat.metric}</div>
                <div className="text-sm text-gray-600">{stat.description}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Research Principles */}
        <div className="mb-16">
          <h3 className="text-2xl font-bold text-center mb-12 text-gray-900">
            Nos Principes Éthiques
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {researchPrinciples.map((principle, index) => (
              <div key={index} className="text-center group">
                <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">
                  {principle.icon}
                </div>
                <h4 className="font-bold text-gray-900 mb-3">{principle.title}</h4>
                <p className="text-gray-600 text-sm leading-relaxed">{principle.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <Card className="p-8 bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-0 max-w-4xl mx-auto">
            <CardContent className="p-0">
              <h3 className="text-2xl font-bold mb-4">Participez à la Recherche-Action Phoenix</h3>
              <p className="text-lg mb-6 opacity-90">
                En utilisant nos outils, vous contribuez à une recherche éthique sur l'IA et la
                reconversion. Vos données restent anonymes et sécurisées selon les standards RGPD
                les plus stricts.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href="https://phoenix-cv.streamlit.app"
                  className="px-6 py-3 bg-white text-indigo-600 rounded-lg font-semibold hover:bg-gray-50 transition-colors duration-300"
                >
                  Essayer Phoenix CV
                </a>
                <a
                  href="https://phoenix-letters.streamlit.app"
                  className="px-6 py-3 border-2 border-white text-white rounded-lg font-semibold hover:bg-white hover:text-indigo-600 transition-colors duration-300"
                >
                  Essayer Phoenix Letters
                </a>
              </div>
              <p className="text-sm mt-4 opacity-75">
                🛡️ 100% anonyme • 📊 Insights collectifs uniquement • ✋ Consentement révocable
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Research Dashboard Link */}
        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">Découvrez nos insights de recherche en temps réel</p>
          <a
            href="/research-dashboard"
            className="inline-flex items-center px-6 py-3 bg-gray-900 text-white rounded-lg font-semibold hover:bg-gray-800 transition-colors duration-300"
          >
            📊 Dashboard de Recherche
            <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </a>
        </div>
      </div>
    </section>
  );
}
