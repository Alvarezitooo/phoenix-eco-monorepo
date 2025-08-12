import React from 'react';
import { Lock, Star, Zap, TrendingUp, Crown } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface LockedResultsProps {
  onUpgrade: () => void;
}

const LockedResults: React.FC<LockedResultsProps> = ({ onUpgrade }) => {
  const { upgradeToPremium } = useAuth();

  const handleUpgrade = () => {
    upgradeToPremium();
    onUpgrade();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl mb-4">
            <Crown className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Vos Pistes de Carrière sont Prêtes !</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Nous avons analysé votre profil et identifié 3 pistes de carrière personnalisées, 
            avec leur score de résilience face à l'IA.
          </p>
        </div>

        {/* Preview Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {[1, 2, 3].map((index) => (
            <div key={index} className="relative">
              <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 opacity-75">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-gray-200 rounded-lg animate-pulse"></div>
                  <div className="flex items-center">
                    <Star className="h-4 w-4 text-yellow-500 mr-1" />
                    <span className="text-sm font-bold text-gray-400">??%</span>
                  </div>
                </div>
                
                <div className="space-y-2 mb-4">
                  <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3 animate-pulse"></div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Zap className="h-4 w-4 text-green-500 mr-1" />
                    <span className="text-sm text-gray-400">IA Score: ??</span>
                  </div>
                  <div className="text-sm text-gray-400">€??k</div>
                </div>
              </div>
              
              {/* Lock Overlay */}
              <div className="absolute inset-0 flex items-center justify-center bg-white/90 rounded-2xl">
                <div className="text-center">
                  <Lock className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-600">Piste #{index}</p>
                  <p className="text-xs text-gray-500">Verrouillée</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Unlock Section */}
        <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl shadow-2xl p-8 text-center text-white mb-8">
          <h2 className="text-2xl font-bold mb-4">Débloquez Votre Avenir Professionnel</h2>
          <p className="text-orange-100 mb-6 max-w-2xl mx-auto">
            Accédez à vos 3 pistes de carrière personnalisées, leur analyse détaillée, 
            et activez votre Trajectory Builder pour un parcours complet.
          </p>
          
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <TrendingUp className="h-6 w-6" />
              </div>
              <h3 className="font-semibold mb-2">Analyses Détaillées</h3>
              <p className="text-sm text-orange-100">Compétences, salaires, perspectives</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <Zap className="h-6 w-6" />
              </div>
              <h3 className="font-semibold mb-2">Score IA</h3>
              <p className="text-sm text-orange-100">Résilience face à l'automatisation</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <Star className="h-6 w-6" />
              </div>
              <h3 className="font-semibold mb-2">Trajectory Builder</h3>
              <p className="text-sm text-orange-100">Plan d'action personnalisé</p>
            </div>
          </div>
          
          <button
            onClick={handleUpgrade}
            className="bg-white text-orange-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-50 transform hover:scale-105 transition-all duration-200 shadow-lg"
          >
            Accéder à Phoenix Premium
          </button>
          
          <p className="text-sm text-orange-200 mt-4">
            Déblocage immédiat • Sans engagement
          </p>
        </div>

        {/* Trust Indicators */}
        <div className="grid md:grid-cols-3 gap-6 text-center">
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="text-2xl font-bold text-gray-900 mb-1">15,000+</div>
            <div className="text-sm text-gray-600">Reconversions réussies</div>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="text-2xl font-bold text-gray-900 mb-1">94%</div>
            <div className="text-sm text-gray-600">Satisfaction client</div>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="text-2xl font-bold text-gray-900 mb-1">6 mois</div>
            <div className="text-sm text-gray-600">Temps moyen de transition</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LockedResults;