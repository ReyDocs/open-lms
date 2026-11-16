import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Settings, Save, ShieldAlert, CheckCircle } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export const SystemSettingsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [appName, setAppName] = useState('');
  const [appLogoUrl, setAppLogoUrl] = useState('');
  const [supportEmail, setSupportEmail] = useState('');
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [staffAccessCode, setStaffAccessCode] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const { data: settings, isLoading } = useQuery({
    queryKey: ['system-settings'],
    queryFn: async () => {
      const res = await apiClient.get('/admin/settings');
      return res.data;
    },
  });

  useEffect(() => {
    if (settings) {
      setAppName(settings.app_name);
      setAppLogoUrl(settings.app_logo_url || '');
      setSupportEmail(settings.support_email);
      setMaintenanceMode(settings.maintenance_mode);
      setStaffAccessCode(settings.staff_access_code || '');
    }
  }, [settings]);

  const updateMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await apiClient.put('/admin/settings', payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-settings'] });
      queryClient.invalidateQueries({ queryKey: ['public-app-settings'] });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    },
  });

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate({
      app_name: appName,
      app_logo_url: appLogoUrl,
      support_email: supportEmail,
      maintenance_mode: maintenanceMode,
      staff_access_code: staffAccessCode,
    });
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight flex items-center gap-2">
            <Settings className="h-7 w-7 text-primary" />
            <span>System Settings</span>
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Global institutional application settings and maintenance controls.
          </p>
        </div>
      </div>

      <Card className="border shadow-sm">
        <CardHeader className="p-6 pb-4 border-b">
          <CardTitle className="text-lg">Institutional Configuration</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          {isLoading ? (
            <div className="space-y-4">
              <div className="h-10 bg-muted/60 rounded animate-pulse" />
              <div className="h-10 bg-muted/60 rounded animate-pulse" />
            </div>
          ) : (
            <form onSubmit={handleSave} className="space-y-5">
              <div className="space-y-1">
                <label className="text-xs font-semibold">Application Name</label>
                <Input
                  value={appName}
                  onChange={(e) => setAppName(e.target.value)}
                  placeholder="e.g. OpenLMS"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold">Application Logo URL</label>
                <Input
                  type="url"
                  value={appLogoUrl}
                  onChange={(e) => setAppLogoUrl(e.target.value)}
                  placeholder="https://example.edu/logo.png"
                />
                <p className="text-xs text-muted-foreground">Leave blank to use the default OpenLMS mark.</p>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold">Institutional Support Email</label>
                <Input
                  type="email"
                  value={supportEmail}
                  onChange={(e) => setSupportEmail(e.target.value)}
                  placeholder="support@openlms.app"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold">Staff Access Code</label>
                <Input
                  type="text"
                  value={staffAccessCode}
                  onChange={(e) => setStaffAccessCode(e.target.value)}
                  placeholder="e.g. OPENLMS-STAFF-2026"
                />
                <p className="text-xs text-muted-foreground">
                  Access key required by teachers and administrators to access the /staff login portal.
                </p>
              </div>

              <div className="pt-2 border-t">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-semibold text-foreground">Maintenance Mode</h4>
                    <p className="text-xs text-muted-foreground">
                      Restrict access to administrators for database updates or maintenance.
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={maintenanceMode}
                    onChange={(e) => setMaintenanceMode(e.target.checked)}
                    className="h-5 w-5 rounded border-input text-primary focus:ring-primary cursor-pointer"
                  />
                </div>
              </div>

              {savedSuccess && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-medium">
                  <CheckCircle className="h-4 w-4" />
                  <span>Settings updated successfully!</span>
                </div>
              )}

              <div className="flex justify-end pt-2">
                <Button type="submit" disabled={updateMutation.isPending} className="gap-2">
                  <Save className="h-4 w-4" />
                  <span>{updateMutation.isPending ? 'Saving...' : 'Save Settings'}</span>
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
