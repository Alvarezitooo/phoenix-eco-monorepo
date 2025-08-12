import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { Bell, X, ExternalLink } from 'lucide-react';
import Link from 'next/link';

export function NotificationPanel() {
  const queryClient = useQueryClient();
  
  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => api.notifications.list(),
  });

  const markReadMutation = useMutation({
    mutationFn: (notificationId: string) => api.notifications.markRead(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const unreadNotifications = notifications?.filter((n: any) => n.status !== 'read') || [];

  if (unreadNotifications.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      {unreadNotifications.slice(0, 2).map((notification: any) => (
        <Card key={notification.id} className="border-primary/20 bg-primary/5">
          <CardContent className="p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3 flex-1">
                <Bell className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-sm">
                      {notification.title}
                    </h4>
                    <Badge variant="secondary" className="text-xs">
                      {notification.type === 'ritual_suggestion' && 'Rituel'}
                      {notification.type === 'streak_milestone' && 'Milestone'}
                      {notification.type === 'mood_reminder' && 'Humeur'}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {notification.message}
                  </p>
                  
                  <div className="flex items-center gap-2 mt-3">
                    {notification.action_url && (
                      <Button asChild size="sm" variant="outline">
                        <Link href={notification.action_url}>
                          <ExternalLink className="h-3 w-3 mr-1" />
                          {notification.action_text || 'Voir'}
                        </Link>
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => markReadMutation.mutate(notification.id)}
                      disabled={markReadMutation.isPending}
                    >
                      Marquer comme lu
                    </Button>
                  </div>
                </div>
              </div>
              
              <Button
                size="sm"
                variant="ghost"
                onClick={() => markReadMutation.mutate(notification.id)}
                className="flex-shrink-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}