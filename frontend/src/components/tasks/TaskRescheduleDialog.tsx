
'use client';

import { useState } from 'react';
import { Task, Priority, TaskStatus } from '@/lib/types/task.types';
import { useUpdateTask } from '@/lib/hooks/mutations/useUpdateTask';
import { useDeleteTask } from '@/lib/hooks/mutations/useDeleteTask';
import { useToast } from '@/lib/hooks/ui/useToast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/Button';
import { Calendar } from '@/components/ui/calendar';
import { Label } from '@/components/ui/label';
import { TimePicker } from '@/components/ui/time-picker';
import { TaskPriorityBadge } from '@/components/tasks/TaskPriorityBadge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { PRIORITY_LEVELS, PRIORITY_LABELS, TASK_STATUSES, TASK_STATUS_LABELS } from '@/lib/constants/task.constants';
import { formatDate } from '@/lib/utils/date';

interface TaskRescheduleDialogProps {
  task: Task;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TaskRescheduleDialog({ task, open, onOpenChange }: TaskRescheduleDialogProps) {
  const currentDate = new Date(task.scheduled_for);
  const [selectedDate, setSelectedDate] = useState<Date>(currentDate);
  const [selectedTime, setSelectedTime] = useState<string>(
    currentDate.toTimeString().slice(0, 5) // HH:MM
  );
  const [selectedPriority, setSelectedPriority] = useState<Priority>(task.priority);
  const [selectedStatus, setSelectedStatus] = useState<TaskStatus>(task.status);

  const { toast } = useToast();
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();

  const handleReschedule = async () => {
    try {
      // Combine date and time
      const [hours, minutes] = selectedTime.split(':');
      const newDate = new Date(selectedDate);
      newDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      // Prepare update data
      const updateData: { scheduled_for: string; priority?: Priority; status?: TaskStatus } = {
        scheduled_for: newDate.toISOString()
      };
      
      // Only include priority if it changed
      if (selectedPriority !== task.priority) {
        updateData.priority = selectedPriority;
      }

      // Only include status if it changed
      if (selectedStatus !== task.status) {
        updateData.status = selectedStatus;
      }

      await updateTask.mutateAsync({
        id: task.id,
        data: updateData
      });

      const changes: string[] = [];
      if (selectedPriority !== task.priority) {
        changes.push(`priority changed to ${PRIORITY_LABELS[selectedPriority]}`);
      }
      if (selectedStatus !== task.status) {
        changes.push(`status changed to ${TASK_STATUS_LABELS[selectedStatus]}`);
      }
      const changesText = changes.length > 0 ? ` and ${changes.join(', ')}` : '';

      toast({
        title: "Task updated",
        description: `Task scheduled for ${formatDate(newDate.toISOString(), 'PPP p')}${changesText}`,
      });

      onOpenChange(false);
    } catch (error: any) {
      toast({
        title: "Error updating task",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task? This will also delete all associated emails.')) {
      return;
    }

    try {
      await deleteTask.mutateAsync(task.id);
      toast({
        title: "Task deleted",
        description: "Task and associated emails have been deleted.",
      });
      onOpenChange(false);
    } catch (error: any) {
      toast({
        title: "Error deleting task",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Reschedule Task</DialogTitle>
          <DialogDescription>
            Choose a new date, time, status, and priority for this task
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>Date</Label>
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={(date) => date && setSelectedDate(date)}
              disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
              className="rounded-md border"
            />
          </div>

          <div className="space-y-2">
            <Label>Time</Label>
            <TimePicker
              value={selectedTime}
              onChange={setSelectedTime}
              disabled={updateTask.isPending}
              placeholder="Select time"
            />
          </div>

          <div className="space-y-2">
            <Label>Status</Label>
            <Select
              value={selectedStatus}
              onValueChange={(value) => setSelectedStatus(value as TaskStatus)}
              disabled={updateTask.isPending}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                {TASK_STATUSES.map((status) => (
                  <SelectItem key={status} value={status}>
                    {TASK_STATUS_LABELS[status]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Priority</Label>
            <Select
              value={selectedPriority}
              onValueChange={(value) => setSelectedPriority(value as Priority)}
              disabled={updateTask.isPending}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select priority" />
              </SelectTrigger>
              <SelectContent>
                {PRIORITY_LEVELS.map((priority) => (
                  <SelectItem key={priority} value={priority}>
                    {PRIORITY_LABELS[priority]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="text-sm text-muted-foreground space-y-1">
            <div>Current schedule: {formatDate(currentDate.toISOString(), 'PPP p')}</div>
            <div>Current status: {TASK_STATUS_LABELS[task.status]}</div>
            <div>Current priority: <TaskPriorityBadge priority={task.priority} /></div>
          </div>
        </div>

        <DialogFooter className="flex justify-between">
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deleteTask.isPending || updateTask.isPending}
          >
            {deleteTask.isPending ? 'Deleting...' : 'Delete Task'}
          </Button>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button onClick={handleReschedule} disabled={updateTask.isPending || deleteTask.isPending}>
              {updateTask.isPending ? 'Updating...' : 'Update Task'}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

