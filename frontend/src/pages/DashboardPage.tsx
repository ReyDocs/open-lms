import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  BookOpen,
  Calendar,
  Clock,
  Megaphone,
  Plus,
  ArrowRight,
  GraduationCap,
} from 'lucide-react';
import { useAuth } from '@/app/providers/AuthProvider';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Modal } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { formatDate } from '@/lib/utils';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [createCourseOpen, setCreateCourseOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newCode, setNewCode] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newSemester, setNewSemester] = useState('Fall 2026');

  // Fetch courses
  const { data: coursesData, isLoading: coursesLoading } = useQuery({
    queryKey: ['dashboard-courses'],
    queryFn: async () => {
      const res = await apiClient.get('/courses?per_page=12');
      return res.data;
    },
  });

  // Fetch upcoming deadlines (next 7 days)
  const { data: deadlinesData, isLoading: deadlinesLoading } = useQuery({
    queryKey: ['upcoming-deadlines'],
    queryFn: async () => {
      const res = await apiClient.get('/assignments/upcoming?days=7');
      return res.data;
    },
  });

  // Fetch recent announcements
  const { data: announcementsData, isLoading: announcementsLoading } = useQuery({
    queryKey: ['recent-announcements'],
    queryFn: async () => {
      const res = await apiClient.get('/announcements/recent?limit=5');
      return res.data;
    },
  });

  // Create course mutation (teachers)
  const createCourseMutation = useMutation({
    mutationFn: async (payload: { title: string; code: string; description: string; semester: string }) => {
      const res = await apiClient.post('/courses', payload);
      return res.data;
    },
    onSuccess: (newCourse) => {
      queryClient.invalidateQueries({ queryKey: ['dashboard-courses'] });
      queryClient.invalidateQueries({ queryKey: ['my-sidebar-courses'] });
      setCreateCourseOpen(false);
      setNewTitle('');
      setNewCode('');
      setNewDesc('');
      navigate(`/courses/${newCourse.id}`);
    },
  });

  const handleCreateCourse = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTitle && newCode) {
      createCourseMutation.mutate({
        title: newTitle,
        code: newCode,
        description: newDesc || 'Course description',
        semester: newSemester,
      });
    }
  };

  return (
    <div className="space-y-8">
      {/* Welcome Hero */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {user?.full_name}!
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            {user?.role === 'teacher'
              ? 'Manage your classrooms, student submissions, and gradebooks.'
              : user?.role === 'admin'
              ? 'Institutional administration and full system oversight.'
              : 'Keep track of your course assignments, resources, and deadlines.'}
          </p>
        </div>
        {user?.role === 'teacher' && (
          <Button onClick={() => setCreateCourseOpen(true)} className="gap-2 shadow">
            <Plus className="h-4 w-4" />
            <span>Create Course</span>
          </Button>
        )}
      </div>

      {/* Grid: Main courses (left 2 cols) & Sidebar info (right 1 col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Course Cards (2 columns on lg) */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary" />
              <span>{user?.role === 'teacher' ? 'Courses You Teach' : 'Enrolled Courses'}</span>
            </h2>
            <Button variant="ghost" size="sm" onClick={() => navigate('/courses')} className="gap-1">
              <span>View all</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>

          {coursesLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-48 rounded-xl bg-card/60 animate-pulse border" />
              ))}
            </div>
          ) : coursesData?.data?.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <GraduationCap className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
              <h3 className="font-semibold text-lg">No courses found</h3>
              <p className="text-sm text-muted-foreground mt-1 mb-4">
                {user?.role === 'teacher'
                  ? 'Get started by creating your first course.'
                  : 'You are not enrolled in any courses yet.'}
              </p>
              {user?.role === 'teacher' && (
                <Button onClick={() => setCreateCourseOpen(true)} size="sm">
                  Create Course
                </Button>
              )}
            </Card>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {coursesData?.data?.map((course: any) => (
                <Card
                  key={course.id}
                  onClick={() => navigate(`/courses/${course.id}`)}
                  className="group overflow-hidden cursor-pointer transition-all hover:shadow-md hover:border-primary/50 flex flex-col justify-between"
                >
                  <div className="h-28 w-full relative overflow-hidden bg-muted">
                    <img
                      src={course.cover_image_url || `https://picsum.photos/seed/${course.code}/600/300`}
                      alt={course.title}
                      className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                    <div className="absolute top-3 left-3">
                      <Badge className="bg-black/70 text-white backdrop-blur border-none font-mono text-xs">
                        {course.code}
                      </Badge>
                    </div>
                  </div>
                  <CardHeader className="p-4 pb-2">
                    <CardTitle className="text-base group-hover:text-primary transition-colors line-clamp-1">
                      {course.title}
                    </CardTitle>
                    <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                      {course.description}
                    </p>
                  </CardHeader>
                  <CardContent className="p-4 pt-2 border-t mt-auto flex items-center justify-between text-xs text-muted-foreground">
                    <span>{course.semester}</span>
                    <span className="text-primary font-medium flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                      Open <ArrowRight className="h-3 w-3" />
                    </span>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Right column: Upcoming Deadlines & Recent Announcements */}
        <div className="space-y-6">
          {/* Upcoming Deadlines (Next 7 days) */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-4 w-4 text-amber-500" />
                <span>Upcoming Deadlines (7 Days)</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {deadlinesLoading ? (
                <div className="space-y-2">
                  <div className="h-10 bg-muted/60 animate-pulse rounded" />
                  <div className="h-10 bg-muted/60 animate-pulse rounded" />
                </div>
              ) : !deadlinesData || deadlinesData.length === 0 ? (
                <div className="py-6 text-center text-sm text-muted-foreground">
                  <p>No deadlines in the next 7 days.</p>
                </div>
              ) : (
                <div className="divide-y">
                  {deadlinesData.slice(0, 5).map((item: any) => (
                    <div
                      key={item.id}
                      onClick={() => navigate(`/courses/${item.course_id}/assignments/${item.id}`)}
                      className="py-2.5 first:pt-0 last:pb-0 cursor-pointer hover:bg-muted/40 rounded px-1 transition-colors"
                    >
                      <div className="text-xs font-semibold text-foreground line-clamp-1">
                        {item.title}
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-muted-foreground mt-0.5">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(item.due_date)}
                        </span>
                        <Badge variant="outline" className="text-[10px]">
                          {item.total_points} pts
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Announcements */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Megaphone className="h-4 w-4 text-primary" />
                <span>Recent Announcements</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {announcementsLoading ? (
                <div className="space-y-2">
                  <div className="h-10 bg-muted/60 animate-pulse rounded" />
                  <div className="h-10 bg-muted/60 animate-pulse rounded" />
                </div>
              ) : !announcementsData || announcementsData.length === 0 ? (
                <div className="py-6 text-center text-sm text-muted-foreground">
                  <p>No recent announcements.</p>
                </div>
              ) : (
                <div className="divide-y">
                  {announcementsData.map((ann: any) => (
                    <div
                      key={ann.id}
                      onClick={() => navigate(`/courses/${ann.course_id}`)}
                      className="py-2.5 first:pt-0 last:pb-0 cursor-pointer hover:bg-muted/40 rounded px-1 transition-colors"
                    >
                      <div className="text-xs font-semibold text-foreground line-clamp-1">
                        {ann.title}
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-muted-foreground mt-0.5">
                        <span>{ann.author_name || 'Instructor'}</span>
                        <span>{formatDate(ann.created_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Create Course Modal */}
      <Modal
        isOpen={createCourseOpen}
        onClose={() => setCreateCourseOpen(false)}
        title="Create New Course"
        description="Add a new course to your curriculum and invite students."
      >
        <form onSubmit={handleCreateCourse} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold">Course Title *</label>
            <Input
              required
              placeholder="e.g. Introduction to Computer Science"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-semibold">Course Code *</label>
              <Input
                required
                placeholder="e.g. CS101"
                value={newCode}
                onChange={(e) => setNewCode(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold">Semester / Term *</label>
              <Input
                required
                placeholder="e.g. Fall 2026"
                value={newSemester}
                onChange={(e) => setNewSemester(e.target.value)}
              />
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold">Description</label>
            <textarea
              className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              placeholder="Provide a syllabus summary or course objective..."
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setCreateCourseOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createCourseMutation.isPending}>
              {createCourseMutation.isPending ? 'Creating...' : 'Create Course'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
