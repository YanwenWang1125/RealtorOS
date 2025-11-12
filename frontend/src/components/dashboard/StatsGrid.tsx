import { DashboardStats } from '@/lib/types/dashboard.types';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { Skeleton } from '@/components/ui/skeleton';
import { Users, UserCheck, Calendar, CheckCircle, Mail, MailOpen, MousePointer, TrendingUp } from 'lucide-react';

interface StatsGridProps {
  stats?: DashboardStats;
  isLoading: boolean;
}

export function StatsGrid({ stats, isLoading }: StatsGridProps) {
  if (isLoading || !stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: 'Total Clients',
      value: stats.total_clients,
      icon: Users,
      link: '/clients',
      color: 'text-primary'
    },
    {
      title: 'Active Clients',
      value: stats.active_clients,
      icon: UserCheck,
      link: '/clients?stage=lead,negotiating',
      color: 'text-green-600'
    },
    {
      title: 'Pending Tasks',
      value: stats.pending_tasks,
      icon: Calendar,
      link: '/tasks?status=pending',
      color: 'text-yellow-600'
    },
    {
      title: 'Completed Tasks',
      value: stats.completed_tasks,
      icon: CheckCircle,
      link: '/tasks?status=completed',
      color: 'text-green-600'
    },
    {
      title: 'Emails Today',
      value: stats.emails_sent_today,
      icon: Mail,
      link: '/emails',
      color: 'text-purple-600'
    },
    {
      title: 'Emails This Week',
      value: stats.emails_sent_this_week,
      icon: Mail,
      link: '/emails',
      color: 'text-purple-600'
    },
    {
      title: 'Open Rate',
      value: `${stats.open_rate.toFixed(1)}%`,
      icon: MailOpen,
      color: stats.open_rate >= 30 ? 'text-green-600' : stats.open_rate >= 20 ? 'text-yellow-600' : 'text-red-600',
      description: stats.open_rate >= 30 ? 'Excellent' : stats.open_rate >= 20 ? 'Good' : 'Needs improvement'
    },
    {
      title: 'Click Rate',
      value: `${stats.click_rate.toFixed(1)}%`,
      icon: MousePointer,
      color: stats.click_rate >= 10 ? 'text-green-600' : stats.click_rate >= 5 ? 'text-yellow-600' : 'text-red-600',
      description: stats.click_rate >= 10 ? 'Excellent' : stats.click_rate >= 5 ? 'Good' : 'Needs improvement'
    },
    {
      title: 'Conversion Rate',
      value: `${stats.conversion_rate.toFixed(1)}%`,
      icon: TrendingUp,
      link: '/clients?stage=closed',
      color: stats.conversion_rate >= 20 ? 'text-green-600' : stats.conversion_rate >= 10 ? 'text-yellow-600' : 'text-red-600',
      description: 'Leads to Closed'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <StatsCard key={index} {...card} />
      ))}
    </div>
  );
}

