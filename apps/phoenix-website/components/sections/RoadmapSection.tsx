import React from 'react';

const RoadmapSection: React.FC = () => {
  return (
    <section className="roadmap py-16 px-4 bg-gray-100">
      <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-gray-800">
        🗓️ La Roadmap Phoenix (Transparence Totale)
      </h2>
      <div className="timeline max-w-4xl mx-auto relative">
        <div className="milestone completed relative mb-12 pl-16 border-l-4 border-green-500">
          <div className="absolute -left-2 top-0 w-4 h-4 bg-green-500 rounded-full"></div>
          <h3 className="text-xl font-semibold mb-2 text-gray-800">✅ Phoenix Letters v1</h3>
          <p className="text-gray-600">Génération lettres reconversion - DISPONIBLE</p>
        </div>
        <div className="milestone current relative mb-12 pl-16 border-l-4 border-blue-500">
          <div className="absolute -left-2 top-0 w-4 h-4 bg-blue-500 rounded-full"></div>
          <h3 className="text-xl font-semibold mb-2 text-gray-800">🔄 Phoenix CV</h3>
          <p className="text-gray-600">Mi-août - Disponible</p>
        </div>
        <div className="milestone future relative mb-12 pl-16 border-l-4 border-gray-400">
          <div className="absolute -left-2 top-0 w-4 h-4 bg-gray-400 rounded-full"></div>
          <h3 className="text-xl font-semibold mb-2 text-gray-800">⏳ Phoenix Rise</h3>
          <p className="text-gray-600">Mi-septembre - Disponible</p>
        </div>
        <div className="milestone future relative pl-16 border-l-4 border-gray-400">
          <div className="absolute -left-2 top-0 w-4 h-4 bg-gray-400 rounded-full"></div>
          <h3 className="text-xl font-semibold mb-2 text-gray-800">🚀 Phoenix Pro</h3>
          <p className="text-gray-600">Date à venir</p>
        </div>
      </div>
    </section>
  );
};

export default RoadmapSection;
