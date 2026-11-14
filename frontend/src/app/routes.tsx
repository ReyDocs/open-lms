import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { LoginPage } from '@/pages/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { CoursesListPage } from '@/pages/CoursesListPage';
import { CoursePage } from '@/pages/CoursePage';
import { AssignmentPage } from '@/pages/AssignmentPage';
import { CalendarPage } from '@/pages/CalendarPage';
import { NotificationsPage } from '@/pages/NotificationsPage';
import { UserManagementPage } from '@/pages/admin/UserManagementPage';
import { AllCoursesPage } from '@/pages/admin/AllCoursesPage';
import { SystemSettingsPage } from '@/pages/admin/SystemSettingsPage';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<AppShell />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="courses" element={<CoursesListPage />} />
        <Route path="courses/:id" element={<CoursePage />} />
        <Route path="courses/:id/assignments/:assignmentId" element={<AssignmentPage />} />
        <Route path="calendar" element={<CalendarPage />} />
        <Route path="notifications" element={<NotificationsPage />} />

        {/* Admin Routes */}
        <Route path="admin/users" element={<UserManagementPage />} />
        <Route path="admin/courses" element={<AllCoursesPage />} />
        <Route path="admin/settings" element={<SystemSettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
