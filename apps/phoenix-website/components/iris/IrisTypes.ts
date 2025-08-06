// 🤖 IRIS TYPES - Interfaces TypeScript pour Phoenix Website
export interface IrisMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  app_context?: string;
}

export interface IrisResponse {
  reply: string;
  status: 'success' | 'auth_error' | 'quota_exceeded' | 'rate_limited' | 'access_denied' | 'service_unavailable' | 'error';
  app_context?: string;
  suggestions?: string[];
  rate_limit_remaining?: number;
}

export interface IrisConfig {
  apiUrl: string;
  appContext: 'phoenix-letters' | 'phoenix-cv' | 'phoenix-rise' | 'phoenix-website';
  timeout: number;
}

export interface IrisUser {
  id: string;
  email: string;
  tier: 'FREE' | 'PREMIUM' | 'ENTERPRISE';
  messagesRemaining?: number;
}