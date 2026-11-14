import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Calendar as CalendarIcon,
  Clock,
  Plus,
  Trash2,
  BookOpen,
  Tag,
} from 'lucide-react';
import { useAuth } from '@/app/providers/AuthProvider';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Modal } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { formatDate } from '@/lib/utils';

export const CalendarPage: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const isTeacher = user?.role === 'teacher' || user?.role === 'admin';

  const [addEventOpen, setAddEventOpen] = useState(false);
  const [courseId, setCourseId] = useState('');
  const [eventTitle, setEventTitle] = useState('');
  const [eventDate, setEventDate] = useState('');
  const [eventDesc, setEventDesc] = useState('');

  // Fetch all calendar events
  const { data: events = [], isLoading } = useQuery({
    queryKey: ['aggregated-calendar'],
    queryFn: async () => {
      const res = await apiClient.get('/calendar');
      return res.data;
    },
  });

  // Fetch teacher's courses for the event creation dropdown
  const { data: coursesData } = useQuery({
    queryKey: ['my-taught-courses'],
    queryFn: async () => {
      const res = await apiClient.get('/courses?per_page=50');
      return res.data;
    },
    enabled: isTeacher,
  });

  const createEventMutation = useMutation({
    mutationFn: async (payload: { course_id: string; title: string; event_datetime: string; description?: string }) => {
      const res = await apiClient.post(`/courses/${payload.course_id}/calendar`, payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['aggregated-calendar'] });
      setAddEventOpen(false);
      setEventTitle('');
      setEventDesc('');
      setEventDate('');
    },
  });

  const deleteEventMutation = useMutation({
    mutationFn: async (eventId: string) => {
      await apiClient.delete(`/calendar/${eventId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['aggregated-calendar'] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight flex items-center gap-2">
            <CalendarIcon className="h-7 w-7 text-primary" />
            <span>Academic Calendar</span>
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Aggregated schedule of assignment due dates and course events.
          </p>
        </div>
        {isTeacher && (
          <Button onClick={() => setAddEventOpen(true)} className="gap-2 shadow">
            <Plus className="h-4 w-4" />
            <span>Add Event</span>
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 rounded-xl bg-card border animate-pulse" />
          ))}
        </div>
      ) : events.length === 0 ? (
        <Card className="p-12 text-center border-dashed">
          <CalendarIcon className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
          <h3 className="font-semibold text-lg">No scheduled events</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Assignment deadlines and custom events will appear here automatically.
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {events.map((ev: any) => (
            <Card key={ev.id} className="border hover:border-primary/40 transition-all">
              <CardContent className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start gap-4">
                  <div
                    className={`flex h-11 w-11 items-center justify-center rounded-xl font-bold text-xs flex-col ${
                      ev.source === 'auto'
                        ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400'
                        : 'bg-primary/10 text-primary'
                    }`}
                  >
                    <Clock className="h-4 w-4" />
                    <span className="text-[10px] mt-0.5 uppercase">{ev.source}</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-base text-foreground flex items-center gap-2">
                      <span>{ev.title}</span>
                      {ev.course_title && (
                        <Badge variant="outline" className="text-[11px] font-normal">
                          {ev.course_title}
                        </Badge>
                      )}
                    </h4>
                    {ev.description && (
                      <p className="text-xs text-muted-foreground mt-0.5">{ev.description}</p>
                    )}
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2 font-medium">
                      <CalendarIcon className="h-3.5 w-3.5" />
                      <span>{formatDate(ev.event_datetime)}</span>
                    </div>
                  </div>
                </div>

                {/* Teacher delete button if manual event */}
                {isTeacher && ev.source === 'manual' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteEventMutation.mutate(ev.id)}
                    className="self-end sm:self-center text-destructive hover:text-destructive hover:bg-destructive/10 h-8 px-2"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Manual Event Modal */}
      <Modal
        isOpen={addEventOpen}
        onClose={() => setAddEventOpen(false)}
        title="Schedule Course Event"
        description="Add review sessions, office hours, or deadlines to the course calendar."
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (courseId && eventTitle && eventDate) {
              createEventMutation.mutate({
                course_id: courseId,
                title: eventTitle,
                event_datetime: new Date(eventDate).toISOString(),
                description: eventDesc,
              });
            }
          }}
          className="space-y-4"
        >
          <div className="space-y-1">
            <label className="text-xs font-semibold">Course *</label>
            <select
              required
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              value={courseId}
              onChange={(e) => setCourseId(e.target.value)}
            >
              <option value="">Select course...</option>
              {coursesData?.data?.map((c: any) => (
                <option key={c.id} value={c.id}>
                  {c.code} - {c.title}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold">Event Title *</label>
            <Input
              required
              placeholder="e.g. Midterm Q&A Review Session"
              value={eventTitle}
              onChange={(e) => setEventTitle(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold">Date & Time *</label>
            <Input
              type="datetime-local"
              required
              value={eventDate}
              onChange={(e) => setEventDate(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold">Description / Location</label>
            <textarea
              className="flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm"
              placeholder="e.g. Zoom link or Hall 401..."
              value={eventDesc}
              onChange={(e) => setEventDesc(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setAddEventOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createEventMutation.isPending}>
              {createEventMutation.isPending ? 'Scheduling...' : 'Add Event'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
