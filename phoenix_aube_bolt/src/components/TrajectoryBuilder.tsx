import React from 'react';
import { Rocket, FileText, User, TrendingUp, CheckCircle, ArrowRight } from 'lucide-react';

const TrajectoryBuilder: React.FC = () => {
  const ecosystemTools = [
    {
      name: 'Phoenix Letters',
      icon: FileText,
      description: 'Générez des lettres de motivation personnalisées pour vos candidatures',
      status: 'Disponible',
      gradient: 'from-blue-500 to-purple-500'
    },
    {
      name: 'Phoenix CV',
      icon: User,
      description: 'Créez un CV optimisé pour vos nouvelles pistes de carrière',
      status: 'Disponible',
      gradient: 'from-green-500 to-teal-500'
    },
    {
      name: 'Phoenix Rise',
      icon: TrendingUp,
      description: 'Bénéficiez d\'un coaching personnalisé pour votre transition',
      status: 'Disponible',
      gradient: 'from-orange-500 to-red-500'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl mb-6">
            <Rocket className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Trajectory Builder</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Votre parcours Phoenix Aube est terminé ! Continuez votre renaissance professionnelle 
            avec nos outils spécialisés.
          </p>
        </div>

        {/* Completion Status */}
        <div className="bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl p-6 mb-8 text-center text-white">
          <div className="flex items-center justify-center mb-4">
            <CheckCircle className="h-8 w-8 mr-3" />
            <span className="text-2xl font-bold">Mission Accomplie !</span>
          </div>
          <p className="text-emerald-100">
            Vous avez identifié vos aspirations et découvert vos 3 pistes de carrière optimales.
          </p>
        </div>

        {/* Ecosystem Tools */}
        <div className="grid gap-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 text-center">
            Continuez avec l'Écosystème Phoenix
          </h2>
          
          {ecosystemTools.map((tool, index) => (
            <div key={index} className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
              <div className="flex items-start">
                <div className={`p-4 bg-gradient-to-r ${tool.gradient} rounded-2xl mr-6`}>
                  <tool.icon className="h-8 w-8 text-white" />
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-2xl font-bold text-gray-900">{tool.name}</h3>
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                      {tool.status}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                    {tool.description}
                  </p>
                  
                  <button className={`bg-gradient-to-r ${tool.gradient} text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 inline-flex items-center`}>
                    Accéder à {tool.name}
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Success Metrics */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 text-center">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Votre Parcours Phoenix</h3>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl">
              <div className="text-3xl font-bold text-blue-600 mb-2">100%</div>
              <div className="text-sm text-gray-600">Diagnostic Complété</div>
            </div>
            
            <div className="p-6 bg-gradient-to-br from-green-50 to-teal-50 rounded-xl">
              <div className="text-3xl font-bold text-green-600 mb-2">3</div>
              <div className="text-sm text-gray-600">Pistes Identifiées</div>
            </div>
            
            <div className="p-6 bg-gradient-to-br from-orange-50 to-red-50 rounded-xl">
              <div className="text-3xl font-bold text-orange-600 mb-2">∞</div>
              <div className="text-sm text-gray-600">Possibilités Ouvertes</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrajectoryBuilder;