'use client';

import { DashboardStats } from '@/lib/types/dashboard.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface EmailEngagementChartProps {
  stats?: DashboardStats;
  isLoading: boolean;
}

export function EmailEngagementChart({ stats, isLoading }: EmailEngagementChartProps) {
  if (isLoading || !stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Email Engagement Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    );
  }

  const chartData = [
    {
      name: 'Today',
      sent: stats.emails_sent_today,
      opened: Math.round(stats.emails_sent_today * (stats.open_rate / 100)),
      clicked: Math.round(stats.emails_sent_today * (stats.click_rate / 100))
    },
    {
      name: 'This Week',
      sent: stats.emails_sent_this_week,
      opened: Math.round(stats.emails_sent_this_week * (stats.open_rate / 100)),
      clicked: Math.round(stats.emails_sent_this_week * (stats.click_rate / 100))
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Email Engagement Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="sent" fill="#8B5CF6" name="Sent" />
            <Bar dataKey="opened" fill="#10B981" name="Opened" />
            <Bar dataKey="clicked" fill="#3B82F6" name="Clicked" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

