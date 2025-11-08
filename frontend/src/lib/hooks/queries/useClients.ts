import { useQuery } from '@tanstack/react-query';
import { clientsApi } from '@/lib/api/endpoints/clients';

export function useClients(params?: { page?: number; limit?: number; stage?: string; search?: string }) {
  return useQuery({
    queryKey: ['clients', params],
    queryFn: () => clientsApi.list(params),
  });
}

export function useClient(id: number, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ['client', id],
    queryFn: () => clientsApi.getById(id),
    enabled: options?.enabled !== false && id > 0 && !isNaN(id),
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
  return useQuery({
    queryKey: ['client', id, 'tasks'],
    queryFn: () => clientsApi.getTasks(id),
    enabled: !!id,
  });
}
