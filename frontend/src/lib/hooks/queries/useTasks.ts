import { useQuery } from '@tanstack/react-query';
import { tasksApi } from '@/lib/api/endpoints/tasks';
import { useAuthStore } from '@/store/useAuthStore';

export function useTasks(params?: { page?: number; limit?: number; status?: string; client_id?: number }) {
  const agent = useAuthStore((state) => state.agent);
  // Include agent_id in queryKey to ensure different agents get different cache entries
  return useQuery({
    queryKey: ['tasks', agent?.id, params],
    queryFn: () => tasksApi.list(params),
    enabled: !!agent?.id, // Only fetch when agent is available
  });
}

export function useTask(id: number, options?: { enabled?: boolean }) {
  const agent = useAuthStore((state) => state.agent);
  return useQuery({
    queryKey: ['task', agent?.id, id],
    queryFn: () => tasksApi.getById(id),
    enabled: (options?.enabled !== false && id > 0 && !!agent?.id),
  });
}
