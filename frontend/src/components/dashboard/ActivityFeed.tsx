'use client';

import { useState } from 'react';
import { ActivityItem } from '@/lib/types/dashboard.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
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

