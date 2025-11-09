import { analyticsClient } from '../client';
import { DashboardStats, ActivityItem } from '@/lib/types/dashboard.types';
import { getApiPath } from '../utils/path';

export const dashboardApi = {
  getStats: async () => {
    const path = getApiPath(analyticsClient.defaults.baseURL, '/dashboard/stats');
    const { data } = await analyticsClient.get<DashboardStats>(path);
    return data;
  },

  getRecentActivity: async (limit?: number) => {
    const path = getApiPath(analyticsClient.defaults.baseURL, '/dashboard/recent-activity');
    const { data } = await analyticsClient.get<ActivityItem[]>(path, {
      params: { limit }
    });
    return data;
  },
};
