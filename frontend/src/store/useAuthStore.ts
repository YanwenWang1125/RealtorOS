import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Agent, TokenResponse } from '@/lib/types/agent.types';

interface AuthState {
  token: string | null;
  agent: Agent | null;
  isAuthenticated: boolean;

  setAuth: (data: TokenResponse) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      agent: null,
      isAuthenticated: false,

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
    }),
    {
      name: 'realtor-auth-storage',
    }
  )
);
