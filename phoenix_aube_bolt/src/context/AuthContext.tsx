import React, { createContext, useContext, useState, ReactNode } from 'react';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (firstName: string, lastName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  upgradeToPremium: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Demo users - in real app this would be handled by your authentication service
    const demoUser: User = {
      id: '1',
      email,
      firstName: email.includes('premium') ? 'Marie' : 'Jean',
      lastName: email.includes('premium') ? 'Premium' : 'Gratuit',
      isPremium: email.includes('premium'),
      hasCompletedDiagnosis: false,
    };
    
    setUser(demoUser);
  };

  const register = async (firstName: string, lastName: string, email: string, password: string) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const newUser: User = {
      id: Date.now().toString(),
      email,
      firstName,
      lastName,
      isPremium: false,
      hasCompletedDiagnosis: false,
    };
    
    setUser(newUser);
  };

  const logout = () => {
    setUser(null);
  };

  const upgradeToPremium = () => {
    if (user) {
      setUser({ ...user, isPremium: true });
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    upgradeToPremium,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};