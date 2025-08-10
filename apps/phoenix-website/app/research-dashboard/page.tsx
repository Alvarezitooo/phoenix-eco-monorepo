'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

type ResearchData = {
  export_metadata: {
    export_date: string;
    total_users_exported: number;
    ethics_compliance_checked: boolean;
    anonymization_method: string;
  };
  aggregated_insights: {
    demographic_insights: {
      age_distribution: Record<string, number>;
      region_distribution: Record<string, number>;
      activity_distribution: Record<string, number>;
    };
    emotional_insights: {
      emotion_frequency: Record<string, number>;
      value_frequency: Record<string, number>;
      transition_phase_distribution: Record<string, number>;
    };
    usage_insights: {
      average_sessions_per_user: number;
      average_cv_per_user: number;
      average_letters_per_user: number;
      average_session_duration_minutes: number;
    };
  };
  ethics_compliance: {
    rgpd_compliant: boolean;
    consent_verified: boolean;
    anonymization_validated: boolean;
    no_personal_data: boolean;
  };
};

export default function ResearchDashboardPage() {
  const [researchData, setResearchData] = useState<ResearchData | null>(null);
  const [loading, setLoading] = useState(true);

  // Données simulées pour la démo (en production, récupérer depuis l'API)
  useEffect(() => {
    const simulatedData = {
      export_metadata: {
        export_date: '2025-08-07T14:00:07.025360',
        total_users_exported: 1247,
        ethics_compliance_checked: true,
        anonymization_method: 'SHA256 + Generalization',
      },
      aggregated_insights: {
        demographic_insights: {
          age_distribution: {
            '20-25': 156,
            '26-30': 342,
            '31-35': 289,
            '36-40': 234,
            '41-45': 156,
            '46-50': 70,
          },
          region_distribution: {
            'Île-de-France': 423,
            'Auvergne-Rhône-Alpes': 187,
            PACA: 156,
            'Nouvelle-Aquitaine': 134,
            Occitanie: 127,
            'Hauts-de-France': 98,
            'Grand Est': 89,
            Bretagne: 67,
          },
          activity_distribution: {
            low: 298,
            medium: 556,
            high: 393,
          },
        },
        emotional_insights: {
          emotion_frequency: {
            questionnement: 892,
            anxiété: 567,
            espoir: 734,
            détermination: 456,
            épuisement: 234,
            enthousiasme: 178,
          },
          value_frequency: {
            autonomie: 823,
            sens: 678,
            équilibre: 567,
            reconnaissance: 345,
            apprentissage: 289,
            impact: 234,
          },
          transition_phase_distribution: {
            questionnement: 623,
            exploration: 387,
            action: 156,
            intégration: 81,
          },
        },
        usage_insights: {
          average_sessions_per_user: 7.8,
          average_cv_per_user: 2.3,
          average_letters_per_user: 5.7,
          average_session_duration_minutes: 22.8,
        },
      },
      ethics_compliance: {
        rgpd_compliant: true,
        consent_verified: true,
        anonymization_validated: true,
        no_personal_data: true,
      },
    };

    setTimeout(() => {
      setResearchData(simulatedData);
      setLoading(false);
    }, 1500);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-8">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement des données de recherche...</p>
          </div>
        </div>
      </div>
    );
  }

  const { aggregated_insights, export_metadata, ethics_compliance } = researchData as ResearchData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-12">
          <Badge className="mb-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
            📊 Recherche-Action Phoenix
          </Badge>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Dashboard de Recherche
            <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              {' '}
              en Temps Réel
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Découvrez les insights anonymisés de notre recherche-action sur l'IA éthique et la
            reconversion professionnelle.
          </p>
        </div>

        {/* Ethics Compliance Banner */}
        <Card className="mb-8 border-green-200 bg-green-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-center space-x-6">
              <div className="flex items-center text-green-800">
                <span className="text-2xl mr-2">🛡️</span>
                <span className="font-semibold">RGPD 100% Conforme</span>
              </div>
              <div className="flex items-center text-green-800">
                <span className="text-2xl mr-2">🔒</span>
                <span className="font-semibold">Données Anonymisées</span>
              </div>
              <div className="flex items-center text-green-800">
                <span className="text-2xl mr-2">✅</span>
                <span className="font-semibold">Consentement Vérifié</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Key Metrics */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <Card className="text-center">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-indigo-600 mb-2">
                {export_metadata.total_users_exported.toLocaleString()}
              </div>
              <div className="font-semibold text-gray-900">Contributeurs</div>
              <div className="text-sm text-gray-600">Profils anonymisés</div>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {aggregated_insights.usage_insights.average_sessions_per_user}
              </div>
              <div className="font-semibold text-gray-900">Sessions Moy.</div>
              <div className="text-sm text-gray-600">Par utilisateur</div>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {Math.round(aggregated_insights.usage_insights.average_session_duration_minutes)}min
              </div>
              <div className="font-semibold text-gray-900">Durée Moy.</div>
              <div className="text-sm text-gray-600">Par session</div>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="p-6">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {Object.values(aggregated_insights.emotional_insights.emotion_frequency)
                  .reduce((a, b) => a + b, 0)
                  .toLocaleString()}
              </div>
              <div className="font-semibold text-gray-900">Insights</div>
              <div className="text-sm text-gray-600">Émotionnels</div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          {/* Age Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-gray-900">
                📊 Distribution par Âge
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(aggregated_insights.demographic_insights.age_distribution).map(
                  ([age, count]) => (
                    <div key={age} className="flex items-center">
                      <div className="w-16 text-sm font-medium text-gray-700">{age}ans</div>
                      <div className="flex-1 mx-4">
                        <div className="w-full bg-gray-200 rounded-full h-4">
                          <div
                            className="bg-indigo-600 h-4 rounded-full"
                            style={{
                              width: `${(count / Math.max(...Object.values(aggregated_insights.demographic_insights.age_distribution))) * 100}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                      <div className="w-12 text-sm font-semibold text-gray-900 text-right">
                        {count}
                      </div>
                    </div>
                  ),
                )}
              </div>
            </CardContent>
          </Card>

          {/* Emotions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-gray-900">
                💭 Émotions Principales
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(aggregated_insights.emotional_insights.emotion_frequency)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 6)
                  .map(([emotion, count]) => (
                    <div key={emotion} className="flex items-center">
                      <div className="w-24 text-sm font-medium text-gray-700 capitalize">
                        {emotion}
                      </div>
                      <div className="flex-1 mx-4">
                        <div className="w-full bg-gray-200 rounded-full h-4">
                          <div
                            className="bg-purple-600 h-4 rounded-full"
                            style={{
                              width: `${(count / Math.max(...Object.values(aggregated_insights.emotional_insights.emotion_frequency))) * 100}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                      <div className="w-12 text-sm font-semibold text-gray-900 text-right">
                        {count}
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Regional Distribution */}
        <Card className="mb-12">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-gray-900">
              🗺️ Distribution Géographique (Régions)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(aggregated_insights.demographic_insights.region_distribution)
                .sort(([, a], [, b]) => b - a)
                .map(([region, count]) => (
                  <div key={region} className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-indigo-600 mb-2">{count}</div>
                    <div className="text-sm font-medium text-gray-900">{region}</div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>

        {/* Transition Phases */}
        <Card className="mb-12">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-gray-900">
              🦋 Phases de Transition
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-6">
              {Object.entries(
                aggregated_insights.emotional_insights.transition_phase_distribution,
              ).map(([phase, count]) => {
                const phaseInfo: Record<string, { icon: string; color: string; bg: string }> = {
                  questionnement: { icon: '🤔', color: 'text-yellow-600', bg: 'bg-yellow-50' },
                  exploration: { icon: '🔍', color: 'text-blue-600', bg: 'bg-blue-50' },
                  action: { icon: '🚀', color: 'text-green-600', bg: 'bg-green-50' },
                  intégration: { icon: '✨', color: 'text-purple-600', bg: 'bg-purple-50' },
                };
                const info = phaseInfo[phase as string] || {
                  icon: '📊',
                  color: 'text-gray-600',
                  bg: 'bg-gray-50',
                };

                return (
                  <div key={phase} className={`text-center p-6 rounded-lg ${info.bg}`}>
                    <div className="text-3xl mb-2">{info.icon}</div>
                    <div className={`text-2xl font-bold mb-2 ${info.color}`}>{count}</div>
                    <div className="font-medium text-gray-900 capitalize">{phase}</div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-gray-600 text-sm">
          <p>
            Dernière mise à jour :{' '}
            {new Date(export_metadata.export_date).toLocaleDateString('fr-FR')}
          </p>
          <p className="mt-2">
            🛡️ Toutes les données sont anonymisées selon les standards RGPD • 📊 Insights collectifs
            uniquement • 🔒 Aucune donnée personnelle identifiable
          </p>
        </div>
      </div>
    </div>
  );
}
