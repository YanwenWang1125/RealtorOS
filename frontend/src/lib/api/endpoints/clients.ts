import { crmClient } from '../client';
import { Client, ClientCreate, ClientUpdate } from '@/lib/types/client.types';
import { Task } from '@/lib/types/task.types';
import { getApiPath } from '../utils/path';

export const clientsApi = {
  list: async (params?: { page?: number; limit?: number; stage?: string; search?: string }) => {
    // FastAPI routes are mounted at "/api/clients/" (with trailing slash)
    const safeParams = params
      ? { ...params, limit: params.limit ? Math.min(params.limit, 100) : params?.limit }
      : undefined;
    const path = getApiPath(crmClient.defaults.baseURL, '/clients/');
    const { data } = await crmClient.get<Client[]>(path, { params: safeParams });
    return data;
  },

  getById: async (id: number) => {
    const path = getApiPath(crmClient.defaults.baseURL, `/clients/${id}`);
    const { data } = await crmClient.get<Client>(path);
    return data;
  },

  create: async (client: ClientCreate) => {
    // Use trailing slash to avoid 307 redirects on POST
    const path = getApiPath(crmClient.defaults.baseURL, '/clients/');
    const { data } = await crmClient.post<Client>(path, client);
    return data;
  },

  update: async (id: number, client: ClientUpdate) => {
    const path = getApiPath(crmClient.defaults.baseURL, `/clients/${id}`);
    const { data } = await crmClient.patch<Client>(path, client);
    return data;
  },

  delete: async (id: number) => {
    const path = getApiPath(crmClient.defaults.baseURL, `/clients/${id}`);
    const { data } = await crmClient.delete<{ success: boolean }>(path);
    return data;
  },

  bulkDelete: async (ids: number[]) => {
    const path = getApiPath(crmClient.defaults.baseURL, '/clients/bulk');
    const { data } = await crmClient.delete<{ success: boolean; deleted_count: number; failed_ids: number[]; total_requested: number }>(path, {
      data: { ids }
    });
    return data;
  },

  getTasks: async (id: number) => {
    const path = getApiPath(crmClient.defaults.baseURL, `/clients/${id}/tasks`);
    const { data } = await crmClient.get<Task[]>(path);
    return data;
  },
};
