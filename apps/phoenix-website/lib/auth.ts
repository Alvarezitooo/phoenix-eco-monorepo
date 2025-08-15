/**
 * 🔐 Phoenix Website - Service d'Authentification Unifié
 * Intégration Supabase Auth pour le website Phoenix
 */

import { createClient } from '@supabase/supabase-js';
import { cookies } from 'next/headers';

// Types Phoenix Auth
export interface PhoenixUser {
  id: string;
  email: string;
  fullName?: string;
  subscriptionTier: 'free' | 'premium' | 'enterprise';
  apps: {
    letters: boolean;
    cv: boolean;
    rise: boolean;
    aube: boolean;
  };
  preferences: {
    newsletter: boolean;
    analytics: boolean;
    marketing: boolean;
  };
  createdAt: string;
  lastLoginAt: string;
}

export interface PhoenixSession {
  user: PhoenixUser;
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

// Configuration Supabase
const supabaseUrl = process.env.SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);

// Service d'authentification Phoenix
export class PhoenixWebsiteAuth {
  private static instance: PhoenixWebsiteAuth;

  static getInstance(): PhoenixWebsiteAuth {
    if (!PhoenixWebsiteAuth.instance) {
      PhoenixWebsiteAuth.instance = new PhoenixWebsiteAuth();
    }
    return PhoenixWebsiteAuth.instance;
  }

  // Inscription utilisateur
  async signUp(email: string, password: string, metadata?: any): Promise<PhoenixUser | null> {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: metadata?.fullName,
            source_app: 'website',
            utm_source: metadata?.utmSource,
            newsletter_opt_in: metadata?.newsletter || false,
          },
        },
      });

      if (error) throw error;

      if (data.user) {
        // Créer profil Phoenix
        await this.createPhoenixProfile(data.user.id, {
          email,
          fullName: metadata?.fullName,
          subscriptionTier: 'free',
          sourceApp: 'website',
        });

        return this.transformToPhoenixUser(data.user);
      }

      return null;
    } catch (error) {
      console.error('Phoenix signup error:', error);
      throw error;
    }
  }

  // Connexion utilisateur
  async signIn(email: string, password: string): Promise<PhoenixUser | null> {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      if (data.user) {
        // Mettre à jour last_login
        await this.updateLastLogin(data.user.id);
        return this.transformToPhoenixUser(data.user);
      }

      return null;
    } catch (error) {
      console.error('Phoenix signin error:', error);
      throw error;
    }
  }

  // Connexion Google OAuth
  async signInWithGoogle(): Promise<{ url: string }> {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        queryParams: {
          source_app: 'website',
        },
      },
    });

    if (error) throw error;
    return { url: data.url };
  }

  // Déconnexion
  async signOut(): Promise<void> {
    await supabase.auth.signOut();
  }

  // Récupérer utilisateur actuel
  async getCurrentUser(): Promise<PhoenixUser | null> {
    try {
      const {
        data: { user },
        error,
      } = await supabase.auth.getUser();

      if (error || !user) return null;

      return this.transformToPhoenixUser(user);
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  }

  // Générer token cross-app
  async generateCrossAppToken(targetApp: 'letters' | 'cv' | 'rise'): Promise<string> {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) throw new Error('No active session');

    // Token JWT personnalisé pour navigation cross-app
    const crossAppToken = btoa(
      JSON.stringify({
        userId: session.user.id,
        email: session.user.email,
        targetApp,
        timestamp: Date.now(),
        signature: this.generateSignature(session.user.id, targetApp),
      }),
    );

    return crossAppToken;
  }

  // Redirection cross-app sécurisée
  async redirectToApp(app: 'letters' | 'cv' | 'rise', userData?: any): Promise<void> {
    const token = await this.generateCrossAppToken(app);

    const urls = {
      letters:
        process.env.NEXT_PUBLIC_PHOENIX_LETTERS_URL || 'https://phoenix-letters.streamlit.app',
      cv: process.env.NEXT_PUBLIC_PHOENIX_CV_URL || 'https://phoenix-cv.streamlit.app',
      rise: process.env.NEXT_PUBLIC_PHOENIX_RISE_URL || 'https://phoenix-rise.streamlit.app',
    };

    const params = new URLSearchParams({
      phoenix_token: token,
      source: 'website',
      ...(userData && { user_data: JSON.stringify(userData) }),
    });

    window.location.href = `${urls[app]}?${params.toString()}`;
  }

  // Helpers privés
  private async createPhoenixProfile(userId: string, data: any): Promise<void> {
    const { error } = await supabase.from('profiles').insert({
      id: userId,
      email: data.email,
      full_name: data.fullName,
      subscription_tier: data.subscriptionTier,
      app_preferences: {
        letters: false,
        cv: false,
        rise: false,
        aube: false,
      },
      created_at: new Date().toISOString(),
    });

    if (error) {
      console.error('Create profile error:', error);
    }
  }

  private async updateLastLogin(userId: string): Promise<void> {
    await supabase
      .from('profiles')
      .update({
        last_login_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      })
      .eq('id', userId);
  }

  private transformToPhoenixUser(user: any): PhoenixUser {
    return {
      id: user.id,
      email: user.email,
      fullName: user.user_metadata?.full_name,
      subscriptionTier: user.app_metadata?.subscription_tier || 'free',
      apps: {
        letters: user.app_metadata?.apps?.letters || false,
        cv: user.app_metadata?.apps?.cv || false,
        rise: user.app_metadata?.apps?.rise || false,
        aube: user.app_metadata?.apps?.aube || false,
      },
      preferences: {
        newsletter: user.user_metadata?.newsletter_opt_in || false,
        analytics: user.user_metadata?.analytics_opt_in || true,
        marketing: user.user_metadata?.marketing_opt_in || false,
      },
      createdAt: user.created_at,
      lastLoginAt: user.last_sign_in_at,
    };
  }

  private generateSignature(userId: string, targetApp: string): string {
    // Signature simple pour validation cross-app
    const secret = process.env.NEXT_PUBLIC_PHOENIX_SECRET || 'phoenix-secret';
    return btoa(`${userId}-${targetApp}-${secret}`);
  }
}

// Instance singleton
export const phoenixAuth = PhoenixWebsiteAuth.getInstance();

// Hook React pour auth
export function usePhoenixAuth() {
  return {
    signUp: phoenixAuth.signUp.bind(phoenixAuth),
    signIn: phoenixAuth.signIn.bind(phoenixAuth),
    signInWithGoogle: phoenixAuth.signInWithGoogle.bind(phoenixAuth),
    signOut: phoenixAuth.signOut.bind(phoenixAuth),
    getCurrentUser: phoenixAuth.getCurrentUser.bind(phoenixAuth),
    redirectToApp: phoenixAuth.redirectToApp.bind(phoenixAuth),
  };
}
