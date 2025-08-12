'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
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
  TrendingUp
} from 'lucide-react';
import Link from 'next/link';

export default function InterviewPreparationPage() {
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);

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
    setSelectedScenario(scenarioId);
    setCurrentQuestion(0);
  };

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

      {!selectedScenario ? (
        <>
          {/* Scenario Selection */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold">Choisissez votre scénario</h2>
              <Badge variant="outline" className="text-xs">
                Personnalisé selon votre profil
              </Badge>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
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
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Commencer la simulation
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
        </>
      ) : (
        /* Interview Simulation */
        <Card className="max-w-4xl mx-auto">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">
              Simulation d'entretien en cours
            </CardTitle>
            <CardDescription>
              Question {currentQuestion + 1} sur {mockQuestions.length}
            </CardDescription>
            <div className="w-full bg-muted rounded-full h-2 mt-4">
              <div 
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentQuestion + 1) / mockQuestions.length) * 100}%` }}
              ></div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center p-6 bg-muted/50 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">
                {mockQuestions[currentQuestion]?.question}
              </h3>
              
              <div className="space-y-4">
                <div className="text-left">
                  <h4 className="font-medium text-primary mb-2">💡 Conseils :</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {mockQuestions[currentQuestion]?.tips.map((tip, index) => (
                      <li key={index}>• {tip}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="text-left">
                  <h4 className="font-medium text-secondary mb-2">🔑 Mots-clés à utiliser :</h4>
                  <div className="flex flex-wrap gap-2">
                    {mockQuestions[currentQuestion]?.keywords.map((keyword) => (
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
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
              >
                Question précédente
              </Button>
              
              <div className="flex gap-2">
                <Button variant="ghost">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Enregistrer ma réponse
                </Button>
                <Button 
                  onClick={() => {
                    if (currentQuestion < mockQuestions.length - 1) {
                      setCurrentQuestion(currentQuestion + 1);
                    } else {
                      // Simulation terminée
                      setSelectedScenario(null);
                    }
                  }}
                >
                  {currentQuestion < mockQuestions.length - 1 ? 'Question suivante' : 'Terminer'}
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}