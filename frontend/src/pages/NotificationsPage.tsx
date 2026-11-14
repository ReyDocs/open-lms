import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Bell,
  Check,
  CheckCheck,
  Megaphone,
  FileText,
  Award,
  UserPlus,
  Clock,
  ArrowRight,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils';

export const NotificationsPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ['user-notifications'],
    queryFn: async () => {
      const res = await apiClient.get('/notifications?per_page=50');
      return res.data;
    },
  });

  const markReadMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.patch(`/notifications/${id}/read`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-notifications'] });
      queryClient.invalidateQueries({ queryKey: ['unread-notifications'] });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: async () => {
      await apiClient.patch('/notifications/read-all');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-notifications'] });
      queryClient.invalidateQueries({ queryKey: ['unread-notifications'] });
    },
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'announcement':
        return <Megaphone className="h-4 w-4 text-primary" />;
      case 'assignment':
        return <FileText className="h-4 w-4 text-blue-500" />;
      case 'grade':
        return <Award className="h-4 w-4 text-emerald-500" />;
      case 'enrollment':
        return <UserPlus className="h-4 w-4 text-amber-500" />;
      default:
        return <Clock className="h-4 w-4 text-purple-500" />;
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight flex items-center gap-2">
            <Bell className="h-7 w-7 text-primary" />
            <span>Notifications</span>
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time updates regarding assignments, grades, announcements, and course enrollments.
          </p>
        </div>
        {notifications.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => markAllReadMutation.mutate()}
            disabled={markAllReadMutation.isPending}
            className="gap-1.5"
          >
            <CheckCheck className="h-4 w-4" />
            <span>Mark All as Read</span>
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 rounded-xl bg-card border animate-pulse" />
          ))}
        </div>
      ) : notifications.length === 0 ? (
        <Card className="p-12 text-center border-dashed">
          <Bell className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
          <h3 className="font-semibold text-lg">No notifications</h3>
          <p className="text-sm text-muted-foreground mt-1">You are completely up to date!</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {notifications.map((n: any) => (
            <Card
              key={n.id}
              className={`border transition-all ${
                n.is_read ? 'bg-card opacity-85' : 'bg-primary/[0.03] border-primary/40 shadow-sm'
              }`}
            >
              <CardContent className="p-4 sm:p-5 flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-muted mt-0.5">
                    {getTypeIcon(n.type)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-sm sm:text-base">{n.title}</h4>
                      <Badge variant="outline" className="text-[10px] capitalize">
                        {n.type}
                      </Badge>
                      {!n.is_read && (
                        <span className="h-2 w-2 rounded-full bg-primary inline-block" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{n.message}</p>
                    <div className="text-[11px] text-muted-foreground mt-2">
                      {formatDate(n.created_at)}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-center">
                  {n.link && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        if (!n.is_read) markReadMutation.mutate(n.id);
                        navigate(n.link);
                      }}
                      className="text-xs gap-1"
                    >
                      <span>View</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Button>
                  )}
                  {!n.is_read && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => markReadMutation.mutate(n.id)}
                      title="Mark as read"
                      className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
