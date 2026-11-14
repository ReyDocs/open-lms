import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, Search, ArrowRight, GraduationCap } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

export const CoursesListPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const queryParam = searchParams.get('search') || '';
  const [search, setSearch] = useState(queryParam);

  const { data: coursesData, isLoading } = useQuery({
    queryKey: ['courses-list', queryParam],
    queryFn: async () => {
      if (queryParam) {
        const res = await apiClient.get(`/courses/search?q=${encodeURIComponent(queryParam)}`);
        return res.data;
      }
      const res = await apiClient.get('/courses?per_page=50');
      return res.data;
    },
  });

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchParams(search ? { search } : {});
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight flex items-center gap-2">
            <BookOpen className="h-7 w-7 text-primary" />
            <span>Courses</span>
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Browse and access your enrolled and taught courses.
          </p>
        </div>
      </div>

      <form onSubmit={handleSearchSubmit} className="relative max-w-md">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by title or course code..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </form>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-56 rounded-xl bg-card border animate-pulse" />
          ))}
        </div>
      ) : !coursesData?.data || coursesData.data.length === 0 ? (
        <Card className="p-12 text-center border-dashed">
          <GraduationCap className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
          <h3 className="font-semibold text-lg">No courses found</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Try adjusting your search query or check back later.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {coursesData.data.map((course: any) => (
            <Card
              key={course.id}
              onClick={() => navigate(`/courses/${course.id}`)}
              className="group overflow-hidden cursor-pointer transition-all hover:shadow-md hover:border-primary/50 flex flex-col justify-between"
            >
              <div className="h-32 w-full relative overflow-hidden bg-muted">
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
                  Enter Course <ArrowRight className="h-3 w-3" />
                </span>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
