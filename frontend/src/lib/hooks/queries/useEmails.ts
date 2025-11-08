import { useQuery } from '@tanstack/react-query';
import { emailsApi } from '@/lib/api/endpoints/emails';

export function useEmails(params?: { page?: number; limit?: number; client_id?: number; status?: string }) {
  return useQuery({
    queryKey: ['emails', params],
    queryFn: () => emailsApi.list(params),
  });
}

export function useEmail(id: number, options?: { enabled?: boolean; refetchInterval?: number | ((data: any) => number | false) }) {
  return useQuery({
    queryKey: ['email', id],
    queryFn: () => emailsApi.getById(id),
    enabled: options?.enabled !== false && id > 0,
    refetchInterval: options?.refetchInterval,
  });
}
