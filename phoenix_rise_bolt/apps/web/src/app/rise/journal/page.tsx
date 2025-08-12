'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { formatDate, moodToEmoji } from '@/lib/utils';
import { BookOpen, Plus, Search, Filter } from 'lucide-react';
import Link from 'next/link';

export default function JournalPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const queryClient = useQueryClient();

  const { data: entries, isLoading } = useQuery({
    queryKey: ['journal', 'list'],
    queryFn: () => api.journal.list(),
  });

  const filteredEntries = entries?.filter((entry: any) =>
    entry.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entry.content?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entry.tags?.some((tag: string) => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  ) || [];

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          <div className="animate-pulse">
            <div className="h-8 bg-muted rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-muted rounded w-2/3"></div>
          </div>
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-muted rounded w-3/4"></div>
                <div className="h-4 bg-muted rounded w-1/2"></div>
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Journal Kaizen
          </h1>
          <p className="text-muted-foreground">
            Écris la version honnête. C'est pour toi.
          </p>
        </div>
        <Button asChild>
          <Link href="/rise/journal/new">
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle entrée
          </Link>
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Rechercher dans vos entrées..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <Button variant="outline" size="sm">
              <Filter className="h-4 w-4 mr-2" />
              Filtres
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Entries List */}
      <div className="space-y-4">
        {filteredEntries.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <BookOpen className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h3 className="text-lg font-semibold mb-2">
                {searchTerm ? 'Aucun résultat' : 'Votre journal vous attend'}
              </h3>
              <p className="text-muted-foreground mb-6">
                {searchTerm 
                  ? `Aucune entrée ne correspond à "${searchTerm}"`
                  : 'Commencez votre première entrée pour débuter votre parcours Kaizen.'
                }
              </p>
              {!searchTerm && (
                <Button asChild>
                  <Link href="/rise/journal/new">
                    <Plus className="h-4 w-4 mr-2" />
                    Première entrée
                  </Link>
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          filteredEntries.map((entry: any) => (
            <Card key={entry.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">
                      {entry.title || 'Sans titre'}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-4 mt-2">
                      <span>{formatDate(entry.created_at)}</span>
                      {entry.mood && (
                        <span className="flex items-center gap-1">
                          {moodToEmoji(entry.mood)}
                          <span className="text-xs">Humeur {entry.mood}/5</span>
                        </span>
                      )}
                      <span className="text-xs">{entry.word_count} mots</span>
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground line-clamp-3 mb-4">
                  {entry.content}
                </p>
                
                {entry.tags && entry.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {entry.tags.map((tag: string) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <Button variant="outline" size="sm" asChild>
                    <Link href={`/rise/journal/${entry.id}`}>
                      Lire la suite
                    </Link>
                  </Button>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/rise/journal/${entry.id}/edit`}>
                      Modifier
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Stats */}
      {filteredEntries.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>{filteredEntries.length} entrée{filteredEntries.length > 1 ? 's' : ''}</span>
              <span>
                {filteredEntries.reduce((acc: number, entry: any) => acc + (entry.word_count || 0), 0)} mots au total
              </span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}