import React from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginForm from './components/LoginForm';
import ZazenTimer from './components/ZazenTimer';
import KaizenGrid from './components/KaizenGrid';
import { useDojoApi } from './hooks/useDojoApi';
import './App.css';

function AppContent() {
  const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const { isLoading } = useDojoApi();

  if (authLoading) {
    return (
      <div className="app">
        <div className="loading-overlay">
          <div className="loading-spinner">Initialisation...</div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="app">
        <LoginForm />
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🌅 Phoenix Rise</h1>
            <p>Dojo Mental pour votre Renaissance Professionnelle</p>
          </div>
          <div className="user-info">
            <span>Bonjour, {user?.firstName || 'Utilisateur'}</span>
            <button onClick={logout} className="logout-button">
              Déconnexion
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">
        <section className="zazen-section">
          <h2>🧘‍♂️ Respiration Zazen</h2>
          <ZazenTimer />
        </section>

        <section className="kaizen-section">
          <h2>📈 Historique Kaizen</h2>
          <KaizenGrid userId={user?.id || ''} />
        </section>

        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner">Chargement...</div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Phoenix Rise - Développé avec ❤️ par l'équipe Phoenix</p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;