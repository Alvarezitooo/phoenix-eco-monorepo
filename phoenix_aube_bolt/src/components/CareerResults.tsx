import React from 'react';
import { Star, Zap, TrendingUp, MapPin, GraduationCap, DollarSign, Users, ArrowRight } from 'lucide-react';
import { CareerPath } from '../types';
import { generateCareerPaths } from '../data/careerPaths';

interface CareerResultsProps {
  onContinue: () => void;
}

const CareerResults: React.FC<CareerResultsProps> = ({ onContinue }) => {
  const careerPaths = generateCareerPaths();

  const getGrowthColor = (outlook: string) => {
    switch (outlook) {
      case 'high': return 'from-green-500 to-emerald-500';
      case 'medium': return 'from-yellow-500 to-orange-500';
      case 'low': return 'from-red-400 to-red-500';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  const getGrowthLabel = (outlook: string) => {
    switch (outlook) {
      case 'high': return 'Forte croissance';
      case 'medium': return 'Croissance modérée';
      case 'low': return 'Croissance faible';
      default: return 'Non défini';
    }
  };

  const getAIScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-orange-600';
  };

  const CareerCard = ({ career, rank }: { career: CareerPath; rank: number }) => (
    <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-full mr-3"></div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-1">{career.title}</h3>
            <div className="flex items-center space-x-3">
              <div className="flex items-center">
                <Star className="h-4 w-4 text-yellow-500 mr-1" />
                <span className="text-sm font-bold text-gray-700">{career.matchScore}% match</span>
              </div>
              <div className="flex items-center">
                <Zap className={`h-4 w-4 mr-1 ${getAIScoreColor(career.aiResilienceScore)}`} />
                <span className={`text-sm font-bold ${getAIScoreColor(career.aiResilienceScore)}`}>
                  IA Score: {career.aiResilienceScore}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">#{rank}</div>
          <div className="text-xs text-gray-500">Recommandation</div>
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-600 mb-6 leading-relaxed">{career.description}</p>

      {/* Details Grid */}
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="space-y-3">
          <div className="flex items-center">
            <DollarSign className="h-4 w-4 text-green-600 mr-2" />
            <span className="text-sm text-gray-700">{career.salaryRange}</span>
          </div>
          <div className="flex items-center">
            <GraduationCap className="h-4 w-4 text-blue-600 mr-2" />
            <span className="text-sm text-gray-700">{career.requiredEducation}</span>
          </div>
        </div>
        <div className="space-y-3">
          <div className="flex items-center">
            <TrendingUp className="h-4 w-4 text-purple-600 mr-2" />
            <span className="text-sm text-gray-700">{getGrowthLabel(career.growthOutlook)}</span>
          </div>
          <div className="flex items-center">
            <Users className="h-4 w-4 text-orange-600 mr-2" />
            <span className="text-sm text-gray-700">{career.workEnvironment}</span>
          </div>
        </div>
      </div>

      {/* Skills */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Compétences clés</h4>
        <div className="flex flex-wrap gap-2">
          {career.keySkills.map((skill, index) => (
            <span 
              key={index} 
              className="px-3 py-1 bg-blue-50 text-blue-800 rounded-full text-xs font-medium"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>

      {/* AI Resilience Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Résilience IA</span>
          <span className={`text-sm font-bold ${getAIScoreColor(career.aiResilienceScore)}`}>
            {career.aiResilienceScore}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-1000 ease-out ${
              career.aiResilienceScore >= 85 ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
              career.aiResilienceScore >= 70 ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
              'bg-gradient-to-r from-orange-500 to-red-500'
            }`}
            style={{ width: `${career.aiResilienceScore}%` }}
          />
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl mb-4">
            <TrendingUp className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Vos 3 Pistes de Carrière</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Basé sur votre profil d'aspiration, voici les carrières qui vous correspondent le mieux, 
            avec leur potentiel de résilience face à l'IA.
          </p>
        </div>

        {/* Career Cards */}
        <div className="space-y-6 mb-8">
          {careerPaths.map((career, index) => (
            <CareerCard key={career.id} career={career} rank={index + 1} />
          ))}
        </div>

        {/* Insights Panel */}
        <div className="bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl shadow-2xl p-8 text-center text-white mb-8">
          <h2 className="text-2xl font-bold mb-4">Trajectory Builder Activé !</h2>
          <p className="text-emerald-100 mb-6 max-w-2xl mx-auto">
            Félicitations ! Votre parcours Phoenix Aube est terminé. 
            Vous avez maintenant accès à tout l'écosystème Phoenix pour concrétiser votre reconversion.
          </p>
          
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white/10 rounded-xl p-4">
              <h3 className="font-semibold mb-2">Phoenix Letters</h3>
              <p className="text-sm text-emerald-100">Lettres de motivation personnalisées</p>
            </div>
            
            <div className="bg-white/10 rounded-xl p-4">
              <h3 className="font-semibold mb-2">Phoenix CV</h3>
              <p className="text-sm text-emerald-100">CV optimisé pour vos nouvelles pistes</p>
            </div>
            
            <div className="bg-white/10 rounded-xl p-4">
              <h3 className="font-semibold mb-2">Phoenix Rise</h3>
              <p className="text-sm text-emerald-100">Coaching et suivi personnalisé</p>
            </div>
          </div>
          
          <button
            onClick={onContinue}
            className="bg-white text-emerald-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-50 transform hover:scale-105 transition-all duration-200 shadow-lg inline-flex items-center"
          >
            Accéder à l'Écosystème Phoenix
            <ArrowRight className="ml-2 h-5 w-5" />
          </button>
        </div>

        {/* Trust by Design Report */}
        <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Trust by Design Report V1</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Méthodologie</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Analyse Big Five certifiée</li>
                <li>• Taxonomie RIASEC validée</li>
                <li>• Matching ROME/ESCO actualisé</li>
                <li>• Score IA basé sur O*NET</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Transparence</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Algorithmes explicables</li>
                <li>• Sources de données publiques</li>
                <li>• Biais identifiés et corrigés</li>
                <li>• Résultats auditables</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CareerResults;