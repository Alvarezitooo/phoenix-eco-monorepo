export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  isPremium: boolean;
  hasCompletedDiagnosis: boolean;
}

export interface DiagnosticQuestion {
  id: string;
  category: 'bigfive' | 'riasec';
  dimension: string;
  question: string;
  type: 'scale' | 'choice';
  options?: string[];
}

export interface DiagnosticResponse {
  questionId: string;
  value: number;
}

export interface AspirationProfile {
  bigFive: {
    openness: number;
    conscientiousness: number;
    extraversion: number;
    agreeableness: number;
    neuroticism: number;
  };
  riasec: {
    realistic: number;
    investigative: number;
    artistic: number;
    social: number;
    enterprising: number;
    conventional: number;
  };
  dominantTraits: string[];
  personalityInsights: string[];
}

export interface CareerPath {
  id: string;
  title: string;
  description: string;
  aiResilienceScore: number;
  matchScore: number;
  keySkills: string[];
  growthOutlook: 'high' | 'medium' | 'low';
  salaryRange: string;
  requiredEducation: string;
  workEnvironment: string;
}