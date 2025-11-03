'use client';

import { useState, useEffect } from 'react';
import { useDashboardStats, useRecentActivity } from '@/lib/hooks/queries/useDashboard';
import { Button } from '@/components/ui/Button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { StatsGrid } from '@/components/dashboard/StatsGrid';
import { ClientStageChart } from '@/components/dashboard/ClientStageChart';
import { EmailEngagementChart } from '@/components/dashboard/EmailEngagementChart';
import { ActivityFeed } from '@/components/dashboard/ActivityFeed';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { RefreshCw } from 'lucide-react';
import { formatDateTime } from '@/lib/utils/format';

export default function DashboardPage() {
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const {
    data: stats,
    isLoading: statsLoading,
    refetch: refetchStats,
    isFetching: statsFetching
  } = useDashboardStats({
    refetchInterval: autoRefresh ? 60000 : false, // 60 seconds
    refetchIntervalInBackground: false
  });

  const {
    data: activities,
    isLoading: activitiesLoading,
    refetch: refetchActivities,
    isFetching: activitiesFetching
  } = useRecentActivity(10, {
    refetchInterval: autoRefresh ? 30000 : false, // 30 seconds
    refetchIntervalInBackground: false
  });

  // Update last updated timestamp
  useEffect(() => {
    if (stats) {
      setLastUpdated(new Date());
    }
  }, [stats]);

  const handleManualRefresh = () => {
    refetchStats();
    refetchActivities();
    setLastUpdated(new Date());
  };

  const isRefreshing = statsFetching || activitiesFetching;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Last updated: {formatDateTime(lastUpdated)}
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Auto-refresh Toggle */}
          <div className="flex items-center space-x-2">
            <Switch
              id="auto-refresh"
              checked={autoRefresh}
              onCheckedChange={setAutoRefresh}
            />
            <Label htmlFor="auto-refresh" className="cursor-pointer">
              Auto-refresh
            </Label>
          </div>

          {/* Manual Refresh Button */}
          <Button
            variant="outline"
            onClick={handleManualRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <StatsGrid stats={stats} isLoading={statsLoading} />

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ClientStageChart stats={stats} isLoading={statsLoading} />
        <EmailEngagementChart stats={stats} isLoading={statsLoading} />
      </div>

      {/* Activity Feed and Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ActivityFeed
            activities={activities || []}
            isLoading={activitiesLoading}
          />
        </div>
        <div>
          <QuickActions />
        </div>
      </div>
    </div>
  );
}
