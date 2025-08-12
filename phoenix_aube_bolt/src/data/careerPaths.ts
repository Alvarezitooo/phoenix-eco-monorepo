import { CareerPath } from '../types';

export const generateCareerPaths = (): CareerPath[] => [
  {
    id: '1',
    title: 'UX/UI Designer',
    description: 'Concevoir des interfaces utilisateur intuitives et créer des expériences numériques exceptionnelles en alliant créativité et analyse comportementale.',
    aiResilienceScore: 85,
    matchScore: 92,
    keySkills: ['Design thinking', 'Prototypage', 'Recherche utilisateur', 'Figma', 'Adobe Creative Suite'],
    growthOutlook: 'high',
    salaryRange: '35k - 65k €',
    requiredEducation: 'Formation courte spécialisée ou reconversion',
    workEnvironment: 'Startup tech, agences digitales, équipes produit'
  },
  {
    id: '2',
    title: 'Data Analyst',
    description: 'Transformer les données en insights stratégiques pour éclairer les décisions business et créer de la valeur à partir de l\'information.',
    aiResilienceScore: 78,
    matchScore: 88,
    keySkills: ['Python/R', 'SQL', 'Visualisation de données', 'Statistiques', 'Business Intelligence'],
    growthOutlook: 'high',
    salaryRange: '40k - 70k €',
    requiredEducation: 'Bootcamp ou formation en ligne intensive',
    workEnvironment: 'Entreprises data-driven, consultanting, scale-ups'
  },
  {
    id: '3',
    title: 'Chef de Projet Digital',
    description: 'Orchestrer des projets numériques en coordonnant équipes techniques et business pour livrer des solutions innovantes.',
    aiResilienceScore: 90,
    matchScore: 86,
    keySkills: ['Gestion de projet', 'Agilité', 'Communication', 'Leadership', 'Outils collaboratifs'],
    growthOutlook: 'high',
    salaryRange: '45k - 75k €',
    requiredEducation: 'Certification PMP ou formation courte',
    workEnvironment: 'ESN, entreprises en transformation, startups'
  }
];