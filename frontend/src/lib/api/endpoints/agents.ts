import { apiClient } from '../client';
import {
  AgentCreate,
  AgentUpdate,
  AgentLogin,
  GoogleLoginRequest,
  TokenResponse,
  Agent,
} from '@/lib/types/agent.types';

export const agentsApi = {
  register: async (data: AgentCreate): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/agents/register', data);
    return response.data;
  },

  loginEmail: async (credentials: AgentLogin): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/agents/login', credentials);
    return response.data;
  },

  loginGoogle: async (googleToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/agents/google', {
      credential: googleToken,
    });
    return response.data;
  },

  getProfile: async (): Promise<Agent> => {
    const response = await apiClient.get<Agent>('/api/agents/me');
    return response.data;
  },

  updateProfile: async (data: AgentUpdate): Promise<Agent> => {
    const response = await apiClient.patch<Agent>('/api/agents/me', data);
    return response.data;
  },
};

