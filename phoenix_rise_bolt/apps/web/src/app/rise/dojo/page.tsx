'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { formatDuration } from '@/lib/utils';
import { Brain, Clock, Zap, Play, Pause, RotateCcw, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

interface ZazenSession {
  id: string;
  ritual_id: string;
  topic: string;
  duration_minutes: number;
  started_at: string;
  is_completed: boolean;
}

export default function DojoPage() {
  const [activeSession, setActiveSession] = useState<ZazenSession | null>(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [breathPhase, setBreathPhase] = useState<'inhale' | 'hold' | 'exhale'>('inhale');
  const [breathCount, setBreathCount] = useState(0);
  
  const queryClient = useQueryClient();

  const { data: rituals, isLoading } = useQuery({
    queryKey: ['zazen', 'rituals'],
    queryFn: () => api.zazen.rituals(),
  });

  const { data: recentSessions } = useQuery({
    queryKey: ['zazen', 'sessions'],
    queryFn: () => api.zazen.sessions(),
  });

  const startSessionMutation = useMutation({
    mutationFn: (data: any) => api.zazen.start(data),
    onSuccess: (session) => {
      setActiveSession(session);
      setTimeLeft(session.duration_minutes * 60);
      toast.success('Session démarrée !');
    },
  });

  const completeSessionMutation = useMutation({
    mutationFn: (data: any) => api.zazen.complete(activeSession?.id || '', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['zazen'] });
      setActiveSession(null);
      setIsRunning(false);
      setTimeLeft(0);
      toast.success('Session terminée ! Bien joué 🧘‍♂️');
    },
  });

  const startRitual = (ritual: any) => {
    startSessionMutation.mutate({
      ritual_id: ritual.id,
      topic: ritual.name,
      duration_minutes: ritual.duration,
    });
  };

  const toggleTimer = () => {
    setIsRunning(!isRunning);
  };

  const resetTimer = () => {
    if (activeSession) {
      setTimeLeft(activeSession.duration_minutes * 60);
      setIsRunning(false);
      setBreathCount(0);
    }
  };

  const completeSession = () => {
    if (activeSession) {
      completeSessionMutation.mutate({
        focus_rating: 4,
        post_session_mood: 4,
        notes: 'Session complétée via l\'interface',
      });
    }
  };

  // Timer effect
  React.useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            setIsRunning(false);
            toast.success('Temps écoulé ! Session terminée.');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isRunning, timeLeft]);

  // Breathing guide effect
  React.useEffect(() => {
    if (!isRunning) return;

    const breathingCycle = () => {
      // 4-4-6 pattern (4s inhale, 4s hold, 6s exhale)
      const phases = [
        { phase: 'inhale', duration: 4000 },
        { phase: 'hold', duration: 4000 },
        { phase: 'exhale', duration: 6000 },
      ];

      let currentPhaseIndex = 0;
      
      const nextPhase = () => {
        setBreathPhase(phases[currentPhaseIndex].phase as any);
        
        setTimeout(() => {
          currentPhaseIndex = (currentPhaseIndex + 1) % phases.length;
          if (currentPhaseIndex === 0) {
            setBreathCount(prev => prev + 1);
          }
          nextPhase();
        }, phases[currentPhaseIndex].duration);
      };

      nextPhase();
    };

    breathingCycle();
  }, [isRunning]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          <div className="animate-pulse">
            <div className="h-8 bg-muted rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-muted rounded w-2/3"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">
          Dojo Mental
        </h1>
        <p className="text-muted-foreground">
          Rituels Zazen pour cultiver légitimité, clarté et courage
        </p>
      </div>

      {/* Active Session */}
      {activeSession ? (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">
              {activeSession.topic}
            </CardTitle>
            <CardDescription>
              Session en cours • Respiration 4-4-6
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Timer */}
            <div className="text-center">
              <div className="text-6xl font-mono font-bold text-primary mb-4">
                {formatTime(timeLeft)}
              </div>
              <div className="text-sm text-muted-foreground">
                {breathCount} cycles de respiration
              </div>
            </div>

            {/* Breathing Guide */}
            <div className="text-center space-y-4">
              <div className={`w-32 h-32 mx-auto rounded-full border-4 transition-all duration-1000 ${
                breathPhase === 'inhale' ? 'border-primary bg-primary/20 scale-110' :
                breathPhase === 'hold' ? 'border-secondary bg-secondary/20 scale-105' :
                'border-accent bg-accent/20 scale-95'
              }`}>
                <div className="flex items-center justify-center h-full">
                  <span className="text-lg font-semibold capitalize">
                    {breathPhase === 'inhale' ? 'Inspirez' :
                     breathPhase === 'hold' ? 'Retenez' : 'Expirez'}
                  </span>
                </div>
              </div>
              
              <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                <div className={`w-2 h-2 rounded-full ${breathPhase === 'inhale' ? 'bg-primary' : 'bg-muted'}`}></div>
                <div className={`w-2 h-2 rounded-full ${breathPhase === 'hold' ? 'bg-secondary' : 'bg-muted'}`}></div>
                <div className={`w-2 h-2 rounded-full ${breathPhase === 'exhale' ? 'bg-accent' : 'bg-muted'}`}></div>
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center justify-center gap-4">
              <Button
                onClick={toggleTimer}
                size="lg"
                className="px-8"
              >
                {isRunning ? (
                  <>
                    <Pause className="h-5 w-5 mr-2" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5 mr-2" />
                    {timeLeft === activeSession.duration_minutes * 60 ? 'Commencer' : 'Reprendre'}
                  </>
                )}
              </Button>
              
              <Button variant="outline" onClick={resetTimer}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset
              </Button>
              
              <Button variant="outline" onClick={completeSession}>
                <CheckCircle className="h-4 w-4 mr-2" />
                Terminer
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        /* Ritual Selection */
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {rituals?.map((ritual: any) => (
            <Card key={ritual.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-primary" />
                  {ritual.name}
                </CardTitle>
                <CardDescription>
                  {ritual.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {ritual.duration} min
                  </div>
                  <div className="flex items-center gap-1">
                    <Zap className="h-4 w-4" />
                    {ritual.breathing_pattern}
                  </div>
                </div>
                
                <Button
                  onClick={() => startRitual(ritual)}
                  disabled={startSessionMutation.isPending}
                  className="w-full"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Commencer
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Recent Sessions */}
      {recentSessions && recentSessions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Sessions récentes</CardTitle>
            <CardDescription>
              Vos dernières pratiques Zazen
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentSessions.slice(0, 5).map((session: any) => (
                <div key={session.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-success-500"></div>
                    <div>
                      <p className="font-medium">{session.topic}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDuration(session.duration_minutes)} • Focus: {session.focus_rating}/5
                      </p>
                    </div>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    Terminé
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}