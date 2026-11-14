import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  FileText,
  Clock,
  ArrowLeft,
  Upload,
  CheckCircle,
  AlertCircle,
  Download,
  Award,
  Send,
  Users,
} from 'lucide-react';
import { useAuth } from '@/app/providers/AuthProvider';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { formatDate, formatFileSize } from '@/lib/utils';

export const AssignmentPage: React.FC = () => {
  const { id, assignmentId } = useParams<{ id: string; assignmentId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const isTeacher = user?.role === 'teacher' || user?.role === 'admin';

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [gradingSubId, setGradingSubId] = useState<string | null>(null);
  const [gradeInput, setGradeInput] = useState<number>(0);
  const [feedbackInput, setFeedbackInput] = useState<string>('');

  // Queries
  const { data: assignment, isLoading: assignmentLoading } = useQuery({
    queryKey: ['assignment', assignmentId],
    queryFn: async () => {
      const res = await apiClient.get(`/assignments/${assignmentId}`);
      return res.data;
    },
  });

  const { data: mySubmission } = useQuery({
    queryKey: ['my-submission', assignmentId],
    queryFn: async () => {
      try {
        const res = await apiClient.get(`/assignments/${assignmentId}/submissions/mine`);
        return res.data;
      } catch {
        return null;
      }
    },
    enabled: !isTeacher,
  });

  const { data: submissions = [] } = useQuery({
    queryKey: ['assignment-submissions', assignmentId],
    queryFn: async () => {
      const res = await apiClient.get(`/assignments/${assignmentId}/submissions`);
      return res.data;
    },
    enabled: isTeacher,
  });

  // Submit file mutation
  const submitFileMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.post(`/assignments/${assignmentId}/submissions`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-submission', assignmentId] });
      setSelectedFile(null);
    },
  });

  // Grade submission mutation
  const gradeMutation = useMutation({
    mutationFn: async ({ submissionId, grade, feedback }: { submissionId: string; grade: number; feedback: string }) => {
      const res = await apiClient.post(`/submissions/${submissionId}/grade`, {
        grade,
        feedback,
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignment-submissions', assignmentId] });
      setGradingSubId(null);
    },
  });

  if (assignmentLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!assignment) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-bold">Assignment not found</h2>
        <Button onClick={() => navigate(`/courses/${id}`)} className="mt-4">
          Back to Course
        </Button>
      </div>
    );
  }

  const isPastDue = new Date() > new Date(assignment.due_date);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Back button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => navigate(`/courses/${id}?tab=assignments`)}
        className="gap-1.5 text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        <span>Back to Assignments</span>
      </Button>

      {/* Assignment Header Card */}
      <Card className="border shadow-sm">
        <CardHeader className="p-6 pb-4 border-b flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <FileText className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold">{assignment.title}</h1>
              <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground mt-1">
                <span className="flex items-center gap-1 font-medium text-foreground">
                  <Clock className="h-3.5 w-3.5 text-amber-500" />
                  Due: {formatDate(assignment.due_date)}
                </span>
                <span>•</span>
                <span className="font-semibold text-primary">{assignment.total_points} Total Points</span>
                <span>•</span>
                <Badge variant={assignment.status === 'published' ? 'default' : 'secondary'}>
                  {assignment.status}
                </Badge>
              </div>
            </div>
          </div>
          {isPastDue && (
            <Badge variant="destructive" className="self-start sm:self-center">
              Past Due (Submissions Closed)
            </Badge>
          )}
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Instructions */}
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-2">
              Instructions
            </h3>
            <div
              className="prose prose-sm dark:prose-invert max-w-none text-sm leading-relaxed"
              dangerouslySetInnerHTML={{ __html: assignment.description }}
            />
          </div>

          {/* Student Area: Submission & Grades */}
          {!isTeacher && (
            <div className="pt-6 border-t space-y-4">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                Your Submission
              </h3>

              {mySubmission ? (
                <div className="p-4 rounded-xl border bg-secondary/30 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                      <CheckCircle className="h-4 w-4" />
                      <span>Submitted on {formatDate(mySubmission.submitted_at)}</span>
                    </div>
                    {mySubmission.grade !== null && mySubmission.grade !== undefined ? (
                      <Badge variant="success" className="text-xs font-mono font-bold">
                        Grade: {mySubmission.grade} / {assignment.total_points}
                      </Badge>
                    ) : (
                      <Badge variant="outline">Ungraded</Badge>
                    )}
                  </div>

                  <div className="flex items-center justify-between p-3 rounded-lg border bg-background text-xs">
                    <span className="font-medium truncate">{mySubmission.file_name}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-muted-foreground">
                        {formatFileSize(mySubmission.file_size)}
                      </span>
                      <a
                        href={mySubmission.file_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-primary hover:underline flex items-center gap-1 font-semibold"
                      >
                        <Download className="h-3.5 w-3.5" />
                        Download
                      </a>
                    </div>
                  </div>

                  {mySubmission.feedback && (
                    <div className="text-xs bg-muted/60 p-3 rounded-lg border">
                      <span className="font-semibold text-foreground">Teacher Feedback:</span>
                      <p className="mt-1 text-muted-foreground italic">"{mySubmission.feedback}"</p>
                    </div>
                  )}

                  {!isPastDue && (
                    <p className="text-[11px] text-muted-foreground">
                      * You may upload a new file below to resubmit before the deadline.
                    </p>
                  )}
                </div>
              ) : (
                <div className="p-4 rounded-xl border bg-muted/20 text-xs text-muted-foreground flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-amber-500" />
                  <span>You have not submitted work for this assignment yet.</span>
                </div>
              )}

              {/* Upload input (if not past due) */}
              {!isPastDue ? (
                <div className="p-4 rounded-xl border bg-card space-y-3">
                  <label className="text-xs font-semibold block">
                    {mySubmission ? 'Resubmit Assignment (Replaces previous submission)' : 'Upload Your Work'}
                  </label>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <Input
                      type="file"
                      onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                      className="text-xs"
                    />
                    <Button
                      disabled={!selectedFile || submitFileMutation.isPending}
                      onClick={() => selectedFile && submitFileMutation.mutate(selectedFile)}
                      className="gap-2 sm:w-44"
                    >
                      <Upload className="h-4 w-4" />
                      <span>{submitFileMutation.isPending ? 'Uploading...' : 'Submit File'}</span>
                    </Button>
                  </div>
                  <p className="text-[11px] text-muted-foreground">
                    Accepted formats: PDF, DOCX, PPTX, XLSX, ZIP, PNG, JPG, MP4, MP3, CSV, TXT (Max 25MB)
                  </p>
                </div>
              ) : (
                <div className="p-4 rounded-lg bg-destructive/10 text-destructive text-xs font-medium">
                  Submissions are closed as the deadline has passed.
                </div>
              )}
            </div>
          )}

          {/* Teacher Area: Student Submissions & Grading */}
          {isTeacher && (
            <div className="pt-6 border-t space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  <span>Student Submissions ({submissions.length})</span>
                </h3>
              </div>

              {submissions.length === 0 ? (
                <div className="p-6 text-center text-sm text-muted-foreground border rounded-lg">
                  No student submissions for this assignment yet.
                </div>
              ) : (
                <div className="divide-y border rounded-xl overflow-hidden bg-card">
                  {submissions.map((sub: any) => (
                    <div key={sub.id} className="p-4 space-y-3">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                        <div>
                          <div className="text-sm font-semibold">{sub.student_name}</div>
                          <div className="text-xs text-muted-foreground">
                            {sub.student_email} • Submitted {formatDate(sub.submitted_at)}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <a
                            href={sub.file_url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1.5 px-3 py-1 text-xs rounded-md border bg-secondary hover:bg-secondary/80 font-medium"
                          >
                            <Download className="h-3.5 w-3.5 text-primary" />
                            <span>{sub.file_name}</span>
                          </a>
                          {sub.grade !== null && sub.grade !== undefined ? (
                            <Badge variant="success" className="font-mono text-xs">
                              {sub.grade} / {assignment.total_points}
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-xs text-amber-500 border-amber-500">
                              Ungraded
                            </Badge>
                          )}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setGradingSubId(sub.id);
                              setGradeInput(sub.grade || 0);
                              setFeedbackInput(sub.feedback || '');
                            }}
                            className="text-xs h-7 px-2"
                          >
                            Grade
                          </Button>
                        </div>
                      </div>

                      {/* Inline grading panel */}
                      {gradingSubId === sub.id && (
                        <div className="p-3 rounded-lg border bg-muted/40 space-y-3 mt-2">
                          <div className="flex items-center gap-3">
                            <div className="w-32">
                              <label className="text-[11px] font-semibold block mb-1">
                                Points (Max {assignment.total_points})
                              </label>
                              <Input
                                type="number"
                                min="0"
                                max={assignment.total_points}
                                value={gradeInput}
                                onChange={(e) => setGradeInput(Number(e.target.value))}
                                className="h-8 text-xs font-mono"
                              />
                            </div>
                            <div className="flex-1">
                              <label className="text-[11px] font-semibold block mb-1">Feedback</label>
                              <Input
                                placeholder="Constructive feedback for the student..."
                                value={feedbackInput}
                                onChange={(e) => setFeedbackInput(e.target.value)}
                                className="h-8 text-xs"
                              />
                            </div>
                            <div className="flex items-end gap-1.5 pt-4">
                              <Button
                                size="sm"
                                onClick={() =>
                                  gradeMutation.mutate({
                                    submissionId: sub.id,
                                    grade: gradeInput,
                                    feedback: feedbackInput,
                                  })
                                }
                                disabled={gradeMutation.isPending}
                                className="h-8 text-xs"
                              >
                                Save Grade
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => setGradingSubId(null)}
                                className="h-8 text-xs"
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
