# CURSOR PROMPT: RealtorOS - MODULE 4 - DASHBOARD

## OBJECTIVE
Build the complete DASHBOARD module for RealtorOS CRM. This includes KPI statistics cards, data visualizations (charts), recent activity feed, quick actions, and real-time auto-refresh functionality. This module aggregates data from all other modules (Clients, Tasks, Emails).

---

## PREREQUISITES VERIFICATION

Before starting, verify these exist:
- ✅ `src/lib/types/dashboard.types.ts` - Dashboard TypeScript types
- ✅ `src/lib/api/endpoints/dashboard.ts` - Dashboard API functions
- ✅ `src/lib/hooks/queries/useDashboard.ts` - React Query hooks
- ✅ **Module 1 (Clients) completed** - Client stats displayed
- ✅ **Module 2 (Tasks) completed** - Task stats displayed
- ✅ **Module 3 (Emails) completed** - Email stats displayed
- ✅ Backend API running at `http://localhost:8000`

---

## MODULE 4: DASHBOARD - COMPLETE IMPLEMENTATION

### **TASK 4.1: Dashboard Page**

**File:** `src/app/(dashboard)/page.tsx`

**Requirements:**
Comprehensive dashboard with KPIs, charts, activity feed, and quick actions.

**Layout:**
1. **Page Header:**
   - Heading: "Dashboard"
   - Auto-refresh toggle (ON/OFF)
   - Manual refresh button
   - Last updated timestamp

2. **KPI Stats Grid (2x5 or 3x3 layout):**
   - Total Clients
   - Active Clients (lead, negotiating, under_contract)
   - Pending Tasks
   - Completed Tasks
   - Emails Sent Today
   - Emails Sent This Week
   - Open Rate %
   - Click Rate %
   - Conversion Rate %

3. **Charts Section (2 columns):**
   - Client Stage Distribution (Pie Chart)
   - Email Engagement Over Time (Line Chart)

4. **Activity Feed:**
   - Recent 10 activities
   - Load more button
   - Auto-refresh every 30 seconds

5. **Quick Actions (Floating or Sidebar):**
   - Create New Client
   - Send Email
   - View Overdue Tasks

**Implementation:**
```tsx
'use client';

import { useState, useEffect } from 'react';
import { useDashboardStats, useRecentActivity } from '@/lib/hooks/queries/useDashboard';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { StatsGrid } from '@/components/dashboard/StatsGrid';
import { ClientStageChart } from '@/components/dashboard/ClientStageChart';
import { EmailEngagementChart } from '@/components/dashboard/EmailEngagementChart';
import { ActivityFeed } from '@/components/dashboard/ActivityFeed';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { RefreshCw } from 'lucide-react';
import { formatDateTime } from '@/lib/utils/date';

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
```

---

### **TASK 4.2: Stats Grid Component**

**File:** `src/components/dashboard/StatsGrid.tsx`

**Implementation:**
```tsx
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
      color: 'text-blue-600'
    },
    {
      title: 'Active Clients',
      value: stats.active_clients,
      icon: UserCheck,
      link: '/clients?stage=lead,negotiating,under_contract',
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
```

---

### **TASK 4.3: Stats Card Component**

**File:** `src/components/dashboard/StatsCard.tsx`

```tsx
'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import Link from 'next/link';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color?: string;
  link?: string;
  description?: string;
}

export function StatsCard({
  title,
  value,
  icon: Icon,
  color = 'text-blue-600',
  link,
  description
}: StatsCardProps) {
  const CardWrapper = link ? Link : 'div';

  return (
    <CardWrapper href={link || '#'} className={link ? 'block' : ''}>
      <Card className={cn(
        'hover:shadow-md transition-shadow',
        link && 'cursor-pointer hover:border-primary'
      )}>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <Icon className={cn('h-5 w-5', color)} />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{value}</div>
          {description && (
            <p className="text-xs text-muted-foreground mt-1">{description}</p>
          )}
        </CardContent>
      </Card>
    </CardWrapper>
  );
}
```

---

### **TASK 4.4: Client Stage Chart**

**File:** `src/components/dashboard/ClientStageChart.tsx`

**Installation:**
```bash
npm install recharts
```

**Implementation:**
```tsx
'use client';

import { DashboardStats } from '@/lib/types/dashboard.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
      if (!client.is_deleted) {
        stageCounts[client.stage] = (stageCounts[client.stage] || 0) + 1;
      }
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
```

---

### **TASK 4.5: Email Engagement Chart**

**File:** `src/components/dashboard/EmailEngagementChart.tsx`

```tsx
'use client';

import { DashboardStats } from '@/lib/types/dashboard.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
```

---

### **TASK 4.6: Activity Feed Component**

**File:** `src/components/dashboard/ActivityFeed.tsx`

