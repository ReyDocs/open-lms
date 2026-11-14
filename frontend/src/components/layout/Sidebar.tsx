import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  Calendar,
  Bell,
  ShieldAlert,
  Users,
  Settings,
  GraduationCap,
} from 'lucide-react';
import { useAuth } from '@/app/providers/AuthProvider';
import { cn } from '@/lib/utils';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const { user } = useAuth();
  const location = useLocation();

  const { data: coursesData } = useQuery({
    queryKey: ['my-sidebar-courses'],
    queryFn: async () => {
      const res = await apiClient.get('/courses?per_page=10');
      return res.data;
    },
    enabled: !!user,
  });

  const mainLinks = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Courses', path: '/courses', icon: BookOpen },
    { label: 'Calendar', path: '/calendar', icon: Calendar },
    { label: 'Notifications', path: '/notifications', icon: Bell },
  ];

  const adminLinks = [
    { label: 'User Management', path: '/admin/users', icon: Users },
    { label: 'All Courses', path: '/admin/courses', icon: GraduationCap },
    { label: 'System Settings', path: '/admin/settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
        />
      )}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r bg-card pt-16 transition-transform duration-200 md:static md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-1 flex-col overflow-y-auto px-4 py-4 space-y-6">
          {/* Main Navigation */}
          <div>
            <p className="px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
              Menu
            </p>
            <nav className="space-y-1">
              {mainLinks.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => onClose && onClose()}
                    className={cn(
                      'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-primary text-primary-foreground shadow-sm'
                        : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>

          {/* Quick Course List */}
          {coursesData?.data && coursesData.data.length > 0 && (
            <div>
              <p className="px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                My Courses
              </p>
              <div className="space-y-1">
                {coursesData.data.slice(0, 5).map((course: any) => {
                  const isCurrentCourse = location.pathname.includes(`/courses/${course.id}`);
                  return (
                    <NavLink
                      key={course.id}
                      to={`/courses/${course.id}`}
                      onClick={() => onClose && onClose()}
                      className={cn(
                        'flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors truncate',
                        isCurrentCourse
                          ? 'bg-secondary font-semibold text-primary'
                          : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                      )}
                    >
                      <span className="font-mono text-[10px] px-1 py-0.5 rounded bg-muted">
                        {course.code}
                      </span>
                      <span className="truncate">{course.title}</span>
                    </NavLink>
                  );
                })}
              </div>
            </div>
          )}

          {/* Admin Navigation */}
          {user?.role === 'admin' && (
            <div className="pt-2 border-t">
              <p className="px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1.5">
                <ShieldAlert className="h-3.5 w-3.5 text-amber-500" />
                <span>Admin Oversight</span>
              </p>
              <nav className="space-y-1">
                {adminLinks.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      onClick={() => onClose && onClose()}
                      className={cn(
                        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-primary text-primary-foreground shadow-sm'
                          : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      <span>{item.label}</span>
                    </NavLink>
                  );
                })}
              </nav>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
