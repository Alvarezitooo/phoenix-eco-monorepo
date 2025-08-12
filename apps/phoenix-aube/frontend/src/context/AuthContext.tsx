import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { AuthContextType } from './AuthTypes';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Simuler une authentification (à remplacer par l'API Phoenix réelle)
  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // TODO: Remplacer par l'appel API Phoenix Auth
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData.user);
        localStorage.setItem('phoenix_auth_token', userData.token);
      } else {
        throw new Error('Échec de la connexion');
      }
    } catch (error) {
      console.error('Erreur de connexion:', error);
      // Mode démonstration - créer un utilisateur fictif
      const demoUser: User = {
        id: 'demo-user-' + Date.now(),
        email,
        firstName: 'Demo',
        lastName: 'User',
        isPremium: Math.random() > 0.5, // 50% chance d'être premium pour les tests
        hasCompletedDiagnosis: false
      };
      setUser(demoUser);
      localStorage.setItem('phoenix_auth_token', 'demo-token');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('phoenix_auth_token');
  };

  // Vérifier le token au chargement
  useEffect(() => {
    const token = localStorage.getItem('phoenix_auth_token');
    if (token && token === 'demo-token') {
      // Mode démonstration
      const demoUser: User = {
        id: 'demo-user',
        email: 'demo@phoenix.fr',
        firstName: 'Demo',
        lastName: 'User',
        isPremium: true, // Pour les tests
        hasCompletedDiagnosis: false
      };
      setUser(demoUser);
    }
    setLoading(false);
  }, []);

  const value = {
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};