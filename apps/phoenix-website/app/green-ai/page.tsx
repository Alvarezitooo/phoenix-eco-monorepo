/**
 * 🌱 Phoenix Green AI - Page dédiée
 *
 * Page complète présentant l'initiative Green AI de Phoenix,
 * les métriques environnementales et la transparence carbone.
 *
 * Author: Claude Phoenix DevSecOps Guardian
 * Version: 1.0.0 - Phoenix Green AI Initiative
 */

import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import {
  Leaf,
  Award,
  TrendingDown,
  BarChart3,
  Shield,
  ExternalLink,
  ArrowRight,
  Users,
  Zap,
  TreePine,
} from 'lucide-react';

// Composants Green AI
import GreenAIBadge from '@/components/green/GreenAIBadge';
import GreenMetricsCard from '@/components/green/GreenMetricsCard';
import CarbonCalculator from '@/components/green/CarbonCalculator';

export const metadata: Metadata = {
  title: 'Phoenix Green AI - Notre engagement écologique',
  description:
    "Phoenix Letters s'engage pour une IA responsable. Découvrez notre démarche éco-responsable et nos initiatives pour réduire l'empreinte carbone.",
  keywords:
    'Green AI, IA responsable, reconversion professionnelle, empreinte carbone, développement durable, Phoenix Letters',
  openGraph: {
    title: 'Phoenix Green AI - IA responsable pour votre reconversion',
    description: 'Notre engagement pour une IA éco-responsable au service des reconversions.',
    type: 'website',
    images: [
      {
        url: '/openart-image_594S3XHV_1753199070084_raw.jpg',
        width: 1200,
        height: 630,
        alt: 'Phoenix Green AI - IA écologique',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Phoenix Green AI - IA responsable',
    description: 'Notre engagement pour une IA éco-responsable au service des reconversions.',
  },
};

export default function GreenAIPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      {/* Hero Section Green AI */}
      <section className="relative pt-20 pb-16 px-4 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            {/* Badge Hero */}
            <div
              className="inline-flex items-center space-x-2 bg-white/80 border border-green-300 
                           rounded-full px-4 py-2 mb-6 backdrop-blur-sm"
            >
              <Leaf className="w-5 h-5 text-green-600" />
              <span className="font-semibold text-green-800">IA Responsable</span>
              <span className="text-green-600">•</span>
              <span className="text-blue-700">Développement durable</span>
            </div>

            {/* Titre principal */}
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Phoenix{' '}
              <span className="bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                Green AI
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
              Notre engagement pour une intelligence artificielle responsable au service de votre
              reconversion professionnelle.
              <strong className="text-green-700">Démarche éco-responsable</strong> en développement
              continu.
            </p>

            {/* CTA principal */}
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4 mb-12">
              <Link
                href="https://phoenix-cv.streamlit.app"
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-green-600 to-emerald-600 
                         text-white px-8 py-4 rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 
                         transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                <Leaf className="w-5 h-5" />
                <span>Essayer Phoenix CV</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              <button
                className="inline-flex items-center space-x-2 text-green-700 hover:text-green-800 
                               font-medium transition-colors"
              >
                <BarChart3 className="w-4 h-4" />
                <span>Voir les métriques live</span>
              </button>
            </div>

            {/* Badge de métriques hero */}
            <GreenAIBadge variant="full" showDetails={true} className="max-w-md mx-auto" />
          </div>
        </div>

        {/* Décoration arrière-plan */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-200/30 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-emerald-200/30 rounded-full blur-3xl"></div>
        </div>
      </section>

      {/* Section Métriques Principales */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Notre Démarche Éco-Responsable
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Nous travaillons activement à réduire notre empreinte environnementale. Découvrez nos
              initiatives et nos objectifs pour une IA plus responsable.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {/* Initiatives écologiques */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-xl mx-auto mb-4 flex items-center justify-center">
                <Leaf className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Optimisation Continue</h3>
              <p className="text-gray-600">
                Amélioration constante de nos algorithmes pour réduire la consommation énergétique.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6 text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-xl mx-auto mb-4 flex items-center justify-center">
                <BarChart3 className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Mesure d'Impact</h3>
              <p className="text-gray-600">
                Mise en place d'outils de mesure pour suivre et améliorer notre empreinte carbone.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6 text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-xl mx-auto mb-4 flex items-center justify-center">
                <Users className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Sensibilisation</h3>
              <p className="text-gray-600">
                Éducation de nos utilisateurs aux bonnes pratiques numériques responsables.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Section Objectifs */}
      <section className="py-16 px-4 bg-white/50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Nos Objectifs Écologiques 2025
            </h2>
            <p className="text-lg text-gray-600">
              Découvrez nos engagements concrets pour une IA plus responsable et notre roadmap
              environnementale.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">Court Terme (6 mois)</h3>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-start space-x-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full mt-2"></span>
                  <span>Audit complet de notre infrastructure</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full mt-2"></span>
                  <span>Optimisation des requêtes IA</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full mt-2"></span>
                  <span>Mise en place d'outils de mesure</span>
                </li>
              </ul>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">Long Terme (12 mois)</h3>
              <ul className="space-y-3 text-gray-600">
                <li className="flex items-start space-x-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mt-2"></span>
                  <span>Réduction mesurable de l'empreinte carbone</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mt-2"></span>
                  <span>Certification environnementale</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mt-2"></span>
                  <span>Transparence totale des métriques</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Section Engagement */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Notre Engagement & Transparence
            </h2>
            <p className="text-lg text-gray-600">
              Nous nous engageons à développer une IA responsable et transparente. Découvrez nos
              valeurs et notre approche éthique.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Transparence */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 text-center hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 bg-blue-100 rounded-xl mx-auto mb-4 flex items-center justify-center">
                <Shield className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Transparence Totale</h3>
              <p className="text-gray-600 mb-4">
                Code open source, métriques publiques et communication transparente sur nos
                pratiques et notre impact.
              </p>
              <div className="inline-flex items-center text-blue-600 hover:text-blue-700 transition-colors">
                <span className="text-sm font-medium">Voir le code</span>
                <ExternalLink className="w-4 h-4 ml-1" />
              </div>
            </div>

            {/* Éthique */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 text-center hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 bg-green-100 rounded-xl mx-auto mb-4 flex items-center justify-center">
                <TreePine className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Éthique & Responsabilité</h3>
              <p className="text-gray-600 mb-4">
                Développement guidé par l'éthique, respect de la vie privée et engagement pour un
                impact positif.
              </p>
              <div className="inline-flex items-center text-green-600 hover:text-green-700 transition-colors">
                <span className="text-sm font-medium">Notre charte</span>
                <ExternalLink className="w-4 h-4 ml-1" />
              </div>
            </div>

            {/* Amélioration Continue */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 text-center hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 bg-yellow-100 rounded-xl mx-auto mb-4 flex items-center justify-center">
                <Award className="w-8 h-8 text-yellow-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Amélioration Continue</h3>
              <p className="text-gray-600 mb-4">
                Écoute des utilisateurs, recherche active et adaptation constante pour améliorer
                notre impact environnemental.
              </p>
              <div className="inline-flex items-center text-yellow-600 hover:text-yellow-700 transition-colors">
                <span className="text-sm font-medium">Nous contacter</span>
                <ExternalLink className="w-4 h-4 ml-1" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section Innovation Green AI */}
      <section className="py-16 px-4 bg-gradient-to-r from-green-900 to-emerald-800 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                L'Innovation Green AI en Action
              </h2>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-green-500/20 rounded-lg">
                    <Zap className="w-6 h-6 text-green-300" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Cache Intelligent</h3>
                    <p className="text-green-100">
                      Notre système de cache avancé évite les requêtes inutiles, réduisant
                      l'empreinte carbone de 85% sur les contenus similaires.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-green-500/20 rounded-lg">
                    <TrendingDown className="w-6 h-6 text-green-300" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Optimisation Continue</h3>
                    <p className="text-green-100">
                      Algorithmes d'apprentissage qui optimisent automatiquement la consommation
                      énergétique sans compromis sur la qualité.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-green-500/20 rounded-lg">
                    <Users className="w-6 h-6 text-green-300" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Impact Collectif</h3>
                    <p className="text-green-100">
                      Chaque reconversion réussie contribue à un avenir plus inclusif. Ensemble,
                      nous bâtissons une communauté responsable.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative">
              {/* Graphique ou visualisation (placeholder) */}
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-8 border border-white/20">
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-green-300 mb-2">
                    Réduction CO2 en Temps Réel
                  </h3>
                  <p className="text-green-100 text-sm">Depuis le lancement Green AI</p>
                </div>

                {/* Nos engagements */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white mb-1">100%</div>
                    <div className="text-green-200 text-sm">open source</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white mb-1">0€</div>
                    <div className="text-green-200 text-sm">pour commencer</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white mb-1">24/7</div>
                    <div className="text-green-200 text-sm">disponible</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white mb-1">∞</div>
                    <div className="text-green-200 text-sm">améliorations</div>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-green-500/20 rounded-lg border border-green-400/30">
                  <p className="text-green-100 text-sm text-center">
                    🌱 Objectif 2025: <strong>Mesurer et réduire</strong> notre empreinte carbone
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Rejoignez la Révolution Green AI
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Transformez votre reconversion professionnelle avec une IA responsable. Même qualité,
            impact environnemental minimal.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Link
              href="https://phoenix-cv.streamlit.app"
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-green-600 to-emerald-600 
                       text-white px-8 py-4 rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 
                       transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <Leaf className="w-5 h-5" />
              <span>Commencer Gratuitement</span>
            </Link>

            <Link
              href="/about"
              className="inline-flex items-center space-x-2 text-gray-700 hover:text-gray-900 
                       font-medium transition-colors"
            >
              <span>En savoir plus sur Phoenix</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="mt-8 flex items-center justify-center space-x-8 text-sm text-gray-500">
            <div className="flex items-center space-x-1">
              <Shield className="w-4 h-4" />
              <span>Développement éthique</span>
            </div>
            <div className="flex items-center space-x-1">
              <TrendingDown className="w-4 h-4" />
              <span>Amélioration continue</span>
            </div>
            <div className="flex items-center space-x-1">
              <Users className="w-4 h-4" />
              <span>Créé par un reconverti</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
