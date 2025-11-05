'use client';

import { GoogleOAuthProvider as GoogleOAuthProviderLib } from '@react-oauth/google';

interface GoogleOAuthProviderProps {
  children: React.ReactNode;
  clientId: string;
}

export function GoogleOAuthProvider({ children, clientId }: GoogleOAuthProviderProps) {
  // Always render the provider to ensure context is available
  // The library will handle empty clientId gracefully
  // If clientId is empty, GoogleLogin won't work but won't throw this error
  return (
    <GoogleOAuthProviderLib clientId={clientId || ''}>
      {children}
    </GoogleOAuthProviderLib>
  );
}

