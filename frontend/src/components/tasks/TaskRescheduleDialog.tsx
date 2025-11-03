
'use client';

import { useState, useId } from 'react';
import { Task } from '@/lib/types/task.types';
import { useUpdateTask } from '@/lib/hooks/mutations/useUpdateTask';
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
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/label';
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
  const timeFieldId = useId();

  const { toast } = useToast();
  const updateTask = useUpdateTask();

  const handleReschedule = async () => {
    try {
      // Combine date and time
      const [hours, minutes] = selectedTime.split(':');
      const newDate = new Date(selectedDate);
      newDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      await updateTask.mutateAsync({
        id: task.id,
        data: { scheduled_for: newDate.toISOString() }
      });

      toast({
        title: "Task rescheduled",
        description: `Task scheduled for ${formatDate(newDate.toISOString(), 'PPP p')}`,
      });

      onOpenChange(false);
    } catch (error: any) {
      toast({
        title: "Error rescheduling task",
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
            Choose a new date and time for this task
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
            <Label htmlFor={timeFieldId}>Time</Label>
            <Input
              id={timeFieldId}
              type="time"
              value={selectedTime}
              onChange={(e) => setSelectedTime(e.target.value)}
            />
          </div>

          <div className="text-sm text-muted-foreground">
            Current: {formatDate(currentDate.toISOString(), 'PPP p')}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleReschedule} disabled={updateTask.isPending}>
            {updateTask.isPending ? 'Rescheduling...' : 'Reschedule'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

