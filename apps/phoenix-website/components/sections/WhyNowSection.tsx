import React from 'react';

const WhyNowSection: React.FC = () => {
  return (
    <section className="why-now py-16 px-4 bg-gray-50">
      <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-gray-800">
        🎯 Pourquoi Choisir Phoenix Maintenant ?
      </h2>
      <div className="reasons-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
        <div className="reason bg-white p-6 rounded-lg shadow-md text-center transform transition duration-300 hover:scale-105 hover:shadow-xl">
          <h3 className="text-xl font-semibold mb-3 text-purple-700">🥇 Vous Êtes les Premiers</h3>
          <p className="text-gray-600">
            Façonnez l'outil avec vos retours. Votre expérience compte.
          </p>
        </div>
        <div className="reason bg-white p-6 rounded-lg shadow-md text-center transform transition duration-300 hover:scale-105 hover:shadow-xl">
          <h3 className="text-xl font-semibold mb-3 text-purple-700">💡 Innovation Pure</h3>
          <p className="text-gray-600">
            Première IA spécialisée reconversion. Vous découvrez avant tout le monde.
          </p>
        </div>
        <div className="reason bg-white p-6 rounded-lg shadow-md text-center transform transition duration-300 hover:scale-105 hover:shadow-xl">
          <h3 className="text-xl font-semibold mb-3 text-purple-700">
            🤝 Communauté Bienveillante
          </h3>
          <p className="text-gray-600">
            Rejoignez des reconvertis comme vous. Entraide et partage d'expérience.
          </p>
        </div>
        <div className="reason bg-white p-6 rounded-lg shadow-md text-center transform transition duration-300 hover:scale-105 hover:shadow-xl">
          <h3 className="text-xl font-semibold mb-3 text-purple-700">💰 Prix Doux</h3>
          <p className="text-gray-600">
            7,99€ vs 23,70€ chez Zety. Accessible à tous les budgets reconversion.
          </p>
        </div>
      </div>
    </section>
  );
};

export default WhyNowSection;
