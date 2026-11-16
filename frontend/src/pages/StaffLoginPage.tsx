import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { KeyRound, ShieldCheck, GraduationCap, Sparkles, Shield } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/app/providers/AuthProvider';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export const StaffLoginPage: React.FC = () => {
  const { user, isAuthenticated, loginWithDev, loginWithGoogle, handleGoogleCallback, logout } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [staffCode, setStaffCode] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [isVerified, setIsVerified] = useState<boolean>(() => {
    return sessionStorage.getItem('staff_code_verified') === 'true';
  });
  const [loadingRole, setLoadingRole] = useState<string | null>(null);

  // If already authenticated, check role
  useEffect(() => {
    if (isAuthenticated && user) {
      if (user.role === 'student') {
        logout();
        toast.error('This login is for staff only. Please use the student login page.');
        navigate('/login', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    }
  }, [isAuthenticated, user, navigate, logout]);

  // Handle Google OAuth callback (?code=...)
  useEffect(() => {
    const code = searchParams.get('code');
    if (code) {
      handleGoogleCallback(code)
        .then((userData) => {
          if (userData && userData.role === 'student') {
            logout();
            toast.error('This login is for staff only. Please use the student login page.');
            navigate('/login', { replace: true });
          } else {
            navigate('/dashboard', { replace: true });
          }
        })
        .catch((err) => {
          toast.error(err.response?.data?.detail || 'Authentication failed');
        });
    }
  }, [searchParams, handleGoogleCallback, logout, navigate]);

  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!staffCode.trim()) {
      toast.error('Please enter the staff access code.');
      return;
    }

    setIsVerifying(true);
    try {
      const res = await apiClient.post('/auth/verify-staff-code', { code: staffCode.trim() });
      if (res.data.valid) {
        setIsVerified(true);
        sessionStorage.setItem('staff_code_verified', 'true');
        toast.success('Access code verified. You may now sign in.');
      } else {
        toast.error('Invalid staff access code. Please contact your system administrator.');
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to verify staff access code.');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleDevLogin = async (role: 'admin' | 'teacher', email: string, name: string) => {
    setLoadingRole(role);
    try {
      await loginWithDev(email, role, name);
      navigate('/dashboard', { replace: true });
    } finally {
      setLoadingRole(null);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-secondary/30 to-background p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-amber-600 text-white shadow-lg mb-2">
            <Shield className="h-6 w-6" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">OpenLMS Staff Portal</h1>
          <p className="text-sm text-muted-foreground">
            Faculty and administrative management access.
          </p>
        </div>

        {!isVerified ? (
          /* Step 1: Staff Access Code Gate */
          <Card className="shadow-lg border">
            <CardHeader className="text-center pb-4">
              <CardTitle className="flex items-center justify-center gap-2">
                <KeyRound className="h-5 w-5 text-amber-500" />
                <span>Staff Access Code</span>
              </CardTitle>
              <CardDescription>
                Enter your institutional staff access code to unlock the staff portal.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleVerifyCode} className="space-y-4">
                <div className="space-y-1">
                  <Input
                    type="password"
                    placeholder="Enter staff access code"
                    value={staffCode}
                    onChange={(e) => setStaffCode(e.target.value)}
                    disabled={isVerifying}
                    className="h-11"
                    autoFocus
                  />
                </div>
                <Button
                  type="submit"
                  disabled={isVerifying}
                  className="w-full h-11 font-semibold"
                >
                  {isVerifying ? 'Verifying...' : 'Verify Access Code'}
                </Button>
              </form>
            </CardContent>
          </Card>
        ) : (
          /* Step 2: Google Sign In + Dev Buttons (Staff Only) */
          <Card className="shadow-lg border">
            <CardHeader className="text-center pb-4">
              <CardTitle>Staff Sign In</CardTitle>
              <CardDescription>Authenticate with your faculty or administrative Google account</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Google OAuth Login Button with state="staff" */}
              <Button
                className="w-full flex items-center justify-center gap-3 py-5 text-base font-semibold shadow-sm"
                onClick={() => loginWithGoogle('staff')}
              >
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  />
                </svg>
                <span>Continue with Google</span>
              </Button>

              <div className="relative my-4">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground font-medium flex items-center gap-1">
                    <Sparkles className="h-3 w-3 text-amber-500" /> Instant Demo / Evaluation Login (Staff)
                  </span>
                </div>
              </div>

              {/* Quick Demo Switcher - Staff only (Admin & Teacher) */}
              <div className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full justify-start gap-2 h-11"
                  disabled={!!loadingRole}
                  onClick={() => handleDevLogin('admin', 'admin@openlms.edu', 'System Admin')}
                >
                  <ShieldCheck className="h-4 w-4 text-amber-500" />
                  <div className="text-left">
                    <div className="text-xs font-semibold">Login as Administrator</div>
                    <div className="text-[11px] text-muted-foreground">admin@openlms.edu</div>
                  </div>
                </Button>

                <Button
                  variant="outline"
                  className="w-full justify-start gap-2 h-11"
                  disabled={!!loadingRole}
                  onClick={() => handleDevLogin('teacher', 'alan.turing@openlms.edu', 'Dr. Alan Turing')}
                >
                  <GraduationCap className="h-4 w-4 text-primary" />
                  <div className="text-left">
                    <div className="text-xs font-semibold">Login as Teacher (Dr. Turing)</div>
                    <div className="text-[11px] text-muted-foreground">alan.turing@openlms.edu</div>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
