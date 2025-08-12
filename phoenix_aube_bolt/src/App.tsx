import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Header from './components/Header';
import AuthForm from './components/AuthForm';
import DiagnosticQuiz from './components/DiagnosticQuiz';
import AspirationProfile from './components/AspirationProfile';
import LockedResults from './components/LockedResults';
import CareerResults from './components/CareerResults';
import TrajectoryBuilder from './components/TrajectoryBuilder';
import { DiagnosticResponse, AspirationProfile as AspirationProfileType } from './types';
import { analyzeDiagnosticResponses } from './utils/diagnosticAnalysis';

type AppState = 'welcome' | 'quiz' | 'profile' | 'results' | 'locked' | 'trajectory';

const AppContent: React.FC = () => {
  const { user } = useAuth();
  const [currentState, setCurrentState] = useState<AppState>('welcome');
  const [aspirationProfile, setAspirationProfile] = useState<AspirationProfileType | null>(null);

  // Simulate event bridge call
  const sendEventToBridge = (eventType: string, data: any) => {
    console.log(`Phoenix Event Bridge: ${eventType}`, data);
    // In real app, this would call your event bridge API
  };

  const handleQuizComplete = (responses: DiagnosticResponse[]) => {
    const profile = analyzeDiagnosticResponses(responses);
    setAspirationProfile(profile);
    setCurrentState('profile');

    // Send CAREER_EXPLORED event
    sendEventToBridge('CAREER_EXPLORED', {
      userId: user?.id,
      profileData: profile,
      timestamp: new Date().toISOString()
    });
  };

  const handleProfileContinue = () => {
    if (user?.isPremium) {
      setCurrentState('results');
    } else {
      setCurrentState('locked');
    }
  };

  const handleUpgradeComplete = () => {
    // Send SUBSCRIPTION_ACTIVATED event
    sendEventToBridge('SUBSCRIPTION_ACTIVATED', {
      userId: user?.id,
      timestamp: new Date().toISOString()
    });
    setCurrentState('results');
  };

  const handleResultsContinue = () => {
    setCurrentState('trajectory');
  };

  if (!user) {
    return <AuthForm />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
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
        <AspirationProfile 
          profile={aspirationProfile} 
          onContinue={handleProfileContinue}
        />
      )}

      {currentState === 'locked' && (
        <LockedResults onUpgrade={handleUpgradeComplete} />
      )}

      {currentState === 'results' && (
        <CareerResults onContinue={handleResultsContinue} />
      )}

      {currentState === 'trajectory' && <TrajectoryBuilder />}
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