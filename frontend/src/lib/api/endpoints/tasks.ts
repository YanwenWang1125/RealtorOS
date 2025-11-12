import { taskClient } from '../client';
import { Task, TaskCreate, TaskUpdate } from '@/lib/types/task.types';
import { getApiPath } from '../utils/path';

export const tasksApi = {
  list: async (params?: { page?: number; limit?: number; status?: string; client_id?: number }) => {
    // FastAPI routes are mounted at "/api/tasks/"
    const safeParams = params
      ? { ...params, limit: params.limit ? Math.min(params.limit, 100) : params?.limit }
      : undefined;
    const path = getApiPath(taskClient.defaults.baseURL, '/tasks/');
    const { data } = await taskClient.get<Task[]>(path, { params: safeParams });
    return data;
  },

  getById: async (id: number) => {
    const path = getApiPath(taskClient.defaults.baseURL, `/tasks/${id}`);
    const { data } = await taskClient.get<Task>(path);
    return data;
  },

  create: async (task: TaskCreate) => {
    // Use trailing slash to avoid 307 redirects on POST
    const path = getApiPath(taskClient.defaults.baseURL, '/tasks/');
    const { data } = await taskClient.post<Task>(path, task);
    return data;
  },

  update: async (id: number, task: TaskUpdate) => {
    const path = getApiPath(taskClient.defaults.baseURL, `/tasks/${id}`);
    const { data } = await taskClient.patch<Task>(path, task);
    return data;
  },

  delete: async (id: number) => {
    const path = getApiPath(taskClient.defaults.baseURL, `/tasks/${id}`);
    const { data } = await taskClient.delete<{ success: boolean }>(path);
    return data;
  },

  bulkDelete: async (ids: number[]) => {
    const path = getApiPath(taskClient.defaults.baseURL, '/tasks/bulk');
    const { data } = await taskClient.delete<{ success: boolean; deleted_count: number; failed_ids: number[]; total_requested: number }>(path, {
      data: { ids }
    });
    return data;
  },
};
