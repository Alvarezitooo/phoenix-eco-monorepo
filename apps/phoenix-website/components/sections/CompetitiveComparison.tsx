import React from 'react';
import { Check, X } from 'lucide-react';

const CompetitiveComparison: React.FC = () => {
  return (
    <section className="py-16 px-4 bg-white">
      <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-gray-800">
        🆚 Phoenix vs Concurrence : La Transparence Avant Tout
      </h2>
      <div className="max-w-4xl mx-auto overflow-x-auto">
        <table className="w-full table-auto border-collapse">
          <thead>
            <tr className="bg-gray-100 text-gray-700 uppercase text-sm leading-normal">
              <th className="py-3 px-6 text-left">Critère</th>
              <th className="py-3 px-6 text-left">🔥 Phoenix</th>
              <th className="py-3 px-6 text-left">Zety</th>
              <th className="py-3 px-6 text-left">CVcrea</th>
            </tr>
          </thead>
          <tbody className="text-gray-600 text-sm font-light">
            <tr className="border-b border-gray-200 hover:bg-gray-100">
              <td className="py-3 px-6 text-left whitespace-nowrap">Spécialisation Reconversion</td>
              <td className="py-3 px-6 text-left font-bold text-green-600">✅ UNIQUE</td>
              <td className="py-3 px-6 text-left text-red-500">❌ Généraliste</td>
              <td className="py-3 px-6 text-left text-red-500">❌ Généraliste</td>
            </tr>
            <tr className="border-b border-gray-200 hover:bg-gray-100">
              <td className="py-3 px-6 text-left">Créé par un Reconverti</td>
              <td className="py-3 px-6 text-left font-bold text-green-600">✅ Matthieu</td>
              <td className="py-3 px-6 text-left text-red-500">❌ Corporate</td>
              <td className="py-3 px-6 text-left text-red-500">❌ Corporate</td>
            </tr>
            <tr className="border-b border-gray-200 hover:bg-gray-100">
              <td className="py-3 px-6 text-left">Prix Accessible</td>
              <td className="py-3 px-6 text-left font-bold text-green-600">✅ 7,99€</td>
              <td className="py-3 px-6 text-left text-red-500">❌ 23,70€</td>
              <td className="py-3 px-6 text-left text-orange-500">⚠️ Freemium</td>
            </tr>
            <tr className="border-b border-gray-200 hover:bg-gray-100">
              <td className="py-3 px-6 text-left">Approche Éthique</td>
              <td className="py-3 px-6 text-left font-bold text-green-600">✅ Fonds Solidaire</td>
              <td className="py-3 px-6 text-left text-red-500">❌ Profit seul</td>
              <td className="py-3 px-6 text-left text-red-500">❌ Profit seul</td>
            </tr>
            <tr className="border-b border-gray-200 hover:bg-gray-100">
              <td className="py-3 px-6 text-left">Compétences Transférables</td>
              <td className="py-3 px-6 text-left font-bold text-green-600">✅ Cœur du produit</td>
              <td className="py-3 px-6 text-left text-red-500">❌ Absent</td>
              <td className="py-3 px-6 text-left text-red-500">❌ Absent</td>
            </tr>
            <tr className="border-b border-gray-200 hover:bg-gray-100">
              <td className="py-3 px-6 text-left">Phase</td>
              <td className="py-3 px-6 text-left font-bold text-green-600">🚀 Lancement</td>
              <td className="py-3 px-6 text-left text-gray-500">😴 Mature</td>
              <td className="py-3 px-6 text-left text-gray-500">😴 Mature</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p className="text-center text-xl font-semibold mt-12 text-gray-800">
        "Phoenix est jeune mais révolutionnaire. Vous rejoignez l'aventure au début !"
      </p>
    </section>
  );
};

export default CompetitiveComparison;
