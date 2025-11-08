import { analyticsClient } from '../client';
import { DashboardStats, ActivityItem } from '@/lib/types/dashboard.types';

export const dashboardApi = {
  getStats: async () => {
    const { data } = await analyticsClient.get<DashboardStats>('/api/dashboard/stats');
    return data;
  },

  getRecentActivity: async (limit?: number) => {
    const { data } = await analyticsClient.get<ActivityItem[]>('/api/dashboard/recent-activity', {
      params: { limit }
    });
    return data;
  },
};
