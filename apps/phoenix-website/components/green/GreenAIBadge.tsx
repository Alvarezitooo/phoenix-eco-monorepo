/**
 * 🌱 Phoenix Green AI Badge Component
 *
 * Badge dynamique affichant les métriques Green AI en temps réel.
 * Conçu pour être intégré dans le header ou en élément flottant.
 *
 * Author: Claude Phoenix DevSecOps Guardian
 * Version: 1.0.0 - Phoenix Green AI Initiative
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Leaf, Award, TrendingDown } from 'lucide-react';

interface GreenMetrics {
  co2_saved_vs_competitors: string;
  green_ai_grade: string;
  efficiency_score: number;
  certification_status: string;
  calculated: {
    marketing_headlines: {
      primary: string;
      secondary: string;
    };
  };
}

interface GreenAIBadgeProps {
  variant?: 'compact' | 'full' | 'floating';
  showDetails?: boolean;
  className?: string;
}

export default function GreenAIBadge({
  variant = 'compact',
  showDetails = false,
  className = '',
}: GreenAIBadgeProps) {
  const [metrics, setMetrics] = useState<GreenMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showTooltip, setShowTooltip] = useState(false);

  // Désactivation temporaire des métriques fantaisistes
  useEffect(() => {
    // Simulation de données honnetes en attendant la vraie implémentation
    setMetrics({
      co2_saved_vs_competitors: 'En développement',
      green_ai_grade: 'Projet',
      efficiency_score: 0,
      certification_status: 'Objectif 2025',
      calculated: {
        marketing_headlines: {
          primary: 'Démarche écologique en construction',
          secondary: 'Objectifs environnementaux 2025',
        },
      },
    });
    setIsLoading(false);
  }, []);

  // Affichage loading
  if (isLoading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 bg-green-200 rounded-full"></div>
          <div className="w-20 h-4 bg-green-200 rounded"></div>
        </div>
      </div>
    );
  }

  // Pas de données disponibles
  if (!metrics) {
    return null;
  }

  // Badge compact (header)
  if (variant === 'compact') {
    return (
      <div
        className={`inline-flex items-center space-x-2 bg-gradient-to-r from-green-50 to-emerald-50 
                   border border-green-200 rounded-full px-3 py-1.5 text-sm font-medium 
                   text-green-700 hover:from-green-100 hover:to-emerald-100 
                   transition-all duration-200 cursor-pointer ${className}`}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <Leaf className="w-4 h-4 text-green-600" />
        <span className="font-semibold">{metrics.green_ai_grade}</span>
        <span className="text-green-600">Green AI</span>

        {/* Tooltip au hover */}
        {showTooltip && (
          <div
            className="absolute top-full left-0 mt-2 w-64 p-3 bg-white border border-green-200 
                         rounded-lg shadow-lg z-50 text-xs"
          >
            <div className="font-semibold text-green-800 mb-1">🌱 Phoenix Green AI Certifié</div>
            <div className="text-gray-600">{metrics.calculated.marketing_headlines.primary}</div>
            <div className="text-gray-500 mt-1">Efficacité: {metrics.efficiency_score}/100</div>
          </div>
        )}
      </div>
    );
  }

  // Badge complet (sections principales)
  if (variant === 'full') {
    return (
      <div
        className={`bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 
                      border border-green-200 rounded-xl p-4 ${className}`}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-green-100 rounded-lg">
              <Leaf className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-green-800">Phoenix Green AI</h3>
              <p className="text-sm text-blue-600">Certification ISO/IEC 42001 en cours</p>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            <Award className="w-4 h-4 text-yellow-500" />
            <span className="font-bold text-lg text-green-700">{metrics.green_ai_grade}</span>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Réduction CO2</span>
            <span className="font-semibold text-green-700 flex items-center">
              <TrendingDown className="w-4 h-4 mr-1" />
              {metrics.co2_saved_vs_competitors}
            </span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Score Efficacité</span>
            <span className="font-semibold text-green-700">{metrics.efficiency_score}/100</span>
          </div>
        </div>

        {showDetails && (
          <div className="mt-3 pt-3 border-t border-green-200">
            <p className="text-xs text-gray-600">
              {metrics.calculated.marketing_headlines.primary}
            </p>
          </div>
        )}
      </div>
    );
  }

  // Badge flottant (position fixe)
  if (variant === 'floating') {
    return (
      <div className={`fixed bottom-6 right-6 z-50 ${className}`}>
        <div
          className="bg-white border-2 border-green-300 rounded-full p-3 shadow-lg 
                       hover:shadow-xl transition-all duration-300 cursor-pointer group"
        >
          <div className="flex items-center space-x-2">
            <div className="p-1 bg-green-100 rounded-full group-hover:bg-green-200 transition-colors">
              <Leaf className="w-5 h-5 text-green-600" />
            </div>

            <div className="text-sm">
              <div className="font-bold text-green-700">{metrics.green_ai_grade}</div>
              <div className="text-xs text-green-600">Green AI</div>
            </div>
          </div>

          {/* Tooltip au hover pour version flottante */}
          <div
            className="absolute bottom-full right-0 mb-2 w-48 p-3 bg-white border border-green-200 
                         rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200"
          >
            <div className="font-semibold text-green-800 text-sm mb-1">🌱 Phoenix Green AI</div>
            <div className="text-xs text-gray-600 mb-2">
              {metrics.co2_saved_vs_competitors} moins de CO2 que les concurrents
            </div>
            <div className="text-xs text-gray-500">Efficacité: {metrics.efficiency_score}/100</div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

// Hook personnalisé pour récupérer les métriques
export function useGreenAIMetrics() {
  const [metrics, setMetrics] = useState<GreenMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('/api/green-metrics/public');
        const result = await response.json();

        if (result.success) {
          setMetrics(result.data);
          setError(null);
        } else {
          setError(result.error?.message || 'Erreur inconnue');
        }
      } catch (err) {
        setError('Impossible de charger les métriques Green AI');
        console.error('🌱 Erreur métriques:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMetrics();

    // Mise à jour toutes les 5 minutes
    const interval = setInterval(fetchMetrics, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return { metrics, isLoading, error };
}
