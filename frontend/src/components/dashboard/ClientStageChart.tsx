'use client';

import { DashboardStats } from '@/lib/types/dashboard.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/skeleton';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { useClients } from '@/lib/hooks/queries/useClients';
import { useMemo } from 'react';
import { CLIENT_STAGE_LABELS } from '@/lib/constants/client.constants';

interface ClientStageChartProps {
  stats?: DashboardStats;
  isLoading: boolean;
}

const COLORS = {
  lead: '#3B82F6',         // blue
  negotiating: '#F59E0B',  // orange
  under_contract: '#8B5CF6', // purple
  closed: '#10B981',       // green
  lost: '#EF4444'          // red
};

export function ClientStageChart({ stats, isLoading }: ClientStageChartProps) {
  const { data: clients } = useClients({ limit: 1000 });

  const chartData = useMemo(() => {
    if (!clients) return [];

    const stageCounts: Record<string, number> = {};

    clients.forEach(client => {
      stageCounts[client.stage] = (stageCounts[client.stage] || 0) + 1;
    });

    return Object.entries(stageCounts).map(([stage, count]) => ({
      name: CLIENT_STAGE_LABELS[stage as keyof typeof CLIENT_STAGE_LABELS],
      value: count,
      stage
    }));
  }, [clients]);

  if (isLoading || chartData.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Client Stage Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Client Stage Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[entry.stage as keyof typeof COLORS] || '#8884d8'}
                />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

