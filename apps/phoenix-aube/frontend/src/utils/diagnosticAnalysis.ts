import { DiagnosticResponse, AspirationProfile } from '../types';

export const analyzeDiagnosticResponses = (responses: DiagnosticResponse[]): AspirationProfile => {
  // Initialize scores
  const bigFive = {
    openness: 0,
    conscientiousness: 0,
    extraversion: 0,
    agreeableness: 0,
    neuroticism: 0
  };

  const riasec = {
    realistic: 0,
    investigative: 0,
    artistic: 0,
    social: 0,
    enterprising: 0,
    conventional: 0
  };

  // Count responses per dimension
  const counts = {
    bigFive: { openness: 0, conscientiousness: 0, extraversion: 0, agreeableness: 0, neuroticism: 0 },
    riasec: { realistic: 0, investigative: 0, artistic: 0, social: 0, enterprising: 0, conventional: 0 }
  };

  // Process responses
  responses.forEach(response => {
    const questionId = response.questionId;
    const value = response.value;

    // Big Five processing
    if (questionId.startsWith('bf_')) {
      const dimension = questionId.split('_')[1];
      const questionNumber = parseInt(questionId.split('_')[2]);
      
      // Reverse scoring for negative questions
      const adjustedValue = (questionNumber === 2 && (dimension === 'openness' || dimension === 'conscientiousness' || dimension === 'extraversion' || dimension === 'neuroticism')) 
        ? 6 - value 
        : value;

      switch (dimension) {
        case 'o':
          bigFive.openness += adjustedValue;
          counts.bigFive.openness++;
          break;
        case 'c':
          bigFive.conscientiousness += adjustedValue;
          counts.bigFive.conscientiousness++;
          break;
        case 'e':
          bigFive.extraversion += adjustedValue;
          counts.bigFive.extraversion++;
          break;
        case 'a':
          bigFive.agreeableness += adjustedValue;
          counts.bigFive.agreeableness++;
          break;
        case 'n':
          bigFive.neuroticism += adjustedValue;
          counts.bigFive.neuroticism++;
          break;
      }
    }
    // RIASEC processing
    else {
      const dimension = questionId.split('_')[0];
      
      switch (dimension) {
        case 'r':
          riasec.realistic += value;
          counts.riasec.realistic++;
          break;
        case 'i':
          riasec.investigative += value;
          counts.riasec.investigative++;
          break;
        case 'a':
          riasec.artistic += value;
          counts.riasec.artistic++;
          break;
        case 's':
          riasec.social += value;
          counts.riasec.social++;
          break;
        case 'e':
          riasec.enterprising += value;
          counts.riasec.enterprising++;
          break;
        case 'c':
          riasec.conventional += value;
          counts.riasec.conventional++;
          break;
      }
    }
  });

  // Calculate averages and convert to percentages
  Object.keys(bigFive).forEach(key => {
    const typedKey = key as keyof typeof bigFive;
    if (counts.bigFive[typedKey] > 0) {
      bigFive[typedKey] = Math.round((bigFive[typedKey] / counts.bigFive[typedKey] / 5) * 100);
    }
  });

  Object.keys(riasec).forEach(key => {
    const typedKey = key as keyof typeof riasec;
    if (counts.riasec[typedKey] > 0) {
      riasec[typedKey] = Math.round((riasec[typedKey] / counts.riasec[typedKey] / 5) * 100);
    }
  });

  // Identify dominant traits
  const bigFiveEntries = Object.entries(bigFive) as [keyof typeof bigFive, number][];
  const riasecEntries = Object.entries(riasec) as [keyof typeof riasec, number][];
  
  const topBigFive = bigFiveEntries
    .sort(([,a], [,b]) => b - a)
    .slice(0, 2)
    .map(([trait]) => trait);
  
  const topRiasec = riasecEntries
    .sort(([,a], [,b]) => b - a)
    .slice(0, 2)
    .map(([trait]) => trait);

  const traitLabels = {
    openness: 'Créatif',
    conscientiousness: 'Rigoureux',
    extraversion: 'Sociable',
    agreeableness: 'Empathique',
    neuroticism: 'Sensible',
    realistic: 'Pragmatique',
    investigative: 'Analytique',
    artistic: 'Créatif',
    social: 'Altruiste',
    enterprising: 'Leader',
    conventional: 'Organisé'
  };

  const dominantTraits = [
    ...topBigFive.map(trait => traitLabels[trait]),
    ...topRiasec.map(trait => traitLabels[trait])
  ];

  // Generate personality insights
  const personalityInsights = generateInsights(bigFive, riasec);

  return {
    bigFive,
    riasec,
    dominantTraits,
    personalityInsights
  };
};

const generateInsights = (
  bigFive: Record<string, number>, 
  riasec: Record<string, number>
): string[] => {
  const insights: string[] = [];

  // Big Five insights
  if (bigFive.openness > 70) {
    insights.push("Vous êtes naturellement curieux et ouvert aux nouvelles expériences");
  }
  if (bigFive.conscientiousness > 70) {
    insights.push("Votre organisation et votre persévérance sont des atouts majeurs");
  }
  if (bigFive.extraversion > 70) {
    insights.push("Vous tirez votre énergie du contact avec les autres");
  }
  if (bigFive.agreeableness > 70) {
    insights.push("Votre empathie naturelle facilite le travail en équipe");
  }

  // RIASEC insights
  const maxRiasec = Math.max(...Object.values(riasec));
  const dominantRiasec = Object.entries(riasec).find(([, value]) => value === maxRiasec);
  
  if (dominantRiasec) {
    const [type] = dominantRiasec;
    switch (type) {
      case 'artistic':
        insights.push("Votre créativité est votre force motrice principale");
        break;
      case 'social':
        insights.push("Aider et accompagner les autres vous motive profondément");
        break;
      case 'enterprising':
        insights.push("Vous avez un potentiel naturel de leadership");
        break;
      case 'investigative':
        insights.push("Résoudre des problèmes complexes vous stimule");
        break;
    }
  }

  return insights;
};