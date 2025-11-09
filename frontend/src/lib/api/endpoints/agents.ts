import { apiClient } from '../client';
import {
  AgentCreate,
  AgentUpdate,
  AgentLogin,
  GoogleLoginRequest,
  TokenResponse,
  Agent,
} from '@/lib/types/agent.types';
import { getApiPath } from '../utils/path';

export const agentsApi = {
  register: async (data: AgentCreate): Promise<TokenResponse> => {
    const path = getApiPath(apiClient.defaults.baseURL, '/agents/register');
    const response = await apiClient.post<TokenResponse>(path, data);
    return response.data;
  },

  loginEmail: async (credentials: AgentLogin): Promise<TokenResponse> => {
    const path = getApiPath(apiClient.defaults.baseURL, '/agents/login');
    const response = await apiClient.post<TokenResponse>(path, credentials);
    return response.data;
  },

  loginGoogle: async (googleToken: string): Promise<TokenResponse> => {
    const path = getApiPath(apiClient.defaults.baseURL, '/agents/google');
    const response = await apiClient.post<TokenResponse>(path, {
      credential: googleToken,
    });
    return response.data;
  },

  getProfile: async (): Promise<Agent> => {
    const path = getApiPath(apiClient.defaults.baseURL, '/agents/me');
    const response = await apiClient.get<Agent>(path);
    return response.data;
  },

  updateProfile: async (data: AgentUpdate): Promise<Agent> => {
    const path = getApiPath(apiClient.defaults.baseURL, '/agents/me');
    const response = await apiClient.patch<Agent>(path, data);
    return response.data;
  },
};

