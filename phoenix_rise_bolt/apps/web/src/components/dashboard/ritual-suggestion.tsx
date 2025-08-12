import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { Brain, Clock, Zap } from 'lucide-react';
import Link from 'next/link';

export function RitualSuggestion() {
  const { data: rituals } = useQuery({
    queryKey: ['zazen', 'rituals'],
    queryFn: () => api.zazen.rituals(),
  });

  const { data: insights } = useQuery({
    queryKey: ['insights', 'today'],
    queryFn: () => api.insights.today(),
  });

  // Suggest ritual based on recent mood/journal content
  const suggestedRitual = rituals?.[0] || {
    id: 'legitimacy',
    name: 'Légitimité',
    description: 'Bâtir sa légitimité intérieure',
    duration: 10,
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          Rituel suggéré
        </CardTitle>
        <CardDescription>
          Basé sur vos dernières réflexions
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="p-4 bg-primary/5 rounded-lg border border-primary/10">
          <h3 className="font-semibold text-primary mb-2">
            {suggestedRitual.name}
          </h3>
          <p className="text-sm text-muted-foreground mb-3">
            {suggestedRitual.description}
          </p>
          
          <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {suggestedRitual.duration} min
            </div>
            <div className="flex items-center gap-1">
              <Zap className="h-3 w-3" />
              4-4-6 respiration
            </div>
          </div>
          
          <Button asChild className="w-full" size="sm">
            <Link href="/rise/dojo">
              Commencer le rituel
            </Link>
          </Button>
        </div>

        <div className="space-y-2">
          <h4 className="text-sm font-medium">Pourquoi ce rituel ?</h4>
          <div className="flex flex-wrap gap-1">
            <Badge variant="outline" className="text-xs">
              Légitimité détectée
            </Badge>
            <Badge variant="outline" className="text-xs">
              Humeur: 4/5
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground">
            Votre journal récent mentionne des questions de légitimité. 
            Ce rituel vous aidera à renforcer votre confiance intérieure.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}