/**
 * Root providers component.
 * Wraps the app with all necessary providers (theme, state management, etc.).
 */

'use client';

import React from 'react';
import { QueryProvider } from './QueryProvider';
import { ThemeProvider } from './ThemeProvider';
import { ToastProvider } from './ToastProvider';

interface ProvidersProps {
  children: React.ReactNode;
}

export const Providers: React.FC<ProvidersProps> = ({ children }) => {
  return (
    <QueryProvider>
      <ThemeProvider>
        {children}
        <ToastProvider />
      </ThemeProvider>
    </QueryProvider>
  );
};

