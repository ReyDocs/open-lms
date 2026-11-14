import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { GraduationCap, ArrowRight, Calendar, User, Search } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { formatDate } from '@/lib/utils';

export const AllCoursesPage: React.FC = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');

  const { data: coursesData, isLoading } = useQuery({
    queryKey: ['admin-all-courses', page],
    queryFn: async () => {
      const res = await apiClient.get(`/admin/courses?page=${page}&per_page=15`);
      return res.data;
    },
  });

  const filteredCourses = coursesData?.data?.filter((c: any) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return c.title.toLowerCase().includes(q) || c.code.toLowerCase().includes(q);
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight flex items-center gap-2">
            <GraduationCap className="h-7 w-7 text-primary" />
            <span>All Institutional Courses</span>
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Administrative oversight: View all active and past courses across all departments.
          </p>
        </div>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Filter courses by title or code..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      <Card className="overflow-x-auto border">
        {isLoading ? (
          <div className="p-8 text-center text-sm text-muted-foreground">Loading courses...</div>
        ) : !filteredCourses || filteredCourses.length === 0 ? (
          <div className="p-8 text-center text-sm text-muted-foreground">No courses found.</div>
        ) : (
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b bg-muted/50 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                <th className="p-3 pl-4">Course</th>
                <th className="p-3">Semester</th>
                <th className="p-3">Created</th>
                <th className="p-3 pr-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredCourses.map((c: any) => (
                <tr key={c.id} className="hover:bg-muted/30">
                  <td className="p-3 pl-4">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-xs">
                        {c.code}
                      </Badge>
                      <span className="font-semibold text-foreground">{c.title}</span>
                    </div>
                    <div className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
                      {c.description}
                    </div>
                  </td>
                  <td className="p-3 text-xs font-medium">{c.semester}</td>
                  <td className="p-3 text-xs text-muted-foreground">{formatDate(c.created_at)}</td>
                  <td className="p-3 pr-4 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/courses/${c.id}`)}
                      className="text-xs gap-1"
                    >
                      <span>Open Course</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
};
