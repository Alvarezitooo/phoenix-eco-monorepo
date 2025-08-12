'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { moodToEmoji } from '@/lib/utils';
import { Save, ArrowLeft, Heart, Tag } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';

export default function NewJournalPage() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [mood, setMood] = useState<number | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');
  
  const router = useRouter();
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: any) => api.journal.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journal'] });
      toast.success('Entrée sauvegardée avec succès !');
      router.push('/rise/journal');
    },
    onError: () => {
      toast.error('Erreur lors de la sauvegarde');
    },
  });

  const handleSave = () => {
    if (!content.trim()) {
      toast.error('Le contenu ne peut pas être vide');
      return;
    }

    const wordCount = content.trim().split(/\s+/).length;
    
    createMutation.mutate({
      title: title.trim() || null,
      content: content.trim(),
      mood,
      tags,
      word_count: wordCount,
    });
  };

  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim().toLowerCase())) {
      setTags([...tags, newTag.trim().toLowerCase()]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const wordCount = content.trim().split(/\s+/).filter(word => word.length > 0).length;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/rise/journal">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Nouvelle entrée
          </h1>
          <p className="text-muted-foreground">
            Exprimez vos pensées en toute liberté
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Editor */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Votre réflexion</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Title */}
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Titre (optionnel)
                </label>
                <input
                  type="text"
                  placeholder="Donnez un titre à votre entrée..."
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Content */}
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Contenu *
                </label>
                <textarea
                  placeholder="Écrivez vos pensées, réflexions, expériences... Soyez authentique, c'est pour vous."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={12}
                  className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                />
                <div className="flex justify-between items-center mt-2 text-xs text-muted-foreground">
                  <span>{wordCount} mot{wordCount > 1 ? 's' : ''}</span>
                  <span>Markdown supporté</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Mood */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Heart className="h-5 w-5 text-primary" />
                Humeur
              </CardTitle>
              <CardDescription>
                Comment vous sentez-vous aujourd'hui ?
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-5 gap-2">
                {[1, 2, 3, 4, 5].map((value) => (
                  <button
                    key={value}
                    onClick={() => setMood(mood === value ? null : value)}
                    className={`p-3 rounded-lg border text-center transition-colors ${
                      mood === value
                        ? 'border-primary bg-primary/10'
                        : 'border-muted hover:border-primary/50'
                    }`}
                  >
                    <div className="text-2xl mb-1">{moodToEmoji(value)}</div>
                    <div className="text-xs text-muted-foreground">{value}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Tags */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Tag className="h-5 w-5 text-primary" />
                Tags
              </CardTitle>
              <CardDescription>
                Organisez vos réflexions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Ajouter un tag..."
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addTag()}
                  className="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <Button size="sm" onClick={addTag}>
                  +
                </Button>
              </div>
              
              {tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <Badge
                      key={tag}
                      variant="secondary"
                      className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground"
                      onClick={() => removeTag(tag)}
                    >
                      {tag} ×
                    </Badge>
                  ))}
                </div>
              )}

              {/* Suggested tags */}
              <div>
                <p className="text-xs text-muted-foreground mb-2">Suggestions :</p>
                <div className="flex flex-wrap gap-1">
                  {['légitimité', 'clarté', 'courage', 'gratitude', 'réflexion'].map((suggestion) => (
                    <Badge
                      key={suggestion}
                      variant="outline"
                      className="cursor-pointer text-xs hover:bg-primary hover:text-primary-foreground"
                      onClick={() => {
                        if (!tags.includes(suggestion)) {
                          setTags([...tags, suggestion]);
                        }
                      }}
                    >
                      {suggestion}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardContent className="p-4 space-y-3">
              <Button
                onClick={handleSave}
                disabled={!content.trim() || createMutation.isPending}
                className="w-full"
              >
                <Save className="h-4 w-4 mr-2" />
                {createMutation.isPending ? 'Sauvegarde...' : 'Sauvegarder'}
              </Button>
              
              <Button variant="outline" className="w-full" asChild>
                <Link href="/rise/journal">
                  Annuler
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}