```tsx
'use client';

import { useState } from 'react';
import { ActivityItem } from '@/lib/types/dashboard.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ActivityItemComponent } from '@/components/dashboard/ActivityItemComponent';
import { EmptyState } from '@/components/ui/EmptyState';
import { Activity } from 'lucide-react';

interface ActivityFeedProps {
  activities: ActivityItem[];
  isLoading: boolean;
}

export function ActivityFeed({ activities, isLoading }: ActivityFeedProps) {
  const [showAll, setShowAll] = useState(false);

  const displayedActivities = showAll ? activities : activities.slice(0, 10);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <EmptyState
            icon={Activity}
            title="No recent activity"
            description="Activity will appear here as you use the system"
          />
        ) : (
          <div className="space-y-4">
            {displayedActivities.map((activity, index) => (
              <ActivityItemComponent key={activity.id || index} activity={activity} />
            ))}

            {activities.length > 10 && !showAll && (
              <Button
                variant="outline"
                className="w-full"
                onClick={() => setShowAll(true)}
              >
                Load More
              </Button>
            )}

            {showAll && (
              <Button
                variant="outline"
                className="w-full"
                onClick={() => setShowAll(false)}
              >
                Show Less
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

---

### **TASK 4.7: Activity Item Component**

**File:** `src/components/dashboard/ActivityItemComponent.tsx`

```tsx
import { ActivityItem } from '@/lib/types/dashboard.types';
import { formatRelativeTime } from '@/lib/utils/date';
import { Mail, UserPlus, CheckCircle, Eye, MousePointer } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils/cn';

interface ActivityItemComponentProps {
  activity: ActivityItem;
}

const activityIcons = {
  email: Mail,
  client_created: UserPlus,
  task_completed: CheckCircle,
  email_opened: Eye,
  email_clicked: MousePointer
};

const activityColors = {
  email: 'text-purple-600 bg-purple-100',
  client_created: 'text-blue-600 bg-blue-100',
  task_completed: 'text-green-600 bg-green-100',
  email_opened: 'text-teal-600 bg-teal-100',
  email_clicked: 'text-indigo-600 bg-indigo-100'
};

export function ActivityItemComponent({ activity }: ActivityItemComponentProps) {
  const Icon = activityIcons[activity.type as keyof typeof activityIcons] || Mail;
  const colorClass = activityColors[activity.type as keyof typeof activityColors] || 'text-gray-600 bg-gray-100';

  // Determine link based on activity type
  let link = '#';
  if (activity.type === 'client_created' && activity.metadata?.client_id) {
    link = `/clients/${activity.metadata.client_id}`;
  } else if (activity.type === 'task_completed' && activity.metadata?.task_id) {
    link = `/tasks/${activity.metadata.task_id}`;
  } else if (activity.type.includes('email') && activity.metadata?.email_id) {
    link = `/emails/${activity.metadata.email_id}`;
  }

  return (
    <Link href={link}>
      <div className="flex gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
        <div className={cn('w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0', colorClass)}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">
            {activity.description}
          </p>
          <p className="text-xs text-muted-foreground">
            {formatRelativeTime(activity.timestamp)}
          </p>
        </div>
      </div>
    </Link>
  );
}
```

---

### **TASK 4.8: Quick Actions Component**

**File:** `src/components/dashboard/QuickActions.tsx`

```tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { UserPlus, Mail, AlertCircle } from 'lucide-react';

