/**
 * 🌱 Phoenix Green Metrics Card Component
 *
 * Carte détaillée affichant les métriques environnementales principales.
 * Utilisée dans les sections du site vitrine et la page dédiée Green AI.
 *
 * Author: Claude Phoenix DevSecOps Guardian
 * Version: 1.0.0 - Phoenix Green AI Initiative
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  Leaf,
  TrendingDown,
  Award,
  BarChart3,
  Users,
  Calendar,
  ExternalLink,
  RefreshCw,
} from 'lucide-react';

interface GreenMetrics {
  daily_co2_grams: number;
  monthly_co2_grams: number;
  co2_saved_vs_competitors: string;
  cache_hit_ratio: number;
  green_ai_grade: string;
  efficiency_score: number;
  total_letters_generated: number;
  green_letters_percentage: number;
  iso_42001_compliance: number;
  vs_chatgpt_improvement: string;
  vs_claude_improvement: string;
  industry_position: string;
  calculated: {
    co2_per_letter: number;
    trees_equivalent_monthly: number;
    marketing_headlines: {
      primary: string;
      secondary: string;
      impact: string;
      certification: string;
    };
  };
  last_updated: string;
}

interface GreenMetricsCardProps {
  variant?: 'overview' | 'detailed' | 'comparison';
  showRefresh?: boolean;
  className?: string;
}

export default function GreenMetricsCard({
  variant = 'overview',
  showRefresh = false,
  className = '',
}: GreenMetricsCardProps) {
  const [metrics, setMetrics] = useState<GreenMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Désactivation temporaire des fausses métriques
  const fetchMetrics = async (force = false) => {
    try {
      if (force) setIsRefreshing(true);

      // Données honnêtes temporaires
      const honestData = {
        daily_co2_grams: 0,
        monthly_co2_grams: 0,
        co2_saved_vs_competitors: 'Non mesuré',
        cache_hit_ratio: 0,
        green_ai_grade: 'En cours',
        efficiency_score: 0,
        total_letters_generated: 0,
        green_letters_percentage: 0,
        iso_42001_compliance: 0,
        vs_chatgpt_improvement: 'Non comparé',
        vs_claude_improvement: 'Non comparé',
        industry_position: 'startup',
        calculated: {
          co2_per_letter: 0,
          trees_equivalent_monthly: 0,
          marketing_headlines: {
            primary: 'Phoenix démarre sa démarche écologique',
            secondary: 'Objectifs et mesures en développement',
            impact: 'Premiers pas vers une IA responsable',
            certification: 'Feuille de route écologique 2025',
          },
        },
        last_updated: new Date().toISOString(),
      };

      setMetrics(honestData);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('🌱 Erreur chargement métriques:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchMetrics();

    // Auto-refresh toutes les 10 minutes
    const interval = setInterval(() => fetchMetrics(), 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Formatage des nombres pour l'affichage
  const formatNumber = (num: number, decimals = 1): string => {
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  };

  // Formatage de la date de dernière mise à jour
  const formatLastUpdate = (date: Date): string => {
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffMinutes < 1) return "À l'instant";
    if (diffMinutes < 60) return `il y a ${diffMinutes}min`;

    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `il y a ${diffHours}h`;

    return date.toLocaleDateString('fr-FR');
  };

  // Affichage loading
  if (isLoading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-200 rounded-lg"></div>
              <div className="w-32 h-6 bg-green-200 rounded"></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="w-full h-16 bg-green-200 rounded-lg"></div>
              <div className="w-full h-16 bg-green-200 rounded-lg"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-xl p-6 ${className}`}>
        <div className="text-center">
          <div className="text-red-600 font-medium">Métriques Green AI indisponibles</div>
          <button
            onClick={() => fetchMetrics(true)}
            className="mt-2 text-sm text-red-500 hover:text-red-700 underline"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  // Vue d'ensemble (homepage, sections principales)
  if (variant === 'overview') {
    return (
      <div
        className={`bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 
                      border border-green-200 rounded-xl p-6 ${className}`}
      >
        {/* Header avec badge certification */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Leaf className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-green-800">Phoenix Green AI</h3>
              <p className="text-sm text-green-600">
                {metrics.calculated.marketing_headlines.certification}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Award className="w-5 h-5 text-yellow-500" />
            <span className="text-2xl font-bold text-green-700">{metrics.green_ai_grade}</span>
          </div>
        </div>

        {/* Métriques principales */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-white/60 rounded-lg p-4 text-center">
            <TrendingDown className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-green-700">
              {metrics.co2_saved_vs_competitors}
            </div>
            <div className="text-sm text-gray-600">moins de CO2</div>
          </div>

          <div className="bg-white/60 rounded-lg p-4 text-center">
            <BarChart3 className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-blue-700">{metrics.efficiency_score}/100</div>
            <div className="text-sm text-gray-600">efficacité</div>
          </div>

          <div className="bg-white/60 rounded-lg p-4 text-center">
            <Users className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-purple-700">
              {formatNumber(metrics.total_letters_generated, 0)}
            </div>
            <div className="text-sm text-gray-600">lettres vertes</div>
          </div>
        </div>

        {/* Message principal */}
        <div className="bg-white/80 rounded-lg p-4 border-l-4 border-green-500">
          <p className="text-green-800 font-medium">
            {metrics.calculated.marketing_headlines.primary}
          </p>
          <p className="text-sm text-gray-600 mt-1">
            {metrics.calculated.marketing_headlines.impact}
          </p>
        </div>

        {/* Footer avec dernière mise à jour */}
        {(showRefresh || lastUpdate) && (
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-green-200">
            {lastUpdate && (
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <Calendar className="w-3 h-3" />
                <span>Mis à jour {formatLastUpdate(lastUpdate)}</span>
              </div>
            )}

            {showRefresh && (
              <button
                onClick={() => fetchMetrics(true)}
                disabled={isRefreshing}
                className="flex items-center space-x-1 text-xs text-green-600 hover:text-green-700 
                         disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span>Actualiser</span>
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  // Vue détaillée (page Green AI dédiée)
  if (variant === 'detailed') {
    return (
      <div className={`space-y-6 ${className}`}>
        {/* Métriques carbone détaillées */}
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Leaf className="w-5 h-5 text-green-600 mr-2" />
            Empreinte Carbone
          </h4>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-700">
                {formatNumber(metrics.daily_co2_grams, 3)}g
              </div>
              <div className="text-sm text-gray-600">CO2 aujourd'hui</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-green-700">
                {formatNumber(metrics.monthly_co2_grams, 1)}g
              </div>
              <div className="text-sm text-gray-600">CO2 ce mois</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-green-700">
                {formatNumber(metrics.calculated.co2_per_letter, 4)}g
              </div>
              <div className="text-sm text-gray-600">CO2 par lettre</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-green-700">
                {formatNumber(metrics.calculated.trees_equivalent_monthly, 2)}
              </div>
              <div className="text-sm text-gray-600">arbres équivalent</div>
            </div>
          </div>
        </div>

        {/* Performance technique */}
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 text-blue-600 mr-2" />
            Performance Green AI
          </h4>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Efficacité Cache</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${metrics.cache_hit_ratio * 100}%` }}
                  ></div>
                </div>
                <span className="font-semibold text-blue-700">
                  {formatNumber(metrics.cache_hit_ratio * 100, 1)}%
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-gray-600">Score Efficacité Globale</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${metrics.efficiency_score}%` }}
                  ></div>
                </div>
                <span className="font-semibold text-green-700">{metrics.efficiency_score}/100</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-gray-600">Conformité ISO/IEC 42001</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-yellow-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${metrics.iso_42001_compliance}%` }}
                  ></div>
                </div>
                <span className="font-semibold text-yellow-700">
                  {formatNumber(metrics.iso_42001_compliance, 1)}/100
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Impact utilisateur */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Users className="w-5 h-5 text-purple-600 mr-2" />
            Impact Reconversions
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="text-3xl font-bold text-purple-700 mb-1">
                {formatNumber(metrics.total_letters_generated, 0)}
              </div>
              <div className="text-gray-600">lettres de motivation générées</div>
              <div className="text-sm text-purple-600 mt-1">
                {formatNumber(metrics.green_letters_percentage, 1)}% avec impact carbone minimal
              </div>
            </div>

            <div className="flex items-center justify-center">
              <div className="text-center">
                <div className="text-lg font-medium text-gray-700 mb-2">Position Marché</div>
                <div className="inline-flex items-center space-x-2 bg-white px-4 py-2 rounded-full border border-purple-200">
                  <Award className="w-4 h-4 text-yellow-500" />
                  <span className="font-semibold text-purple-700 capitalize">
                    {metrics.industry_position}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Vue comparaison concurrents
  if (variant === 'comparison') {
    return (
      <div className={`bg-white border border-gray-200 rounded-xl p-6 ${className}`}>
        <h4 className="text-lg font-semibold text-gray-800 mb-6 flex items-center">
          <TrendingDown className="w-5 h-5 text-green-600 mr-2" />
          Comparaison Industrie
        </h4>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <Leaf className="w-4 h-4 text-green-600" />
              </div>
              <div>
                <div className="font-semibold text-green-800">Phoenix Letters</div>
                <div className="text-sm text-green-600">Green AI Certifié</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-green-700">{metrics.green_ai_grade}</div>
              <div className="text-sm text-green-600">Champion</div>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                <span className="text-xs font-bold text-gray-600">GPT</span>
              </div>
              <div>
                <div className="font-medium text-gray-700">ChatGPT</div>
                <div className="text-sm text-gray-500">Standard industrie</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-red-600">{metrics.vs_chatgpt_improvement}</div>
              <div className="text-sm text-gray-500">plus de CO2</div>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                <span className="text-xs font-bold text-gray-600">CL</span>
              </div>
              <div>
                <div className="font-medium text-gray-700">Claude</div>
                <div className="text-sm text-gray-500">Concurrent direct</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-orange-600">
                {metrics.vs_claude_improvement}
              </div>
              <div className="text-sm text-gray-500">plus de CO2</div>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
          <div className="flex items-start space-x-2">
            <ExternalLink className="w-4 h-4 text-blue-600 mt-0.5" />
            <div className="text-sm">
              <div className="font-medium text-blue-800">Leadership Green AI</div>
              <div className="text-blue-700 mt-1">
                Phoenix est le premier générateur de lettres de motivation certifié Green AI en
                France. Nos optimisations permettent une réduction significative de l'empreinte
                carbone tout en maintenant une qualité de génération supérieure.
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
