import { Badge } from '@/components/ui/badge';
import { TaskStatus } from '@/lib/types/task.types';
import { TASK_STATUS_LABELS, TASK_STATUS_COLORS } from '@/lib/constants/task.constants';
import { cn } from '@/lib/utils/index';

interface TaskStatusBadgeProps {
  status: TaskStatus;
}

export function TaskStatusBadge({ status }: TaskStatusBadgeProps) {
  return (
    <Badge className={cn(TASK_STATUS_COLORS[status])}>
      {TASK_STATUS_LABELS[status]}
    </Badge>
  );
}

