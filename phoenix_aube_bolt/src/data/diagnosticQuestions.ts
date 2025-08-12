import { DiagnosticQuestion } from '../types';

export const diagnosticQuestions: DiagnosticQuestion[] = [
  // Big Five Questions
  {
    id: 'bf_o_1',
    category: 'bigfive',
    dimension: 'openness',
    question: 'J\'aime explorer de nouvelles idées et expériences',
    type: 'scale'
  },
  {
    id: 'bf_o_2',
    category: 'bigfive',
    dimension: 'openness',
    question: 'Je préfère les routines établies aux changements',
    type: 'scale'
  },
  {
    id: 'bf_c_1',
    category: 'bigfive',
    dimension: 'conscientiousness',
    question: 'Je suis très organisé(e) dans mon travail',
    type: 'scale'
  },
  {
    id: 'bf_c_2',
    category: 'bigfive',
    dimension: 'conscientiousness',
    question: 'J\'ai tendance à remettre les choses à plus tard',
    type: 'scale'
  },
  {
    id: 'bf_e_1',
    category: 'bigfive',
    dimension: 'extraversion',
    question: 'J\'aime être entouré(e) de beaucoup de monde',
    type: 'scale'
  },
  {
    id: 'bf_e_2',
    category: 'bigfive',
    dimension: 'extraversion',
    question: 'Je préfère les activités calmes aux activités stimulantes',
    type: 'scale'
  },
  {
    id: 'bf_a_1',
    category: 'bigfive',
    dimension: 'agreeableness',
    question: 'Je fais confiance aux autres facilement',
    type: 'scale'
  },
  {
    id: 'bf_a_2',
    category: 'bigfive',
    dimension: 'agreeableness',
    question: 'J\'aime aider les autres, même si cela me coûte',
    type: 'scale'
  },
  {
    id: 'bf_n_1',
    category: 'bigfive',
    dimension: 'neuroticism',
    question: 'Je me sens souvent stressé(e) ou anxieux(se)',
    type: 'scale'
  },
  {
    id: 'bf_n_2',
    category: 'bigfive',
    dimension: 'neuroticism',
    question: 'Je reste calme même dans les situations difficiles',
    type: 'scale'
  },
  
  // RIASEC Questions
  {
    id: 'r_1',
    category: 'riasec',
    dimension: 'realistic',
    question: 'Travailler avec mes mains et créer des objets concrets',
    type: 'scale'
  },
  {
    id: 'r_2',
    category: 'riasec',
    dimension: 'realistic',
    question: 'Utiliser des outils et des machines dans mon travail',
    type: 'scale'
  },
  {
    id: 'i_1',
    category: 'riasec',
    dimension: 'investigative',
    question: 'Résoudre des problèmes complexes et analyser des données',
    type: 'scale'
  },
  {
    id: 'i_2',
    category: 'riasec',
    dimension: 'investigative',
    question: 'Mener des recherches et découvrir de nouvelles connaissances',
    type: 'scale'
  },
  {
    id: 'a_1',
    category: 'riasec',
    dimension: 'artistic',
    question: 'Exprimer ma créativité à travers l\'art ou le design',
    type: 'scale'
  },
  {
    id: 'a_2',
    category: 'riasec',
    dimension: 'artistic',
    question: 'Créer du contenu original et innovant',
    type: 'scale'
  },
  {
    id: 's_1',
    category: 'riasec',
    dimension: 'social',
    question: 'Aider les autres et contribuer à leur bien-être',
    type: 'scale'
  },
  {
    id: 's_2',
    category: 'riasec',
    dimension: 'social',
    question: 'Travailler en équipe et collaborer étroitement',
    type: 'scale'
  },
  {
    id: 'e_1',
    category: 'riasec',
    dimension: 'enterprising',
    question: 'Diriger des projets et prendre des décisions importantes',
    type: 'scale'
  },
  {
    id: 'e_2',
    category: 'riasec',
    dimension: 'enterprising',
    question: 'Convaincre et influencer les autres',
    type: 'scale'
  },
  {
    id: 'c_1',
    category: 'riasec',
    dimension: 'conventional',
    question: 'Organiser et gérer des données de manière structurée',
    type: 'scale'
  },
  {
    id: 'c_2',
    category: 'riasec',
    dimension: 'conventional',
    question: 'Suivre des procédures établies et des règles claires',
    type: 'scale'
  }
];