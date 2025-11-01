import { Calendar } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Task } from '@/lib/types/task.types';
import { TASK_STATUS_LABELS, TASK_STATUS_COLORS } from '@/lib/constants/task.constants';
import { formatDateString } from '@/lib/utils/format';
import { cn } from '@/lib/utils/index';

export function ClientTimeline({ tasks }: { tasks: Task[] }) {
  if (tasks.length === 0) {
    return (
      <EmptyState
        icon={Calendar}
        title="No tasks yet"
        description="Follow-up tasks are being created in the background."
      />
    );
  }

  const sortedTasks = [...tasks].sort(
    (a, b) => new Date(a.scheduled_for).getTime() - new Date(b.scheduled_for).getTime()
  );

  return (
    <div className="space-y-4">
      {sortedTasks.map((task, index) => (
        <div key={task.id} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div
              className={cn(
                "w-3 h-3 rounded-full flex-shrink-0 mt-1",
                task.status === 'completed' ? "bg-green-500" :
                task.status === 'pending' ? "bg-yellow-500" :
                "bg-gray-300"
              )}
            />
            {index < sortedTasks.length - 1 && (
              <div className="w-px h-full bg-border mt-1 min-h-[40px]" />
            )}
          </div>
          <Card className="flex-1">
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{task.followup_type}</h3>
                  <p className="text-sm text-muted-foreground">
                    {formatDateString(task.scheduled_for)}
                  </p>
                  {task.notes && (
                    <p className="text-sm text-muted-foreground mt-1">{task.notes}</p>
                  )}
                </div>
                <Badge className={TASK_STATUS_COLORS[task.status]}>
                  {TASK_STATUS_LABELS[task.status]}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      ))}
    </div>
  );
}

