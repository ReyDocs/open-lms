import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Search, LogOut, Sun, Moon, BookOpen, Menu } from 'lucide-react';
import { useAuth } from '@/app/providers/AuthProvider';
import { useTheme } from '@/app/providers/ThemeProvider';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

interface HeaderProps {
  onToggleSidebar?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const { data: unreadData } = useQuery({
    queryKey: ['unread-notifications'],
    queryFn: async () => {
      const res = await apiClient.get('/notifications/unread-count');
      return res.data;
    },
    refetchInterval: 30000,
  });

  const { data: appSettings } = useQuery({
    queryKey: ['public-app-settings'],
    queryFn: async () => {
      const res = await apiClient.get('/admin/settings/public');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/courses?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-40 flex h-16 w-full items-center justify-between border-b bg-card/95 px-4 sm:px-6 backdrop-blur">
      <div className="flex items-center gap-4">
        {onToggleSidebar && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleSidebar}
            className="md:hidden"
          >
            <Menu className="h-5 w-5" />
          </Button>
        )}
        <div
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 font-bold text-lg text-primary cursor-pointer select-none"
        >
          <div className="flex h-9 w-9 items-center justify-center overflow-hidden rounded-lg bg-primary text-primary-foreground shadow">
            {appSettings?.app_logo_url ? (
              <img src={appSettings.app_logo_url} alt="" className="h-full w-full object-contain" />
            ) : (
              <BookOpen className="h-5 w-5" />
            )}
          </div>
          <span>{appSettings?.app_name || 'OpenLMS'}</span>
        </div>
      </div>

      {/* Global Search Bar */}
      <form
        onSubmit={handleSearchSubmit}
        className="hidden md:flex relative w-72 lg:w-96 items-center"
      >
        <Search className="absolute left-3 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search courses by name or code..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="h-9 w-full rounded-full border bg-background pl-9 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-primary shadow-sm"
        />
      </form>

      <div className="flex items-center gap-3">
        {/* Theme toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="h-9 w-9 rounded-full"
        >
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>

        {/* Notifications Bell */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate('/notifications')}
          className="relative h-9 w-9 rounded-full"
        >
          <Bell className="h-4 w-4" />
          {unreadData?.unread_count > 0 && (
            <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-destructive-foreground">
              {unreadData.unread_count > 9 ? '9+' : unreadData.unread_count}
            </span>
          )}
        </Button>

        {/* User avatar and profile */}
        {user && (
          <div className="flex items-center gap-3 pl-2 border-l">
            <img
              src={user.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.email}`}
              alt={user.full_name}
              className="h-8 w-8 rounded-full border bg-muted"
            />
            <div className="hidden lg:flex flex-col text-left">
              <span className="text-sm font-medium leading-none">{user.full_name}</span>
              <div className="flex items-center gap-1 mt-0.5">
                <Badge variant="outline" className="text-[10px] px-1.5 py-0 capitalize">
                  {user.role}
                </Badge>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={logout}
              title="Logout"
              className="h-8 w-8 text-muted-foreground hover:text-destructive"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </header>
  );
};
