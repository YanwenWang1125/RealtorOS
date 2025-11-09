import { useQuery } from '@tanstack/react-query';
import { clientsApi } from '@/lib/api/endpoints/clients';
import { useAuthStore } from '@/store/useAuthStore';

export function useClients(params?: { page?: number; limit?: number; stage?: string; search?: string }) {
  const agent = useAuthStore((state) => state.agent);
  // Include agent_id in queryKey to ensure different agents get different cache entries
  return useQuery({
    queryKey: ['clients', agent?.id, params],
    queryFn: () => clientsApi.list(params),
    enabled: !!agent?.id, // Only fetch when agent is available
  });
}

export function useClient(id: number, options?: { enabled?: boolean }) {
  const agent = useAuthStore((state) => state.agent);
  return useQuery({
    queryKey: ['client', agent?.id, id],
    queryFn: () => clientsApi.getById(id),
    enabled: (options?.enabled !== false && id > 0 && !isNaN(id) && !!agent?.id),
    retry: (failureCount, error: any) => {
      // Don't retry on 404 errors (client not found)
      if (error?.response?.status === 404) {
        return false;
      }
      return failureCount < 2;
    },
  });
}

export function useClientTasks(id: number) {
  const agent = useAuthStore((state) => state.agent);
  return useQuery({
    queryKey: ['client', agent?.id, id, 'tasks'],
    queryFn: () => clientsApi.getTasks(id),
    enabled: !!id && !!agent?.id,
  });
}
