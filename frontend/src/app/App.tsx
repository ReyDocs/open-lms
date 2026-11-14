import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { QueryProvider } from './providers/QueryProvider';
import { AuthProvider } from './providers/AuthProvider';
import { ThemeProvider } from './providers/ThemeProvider';
import { AppRoutes } from './routes';
import { Toaster } from 'sonner';

export const App: React.FC = () => {
  return (
    <ThemeProvider defaultTheme="light">
      <QueryProvider>
        <AuthProvider>
          <BrowserRouter>
            <AppRoutes />
            <Toaster position="top-right" richColors />
          </BrowserRouter>
        </AuthProvider>
      </QueryProvider>
    </ThemeProvider>
  );
};

export default App;
