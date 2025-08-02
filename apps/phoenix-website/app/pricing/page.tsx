import React from 'react';
import IndividualAppPricing from '@/components/sections/IndividualAppPricing';
import BundlePricing from '@/components/sections/BundlePricing';
import CompetitiveComparison from '@/components/sections/CompetitiveComparison';

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white py-16">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            Une tarification juste et transparente,
            <span className="text-purple-700"> pour tous les besoins</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Phoenix vous propose des outils puissants et accessibles pour votre reconversion.
          </p>
        </div>

        <IndividualAppPricing />
        <BundlePricing />
        <CompetitiveComparison />

        <div className="text-center mt-16">
          <p className="text-lg text-gray-700">
            <strong className="text-purple-700">Avantages Pricing :</strong>
          </p>
          <ul className="list-disc list-inside text-gray-600 mt-4 inline-block text-left">
            <li>
              🎯 <strong className="text-purple-700">7,99€ = prix psychologique parfait</strong>{' '}
              (sous 10€)
            </li>
            <li>
              📈 <strong className="text-purple-700">Montée en gamme naturelle</strong> (1 app →
              bundle)
            </li>
            <li>
              💪 <strong className="text-purple-700">66% moins cher que Zety</strong> (7,99€ vs
              23,70€)
            </li>
            <li>
              🚀{' '}
              <strong className="text-purple-700">Accessible étudiants/demandeurs d'emploi</strong>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
