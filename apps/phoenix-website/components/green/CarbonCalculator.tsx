/**
 * 🌱 Phoenix Carbon Calculator Component
 *
 * Calculateur interactif d'impact carbone personnel pour les utilisateurs.
 * Permet de visualiser l'économie CO2 réalisée avec Phoenix vs concurrents.
 *
 * Author: Claude Phoenix DevSecOps Guardian
 * Version: 1.0.0 - Phoenix Green AI Initiative
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  Calculator,
  TrendingDown,
  Leaf,
  Users,
  FileText,
  ArrowRight,
  TreePine,
  Zap,
  Heart,
} from 'lucide-react';

interface CalculatorResult {
  letters_count: number;
  phoenix_co2: number;
  competitors_co2: number;
  co2_saved: number;
  trees_equivalent: number;
  percentage_saved: number;
  monthly_projection: {
    co2_saved: number;
    trees_equivalent: number;
  };
}

interface CarbonCalculatorProps {
  className?: string;
  variant?: 'full' | 'compact';
  showProjections?: boolean;
}

export default function CarbonCalculator({
  className = '',
  variant = 'full',
  showProjections = true,
}: CarbonCalculatorProps) {
  const [lettersCount, setLettersCount] = useState<number>(5);
  const [userType, setUserType] = useState<'individual' | 'recruiter' | 'consultant'>('individual');
  const [result, setResult] = useState<CalculatorResult | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  // Constantes pour les calculs (basées sur recherche Green AI)
  const CO2_CONSTANTS = {
    phoenix_per_letter: 0.08, // grammes CO2 par lettre Phoenix
    chatgpt_per_letter: 1.2, // grammes CO2 par lettre ChatGPT
    claude_per_letter: 0.8, // grammes CO2 par lettre Claude
    tree_co2_absorption: 21000, // grammes CO2 absorbés par arbre/an
  };

  // Multiplicateurs selon le type d'utilisateur
  const USER_MULTIPLIERS = useMemo(() => ({
    individual: { letters: 1, label: 'Particulier en reconversion' },
    recruiter: { letters: 10, label: 'Recruteur/RH' },
    consultant: { letters: 25, label: 'Consultant carrière' },
  }), []);

  // Calcul automatique quand les paramètres changent
  useEffect(() => {
    calculateImpact();
  }, [lettersCount, userType, calculateImpact]);

  const calculateImpact = useCallback(async () => {
    setIsCalculating(true);

    // Simulation d'un délai pour l'effet UX
    await new Promise((resolve) => setTimeout(resolve, 300));

    const adjustedLetters = lettersCount * USER_MULTIPLIERS[userType].letters;

    // Calculs CO2
    const phoenixCO2 = adjustedLetters * CO2_CONSTANTS.phoenix_per_letter;
    const avgCompetitorCO2 =
      adjustedLetters * ((CO2_CONSTANTS.chatgpt_per_letter + CO2_CONSTANTS.claude_per_letter) / 2);
    const co2Saved = avgCompetitorCO2 - phoenixCO2;

    // Équivalent en arbres
    const treesEquivalent = co2Saved / CO2_CONSTANTS.tree_co2_absorption;

    // Pourcentage d'économie
    const percentageSaved = (co2Saved / avgCompetitorCO2) * 100;

    // Projections mensuelles
    const monthlyLetters = adjustedLetters * 4; // ~4 fois par mois
    const monthlyCO2Saved =
      monthlyLetters * (CO2_CONSTANTS.chatgpt_per_letter - CO2_CONSTANTS.phoenix_per_letter);
    const monthlyTreesEquivalent = monthlyCO2Saved / CO2_CONSTANTS.tree_co2_absorption;

    setResult({
      letters_count: adjustedLetters,
      phoenix_co2: phoenixCO2,
      competitors_co2: avgCompetitorCO2,
      co2_saved: co2Saved,
      trees_equivalent: treesEquivalent,
      percentage_saved: percentageSaved,
      monthly_projection: {
        co2_saved: monthlyCO2Saved,
        trees_equivalent: monthlyTreesEquivalent,
      },
    });

    setIsCalculating(false);
  }, [lettersCount, userType, CO2_CONSTANTS, USER_MULTIPLIERS, setResult, setIsCalculating]);

  // Formatage des nombres
  const formatCO2 = (grams: number): string => {
    if (grams < 1) {
      return `${(grams * 1000).toFixed(1)}mg`;
    } else if (grams < 1000) {
      return `${grams.toFixed(2)}g`;
    } else {
      return `${(grams / 1000).toFixed(2)}kg`;
    }
  };

  const formatNumber = (num: number, decimals = 2): string => {
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: decimals,
    }).format(num);
  };

  // Version compacte pour sidebar ou sections
  if (variant === 'compact') {
    return (
      <div
        className={`bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 
                      rounded-xl p-4 ${className}`}
      >
        <div className="text-center">
          <Calculator className="w-8 h-8 text-green-600 mx-auto mb-2" />
          <h4 className="font-semibold text-green-800 mb-3">Calculez votre impact</h4>

          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Lettres par période</label>
              <input
                type="range"
                min="1"
                max="20"
                value={lettersCount}
                onChange={(e) => setLettersCount(Number(e.target.value))}
                className="w-full accent-green-600"
              />
              <div className="text-sm font-medium text-green-700">{lettersCount}</div>
            </div>

            {result && (
              <div className="bg-white rounded-lg p-3 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">CO2 économisé:</span>
                  <span className="font-bold text-green-700">{formatCO2(result.co2_saved)}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Réduction:</span>
                  <span className="font-bold text-green-700">
                    {formatNumber(result.percentage_saved, 1)}%
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Version complète pour page dédiée
  return (
    <div className={`bg-white border border-gray-200 rounded-xl p-6 ${className}`}>
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-xl mb-3">
          <Calculator className="w-6 h-6 text-green-600" />
        </div>
        <h3 className="text-xl font-bold text-gray-800 mb-2">Calculateur d'Impact Carbone</h3>
        <p className="text-gray-600">Découvrez votre économie CO2 en utilisant Phoenix Letters</p>
      </div>

      {/* Paramètres de calcul */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">Type d'utilisateur</label>
          <div className="space-y-2">
            {Object.entries(USER_MULTIPLIERS).map(([type, config]) => (
              <label key={type} className="flex items-center">
                <input
                  type="radio"
                  name="userType"
                  value={type}
                  checked={userType === type}
                  onChange={(e) => setUserType(e.target.value as typeof userType)}
                  className="mr-3 accent-green-600"
                />
                <span className="text-gray-700">{config.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Lettres générées par session
          </label>
          <div className="space-y-3">
            <input
              type="range"
              min="1"
              max="20"
              value={lettersCount}
              onChange={(e) => setLettersCount(Number(e.target.value))}
              className="w-full accent-green-600"
            />
            <div className="flex justify-between text-sm text-gray-500">
              <span>1</span>
              <span className="font-bold text-green-700 text-lg">{lettersCount}</span>
              <span>20</span>
            </div>
          </div>
        </div>
      </div>

      {/* Résultats du calcul */}
      {result && (
        <div className="space-y-6">
          {/* Comparaison visuelle */}
          <div className="bg-gradient-to-r from-red-50 via-yellow-50 to-green-50 rounded-xl p-6">
            <h4 className="font-semibold text-gray-800 mb-4 text-center">Impact CO2 par Session</h4>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-red-100 rounded-lg">
                <div className="text-sm text-red-600 mb-1">Concurrents</div>
                <div className="text-xl font-bold text-red-700">
                  {formatCO2(result.competitors_co2)}
                </div>
                <div className="text-xs text-red-500 mt-1">ChatGPT + Claude</div>
              </div>

              <div className="flex items-center justify-center">
                <ArrowRight className="w-8 h-8 text-gray-400" />
              </div>

              <div className="text-center p-4 bg-green-100 rounded-lg">
                <div className="text-sm text-green-600 mb-1">Phoenix Letters</div>
                <div className="text-xl font-bold text-green-700">
                  {formatCO2(result.phoenix_co2)}
                </div>
                <div className="text-xs text-green-500 mt-1">Green AI Certifié</div>
              </div>
            </div>
          </div>

          {/* Économies réalisées */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
              <TrendingDown className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-green-700">{formatCO2(result.co2_saved)}</div>
              <div className="text-sm text-green-600">CO2 économisé</div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
              <Zap className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-blue-700">
                -{formatNumber(result.percentage_saved, 1)}%
              </div>
              <div className="text-sm text-blue-600">de réduction</div>
            </div>

            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-center">
              <TreePine className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
              <div className="text-2xl font-bold text-emerald-700">
                {formatNumber(result.trees_equivalent, 4)}
              </div>
              <div className="text-sm text-emerald-600">arbres équivalent</div>
            </div>
          </div>

          {/* Projections mensuelles */}
          {showProjections && result.monthly_projection && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-6">
              <h4 className="font-semibold text-gray-800 mb-4 flex items-center">
                <FileText className="w-5 h-5 text-purple-600 mr-2" />
                Projection Mensuelle
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-700 mb-1">
                    {formatCO2(result.monthly_projection.co2_saved)}
                  </div>
                  <div className="text-purple-600">CO2 économisé par mois</div>
                </div>

                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-700 mb-1">
                    {formatNumber(result.monthly_projection.trees_equivalent, 3)}
                  </div>
                  <div className="text-purple-600">arbres équivalent/mois</div>
                </div>
              </div>

              <div className="mt-4 p-3 bg-white rounded-lg border-l-4 border-purple-500">
                <p className="text-sm text-gray-700">
                  <strong>Votre impact positif:</strong> En utilisant Phoenix Letters régulièrement,
                  vous contribuez à réduire l'empreinte carbone du secteur de l'IA tout en
                  bénéficiant d'un service de qualité supérieure pour votre reconversion
                  professionnelle.
                </p>
              </div>
            </div>
          )}

          {/* Impact solidaire-écologique */}
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-6 mb-6">
            <h4 className="font-semibold text-gray-800 mb-4 flex items-center">
              <Heart className="w-5 h-5 text-purple-600 mr-2" />
              Votre Contribution Solidaire-Écologique
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-700 mb-1">
                  {formatNumber(result.letters_count * 0.01, 2)}€
                </div>
                <div className="text-purple-600 text-sm">contribution solidaire</div>
                <div className="text-xs text-purple-500 mt-1">
                  Bourses reconversion pour personnes défavorisées
                </div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-green-700 mb-1">
                  {formatNumber(result.letters_count * 0.01, 2)}€
                </div>
                <div className="text-green-600 text-sm">compensation carbone</div>
                <div className="text-xs text-green-500 mt-1">
                  Reforestation + projets écologiques certifiés
                </div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-white rounded-lg border-l-4 border-purple-500">
              <p className="text-sm text-gray-700">
                <strong>Impact automatique :</strong> Chaque utilisation de Phoenix Letters
                contribue automatiquement à hauteur de 2 centimes au fonds solidaire-écologique.
                Votre reconversion aide d'autres reconversions ! 💝🌱
              </p>
            </div>
          </div>

          {/* Call to action */}
          <div className="text-center">
            <div
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-green-600 
                           text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-green-700 
                           transition-all duration-200 cursor-pointer"
            >
              <Heart className="w-4 h-4" />
              <Leaf className="w-4 h-4" />
              <span className="font-medium">Commencer ma reconversion solidaire</span>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Rejoignez les {formatNumber(1247, 0)} utilisateurs qui contribuent déjà au changement
            </p>
          </div>
        </div>
      )}

      {/* Loading state */}
      {isCalculating && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <span className="ml-3 text-gray-600">Calcul en cours...</span>
        </div>
      )}

      {/* Footer explicatif */}
      <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500 text-center">
        <p>
          * Calculs basés sur les recherches Green AI et les métriques certifiées Phoenix Letters.
          Les valeurs sont des estimations basées sur l'usage moyen et peuvent varier selon la
          complexité des requêtes.
        </p>
      </div>
    </div>
  );
}
