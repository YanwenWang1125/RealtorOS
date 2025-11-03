import { Badge } from '@/components/ui/badge';
import { Priority } from '@/lib/types/task.types';
import { PRIORITY_LABELS, PRIORITY_COLORS } from '@/lib/constants/task.constants';
import { cn } from '@/lib/utils/index';

interface TaskPriorityBadgeProps {
  priority: Priority;
}

export function TaskPriorityBadge({ priority }: TaskPriorityBadgeProps) {
  return (
    <Badge className={cn(PRIORITY_COLORS[priority])}>
      {PRIORITY_LABELS[priority]}
    </Badge>
  );
}

