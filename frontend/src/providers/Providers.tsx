/**
 * Root providers component.
 * Wraps the app with all necessary providers (theme, state management, etc.).
 */

'use client';

import React from 'react';
import { QueryProvider } from './QueryProvider';
import { ThemeProvider } from './ThemeProvider';
import { ToastProvider } from './ToastProvider';
import { GoogleOAuthProvider } from './GoogleOAuthProvider';

interface ProvidersProps {
  children: React.ReactNode;
  googleClientId?: string;
}

export const Providers: React.FC<ProvidersProps> = ({ children, googleClientId }) => {
  return (
    <GoogleOAuthProvider clientId={googleClientId || ''}>
      <QueryProvider>
        <ThemeProvider>
          {children}
          <ToastProvider />
        </ThemeProvider>
      </QueryProvider>
    </GoogleOAuthProvider>
  );
};

