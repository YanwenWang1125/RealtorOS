'use client';

import { useState } from 'react';
import { Task } from '@/lib/types/task.types';
import { useUpdateTask } from '@/lib/hooks/mutations/useUpdateTask';
import { useToast } from '@/lib/hooks/ui/useToast';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/Button';
import { TaskRescheduleDialog } from '@/components/tasks/TaskRescheduleDialog';
import { MoreVertical, Calendar, CheckCircle, XCircle, SkipForward, Mail } from 'lucide-react';

interface TaskActionsMenuProps {
  task: Task;
}

export function TaskActionsMenu({ task }: TaskActionsMenuProps) {
  const { toast } = useToast();
  const updateTask = useUpdateTask();
  const [rescheduleOpen, setRescheduleOpen] = useState(false);

  const handleStatusChange = async (status: 'completed' | 'skipped' | 'cancelled') => {
    try {
      await updateTask.mutateAsync({
        id: task.id,
        data: { status }
      });
      toast({
        title: "Task updated",
        description: `Task marked as ${status}`,
      });
    } catch (error: any) {
      toast({
        title: "Error updating task",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => setRescheduleOpen(true)}>
            <Calendar className="h-4 w-4 mr-2" />
            Reschedule
          </DropdownMenuItem>

          {task.status === 'pending' && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleStatusChange('completed')}>
                <CheckCircle className="h-4 w-4 mr-2" />
                Mark Complete
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleStatusChange('skipped')}>
                <SkipForward className="h-4 w-4 mr-2" />
                Skip Task
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => handleStatusChange('cancelled')}
                className="text-destructive"
              >
                <XCircle className="h-4 w-4 mr-2" />
                Cancel Task
              </DropdownMenuItem>

              {!task.email_sent_id && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <Mail className="h-4 w-4 mr-2" />
                    Send Email
                  </DropdownMenuItem>
                </>
              )}
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>

      <TaskRescheduleDialog
        task={task}
        open={rescheduleOpen}
        onOpenChange={setRescheduleOpen}
      />
    </>
  );
}

