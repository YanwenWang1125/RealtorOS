'use client';

import { useState, useId } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { taskCreateSchema, TaskCreateFormData } from '@/lib/schemas/task.schema';
import { useCreateTask } from '@/lib/hooks/mutations/useCreateTask';
import { useToast } from '@/lib/hooks/ui/useToast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Calendar } from '@/components/ui/calendar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { ClientAutocomplete } from '@/components/tasks/ClientAutocomplete';
import { PRIORITY_LEVELS, PRIORITY_LABELS } from '@/lib/constants/task.constants';

interface CreateTaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultClientId?: number;
}

export function CreateTaskDialog({ open, onOpenChange, defaultClientId }: CreateTaskDialogProps) {
  const { toast } = useToast();
  const createTask = useCreateTask();
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [selectedTime, setSelectedTime] = useState<string>('09:00');

  const form = useForm<TaskCreateFormData>({
    resolver: zodResolver(taskCreateSchema),
    defaultValues: {
      client_id: defaultClientId ?? null,
      followup_type: 'Custom',
      scheduled_for: new Date().toISOString(),
      priority: 'medium',
      notes: '',
    },
    mode: 'onSubmit',
    reValidateMode: 'onChange',
  });

  const clientFieldId = useId();
  const timeFieldId = useId();

  const handleSubmit = async (data: TaskCreateFormData) => {
    try {
      // Combine date + time
      const [hours, minutes] = selectedTime.split(':');
      const scheduledDate = new Date(selectedDate);
      scheduledDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      await createTask.mutateAsync({
        ...data,
        scheduled_for: scheduledDate.toISOString(),
      });

      toast({
        title: 'Task created',
        description: 'Custom follow-up task added successfully.',
      });

      form.reset();
      setSelectedDate(new Date());
      setSelectedTime('09:00');
      onOpenChange(false);
    } catch (error: any) {
      toast({
        title: 'Error creating task',
        description: error?.response?.data?.detail || 'Please try again.',
        variant: 'destructive',
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Custom Task</DialogTitle>
          <DialogDescription>Add a custom follow-up task for a client.</DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-5">
            {/* Client */}
            <FormField
              control={form.control}
              name="client_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor={clientFieldId}>Client *</FormLabel>
                  <FormControl>
                    <ClientAutocomplete
                      id={clientFieldId}
                      value={field.value}
                      onChange={(id) => field.onChange(id)}
                      disabled={createTask.isPending}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Priority */}
            <FormField
              control={form.control}
              name="priority"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Priority *</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={String(field.value || 'medium')}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {PRIORITY_LEVELS.map((priority) => (
                        <SelectItem key={priority} value={priority}>
                          {PRIORITY_LABELS[priority]}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Date */}
            <div className="space-y-2">
              <Label>Scheduled Date *</Label>
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={(date) => date && setSelectedDate(date)}
                disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
                className="rounded-md border"
              />
            </div>

            {/* Time */}
            <div className="space-y-2">
              <Label htmlFor={timeFieldId}>Scheduled Time *</Label>
              <Input
                id={timeFieldId}
                type="time"
                value={selectedTime}
                onChange={(e) => setSelectedTime(e.target.value)}
              />
            </div>

            {/* Notes */}
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Add notes about this task..."
                      className="resize-none"
                      rows={3}
                      {...field}
                      maxLength={500}
                    />
                  </FormControl>
                  <FormDescription>{field.value?.length || 0}/500 characters</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={createTask.isPending}>
                {createTask.isPending ? 'Creating...' : 'Create Task'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
