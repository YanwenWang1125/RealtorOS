import { ActivityItem } from '@/lib/types/dashboard.types';
import { formatRelativeTime } from '@/lib/utils/format';
import { Mail, UserPlus, CheckCircle, Eye, MousePointer } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils/cn';

interface ActivityItemComponentProps {
  activity: ActivityItem;
}

const activityIcons = {
  email_sent: Mail,
  email: Mail,
  client_created: UserPlus,
  task_completed: CheckCircle,
  email_opened: Eye,
  email_clicked: MousePointer
};

const activityColors = {
  email_sent: 'text-purple-600 bg-purple-100',
  email: 'text-purple-600 bg-purple-100',
  client_created: 'text-primary bg-primary/10',
  task_completed: 'text-green-600 bg-green-100',
  email_opened: 'text-teal-600 bg-teal-100',
  email_clicked: 'text-indigo-600 bg-indigo-100'
};

export function ActivityItemComponent({ activity }: ActivityItemComponentProps) {
  const Icon = activityIcons[activity.type as keyof typeof activityIcons] || Mail;
  const colorClass = activityColors[activity.type as keyof typeof activityColors] || 'text-muted-foreground bg-muted';

  // Determine link based on activity type
  let link = '#';
  if (activity.type === 'client_created' && activity.metadata?.client_id) {
    link = `/clients/${activity.metadata.client_id}`;
  } else if (activity.type === 'task_completed' && activity.metadata?.task_id) {
    link = `/tasks/${activity.metadata.task_id}`;
  } else if ((activity.type.includes('email') || activity.type === 'email_sent') && activity.metadata?.email_id) {
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

