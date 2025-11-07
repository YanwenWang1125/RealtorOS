import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Agent, TokenResponse } from '@/lib/types/agent.types';

interface AuthState {
  token: string | null;
  agent: Agent | null;
  isAuthenticated: boolean;
  hasHydrated: boolean;

  setAuth: (data: TokenResponse) => void;
  logout: () => void;
  setHasHydrated: (state: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      agent: null,
      isAuthenticated: false,
      hasHydrated: false,

      setAuth: (data: TokenResponse) => {
        set({
          token: data.access_token,
          agent: data.agent,
          isAuthenticated: true,
        });
      },

      logout: () => {
        set({
          token: null,
          agent: null,
          isAuthenticated: false,
        });
      },

      setHasHydrated: (state: boolean) => {
        set({
          hasHydrated: state,
        });
      },
    }),
    {
      name: 'realtor-auth-storage',
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
