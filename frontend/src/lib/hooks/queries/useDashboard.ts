import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/lib/api/endpoints/dashboard';

export function useDashboardStats(options?: {
  refetchInterval?: number | false;
  refetchIntervalInBackground?: boolean;
}) {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: dashboardApi.getStats,
    refetchInterval: options?.refetchInterval,
    refetchIntervalInBackground: options?.refetchIntervalInBackground
  });
}

export function useRecentActivity(limit?: number, options?: {
  refetchInterval?: number | false;
  refetchIntervalInBackground?: boolean;
}) {
  return useQuery({
    queryKey: ['dashboard', 'activity', limit],
    queryFn: () => dashboardApi.getRecentActivity(limit),
    refetchInterval: options?.refetchInterval,
    refetchIntervalInBackground: options?.refetchIntervalInBackground
  });
}
