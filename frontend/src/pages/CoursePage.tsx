import React, { useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  BookOpen,
  Layers,
  FileText,
  Megaphone,
  GraduationCap,
  Users,
  Plus,
  Calendar,
  Download,
  Trash2,
  Send,
  Upload,
  CheckCircle,
  Clock,
  UserPlus,
  ExternalLink,
} from 'lucide-react';
import { useAuth } from '@/app/providers/AuthProvider';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Modal } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { formatDate, formatFileSize } from '@/lib/utils';

export const CoursePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTab = searchParams.get('tab') || 'modules';
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const isTeacher = user?.role === 'teacher' || user?.role === 'admin';

  // Modals state
  const [addModuleOpen, setAddModuleOpen] = useState(false);
  const [moduleTitle, setModuleTitle] = useState('');
  const [moduleDesc, setModuleDesc] = useState('');

  const [addAssignmentOpen, setAddAssignmentOpen] = useState(false);
  const [assignModuleId, setAssignModuleId] = useState('');
  const [assignTitle, setAssignTitle] = useState('');
  const [assignDesc, setAssignDesc] = useState('');
  const [assignPoints, setAssignPoints] = useState(100);
  const [assignDueDate, setAssignDueDate] = useState('');
  const [assignStatus, setAssignStatus] = useState('published');

  const [addAnnouncementOpen, setAddAnnouncementOpen] = useState(false);
  const [annTitle, setAnnTitle] = useState('');
  const [annContent, setAnnContent] = useState('');

  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');

  const [poolEnrollOpen, setPoolEnrollOpen] = useState(false);
  const [selectedStudentIds, setSelectedStudentIds] = useState<string[]>([]);

  const [uploadResourceModuleId, setUploadResourceModuleId] = useState<string | null>(null);
  const [resourceFile, setResourceFile] = useState<File | null>(null);

  // Queries
  const { data: course, isLoading: courseLoading } = useQuery({
    queryKey: ['course', id],
    queryFn: async () => {
      const res = await apiClient.get(`/courses/${id}`);
      return res.data;
    },
  });

  const { data: modules = [] } = useQuery({
    queryKey: ['course-modules', id],
    queryFn: async () => {
      const res = await apiClient.get(`/courses/${id}/modules`);
      return res.data;
    },
    enabled: currentTab === 'modules',
  });

  const { data: assignments = [] } = useQuery({
    queryKey: ['course-assignments', id],
    queryFn: async () => {
      const res = await apiClient.get(`/courses/${id}/assignments`);
      return res.data;
    },
    enabled: currentTab === 'assignments' || currentTab === 'modules',
  });

  const { data: announcements = [] } = useQuery({
    queryKey: ['course-announcements', id],
    queryFn: async () => {
      const res = await apiClient.get(`/courses/${id}/announcements`);
      return res.data;
    },
    enabled: currentTab === 'announcements',
  });

  const { data: students = [] } = useQuery({
    queryKey: ['course-students', id],
    queryFn: async () => {
      const res = await apiClient.get(`/courses/${id}/students`);
      return res.data;
    },
    enabled: currentTab === 'students' || isTeacher,
  });

  const { data: poolStudents = [] } = useQuery({
    queryKey: ['pool-students'],
    queryFn: async () => {
      const res = await apiClient.get('/users?role=student&per_page=100');
      return res.data.data;
    },
    enabled: poolEnrollOpen,
  });

  const { data: gradebook } = useQuery({
    queryKey: ['course-gradebook', id],
    queryFn: async () => {
      const res = await apiClient.get(`/courses/${id}/gradebook`);
      return res.data;
    },
    enabled: currentTab === 'gradebook' && isTeacher,
  });

  const { data: myGrades = [] } = useQuery({
    queryKey: ['my-grades', id],
    queryFn: async () => {
      const res = await apiClient.get(`/courses/${id}/grades/mine`);
      return res.data;
    },
    enabled: currentTab === 'gradebook' && !isTeacher,
  });

  // Mutations
  const createModuleMutation = useMutation({
    mutationFn: async (payload: { title: string; description: string; sort_order: number }) => {
      const res = await apiClient.post(`/courses/${id}/modules`, payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-modules', id] });
      setAddModuleOpen(false);
      setModuleTitle('');
      setModuleDesc('');
    },
  });

  const createAssignmentMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await apiClient.post(`/modules/${payload.module_id}/assignments`, payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-assignments', id] });
      setAddAssignmentOpen(false);
      setAssignTitle('');
      setAssignDesc('');
    },
  });

  const createAnnouncementMutation = useMutation({
    mutationFn: async (payload: { title: string; content: string }) => {
      const res = await apiClient.post(`/courses/${id}/announcements`, payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-announcements', id] });
      setAddAnnouncementOpen(false);
      setAnnTitle('');
      setAnnContent('');
    },
  });

  const inviteStudentMutation = useMutation({
    mutationFn: async (email: string) => {
      const res = await apiClient.post(`/courses/${id}/invite`, { email });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-students', id] });
      setInviteOpen(false);
      setInviteEmail('');
    },
  });

  const enrollPoolMutation = useMutation({
    mutationFn: async (student_ids: string[]) => {
      const res = await apiClient.post(`/courses/${id}/enroll`, { student_ids });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-students', id] });
      setPoolEnrollOpen(false);
      setSelectedStudentIds([]);
    },
  });

  const removeStudentMutation = useMutation({
    mutationFn: async (studentId: string) => {
      await apiClient.delete(`/courses/${id}/students/${studentId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-students', id] });
    },
  });

  const uploadResourceMutation = useMutation({
    mutationFn: async ({ moduleId, file }: { moduleId: string; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.post(`/modules/${moduleId}/files`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['course-modules', id] });
      setUploadResourceModuleId(null);
      setResourceFile(null);
    },
  });

  if (courseLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!course) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-bold">Course not found</h2>
        <Button onClick={() => navigate('/dashboard')} className="mt-4">
          Back to Dashboard
        </Button>
      </div>
    );
  }

  const tabs = [
    { id: 'modules', label: 'Modules', icon: Layers },
    { id: 'assignments', label: 'Assignments', icon: FileText },
    { id: 'announcements', label: 'Announcements', icon: Megaphone },
    { id: 'gradebook', label: isTeacher ? 'Gradebook' : 'My Grades', icon: GraduationCap },
    { id: 'students', label: `People (${students.length})`, icon: Users },
  ];

  return (
    <div className="space-y-6">
      {/* Course Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary/90 to-primary text-primary-foreground p-6 sm:p-8 shadow-md">
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-black/30 text-white font-mono uppercase border-none text-xs">
                {course.code}
              </Badge>
              <span className="text-xs text-primary-foreground/80 font-medium">{course.semester}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">{course.title}</h1>
            <p className="text-sm text-primary-foreground/90 mt-2 max-w-2xl">{course.description}</p>
          </div>
          {isTeacher && (
            <div className="flex flex-wrap gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setInviteOpen(true)}
                className="gap-1.5 shadow"
              >
                <UserPlus className="h-4 w-4" />
                <span>Invite Student</span>
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPoolEnrollOpen(true)}
                className="gap-1.5 shadow"
              >
                <Users className="h-4 w-4" />
                <span>Add from Pool</span>
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Tabs Header */}
      <div className="flex border-b overflow-x-auto space-x-1 sm:space-x-4">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setSearchParams({ tab: tab.id })}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-semibold border-b-2 whitespace-nowrap transition-colors ${
                isActive
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: MODULES */}
      {currentTab === 'modules' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold">Course Modules</h2>
            {isTeacher && (
              <Button size="sm" onClick={() => setAddModuleOpen(true)} className="gap-1.5">
                <Plus className="h-4 w-4" />
                <span>Add Module</span>
              </Button>
            )}
          </div>

          {modules.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <Layers className="h-10 w-10 text-muted-foreground mx-auto mb-2" />
              <h3 className="font-semibold text-base">No modules yet</h3>
              <p className="text-xs text-muted-foreground mt-1 mb-4">
                Organize weekly topics, lessons, and assignments inside modules.
              </p>
              {isTeacher && (
                <Button size="sm" onClick={() => setAddModuleOpen(true)}>
                  Create First Module
                </Button>
              )}
            </Card>
          ) : (
            <div className="space-y-4">
              {modules.map((m: any, idx: number) => {
                const moduleAssignments = assignments.filter((a: any) => a.module_id === m.id);
                return (
                  <Card key={m.id} className="overflow-hidden border">
                    <CardHeader className="bg-secondary/40 p-4 border-b flex flex-row items-center justify-between">
                      <div>
                        <CardTitle className="text-base font-bold flex items-center gap-2">
                          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-primary text-xs font-bold">
                            {idx + 1}
                          </span>
                          <span>{m.title}</span>
                        </CardTitle>
                        {m.description && (
                          <p className="text-xs text-muted-foreground mt-1">{m.description}</p>
                        )}
                      </div>
                      {isTeacher && (
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setAssignModuleId(m.id);
                              setAddAssignmentOpen(true);
                            }}
                            className="text-xs h-8 gap-1"
                          >
                            <Plus className="h-3.5 w-3.5" />
                            <span>Add Assignment</span>
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setUploadResourceModuleId(m.id)}
                            className="text-xs h-8 gap-1"
                          >
                            <Upload className="h-3.5 w-3.5" />
                            <span>Add File</span>
                          </Button>
                        </div>
                      )}
                    </CardHeader>
                    <CardContent className="p-4 space-y-3">
                      {/* File resources */}
                      {m.resources && m.resources.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                            Resources & Downloads
                          </p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {m.resources.map((res: any) => (
                              <a
                                key={res.id}
                                href={res.file_url}
                                target="_blank"
                                rel="noreferrer"
                                className="flex items-center justify-between p-2.5 rounded-lg border bg-background hover:bg-muted/50 transition-colors text-xs"
                              >
                                <span className="font-medium truncate flex-1">{res.file_name}</span>
                                <div className="flex items-center gap-2 text-muted-foreground ml-2">
                                  <span>{formatFileSize(res.file_size)}</span>
                                  <Download className="h-3.5 w-3.5 text-primary" />
                                </div>
                              </a>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Module assignments */}
                      {moduleAssignments.length > 0 && (
                        <div className="space-y-2 pt-2">
                          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                            Assignments
                          </p>
                          <div className="space-y-2">
                            {moduleAssignments.map((a: any) => (
                              <div
                                key={a.id}
                                onClick={() => navigate(`/courses/${id}/assignments/${a.id}`)}
                                className="flex items-center justify-between p-3 rounded-lg border bg-background hover:border-primary/50 cursor-pointer transition-all"
                              >
                                <div className="flex items-center gap-3">
                                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                                    <FileText className="h-4 w-4" />
                                  </div>
                                  <div>
                                    <div className="text-sm font-semibold">{a.title}</div>
                                    <div className="text-xs text-muted-foreground flex items-center gap-2 mt-0.5">
                                      <Clock className="h-3 w-3" />
                                      <span>Due: {formatDate(a.due_date)}</span>
                                      <span>•</span>
                                      <span>{a.total_points} Points</span>
                                    </div>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Badge
                                    variant={a.status === 'published' ? 'default' : 'secondary'}
                                    className="text-[10px]"
                                  >
                                    {a.status}
                                  </Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {(!m.resources || m.resources.length === 0) && moduleAssignments.length === 0 && (
                        <p className="text-xs text-muted-foreground italic py-2">
                          No items in this module yet.
                        </p>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: ASSIGNMENTS */}
      {currentTab === 'assignments' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold">All Course Assignments</h2>
            {isTeacher && (
              <Button
                size="sm"
                onClick={() => {
                  if (modules.length > 0) {
                    setAssignModuleId(modules[0].id);
                  }
                  setAddAssignmentOpen(true);
                }}
                className="gap-1.5"
              >
                <Plus className="h-4 w-4" />
                <span>New Assignment</span>
              </Button>
            )}
          </div>

          {assignments.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <FileText className="h-10 w-10 text-muted-foreground mx-auto mb-2" />
              <h3 className="font-semibold text-base">No assignments created</h3>
              <p className="text-xs text-muted-foreground mt-1 mb-4">
                Assignments created in modules will appear here.
              </p>
            </Card>
          ) : (
            <div className="space-y-3">
              {assignments.map((a: any) => (
                <Card
                  key={a.id}
                  onClick={() => navigate(`/courses/${id}/assignments/${a.id}`)}
                  className="hover:border-primary/50 cursor-pointer transition-all border"
                >
                  <CardContent className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-sm sm:text-base">{a.title}</h4>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            Due: {formatDate(a.due_date)}
                          </span>
                          <span>•</span>
                          <span>{a.total_points} Points</span>
                        </div>
                      </div>
                    </div>
                    <Badge variant={a.status === 'published' ? 'default' : 'secondary'}>
                      {a.status}
                    </Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: ANNOUNCEMENTS */}
      {currentTab === 'announcements' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold">Course Announcements</h2>
            {isTeacher && (
              <Button size="sm" onClick={() => setAddAnnouncementOpen(true)} className="gap-1.5">
                <Plus className="h-4 w-4" />
                <span>Post Announcement</span>
              </Button>
            )}
          </div>

          {announcements.length === 0 ? (
            <Card className="p-8 text-center border-dashed">
              <Megaphone className="h-10 w-10 text-muted-foreground mx-auto mb-2" />
              <h3 className="font-semibold text-base">No announcements yet</h3>
              <p className="text-xs text-muted-foreground mt-1">
                Important course updates and news will be posted here.
              </p>
            </Card>
          ) : (
            <div className="space-y-4">
              {announcements.map((ann: any) => (
                <Card key={ann.id} className="border">
                  <CardHeader className="p-5 pb-3 border-b flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-base font-bold">{ann.title}</CardTitle>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Posted by {ann.author_name || 'Instructor'} on {formatDate(ann.created_at)}
                      </p>
                    </div>
                  </CardHeader>
                  <CardContent className="p-5 space-y-4">
                    <div
                      className="prose prose-sm dark:prose-invert max-w-none text-sm leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: ann.content }}
                    />
                    {ann.attachments && ann.attachments.length > 0 && (
                      <div className="pt-3 border-t">
                        <p className="text-xs font-semibold text-muted-foreground mb-2">Attachments:</p>
                        <div className="flex flex-wrap gap-2">
                          {ann.attachments.map((att: any) => (
                            <a
                              key={att.id}
                              href={att.file_url}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border bg-secondary/50 text-xs hover:bg-secondary transition-colors"
                            >
                              <Download className="h-3.5 w-3.5 text-primary" />
                              <span>{att.file_name}</span>
                              <span className="text-muted-foreground">({formatFileSize(att.file_size)})</span>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: GRADEBOOK */}
      {currentTab === 'gradebook' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold">
              {isTeacher ? 'Gradebook Overview' : 'My Grades & Performance'}
            </h2>
            {isTeacher && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  window.open(`/api/v1/courses/${id}/gradebook/export`, '_blank');
                }}
                className="gap-1.5"
              >
                <Download className="h-4 w-4" />
                <span>Export CSV</span>
              </Button>
            )}
          </div>

          {isTeacher ? (
            /* Teacher view: table of students x assignments */
            <Card className="overflow-x-auto">
              {!gradebook || gradebook.students.length === 0 ? (
                <div className="p-8 text-center text-sm text-muted-foreground">
                  No enrolled students or assignments to display in gradebook.
                </div>
              ) : (
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="border-b bg-muted/50 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                      <th className="p-3 pl-4">Student</th>
                      {gradebook.assignments.map((a: any) => (
                        <th key={a.id} className="p-3 text-center">
                          <div>{a.title}</div>
                          <div className="text-[10px] text-muted-foreground font-normal">
                            ({a.total_points} pts)
                          </div>
                        </th>
                      ))}
                      <th className="p-3 text-center font-bold">Total Earned</th>
                      <th className="p-3 pr-4 text-center font-bold">Overall %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {gradebook.students.map((st: any) => (
                      <tr key={st.student_id} className="hover:bg-muted/30">
                        <td className="p-3 pl-4 font-medium">
                          <div>{st.student_name}</div>
                          <div className="text-xs text-muted-foreground">{st.student_email}</div>
                        </td>
                        {gradebook.assignments.map((a: any) => {
                          const pts = st.grades[a.id];
                          return (
                            <td key={a.id} className="p-3 text-center font-mono">
                              {pts !== null && pts !== undefined ? (
                                <Badge variant="outline" className="font-mono text-xs">
                                  {pts} / {a.total_points}
                                </Badge>
                              ) : (
                                <span className="text-muted-foreground">-</span>
                              )}
                            </td>
                          );
                        })}
                        <td className="p-3 text-center font-bold font-mono">
                          {st.total_earned} / {st.total_possible}
                        </td>
                        <td className="p-3 pr-4 text-center font-bold">
                          <Badge
                            variant={st.overall_percentage >= 70 ? 'success' : 'warning'}
                            className="text-xs"
                          >
                            {st.overall_percentage}%
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </Card>
          ) : (
            /* Student view: own grades */
            <div className="space-y-3">
              {myGrades.length === 0 ? (
                <Card className="p-8 text-center text-sm text-muted-foreground">
                  No graded assignments yet.
                </Card>
              ) : (
                myGrades.map((g: any) => (
                  <Card key={g.assignment_id} className="p-4 flex items-center justify-between border">
                    <div>
                      <h4 className="font-semibold text-sm">{g.assignment_title}</h4>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {g.points_earned !== null
                          ? `Graded on ${formatDate(g.graded_at)}`
                          : 'Not graded yet'}
                      </p>
                      {g.feedback && (
                        <p className="text-xs bg-muted p-2 rounded mt-2 text-foreground/90 italic">
                          Feedback: "{g.feedback}"
                        </p>
                      )}
                    </div>
                    <div className="text-right">
                      {g.points_earned !== null ? (
                        <div>
                          <div className="text-lg font-bold font-mono text-primary">
                            {g.points_earned} / {g.total_points}
                          </div>
                          <Badge variant="outline" className="text-xs mt-1">
                            {g.percentage}%
                          </Badge>
                        </div>
                      ) : (
                        <Badge variant="secondary">Pending Grade</Badge>
                      )}
                    </div>
                  </Card>
                ))
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 5: STUDENTS */}
      {currentTab === 'students' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold">Enrolled Students ({students.length})</h2>
            {isTeacher && (
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={() => setPoolEnrollOpen(true)} className="gap-1.5">
                  <Users className="h-4 w-4" />
                  <span>Pool Import</span>
                </Button>
                <Button size="sm" onClick={() => setInviteOpen(true)} className="gap-1.5">
                  <UserPlus className="h-4 w-4" />
                  <span>Email Invite</span>
                </Button>
              </div>
            )}
          </div>

          <Card>
            <div className="divide-y">
              {students.map((st: any) => (
                <div key={st.id} className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    <img
                      src={st.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${st.email}`}
                      alt={st.full_name}
                      className="h-9 w-9 rounded-full border bg-muted"
                    />
                    <div>
                      <div className="text-sm font-semibold">{st.full_name}</div>
                      <div className="text-xs text-muted-foreground">
                        {st.email} {st.student_id ? `• ${st.student_id}` : ''}
                      </div>
                    </div>
                  </div>
                  {isTeacher && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeStudentMutation.mutate(st.id)}
                      className="text-destructive hover:text-destructive hover:bg-destructive/10 h-8 px-2"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Add Module Modal */}
      <Modal
        isOpen={addModuleOpen}
        onClose={() => setAddModuleOpen(false)}
        title="Add Course Module"
        description="Create a section to group assignments and readings (e.g. Week 1: Introduction)."
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (moduleTitle) {
              createModuleMutation.mutate({
                title: moduleTitle,
                description: moduleDesc,
                sort_order: modules.length,
              });
            }
          }}
          className="space-y-4"
        >
          <div className="space-y-1">
            <label className="text-xs font-semibold">Module Title *</label>
            <Input
              required
              placeholder="e.g. Week 1: Orientation & Foundations"
              value={moduleTitle}
              onChange={(e) => setModuleTitle(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold">Description</label>
            <Input
              placeholder="Optional overview..."
              value={moduleDesc}
              onChange={(e) => setModuleDesc(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setAddModuleOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createModuleMutation.isPending}>
              Create Module
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Assignment Modal */}
      <Modal
        isOpen={addAssignmentOpen}
        onClose={() => setAddAssignmentOpen(false)}
        title="Create Assignment"
        description="Add a points-based assignment with submission deadline."
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (assignTitle && assignModuleId && assignDueDate) {
              createAssignmentMutation.mutate({
                module_id: assignModuleId,
                title: assignTitle,
                description: assignDesc || 'Submit your work for this assignment.',
                total_points: Number(assignPoints),
                due_date: new Date(assignDueDate).toISOString(),
                status: assignStatus,
              });
            }
          }}
          className="space-y-4"
        >
          <div className="space-y-1">
            <label className="text-xs font-semibold">Module *</label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              value={assignModuleId}
              onChange={(e) => setAssignModuleId(e.target.value)}
              required
            >
              <option value="">Select target module...</option>
              {modules.map((m: any) => (
                <option key={m.id} value={m.id}>
                  {m.title}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold">Assignment Title *</label>
            <Input
              required
              placeholder="e.g. Problem Set 1"
              value={assignTitle}
              onChange={(e) => setAssignTitle(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-semibold">Total Points *</label>
              <Input
                type="number"
                min="1"
                required
                value={assignPoints}
                onChange={(e) => setAssignPoints(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold">Status *</label>
              <select
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                value={assignStatus}
                onChange={(e) => setAssignStatus(e.target.value)}
              >
                <option value="published">Published</option>
                <option value="draft">Draft</option>
              </select>
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold">Due Date & Time *</label>
            <Input
              type="datetime-local"
              required
              value={assignDueDate}
              onChange={(e) => setAssignDueDate(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold">Description & Instructions</label>
            <textarea
              className="flex min-h-[70px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm"
              placeholder="Provide instructions and submission requirements..."
              value={assignDesc}
              onChange={(e) => setAssignDesc(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setAddAssignmentOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createAssignmentMutation.isPending}>
              Create Assignment
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Announcement Modal */}
      <Modal
        isOpen={addAnnouncementOpen}
        onClose={() => setAddAnnouncementOpen(false)}
        title="Post Announcement"
        description="Notify all enrolled students via in-app and email notification."
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (annTitle && annContent) {
              createAnnouncementMutation.mutate({
                title: annTitle,
                content: `<p>${annContent.replace(/\n/g, '<br/>')}</p>`,
              });
            }
          }}
          className="space-y-4"
        >
          <div className="space-y-1">
            <label className="text-xs font-semibold">Announcement Title *</label>
            <Input
              required
              placeholder="e.g. Midterm exam review schedule"
              value={annTitle}
              onChange={(e) => setAnnTitle(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold">Content *</label>
            <textarea
              className="flex min-h-[120px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm"
              placeholder="Write your announcement message..."
              required
              value={annContent}
              onChange={(e) => setAnnContent(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setAddAnnouncementOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createAnnouncementMutation.isPending}>
              Post Announcement
            </Button>
          </div>
        </form>
      </Modal>

      {/* Email Invite Modal (Pathway B) */}
      <Modal
        isOpen={inviteOpen}
        onClose={() => setInviteOpen(false)}
        title="Invite Student by Email (Pathway B)"
        description="The student will receive an invitation email and be enrolled automatically upon login."
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (inviteEmail) {
              inviteStudentMutation.mutate(inviteEmail);
            }
          }}
          className="space-y-4"
        >
          <div className="space-y-1">
            <label className="text-xs font-semibold">Student Google Email *</label>
            <Input
              type="email"
              required
              placeholder="student@university.edu"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => setInviteOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={inviteStudentMutation.isPending}>
              {inviteStudentMutation.isPending ? 'Sending Invite...' : 'Send Invite'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Pool Enrollment Modal (Pathway A) */}
      <Modal
        isOpen={poolEnrollOpen}
        onClose={() => setPoolEnrollOpen(false)}
        title="Enroll from Student Pool (Pathway A)"
        description="Select pre-registered students to add directly to this course."
        maxWidth="max-w-xl"
      >
        <div className="space-y-4">
          <div className="max-h-60 overflow-y-auto divide-y border rounded-lg p-2">
            {poolStudents.map((st: any) => {
              const isAlreadyEnrolled = students.some((s: any) => s.id === st.id);
              const isSelected = selectedStudentIds.includes(st.id);
              return (
                <div
                  key={st.id}
                  onClick={() => {
                    if (isAlreadyEnrolled) return;
                    setSelectedStudentIds((prev) =>
                      isSelected ? prev.filter((id) => id !== st.id) : [...prev, st.id]
                    );
                  }}
                  className={`flex items-center justify-between p-2 rounded cursor-pointer ${
                    isAlreadyEnrolled
                      ? 'opacity-40 cursor-not-allowed'
                      : isSelected
                      ? 'bg-primary/10'
                      : 'hover:bg-muted/50'
                  }`}
                >
                  <div>
                    <div className="text-xs font-semibold">{st.full_name}</div>
                    <div className="text-[11px] text-muted-foreground">{st.email}</div>
                  </div>
                  {isAlreadyEnrolled ? (
                    <Badge variant="outline" className="text-[10px]">
                      Enrolled
                    </Badge>
                  ) : (
                    <input
                      type="checkbox"
                      checked={isSelected}
                      readOnly
                      className="rounded border-input text-primary"
                    />
                  )}
                </div>
              );
            })}
          </div>

          <div className="flex justify-between items-center pt-2">
            <span className="text-xs text-muted-foreground">
              {selectedStudentIds.length} student(s) selected
            </span>
            <div className="flex gap-2">
              <Button type="button" variant="outline" onClick={() => setPoolEnrollOpen(false)}>
                Cancel
              </Button>
              <Button
                disabled={selectedStudentIds.length === 0 || enrollPoolMutation.isPending}
                onClick={() => enrollPoolMutation.mutate(selectedStudentIds)}
              >
                {enrollPoolMutation.isPending ? 'Enrolling...' : 'Enroll Selected'}
              </Button>
            </div>
          </div>
        </div>
      </Modal>

      {/* Upload File Resource Modal */}
      <Modal
        isOpen={!!uploadResourceModuleId}
        onClose={() => setUploadResourceModuleId(null)}
        title="Upload Module Resource"
        description="Upload lecture slides, reading PDFs, or assignments notes (max 25MB)."
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (uploadResourceModuleId && resourceFile) {
              uploadResourceMutation.mutate({
                moduleId: uploadResourceModuleId,
                file: resourceFile,
              });
            }
          }}
          className="space-y-4"
        >
          <div className="space-y-1">
            <label className="text-xs font-semibold">Select File *</label>
            <Input
              type="file"
              required
              onChange={(e) => setResourceFile(e.target.files?.[0] || null)}
            />
            <p className="text-[11px] text-muted-foreground">
              Accepted: PDF, DOCX, PPTX, XLSX, ZIP, PNG, JPG, MP4, CSV, TXT (Max 25MB)
            </p>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setUploadResourceModuleId(null)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={!resourceFile || uploadResourceMutation.isPending}>
              {uploadResourceMutation.isPending ? 'Uploading...' : 'Upload File'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
