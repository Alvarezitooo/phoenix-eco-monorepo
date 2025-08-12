import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

interface LoginFormProps {
  onSuccess?: () => void;
}

export default function LoginForm({ onSuccess }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    console.log('🔍 Tentative de connexion:', { email, password });
    
    try {
      const success = await login(email, password);
      console.log('🔍 Résultat login:', success);
      
      if (success) {
        console.log('✅ Connexion réussie');
        onSuccess?.();
      } else {
        console.log('❌ Connexion échouée');
        setError('Email ou mot de passe incorrect');
      }
    } catch (error) {
      console.error('🚨 Erreur login:', error);
      setError('Erreur de connexion: ' + error);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>🌅 Connexion Phoenix Rise</h2>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Mot de passe</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>

        <button 
          type="submit" 
          className="login-button"
          disabled={isLoading}
        >
          {isLoading ? 'Connexion...' : 'Se connecter'}
        </button>

        <div className="demo-credentials">
          <p><strong>Phoenix Rise</strong></p>
          <p>Connectez-vous avec votre compte Phoenix</p>
        </div>
      </form>
    </div>
  );
}