export function QuickActions() {
  const router = useRouter();

  const actions = [
    {
      label: 'Create New Client',
      description: 'Add a new client to your CRM',
      icon: UserPlus,
      onClick: () => router.push('/clients/new'),
      color: 'bg-blue-100 text-blue-600 hover:bg-blue-200'
    },
    {
      label: 'Send Email',
      description: 'Compose and send an email',
      icon: Mail,
      onClick: () => router.push('/emails'),
      color: 'bg-purple-100 text-purple-600 hover:bg-purple-200'
    },
    {
      label: 'View Overdue Tasks',
      description: 'Check tasks that need attention',
      icon: AlertCircle,
      onClick: () => router.push('/tasks?filter=overdue'),
      color: 'bg-red-100 text-red-600 hover:bg-red-200'
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <Button
              key={index}
              variant="outline"
              className="w-full justify-start h-auto py-3"
              onClick={action.onClick}
            >
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center mr-3 ${action.color}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="text-left">
                <p className="font-medium text-sm">{action.label}</p>
                <p className="text-xs text-muted-foreground">{action.description}</p>
              </div>
            </Button>
          );
        })}
      </CardContent>
    </Card>
  );
}
```

---

### **TASK 4.9: Update Dashboard Query Hooks**

**File:** `src/lib/hooks/queries/useDashboard.ts`

```typescript
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
```

---

### **TASK 4.10: Add Switch Component (if not exists)**

**Installation:**
```bash
npx shadcn-ui@latest add switch
```

---

## TESTING CHECKLIST

After implementing all tasks, verify:

### **Functionality:**
- [ ] Dashboard page loads successfully
- [ ] All 9 KPI cards display correctly
- [ ] Stats refresh when clicking refresh button
- [ ] Auto-refresh toggle works (60s for stats, 30s for activity)
- [ ] Last updated timestamp updates
- [ ] Client stage pie chart renders correctly
- [ ] Email engagement bar chart renders correctly
- [ ] Activity feed displays recent activities
- [ ] Load more button works in activity feed
- [ ] Quick action buttons navigate correctly
- [ ] Clicking KPI cards navigates to filtered views
- [ ] Color coding works (green/yellow/red for rates)

### **Auto-Refresh:**
- [ ] Stats auto-refresh every 60 seconds when enabled
- [ ] Activity feed auto-refreshes every 30 seconds when enabled
- [ ] Refresh stops when toggle is off
- [ ] No refresh when tab is in background (refetchIntervalInBackground: false)
- [ ] Loading indicator shows during refresh

### **UI/UX:**
- [ ] Loading skeletons appear while fetching
- [ ] Empty state for activity feed
- [ ] Charts responsive on mobile
- [ ] Stats grid adapts to screen size
- [ ] Smooth animations during refresh
- [ ] No layout shift during data updates

### **Performance:**
- [ ] Dashboard loads in < 2 seconds
- [ ] Charts render smoothly
- [ ] Auto-refresh doesn't impact UI performance
- [ ] No memory leaks from intervals

---

## COMMON ISSUES & SOLUTIONS

### **Issue: "Charts not rendering"**
**Solution:** Ensure recharts is installed:
```bash
npm install recharts
```

### **Issue: "Auto-refresh not working"**
**Solution:** Check refetchInterval in query hook:
```typescript
refetchInterval: autoRefresh ? 60000 : false
```

### **Issue: "Stats showing stale data"**
**Solution:** Invalidate queries on mutations:
```typescript
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: ['dashboard'] });
}
```

### **Issue: "Activity feed empty"**
**Solution:** Check backend implementation of recent activity endpoint. May need to implement activity logging in backend.

### **Issue: "Charts overlapping on mobile"**
**Solution:** Use grid breakpoints:
```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
```

---

## SUCCESS CRITERIA

Module 4 (Dashboard) is complete when:
- ✅ All 9 KPI cards displaying correct data
- ✅ Client stage pie chart working
- ✅ Email engagement bar chart working
- ✅ Activity feed showing recent activities
- ✅ Auto-refresh working (stats: 60s, activity: 30s)
- ✅ Manual refresh button working
- ✅ Quick actions navigating correctly
- ✅ KPI cards linking to filtered views
- ✅ Color coding for rates (green/yellow/red)
- ✅ Loading states for all sections
- ✅ Responsive on all screen sizes
- ✅ Last updated timestamp accurate

---

## FINAL INTEGRATION CHECKLIST

After completing all 4 modules, verify end-to-end workflows:

### **Workflow 1: Client Onboarding**
- [ ] Create client → tasks auto-created in background
- [ ] Navigate to client detail → see 5 tasks
- [ ] Dashboard updates with new client count
- [ ] Activity feed shows "Client created" event

### **Workflow 2: Email Send**
- [ ] From task detail, click "Send Email"
- [ ] Email preview modal opens with AI-generated content
- [ ] Edit and send email
- [ ] Email appears in email list
- [ ] Task marked as completed
- [ ] Dashboard email count updates
- [ ] Activity feed shows "Email sent" event

### **Workflow 3: Email Engagement**
- [ ] Open email detail page
- [ ] See engagement timeline
- [ ] Wait for email to be opened (test with real email)
- [ ] Page auto-refreshes every 10 seconds
- [ ] Engagement icons update when opened
- [ ] Activity feed shows "Email opened" event

### **Workflow 4: Task Management**
- [ ] View tasks in calendar view
- [ ] Click task → detail modal opens
- [ ] Reschedule task → date picker works
- [ ] Mark task complete → status updates
- [ ] Dashboard pending tasks count decreases
- [ ] Activity feed shows "Task completed" event

### **Performance Testing:**
- [ ] All pages load in < 2 seconds
- [ ] Dashboard refresh doesn't freeze UI
- [ ] No console errors
- [ ] No memory leaks (check Chrome DevTools)
- [ ] Smooth transitions between pages

---

## DEPLOYMENT PREPARATION

Before deploying to production:

1. **Environment Variables:**
   - Set `NEXT_PUBLIC_API_URL` to production API
   - Verify all API keys configured on backend

2. **Build Test:**
   ```bash
   npm run build
   npm run start
   ```
   - Verify no build errors
   - Test all features in production mode

3. **Performance Audit:**
   - Run Lighthouse audit
   - Optimize images if needed
   - Check bundle size

4. **Error Tracking:**
   - Set up Sentry or similar
   - Add error boundaries

5. **Analytics:**
   - Set up Google Analytics or similar
   - Track key user actions

---

## CONGRATULATIONS!

You've completed all 4 modules of RealtorOS CRM:
- ✅ **Module 1: Clients** - Client management with custom fields
- ✅ **Module 2: Tasks** - Task scheduling with calendar view
- ✅ **Module 3: Emails** - AI-powered email with engagement tracking
- ✅ **Module 4: Dashboard** - Real-time analytics and insights

**Your RealtorOS CRM is now production-ready!** 🎉

---

**START IMPLEMENTING MODULE 4 NOW!** This is the final module. Follow tasks in order (4.1 → 4.10). Test thoroughly. Good luck! 🚀
