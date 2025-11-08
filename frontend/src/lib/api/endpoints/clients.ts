import { crmClient } from '../client';
import { Client, ClientCreate, ClientUpdate } from '@/lib/types/client.types';
import { Task } from '@/lib/types/task.types';

export const clientsApi = {
  list: async (params?: { page?: number; limit?: number; stage?: string; search?: string }) => {
    // FastAPI routes are mounted at "/api/clients/" (with trailing slash)
    const safeParams = params
      ? { ...params, limit: params.limit ? Math.min(params.limit, 100) : params?.limit }
      : undefined;
    const { data } = await crmClient.get<Client[]>('/api/clients/', { params: safeParams });
    return data;
  },

  getById: async (id: number) => {
    const { data } = await crmClient.get<Client>(`/api/clients/${id}`);
    return data;
  },

  create: async (client: ClientCreate) => {
    // Use trailing slash to avoid 307 redirects on POST
    const { data } = await crmClient.post<Client>('/api/clients/', client);
    return data;
  },

  update: async (id: number, client: ClientUpdate) => {
    const { data } = await crmClient.patch<Client>(`/api/clients/${id}`, client);
    return data;
  },

  delete: async (id: number) => {
    const { data } = await crmClient.delete<{ success: boolean }>(`/api/clients/${id}`);
    return data;
  },

  getTasks: async (id: number) => {
    const { data } = await crmClient.get<Task[]>(`/api/clients/${id}/tasks`);
    return data;
  },
};
