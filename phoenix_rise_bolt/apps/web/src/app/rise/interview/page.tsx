'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Briefcase, 
  Target, 
  MessageSquare, 
  CheckCircle, 
  Clock, 
  Star,
  ArrowRight,
  Play,
  BookOpen,
  Users,
  TrendingUp,
  Settings,
  Zap,
  Brain,
  ArrowLeft
} from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';

export default function InterviewPreparationPage() {
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [showCustomConfig, setShowCustomConfig] = useState(false);
  const [customConfig, setCustomConfig] = useState({
    targetRole: '',
    company: '',
    experience: '',
    challenges: [] as string[],
  });

  // Mock data for interview preparation
  const interviewScenarios = [
    {
      id: 'tech-transition',
      title: 'Reconversion vers le Tech',
      description: 'Questions spécifiques pour une transition vers les métiers du numérique',
      difficulty: 'Intermédiaire',
      duration: '15 min',
      questions: 12,
      color: 'bg-primary/10 border-primary/20',
    },
    {
      id: 'management',
      title: 'Évolution vers le Management',
      description: 'Préparez-vous aux questions de leadership et gestion d\'équipe',
      difficulty: 'Avancé',
      duration: '20 min',
      questions: 15,
      color: 'bg-secondary/10 border-secondary/20',
    },
    {
      id: 'startup',
      title: 'Intégrer une Startup',
      description: 'Questions sur l\'adaptabilité et l\'esprit entrepreneurial',
      difficulty: 'Débutant',
      duration: '12 min',
      questions: 10,
      color: 'bg-accent/10 border-accent/20',
    },
    {
      id: 'custom',
      title: 'Scénario Personnalisé',
      description: 'Créez votre simulation sur mesure basée sur votre profil Phoenix (CV, Letters, Aube)',
      difficulty: 'Sur mesure',
      duration: 'Variable',
      questions: 'Personnalisé',
      color: 'bg-gradient-to-r from-primary/10 to-secondary/10 border-primary/30',
    },
  ];

  const mockQuestions = [
    {
      id: 1,
      question: "Pourquoi avez-vous choisi de vous reconvertir dans ce domaine ?",
      tips: [
        "Montrez votre passion et votre motivation intrinsèque",
        "Reliez vos expériences passées à ce nouveau domaine",
        "Démontrez que c'est un choix réfléchi, pas une fuite"
      ],
      keywords: ["passion", "évolution", "compétences transférables"]
    },
    {
      id: 2,
      question: "Comment vos expériences précédentes vous préparent-elles à ce poste ?",
      tips: [
        "Identifiez les compétences transférables",
        "Donnez des exemples concrets",
        "Montrez votre capacité d'adaptation"
      ],
      keywords: ["compétences", "expérience", "adaptation"]
    }
  ];

  const customQuestions = [
    {
      id: 1,
      question: `Pourquoi souhaitez-vous rejoindre ${customConfig.company || '[Entreprise]'} en tant que ${customConfig.targetRole || '[Poste]'} ?`,
      phoenixContext: "Basé sur votre profil Phoenix CV et vos motivations détectées dans Phoenix Letters",
      tips: [
        "Connectez vos valeurs personnelles aux valeurs de l'entreprise",
        "Montrez votre connaissance approfondie de l'entreprise",
        "Expliquez comment ce poste s'inscrit dans votre projet professionnel"
      ],
      keywords: ["motivation", "valeurs", "projet professionnel", "entreprise"]
    },
    {
      id: 2,
      question: "Comment votre parcours atypique est-il un atout pour ce poste ?",
      phoenixContext: "Analyse de votre parcours Phoenix CV - Reconversion détectée",
      tips: [
        "Transformez votre différence en force",
        "Donnez des exemples concrets de compétences transférables",
        "Montrez votre capacité d'adaptation et d'apprentissage"
      ],
      keywords: ["parcours atypique", "compétences transférables", "adaptabilité", "apprentissage"]
    },
    {
      id: 3,
      question: "Comment gérez-vous le syndrome de l'imposteur dans cette transition ?",
      phoenixContext: "Détecté dans vos réflexions Phoenix Rise - Travail sur la légitimité",
      tips: [
        "Reconnaissez le sentiment sans le minimiser",
        "Montrez votre travail de développement personnel",
        "Donnez des exemples de défis surmontés"
      ],
      keywords: ["légitimité", "développement personnel", "confiance", "défis"]
    }
  ];

  const recentPreparations = [
    {
      id: '1',
      scenario: 'Reconversion vers le Tech',
      score: 85,
      completed_at: '2025-01-27T10:30:00Z',
      duration: '14 min',
    },
    {
      id: '2',
      scenario: 'Évolution vers le Management',
      score: 78,
      completed_at: '2025-01-26T16:45:00Z',
      duration: '18 min',
    },
  ];

  const startScenario = (scenarioId: string) => {
    if (scenarioId === 'custom') {
      setShowCustomConfig(true);
      return;
    }
    setSelectedScenario(scenarioId);
    setCurrentQuestion(0);
    toast.success('Simulation démarrée !');
  };

  const startCustomScenario = () => {
    if (!customConfig.targetRole || !customConfig.company) {
      toast.error('Veuillez remplir au minimum le poste et l\'entreprise');
      return;
    }
    setSelectedScenario('custom-configured');
    setCurrentQuestion(0);
    setShowCustomConfig(false);
    toast.success(`Simulation personnalisée démarrée pour ${customConfig.targetRole} chez ${customConfig.company} !`);
  };

  const toggleChallenge = (challenge: string) => {
    setCustomConfig(prev => ({
      ...prev,
      challenges: prev.challenges.includes(challenge)
        ? prev.challenges.filter(c => c !== challenge)
        : [...prev.challenges, challenge]
    }));
  };

  const nextQuestion = () => {
    const totalQuestions = selectedScenario === 'custom-configured' 
      ? customQuestions.length 
      : mockQuestions.length;
    
    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion(currentQuestion + 1);
      toast.success('Question suivante !');
    } else {
      // Simulation terminée
      const score = Math.floor(Math.random() * 20) + 75; // Score entre 75-95
      toast.success(`Simulation terminée ! Score: ${score}%`);
      setSelectedScenario(null);
      setShowCustomConfig(false);
      setCurrentQuestion(0);
    }
  };

  const previousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const resetSimulation = () => {
    setSelectedScenario(null);
    setShowCustomConfig(false);
    setCurrentQuestion(0);
    setCustomConfig({
      targetRole: '',
      company: '',
      experience: '',
      challenges: [],
    });
  };

  // Configuration personnalisée
  if (showCustomConfig) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-6">
          {/* Header */}
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="p-3 rounded-full bg-gradient-to-r from-primary/20 to-secondary/20">
                <Settings className="h-8 w-8 text-primary" />
              </div>
            </div>
            <h1 className="text-3xl font-bold tracking-tight">
              Configuration Personnalisée
            </h1>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Créons ensemble votre simulation d'entretien sur mesure en utilisant vos données Phoenix
            </p>
          </div>

          {/* Phoenix Integration */}
          <Card className="bg-gradient-to-r from-primary/5 to-secondary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-primary" />
                Intégration Écosystème Phoenix
              </CardTitle>
              <CardDescription>
                Nous analysons vos données pour personnaliser l'entretien
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center p-4 bg-white/50 rounded-lg">
                  <div className="w-12 h-12 mx-auto mb-2 bg-primary/10 rounded-full flex items-center justify-center">
                    <Briefcase className="h-6 w-6 text-primary" />
                  </div>
                  <h4 className="font-semibold text-sm">Phoenix CV</h4>
                  <p className="text-xs text-muted-foreground">Analyse de votre parcours</p>
                </div>
                <div className="text-center p-4 bg-white/50 rounded-lg">
                  <div className="w-12 h-12 mx-auto mb-2 bg-secondary/10 rounded-full flex items-center justify-center">
                    <MessageSquare className="h-6 w-6 text-secondary" />
                  </div>
                  <h4 className="font-semibold text-sm">Phoenix Letters</h4>
                  <p className="text-xs text-muted-foreground">Motivations détectées</p>
                </div>
                <div className="text-center p-4 bg-white/50 rounded-lg">
                  <div className="w-12 h-12 mx-auto mb-2 bg-accent/10 rounded-full flex items-center justify-center">
                    <Target className="h-6 w-6 text-accent" />
                  </div>
                  <h4 className="font-semibold text-sm">Phoenix Aube</h4>
                  <p className="text-xs text-muted-foreground">Métier cible identifié</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Configuration Form */}
          <Card>
            <CardHeader>
              <CardTitle>Paramètres de l'entretien</CardTitle>
              <CardDescription>
                Personnalisez votre simulation selon votre situation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Poste visé *
                  </label>
                  <input
                    type="text"
                    placeholder="ex: Développeur Full-Stack"
                    value={customConfig.targetRole}
                    onChange={(e) => setCustomConfig(prev => ({ ...prev, targetRole: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    Entreprise cible *
                  </label>
                  <input
                    type="text"
                    placeholder="ex: Phoenix Tech"
                    value={customConfig.company}
                    onChange={(e) => setCustomConfig(prev => ({ ...prev, company: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">
                  Niveau d'expérience
                </label>
                <select
                  value={customConfig.experience}
                  onChange={(e) => setCustomConfig(prev => ({ ...prev, experience: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">Sélectionnez votre niveau</option>
                  <option value="junior">Junior (0-2 ans)</option>
                  <option value="intermediate">Intermédiaire (2-5 ans)</option>
                  <option value="senior">Senior (5+ ans)</option>
                  <option value="reconversion">En reconversion</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium mb-3 block">
                  Défis à travailler (optionnel)
                </label>
                <div className="grid gap-2 md:grid-cols-2">
                  {[
                    'Légitimité professionnelle',
                    'Transition de carrière',
                    'Syndrome de l\'imposteur',
                    'Communication',
                    'Leadership',
                    'Gestion du stress'
                  ].map((challenge) => (
                    <label key={challenge} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={customConfig.challenges.includes(challenge)}
                        onChange={() => toggleChallenge(challenge)}
                        className="rounded border-gray-300"
                      />
                      <span className="text-sm">{challenge}</span>
                    </label>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Phoenix Insights */}
          <Card className="bg-gradient-to-r from-secondary/5 to-accent/5 border-secondary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-secondary" />
                Insights Phoenix
              </CardTitle>
              <CardDescription>
                Analyse de votre profil pour l'entretien
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <h4 className="font-semibold text-secondary mb-2">Points forts détectés</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Parcours riche et diversifié</li>
                    <li>• Capacité d'adaptation prouvée</li>
                    <li>• Motivation forte pour la reconversion</li>
                    <li>• Travail sur le développement personnel</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-accent mb-2">Axes d'amélioration</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Renforcer la confiance en soi</li>
                    <li>• Structurer le discours de transition</li>
                    <li>• Préparer des exemples concrets</li>
                    <li>• Travailler la légitimité</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={() => setShowCustomConfig(false)}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour aux scénarios
            </Button>
            <Button
              onClick={startCustomScenario}
              disabled={!customConfig.targetRole || !customConfig.company}
              className="px-8"
            >
              <Play className="h-4 w-4 mr-2" />
              Lancer ma simulation
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Simulation en cours
  if (selectedScenario) {
    const isCustom = selectedScenario === 'custom-configured';
    const questions = isCustom ? customQuestions : mockQuestions;
    const currentQ = questions[currentQuestion];
    
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="border-primary/20">
          <CardHeader className="text-center">
            {isCustom && (
              <Badge variant="outline" className="mb-2 mx-auto">
                🚀 Simulation Phoenix Personnalisée
              </Badge>
            )}
            <CardTitle className="text-2xl">
              {isCustom 
                ? `Entretien ${customConfig.targetRole} - ${customConfig.company}` 
                : 'Simulation d\'entretien en cours'
              }
            </CardTitle>
            <CardDescription>
              Question {currentQuestion + 1} sur {questions.length}
            </CardDescription>
            <div className="w-full bg-muted rounded-full h-2 mt-4">
              <div 
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
              ></div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center p-6 bg-muted/50 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">
                {currentQ?.question}
              </h3>
              
              <div className="space-y-4">
                {isCustom && currentQ?.phoenixContext && (
                  <div className="text-left p-3 bg-primary/5 rounded-lg border border-primary/20">
                    <h4 className="font-medium text-primary mb-1 flex items-center gap-2">
                      <span className="text-sm">🔮</span>
                      Context Phoenix
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      {currentQ.phoenixContext}
                    </p>
                  </div>
                )}
                
                <div className="text-left">
                  <h4 className="font-medium text-primary mb-2">💡 Conseils :</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {currentQ?.tips?.map((tip, index) => (
                      <li key={index}>• {tip}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="text-left">
                  <h4 className="font-medium text-secondary mb-2">🔑 Mots-clés à utiliser :</h4>
                  <div className="flex flex-wrap gap-2">
                    {currentQ?.keywords?.map((keyword) => (
                      <Badge key={keyword} variant="outline" className="text-xs">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <Button 
                variant="outline"
                onClick={previousQuestion}
                disabled={currentQuestion === 0}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Question précédente
              </Button>
              
              <div className="flex gap-2">
                <Button variant="ghost">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Enregistrer ma réponse
                </Button>
                <Button onClick={nextQuestion}>
                  {currentQuestion < questions.length - 1 ? 'Question suivante' : 'Terminer'}
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>

            <div className="text-center">
              <Button variant="ghost" size="sm" onClick={resetSimulation}>
                Abandonner la simulation
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Page principale
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="p-3 rounded-full bg-primary/10">
            <Briefcase className="h-8 w-8 text-primary" />
          </div>
        </div>
        <h1 className="text-3xl font-bold tracking-tight">
          Préparation à l'Entretien
        </h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Préparez-vous aux entretiens de reconversion avec des simulations personnalisées. 
          Développez votre confiance et vos arguments clés pour réussir cette étape cruciale.
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4 text-center">
            <Target className="h-8 w-8 mx-auto mb-2 text-primary" />
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">Simulations complétées</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <TrendingUp className="h-8 w-8 mx-auto mb-2 text-secondary" />
            <div className="text-2xl font-bold">82%</div>
            <p className="text-xs text-muted-foreground">Score moyen</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <Clock className="h-8 w-8 mx-auto mb-2 text-accent" />
            <div className="text-2xl font-bold">3h</div>
            <p className="text-xs text-muted-foreground">Temps de pratique</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <Star className="h-8 w-8 mx-auto mb-2 text-warning-500" />
            <div className="text-2xl font-bold">7</div>
            <p className="text-xs text-muted-foreground">Jours de streak</p>
          </CardContent>
        </Card>
      </div>

      {/* Scenario Selection */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold">Choisissez votre scénario</h2>
          <Badge variant="outline" className="text-xs">
            Personnalisé selon votre profil
          </Badge>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2">
          {interviewScenarios.map((scenario) => (
            <Card key={scenario.id} className={`hover:shadow-lg transition-all cursor-pointer ${scenario.color}`}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>{scenario.title}</span>
                  <Badge variant="secondary" className="text-xs">
                    {scenario.difficulty}
                  </Badge>
                </CardTitle>
                <CardDescription>
                  {scenario.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {scenario.duration}
                  </div>
                  <div className="flex items-center gap-1">
                    <MessageSquare className="h-4 w-4" />
                    {scenario.questions} questions
                  </div>
                </div>
                
                <Button 
                  onClick={() => startScenario(scenario.id)}
                  className="w-full"
                  variant={scenario.id === 'custom' ? 'default' : 'default'}
                >
                  <Play className="h-4 w-4 mr-2" />
                  {scenario.id === 'custom' ? 'Paramétrer mon entretien' : 'Commencer la simulation'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Quick Tips */}
      <Card className="bg-gradient-to-r from-primary/5 to-secondary/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            Conseils pour réussir
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <h4 className="font-semibold text-primary">Avant l'entretien</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Recherchez l'entreprise et ses valeurs</li>
                <li>• Préparez vos exemples STAR</li>
                <li>• Entraînez-vous à haute voix</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-secondary">Pendant l'entretien</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Écoutez activement les questions</li>
                <li>• Donnez des exemples concrets</li>
                <li>• Posez des questions pertinentes</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Sessions */}
      {recentPreparations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-primary" />
              Dernières simulations
            </CardTitle>
            <CardDescription>
              Vos performances récentes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentPreparations.map((session) => (
                <div key={session.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      session.score >= 80 ? 'bg-success-500' : 
                      session.score >= 60 ? 'bg-warning-500' : 'bg-error-500'
                    }`}></div>
                    <div>
                      <p className="font-medium">{session.scenario}</p>
                      <p className="text-sm text-muted-foreground">
                        {session.duration} • Score: {session.score}%
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    Revoir
                    <ArrowRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}