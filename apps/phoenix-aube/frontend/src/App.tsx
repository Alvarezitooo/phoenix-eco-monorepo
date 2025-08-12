import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import DiagnosticQuiz from './components/DiagnosticQuiz';
import { DiagnosticResponse, AspirationProfile } from './types';
import { analyzeDiagnosticResponses } from './utils/diagnosticAnalysis';

type AppState = 'welcome' | 'quiz' | 'profile' | 'results' | 'locked' | 'trajectory';

const AppContent: React.FC = () => {
  const { user, login, logout } = useAuth();
  const [currentState, setCurrentState] = useState<AppState>('welcome');
  const [aspirationProfile, setAspirationProfile] = useState<AspirationProfile | null>(null);

  // Interface vers Phoenix Event Bridge
  const sendEventToBridge = async (eventType: string, data: Record<string, unknown>) => {
    try {
      // TODO: Remplacer par l'API Phoenix Event Bridge réelle
      const response = await fetch('/api/v1/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('phoenix_auth_token')}`
        },
        body: JSON.stringify({
          event_type: eventType,
          data,
          timestamp: new Date().toISOString(),
          user_id: user?.id
        })
      });
      
      if (!response.ok) {
        console.warn('Événement non envoyé au bridge:', eventType);
      } else {
        console.log('✅ Événement envoyé:', eventType, data);
      }
    } catch (error) {
      console.warn('Erreur Event Bridge:', error);
    }
  };

  const handleQuizComplete = async (responses: DiagnosticResponse[]) => {
    const profile = analyzeDiagnosticResponses(responses);
    setAspirationProfile(profile);
    setCurrentState('profile');

    // Envoyer l'événement au Phoenix Event Bridge
    await sendEventToBridge('CAREER_EXPLORED', {
      userId: user?.id,
      profileData: profile,
      responses: responses.length,
      completedAt: new Date().toISOString()
    });
  };

  const handleProfileContinue = () => {
    if (user?.isPremium) {
      setCurrentState('results');
    } else {
      setCurrentState('locked');
    }
  };

  // Formulaire de connexion simple
  const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
      e.preventDefault();
      await login(email, password);
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Phoenix Aube
            </h1>
            <p className="text-gray-600">
              Connexion à votre espace d'exploration carrière
            </p>
          </div>
          
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="votre@email.com"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
            
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 rounded-xl font-semibold hover:from-orange-600 hover:to-red-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
            >
              Se connecter
            </button>
          </form>
          
          <div className="mt-6 text-center text-sm text-gray-500">
            Connectez-vous avec votre compte Phoenix
          </div>
        </div>
      </div>
    );
  };

  if (!user) {
    return <LoginForm />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Phoenix Aube</h1>
              {user.isPremium && (
                <span className="ml-3 px-2 py-1 text-xs font-semibold text-orange-600 bg-orange-100 rounded-full">
                  Premium
                </span>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {user.firstName} {user.lastName}
              </span>
              <button
                onClick={logout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Déconnexion
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Contenu principal */}
      {currentState === 'welcome' && (
        <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 flex items-center justify-center p-4">
          <div className="max-w-2xl text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-6">
              Bienvenue dans Phoenix Aube
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Découvrez vos aspirations profondes et explorez les carrières 
              qui vous correspondent vraiment. Résolvez votre double anxiété 
              face à l'incertitude et à l'évolution de l'IA.
            </p>
            <button
              onClick={() => setCurrentState('quiz')}
              className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-orange-600 hover:to-red-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
            >
              Commencer mon diagnostic
            </button>
          </div>
        </div>
      )}

      {currentState === 'quiz' && (
        <DiagnosticQuiz onComplete={handleQuizComplete} />
      )}

      {currentState === 'profile' && aspirationProfile && (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Votre Profil d'Aspiration</h2>
              
              {/* Traits dominants */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Vos traits dominants</h3>
                <div className="flex flex-wrap gap-3">
                  {aspirationProfile.dominantTraits.map((trait, index) => (
                    <span
                      key={index}
                      className="px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full font-medium"
                    >
                      {trait}
                    </span>
                  ))}
                </div>
              </div>

              {/* Insights personnalité */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Insights sur votre personnalité</h3>
                <div className="space-y-3">
                  {aspirationProfile.personalityInsights.map((insight, index) => (
                    <div key={index} className="flex items-start">
                      <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3"></div>
                      <p className="text-gray-700">{insight}</p>
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={handleProfileContinue}
                className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-4 rounded-xl font-semibold text-lg hover:from-orange-600 hover:to-red-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                Voir mes recommandations carrière
              </button>
            </div>
          </div>
        </div>
      )}

      {currentState === 'locked' && (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 p-4 flex items-center justify-center">
          <div className="max-w-md text-center bg-white rounded-2xl shadow-xl p-8">
            <div className="mb-6">
              <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">🔒</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Contenu Premium
              </h2>
              <p className="text-gray-600">
                Pour accéder aux recommandations personnalisées et à l'analyse IA avancée, 
                passez à Phoenix Premium.
              </p>
            </div>
            
            <button
              onClick={() => {
                // TODO: Intégrer avec le système de paiement Phoenix
                alert('Redirection vers les offres Premium...');
              }}
              className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-4 rounded-xl font-semibold text-lg hover:from-orange-600 hover:to-red-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
            >
              Passer Premium
            </button>
          </div>
        </div>
      )}

      {currentState === 'results' && (
        <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                Vos Carrières Recommandées
              </h2>
              <p className="text-gray-600 mb-8">
                Basé sur votre profil, voici les carrières les mieux adaptées avec leur résistance à l'IA.
              </p>
              
              {/* Placeholder pour les résultats - à connecter avec l'API */}
              <div className="space-y-4">
                {[
                  { title: "Coach en transformation digitale", score: 92, resilience: 85 },
                  { title: "Consultant en conduite du changement", score: 88, resilience: 90 },
                  { title: "Formateur en soft skills", score: 85, resilience: 88 }
                ].map((career, index) => (
                  <div key={index} className="border border-gray-200 rounded-xl p-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{career.title}</h3>
                    <div className="flex items-center space-x-6">
                      <div>
                        <span className="text-sm text-gray-600">Score de correspondance</span>
                        <div className="text-2xl font-bold text-green-600">{career.score}%</div>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Résistance IA</span>
                        <div className="text-2xl font-bold text-blue-600">{career.resilience}%</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;