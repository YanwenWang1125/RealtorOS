'use client';

import { GoogleOAuthProvider as GoogleOAuthProviderLib } from '@react-oauth/google';
import { createContext, useContext } from 'react';

interface GoogleOAuthProviderProps {
  children: React.ReactNode;
  clientId: string;
}

// Context to expose whether Google OAuth is available
const GoogleOAuthContext = createContext<{ isAvailable: boolean }>({ isAvailable: false });

export const useGoogleOAuth = () => useContext(GoogleOAuthContext);

export function GoogleOAuthProvider({ children, clientId }: GoogleOAuthProviderProps) {
  const isAvailable = !!(clientId && clientId.trim() !== '');
  
  // Only render the provider if clientId is provided
  // The Google Sign-In library requires a valid clientId, otherwise it throws an error
  if (!isAvailable) {
    // Return children without the provider if no clientId is available
    return (
      <GoogleOAuthContext.Provider value={{ isAvailable: false }}>
        {children}
      </GoogleOAuthContext.Provider>
    );
  }

  return (
    <GoogleOAuthProviderLib clientId={clientId}>
      <GoogleOAuthContext.Provider value={{ isAvailable: true }}>
        {children}
      </GoogleOAuthContext.Provider>
    </GoogleOAuthProviderLib>
  );
}

