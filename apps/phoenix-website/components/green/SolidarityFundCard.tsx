/**
 * 💝🌱 Phoenix Solidarity-Ecological Fund Card Component
 *
 * Carte affichant l'impact du fonds solidaire-écologique en temps réel.
 * Combine transparence sociale et environnementale.
 *
 * Author: Claude Phoenix DevSecOps Guardian
 * Version: 1.0.0 - Phoenix Solidarity-Green Initiative
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  Heart,
  TreePine,
  Users,
  TrendingUp,
  Euro,
  Award,
  ExternalLink,
  RefreshCw,
  Calendar,
} from 'lucide-react';

interface SolidarityFundMetrics {
  total_contributions: number;
  total_solidarity_collected: number;
  total_ecological_collected: number;
  available_solidarity_funds: number;
  available_ecological_funds: number;

  solidarity_impact: {
    total_letters_sponsored: number;
    total_coaching_hours: number;
    unique_beneficiaries_estimated: number;
    actions_count: number;
  };

  ecological_impact: {
    total_co2_offset_tons: number;
    total_trees_planted: number;
    actions_count: number;
    partner_organizations: number;
  };

  efficiency_metrics: {
    admin_percentage: number;
    deployment_rate_solidarity: number;
    deployment_rate_ecological: number;
  };

  last_updated: string;
}

interface SolidarityFundCardProps {
  variant?: 'overview' | 'detailed' | 'compact';
  showTransparency?: boolean;
  className?: string;
}

export default function SolidarityFundCard({
  variant = 'overview',
  showTransparency = true,
  className = '',
}: SolidarityFundCardProps) {
  const [metrics, setMetrics] = useState<SolidarityFundMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Récupération des métriques du fonds
  const fetchMetrics = async (force = false) => {
    try {
      if (force) setIsRefreshing(true);

      // TODO: Remplacer par vraie API call vers Phoenix Letters
      // const response = await fetch('/api/solidarity-fund/metrics');

      // Simulation de données réalistes pour la démo
      const simulatedMetrics: SolidarityFundMetrics = {
        total_contributions: 24.36,
        total_solidarity_collected: 12.18,
        total_ecological_collected: 10.98,
        available_solidarity_funds: 8.45,
        available_ecological_funds: 7.22,

        solidarity_impact: {
          total_letters_sponsored: 78,
          total_coaching_hours: 12,
          unique_beneficiaries_estimated: 23,
          actions_count: 15,
        },

        ecological_impact: {
          total_co2_offset_tons: 0.34,
          total_trees_planted: 8,
          actions_count: 3,
          partner_organizations: 2,
        },

        efficiency_metrics: {
          admin_percentage: 5.0,
          deployment_rate_solidarity: 69.4,
          deployment_rate_ecological: 65.8,
        },

        last_updated: new Date().toISOString(),
      };

      setMetrics(simulatedMetrics);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('💝🌱 Erreur chargement métriques fonds:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchMetrics();

    // Auto-refresh toutes les 15 minutes
    const interval = setInterval(() => fetchMetrics(), 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Formatage des nombres
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatNumber = (num: number, decimals = 0): string => {
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  };

  // Formatage de la date
  const formatLastUpdate = (date: Date): string => {
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffMinutes < 1) return "À l'instant";
    if (diffMinutes < 60) return `il y a ${diffMinutes}min`;

    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `il y a ${diffHours}h`;

    return date.toLocaleDateString('fr-FR');
  };

  // Loading state
  if (isLoading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-purple-200 rounded-lg"></div>
              <div className="w-40 h-6 bg-purple-200 rounded"></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="w-full h-20 bg-purple-200 rounded-lg"></div>
              <div className="w-full h-20 bg-purple-200 rounded-lg"></div>
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
          <div className="text-red-600 font-medium">Métriques du fonds indisponibles</div>
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

  // Version compacte
  if (variant === 'compact') {
    return (
      <div
        className={`bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-4 ${className}`}
      >
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-3">
            <Heart className="w-5 h-5 text-purple-600" />
            <TreePine className="w-5 h-5 text-green-600" />
          </div>
          <h4 className="font-semibold text-purple-800 mb-2">Fonds Solidaire-Écologique</h4>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-white/60 rounded-lg p-2">
              <div className="font-bold text-purple-700">
                {metrics.solidarity_impact.unique_beneficiaries_estimated}
              </div>
              <div className="text-purple-600 text-xs">reconversions aidées</div>
            </div>
            <div className="bg-white/60 rounded-lg p-2">
              <div className="font-bold text-green-700">
                {formatNumber(metrics.ecological_impact.total_co2_offset_tons, 2)}t
              </div>
              <div className="text-green-600 text-xs">CO2 compensé</div>
            </div>
          </div>

          <div className="mt-3 text-xs text-gray-600">
            {formatCurrency(metrics.total_contributions)} collectés
          </div>
        </div>
      </div>
    );
  }

  // Version aperçu (défaut)
  if (variant === 'overview') {
    return (
      <div
        className={`bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50 
                      border border-purple-200 rounded-xl p-6 ${className}`}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <div className="flex items-center space-x-1">
                <Heart className="w-5 h-5 text-purple-600" />
                <TreePine className="w-5 h-5 text-green-600" />
              </div>
            </div>
            <div>
              <h3 className="text-lg font-bold text-purple-800">Phoenix Solidaire-Écologique</h3>
              <p className="text-sm text-purple-600">Chaque utilisation contribue au bien commun</p>
            </div>
          </div>

          <div className="text-right">
            <div className="text-2xl font-bold text-purple-700">
              {formatCurrency(metrics.total_contributions)}
            </div>
            <div className="text-sm text-purple-600">collectés</div>
          </div>
        </div>

        {/* Répartition des fonds */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-white/60 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Users className="w-5 h-5 text-purple-600" />
              <span className="font-semibold text-purple-800">Impact Solidaire</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Reconversions aidées:</span>
                <span className="font-semibold text-purple-700">
                  {metrics.solidarity_impact.unique_beneficiaries_estimated}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Lettres sponsorisées:</span>
                <span className="font-semibold text-purple-700">
                  {metrics.solidarity_impact.total_letters_sponsored}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Fonds disponibles:</span>
                <span className="font-semibold text-purple-700">
                  {formatCurrency(metrics.available_solidarity_funds)}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white/60 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TreePine className="w-5 h-5 text-green-600" />
              <span className="font-semibold text-green-800">Impact Écologique</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">CO2 compensé:</span>
                <span className="font-semibold text-green-700">
                  {formatNumber(metrics.ecological_impact.total_co2_offset_tons, 2)}t
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Arbres plantés:</span>
                <span className="font-semibold text-green-700">
                  {metrics.ecological_impact.total_trees_planted}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Fonds disponibles:</span>
                <span className="font-semibold text-green-700">
                  {formatCurrency(metrics.available_ecological_funds)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Efficacité et transparence */}
        <div className="bg-white/80 rounded-lg p-4 border-l-4 border-purple-500">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-purple-800">Transparence & Efficacité</h4>
            <Award className="w-5 h-5 text-yellow-500" />
          </div>
          <div className="grid grid-cols-3 gap-4 text-center text-sm">
            <div>
              <div className="font-bold text-purple-700">
                {metrics.efficiency_metrics.admin_percentage}%
              </div>
              <div className="text-gray-600">frais admin</div>
            </div>
            <div>
              <div className="font-bold text-purple-700">
                {formatNumber(metrics.efficiency_metrics.deployment_rate_solidarity, 1)}%
              </div>
              <div className="text-gray-600">déployé solidaire</div>
            </div>
            <div>
              <div className="font-bold text-green-700">
                {formatNumber(metrics.efficiency_metrics.deployment_rate_ecological, 1)}%
              </div>
              <div className="text-gray-600">déployé écologique</div>
            </div>
          </div>
        </div>

        {/* Footer avec actions */}
        {showTransparency && (
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-purple-200">
            <div className="flex items-center space-x-4">
              {lastUpdate && (
                <div className="flex items-center space-x-1 text-xs text-gray-500">
                  <Calendar className="w-3 h-3" />
                  <span>Mis à jour {formatLastUpdate(lastUpdate)}</span>
                </div>
              )}

              <button
                onClick={() => fetchMetrics(true)}
                disabled={isRefreshing}
                className="flex items-center space-x-1 text-xs text-purple-600 hover:text-purple-700 
                         disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span>Actualiser</span>
              </button>
            </div>

            <div className="flex items-center space-x-2">
              <button className="flex items-center space-x-1 text-xs text-purple-600 hover:text-purple-700">
                <ExternalLink className="w-3 h-3" />
                <span>Rapport complet</span>
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Version détaillée
  if (variant === 'detailed') {
    return (
      <div className={`space-y-6 ${className}`}>
        {/* Vue d'ensemble avec charts */}
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 text-purple-600 mr-2" />
            Répartition du Fonds
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-700 mb-2">
                {formatCurrency(metrics.total_solidarity_collected)}
              </div>
              <div className="text-purple-600">Fonds Solidaire</div>
              <div className="text-sm text-gray-500 mt-1">
                {metrics.solidarity_impact.actions_count} actions menées
              </div>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-green-700 mb-2">
                {formatCurrency(metrics.total_ecological_collected)}
              </div>
              <div className="text-green-600">Fonds Écologique</div>
              <div className="text-sm text-gray-500 mt-1">
                {metrics.ecological_impact.actions_count} projets financés
              </div>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-gray-700 mb-2">
                {metrics.efficiency_metrics.admin_percentage}%
              </div>
              <div className="text-gray-600">Frais Admin</div>
              <div className="text-sm text-gray-500 mt-1">Maximum 5% par règlement</div>
            </div>
          </div>
        </div>

        {/* Impact détaillé */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Impact solidaire détaillé */}
          <div className="bg-purple-50 border border-purple-200 rounded-xl p-6">
            <h4 className="text-lg font-semibold text-purple-800 mb-4 flex items-center">
              <Users className="w-5 h-5 text-purple-600 mr-2" />
              Impact Solidaire Détaillé
            </h4>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-purple-700">Personnes accompagnées</span>
                <span className="text-2xl font-bold text-purple-800">
                  {metrics.solidarity_impact.unique_beneficiaries_estimated}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-purple-700">Lettres sponsorisées</span>
                <span className="text-xl font-semibold text-purple-800">
                  {metrics.solidarity_impact.total_letters_sponsored}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-purple-700">Heures de coaching</span>
                <span className="text-xl font-semibold text-purple-800">
                  {metrics.solidarity_impact.total_coaching_hours}h
                </span>
              </div>

              <div className="bg-white/60 rounded-lg p-3 mt-4">
                <div className="text-sm text-purple-700 font-medium mb-1">Taux de déploiement</div>
                <div className="w-full bg-purple-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${metrics.efficiency_metrics.deployment_rate_solidarity}%` }}
                  ></div>
                </div>
                <div className="text-xs text-purple-600 mt-1">
                  {formatNumber(metrics.efficiency_metrics.deployment_rate_solidarity, 1)}% des
                  fonds déployés
                </div>
              </div>
            </div>
          </div>

          {/* Impact écologique détaillé */}
          <div className="bg-green-50 border border-green-200 rounded-xl p-6">
            <h4 className="text-lg font-semibold text-green-800 mb-4 flex items-center">
              <TreePine className="w-5 h-5 text-green-600 mr-2" />
              Impact Écologique Détaillé
            </h4>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-green-700">CO2 compensé</span>
                <span className="text-2xl font-bold text-green-800">
                  {formatNumber(metrics.ecological_impact.total_co2_offset_tons, 2)}t
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-green-700">Arbres plantés</span>
                <span className="text-xl font-semibold text-green-800">
                  {metrics.ecological_impact.total_trees_planted}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-green-700">Organisations partenaires</span>
                <span className="text-xl font-semibold text-green-800">
                  {metrics.ecological_impact.partner_organizations}
                </span>
              </div>

              <div className="bg-white/60 rounded-lg p-3 mt-4">
                <div className="text-sm text-green-700 font-medium mb-1">Taux de déploiement</div>
                <div className="w-full bg-green-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${metrics.efficiency_metrics.deployment_rate_ecological}%` }}
                  ></div>
                </div>
                <div className="text-xs text-green-600 mt-1">
                  {formatNumber(metrics.efficiency_metrics.deployment_rate_ecological, 1)}% des
                  fonds déployés
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Actions récentes et gouvernance */}
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">Gouvernance & Transparence</h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h5 className="font-medium text-gray-700 mb-2">Principe de Fonctionnement</h5>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 2 centimes par utilisation Phoenix Letters</li>
                <li>• Répartition automatique 50% solidaire / 45% écologique / 5% admin max</li>
                <li>• Allocation mensuelle par vote communautaire</li>
                <li>• Audit trimestriel par organisme indépendant</li>
              </ul>
            </div>

            <div>
              <h5 className="font-medium text-gray-700 mb-2">Prochaines Actions</h5>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Bourses reconversion pour 5 demandeurs d'emploi</li>
                <li>• Plantation de 25 arbres avec Reforest'Action</li>
                <li>• Partenariat avec une association locale d'insertion</li>
                <li>• Compensation carbone certification Gold Standard</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
