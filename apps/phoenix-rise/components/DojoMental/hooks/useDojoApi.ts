/**
 * Hook custom pour les appels API Dojo Mental
 * Externalise toute la logique réseau du composant UI
 * 
 * Author: Claude Phoenix DevSecOps Guardian
 * Version: 1.0.0 - Clean Architecture Pattern
 */

import { useState, useCallback } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_DOJO_API_URL || "http://127.0.0.1:8000";

interface KaizenEntry {
  user_id: string;
  action: string;
  date: string;
  completed: boolean;
}

interface ZazenSession {
  user_id: string;
  timestamp: string;
  duration: number;
  triggered_by?: string;
}

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  status?: number;
}

export const useDojoApi = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createKaizen = useCallback(async (kaizenData: KaizenEntry): Promise<ApiResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/kaizen`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(kaizenData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("✅ Kaizen created:", data);
      
      return {
        success: true,
        data,
        status: response.status
      };

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error("❌ Error creating Kaizen:", errorMessage);
      setError(errorMessage);
      
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createZazenSession = useCallback(async (sessionData: ZazenSession): Promise<ApiResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/zazen-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("✅ Zazen session created:", data);
      
      return {
        success: true,
        data,
        status: response.status
      };

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error("❌ Error creating Zazen session:", errorMessage);
      setError(errorMessage);
      
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getUserKaizens = useCallback(async (userId: string): Promise<ApiResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/kaizen/${userId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("✅ Kaizens retrieved:", data.length, "entries");
      
      return {
        success: true,
        data,
        status: response.status
      };

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error("❌ Error retrieving Kaizens:", errorMessage);
      setError(errorMessage);
      
      return {
        success: false,
        error: errorMessage
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // Actions
    createKaizen,
    createZazenSession,
    getUserKaizens,
    clearError,
    
    // State
    isLoading,
    error,
    
    // Utils
    apiBaseUrl: API_BASE_URL
  };
};

export default useDojoApi;