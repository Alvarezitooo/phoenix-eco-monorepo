import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { formatDate, moodToEmoji } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { BookOpen } from 'lucide-react';

export function RecentEntries() {
  const { data: entries, isLoading } = useQuery({
    queryKey: ['journal', 'recent'],
    queryFn: () => api.journal.list(),
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse">
            <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-muted rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  const recentEntries = entries?.slice(0, 3) || [];

  if (recentEntries.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p>Aucune entrée pour le moment</p>
        <p className="text-sm">Commencez votre premier journal !</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {recentEntries.map((entry: any) => (
        <div key={entry.id} className="border-l-2 border-primary/20 pl-4 hover:border-primary/40 transition-colors">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <h4 className="font-medium truncate">
                {entry.title || 'Sans titre'}
              </h4>
              <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                {entry.content}
              </p>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-xs text-muted-foreground">
                  {formatDate(entry.created_at)}
                </span>
                {entry.mood && (
                  <span className="text-sm">
                    {moodToEmoji(entry.mood)}
                  </span>
                )}
                <span className="text-xs text-muted-foreground">
                  {entry.word_count} mots
                </span>
              </div>
            </div>
          </div>
          {entry.tags && entry.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {entry.tags.slice(0, 3).map((tag: string) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}