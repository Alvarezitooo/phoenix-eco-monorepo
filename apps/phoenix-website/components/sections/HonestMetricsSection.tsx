import React from 'react';

const HonestMetricsSection: React.FC = () => {
  return (
    <section className="honest-metrics py-16 px-4 bg-white">
      <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-gray-800">
        🚀 Phoenix Démarre - Soyez les Premiers !
      </h2>
      <div className="honest-stats grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
        <div className="stat-card bg-purple-100 p-6 rounded-lg shadow-md text-center">
          <div className="stat-number text-5xl font-bold text-purple-700">1</div>
          <div className="stat-label text-lg font-semibold text-gray-700">Reconversion Prouvée</div>
          <small className="text-gray-500">(Matthieu : Aide-soignant → Tech)</small>
        </div>
        <div className="stat-card bg-purple-100 p-6 rounded-lg shadow-md text-center">
          <div className="stat-number text-5xl font-bold text-purple-700">3</div>
          <div className="stat-label text-lg font-semibold text-gray-700">
            Apps en Développement
          </div>
          <small className="text-gray-500">Letters, CV, Rise</small>
        </div>
        <div className="stat-card bg-purple-100 p-6 rounded-lg shadow-md text-center">
          <div className="stat-number text-5xl font-bold text-purple-700">100%</div>
          <div className="stat-label text-lg font-semibold text-gray-700">
            Gratuit pour Commencer
          </div>
          <small className="text-gray-500">Testez sans risque</small>
        </div>
        <div className="stat-card bg-purple-100 p-6 rounded-lg shadow-md text-center">
          <div className="stat-number text-5xl font-bold text-purple-700">∞</div>
          <div className="stat-label text-lg font-semibold text-gray-700">
            Potentiel de Votre Reconversion
          </div>
          <small className="text-gray-500">C'est parti !</small>
        </div>
      </div>
      <p className="text-center text-xl font-semibold mt-12 text-gray-800">
        <strong className="text-purple-700">🎯 Objectif 2025 :</strong> Aider 1000 personnes à
        réussir leur reconversion
      </p>
    </section>
  );
};

export default HonestMetricsSection;
