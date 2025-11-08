import { taskClient } from '../client';
import { Task, TaskCreate, TaskUpdate } from '@/lib/types/task.types';

export const tasksApi = {
  list: async (params?: { page?: number; limit?: number; status?: string; client_id?: number }) => {
    // FastAPI routes are mounted at "/api/tasks/"
    const safeParams = params
      ? { ...params, limit: params.limit ? Math.min(params.limit, 100) : params?.limit }
      : undefined;
    const { data } = await taskClient.get<Task[]>('/api/tasks/', { params: safeParams });
    return data;
  },

  getById: async (id: number) => {
    const { data } = await taskClient.get<Task>(`/api/tasks/${id}`);
    return data;
  },

  create: async (task: TaskCreate) => {
    // Use trailing slash to avoid 307 redirects on POST
    const { data } = await taskClient.post<Task>('/api/tasks/', task);
    return data;
  },

  update: async (id: number, task: TaskUpdate) => {
    const { data } = await taskClient.patch<Task>(`/api/tasks/${id}`, task);
    return data;
  },
};
