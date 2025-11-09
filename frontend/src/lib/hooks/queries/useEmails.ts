import { useQuery } from '@tanstack/react-query';
import { emailsApi } from '@/lib/api/endpoints/emails';
import { useAuthStore } from '@/store/useAuthStore';

export function useEmails(params?: { page?: number; limit?: number; client_id?: number; status?: string }) {
  const agent = useAuthStore((state) => state.agent);
  // Include agent_id in queryKey to ensure different agents get different cache entries
  return useQuery({
    queryKey: ['emails', agent?.id, params],
    queryFn: () => emailsApi.list(params),
    enabled: !!agent?.id, // Only fetch when agent is available
  });
}

export function useEmail(id: number, options?: { enabled?: boolean; refetchInterval?: number | ((data: any) => number | false) }) {
  const agent = useAuthStore((state) => state.agent);
  return useQuery({
    queryKey: ['email', agent?.id, id],
    queryFn: () => emailsApi.getById(id),
    enabled: (options?.enabled !== false && id > 0 && !!agent?.id),
    refetchInterval: options?.refetchInterval,
  });
}
