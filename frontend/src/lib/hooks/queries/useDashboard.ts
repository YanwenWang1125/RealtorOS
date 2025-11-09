import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/lib/api/endpoints/dashboard';
import { useAuthStore } from '@/store/useAuthStore';

export function useDashboardStats(options?: {
  refetchInterval?: number | false;
  refetchIntervalInBackground?: boolean;
}) {
  const agent = useAuthStore((state) => state.agent);
  // Include agent_id in queryKey to ensure different agents get different cache entries
  return useQuery({
    queryKey: ['dashboard', 'stats', agent?.id],
    queryFn: dashboardApi.getStats,
    enabled: !!agent?.id, // Only fetch when agent is available
    refetchInterval: options?.refetchInterval,
    refetchIntervalInBackground: options?.refetchIntervalInBackground
  });
}

export function useRecentActivity(limit?: number, options?: {
  refetchInterval?: number | false;
  refetchIntervalInBackground?: boolean;
}) {
  const agent = useAuthStore((state) => state.agent);
  // Include agent_id in queryKey to ensure different agents get different cache entries
  return useQuery({
    queryKey: ['dashboard', 'activity', agent?.id, limit],
    queryFn: () => dashboardApi.getRecentActivity(limit),
    enabled: !!agent?.id, // Only fetch when agent is available
    refetchInterval: options?.refetchInterval,
    refetchIntervalInBackground: options?.refetchIntervalInBackground
  });
}
