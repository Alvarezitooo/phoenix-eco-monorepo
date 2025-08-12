import React from 'react';
import { AspirationProfile as AspirationProfileType } from '../types';
import { Brain, Target, TrendingUp, Lightbulb } from 'lucide-react';

interface AspirationProfileProps {
  profile: AspirationProfileType;
  onContinue: () => void;
}

const AspirationProfile: React.FC<AspirationProfileProps> = ({ profile, onContinue }) => {
  const bigFiveLabels = {
    openness: 'Ouverture',
    conscientiousness: 'Conscienciosité',
    extraversion: 'Extraversion',
    agreeableness: 'Amabilité',
    neuroticism: 'Névrosisme'
  };

  const riasecLabels = {
    realistic: 'Réaliste',
    investigative: 'Investigateur',
    artistic: 'Artistique',
    social: 'Social',
    enterprising: 'Entreprenant',
    conventional: 'Conventionnel'
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'from-green-500 to-emerald-500';
    if (score >= 60) return 'from-blue-500 to-cyan-500';
    if (score >= 40) return 'from-yellow-500 to-orange-500';
    return 'from-gray-400 to-gray-500';
  };

  const ScoreBar = ({ label, score, description }: { label: string; score: number; description?: string }) => (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-bold text-gray-900">{score}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div 
          className={`bg-gradient-to-r ${getScoreColor(score)} h-3 rounded-full transition-all duration-1000 ease-out`}
          style={{ width: `${score}%` }}
        />
      </div>
      {description && (
        <p className="text-xs text-gray-600">{description}</p>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl mb-4">
            <Brain className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Votre Profil d'Aspiration</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Découvrez vos traits de personnalité dominants et vos préférences professionnelles 
            pour mieux comprendre vos aspirations de carrière.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Big Five Personality */}
          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
            <div className="flex items-center mb-6">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <Brain className="h-5 w-5 text-blue-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Traits de Personnalité</h2>
            </div>
            
            <div className="space-y-6">
              {Object.entries(profile.bigFive).map(([key, value]) => (
                <ScoreBar 
                  key={key} 
                  label={bigFiveLabels[key as keyof typeof bigFiveLabels]} 
                  score={value} 
                />
              ))}
            </div>
          </div>

          {/* RIASEC Interests */}
          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
            <div className="flex items-center mb-6">
              <div className="p-2 bg-green-100 rounded-lg mr-3">
                <Target className="h-5 w-5 text-green-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Intérêts Professionnels</h2>
            </div>
            
            <div className="space-y-6">
              {Object.entries(profile.riasec).map(([key, value]) => (
                <ScoreBar 
                  key={key} 
                  label={riasecLabels[key as keyof typeof riasecLabels]} 
                  score={value} 
                />
              ))}
            </div>
          </div>
        </div>

        {/* Insights */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Dominant Traits */}
          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-orange-100 rounded-lg mr-3">
                <TrendingUp className="h-5 w-5 text-orange-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Traits Dominants</h3>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {profile.dominantTraits.map((trait, index) => (
                <span 
                  key={index} 
                  className="px-3 py-1 bg-gradient-to-r from-orange-100 to-red-100 text-orange-800 rounded-full text-sm font-medium"
                >
                  {trait}
                </span>
              ))}
            </div>
          </div>

          {/* Personality Insights */}
          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-purple-100 rounded-lg mr-3">
                <Lightbulb className="h-5 w-5 text-purple-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Insights Clés</h3>
            </div>
            
            <ul className="space-y-2">
              {profile.personalityInsights.map((insight, index) => (
                <li key={index} className="flex items-start">
                  <div className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-sm text-gray-700">{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <button
            onClick={onContinue}
            className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-indigo-600 hover:to-purple-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
          >
            Découvrir mes pistes de carrière
          </button>
        </div>
      </div>
    </div>
  );
};

export default AspirationProfile;