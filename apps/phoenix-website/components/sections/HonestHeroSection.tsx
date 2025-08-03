import React from 'react';

const HonestHeroSection: React.FC = () => {
  return (
    <div className="hero-honest bg-gradient-to-r from-purple-600 to-indigo-700 text-white py-20 px-4 text-center">
      <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
        🔥 Phoenix : Votre Reconversion Propulsée par l'IA. Des Outils Nés de l'Expérience.
      </h1>
      <p className="text-lg md:text-xl mb-8 max-w-3xl mx-auto">
        Votre transition. <strong className="font-extrabold">Vous êtes les premiers !</strong>
      </p>

      <div className="early-adopter-cta mt-8">
        <a
          href="https://phoenixcreator.netlify.app/"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary bg-white text-purple-700 hover:bg-gray-100 font-bold py-3 px-8 rounded-full text-lg transition duration-300 ease-in-out shadow-lg"
        >
          🚀 Commencer Gratuitement
        </a>
        <small className="block mt-2 text-sm opacity-80">
          Testez, donnez votre avis, façonnez Phoenix avec nous
        </small>
      </div>
    </div>
  );
};

export default HonestHeroSection;
