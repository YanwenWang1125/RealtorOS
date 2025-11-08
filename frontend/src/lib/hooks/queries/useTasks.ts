import { useQuery } from '@tanstack/react-query';
import { tasksApi } from '@/lib/api/endpoints/tasks';

export function useTasks(params?: { page?: number; limit?: number; status?: string; client_id?: number }) {
  return useQuery({
    queryKey: ['tasks', params],
    queryFn: () => tasksApi.list(params),
  });
}

export function useTask(id: number, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ['task', id],
    queryFn: () => tasksApi.getById(id),
    enabled: options?.enabled !== false && id > 0,
  });
}
