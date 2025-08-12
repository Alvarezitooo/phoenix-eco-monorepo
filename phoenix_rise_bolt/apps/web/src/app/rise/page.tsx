'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { MoodChart } from '@/components/dashboard/mood-chart';
import { RecentEntries } from '@/components/dashboard/recent-entries';
import { RitualSuggestion } from '@/components/dashboard/ritual-suggestion';
import { NotificationPanel } from '@/components/dashboard/notification-panel';
import { Heart, BookOpen, Brain, TrendingUp, Zap, Briefcase } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { data: insights, isLoading } = useQuery({
    queryKey: ['insights', 'dashboard'],
    queryFn: () => api.insights.dashboard(),
  });

  const { data: moodData } = useQuery({
    queryKey: ['mood', 'weekly'],
    queryFn: () => api.mood.weekly(),
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 space-y-8">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="pb-2">
                <div className="h-4 bg-muted rounded w-3/4"></div>
                <div className="h-6 bg-muted rounded w-1/2 mt-2"></div>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">
          Rise Dashboard
        </h1>
        <p className="text-muted-foreground">
          Écris la version honnête. C'est pour toi.
        </p>
      </div>

      {/* Notifications */}
      <NotificationPanel />

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Humeur moyenne
            </CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {insights?.mood_average?.toFixed(1) || '0'}/5
            </div>
            <p className="text-xs text-muted-foreground">
              Cette semaine
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Entrées journal
            </CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {insights?.journal_count || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Cette semaine
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Sessions Zazen
            </CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {insights?.zazen_count || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {insights?.zazen_streak || 0} jours de suite
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Momentum
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center gap-2">
              <Zap className="h-5 w-5 text-accent" />
              {insights?.momentum_score || 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              Score global
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Mood Chart */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Évolution de l'humeur</CardTitle>
              <CardDescription>
                Derniers 7 jours
              </CardDescription>
            </CardHeader>
            <CardContent>
              <MoodChart data={moodData} />
            </CardContent>
          </Card>

          {/* Recent Journal Entries */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Entrées récentes</CardTitle>
                <CardDescription>
                  Tes 3 dernières réflexions
                </CardDescription>
              </div>
              <Button asChild variant="outline" size="sm">
                <Link href="/rise/journal">
                  Voir tout
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              <RecentEntries />
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Rituals */}
        <div className="space-y-6">
          <RitualSuggestion />
          
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions rapides</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button asChild className="w-full" variant="outline">
                <Link href="/rise/journal">
                  <BookOpen className="h-4 w-4 mr-2" />
                  Nouvelle entrée
                </Link>
              </Button>
              <Button asChild className="w-full" variant="outline">
                <Link href="/rise/dojo">
                  <Brain className="h-4 w-4 mr-2" />
                  Rituel Zazen
                </Link>
              </Button>
              <Button asChild className="w-full" variant="outline">
                <Link href="/rise/analytics">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Analytics
                </Link>
              </Button>
              <Button asChild className="w-full" variant="outline">
                <Link href="/rise/interview">
                  <Briefcase className="h-4 w-4 mr-2" />
                  Préparation entretien
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}