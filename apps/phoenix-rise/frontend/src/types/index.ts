// Types pour Phoenix Rise Frontend
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  isPremium: boolean;
  createdAt: string;
}

export interface KaizenEntry {
  id?: number;
  user_id: string;
  action: string;
  date: string;
  completed: boolean;
  created_at?: string;
}

export interface ZazenSession {
  id?: number;
  user_id: string;
  timestamp: string;
  duration: number;
  triggered_by?: string;
  notes?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  status?: number;
}

export interface DojoStats {
  totalKaizens: number;
  completedKaizens: number;
  totalZazenMinutes: number;
  streak: number;
  averageSessionDuration: number;
}

export interface JournalEntry {
  id?: number;
  user_id: string;
  content: string;
  mood_score: number;
  created_at: string;
  tags?: string[];
}

export interface RenaissanceState {
  currentPhase: 'awakening' | 'exploration' | 'transformation' | 'integration';
  progress: number;
  insights: string[];
  challenges: string[];
  nextSteps: string[];
}