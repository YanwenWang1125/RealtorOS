'use client';

import { useState } from 'react';
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
import { Button } from '@/components/ui/Button';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { FOLLOWUP_TYPES } from '@/lib/constants/task.constants';
import { TaskCreate } from '@/lib/types/task.types';

interface TaskSelectionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  clientId: number;
  clientName: string;
}

// Followup type configuration matching backend
const FOLLOWUP_CONFIG: Record<string, { days: number; priority: 'high' | 'medium' | 'low'; description: string }> = {
  'Day 1': { days: 1, priority: 'high', description: 'First follow-up after initial contact' },
  'Day 3': { days: 3, priority: 'medium', description: 'Second follow-up to maintain engagement' },
  'Week 1': { days: 7, priority: 'medium', description: 'Weekly check-in to provide updates' },
  'Week 2': { days: 14, priority: 'low', description: 'Bi-weekly follow-up for nurturing' },
  'Month 1': { days: 30, priority: 'low', description: 'Monthly follow-up for long-term nurturing' },
};

export function TaskSelectionDialog({ open, onOpenChange, clientId, clientName }: TaskSelectionDialogProps) {
  const { toast } = useToast();
  const createTask = useCreateTask();
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set(['Day 1'])); // Default to Day 1
  const [isCreating, setIsCreating] = useState(false);

  const handleToggle = (type: string) => {
    setSelectedTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    const allTypes = FOLLOWUP_TYPES.filter((type) => type !== 'Custom');
    setSelectedTypes(new Set(allTypes));
  };

  const handleDeselectAll = () => {
    setSelectedTypes(new Set());
  };

  const handleCreate = async () => {
    if (selectedTypes.size === 0) {
      toast({
        title: 'No tasks selected',
        description: 'Please select at least one follow-up task to create.',
        variant: 'destructive',
      });
      return;
    }

    setIsCreating(true);
    const now = new Date();
    const tasksToCreate: TaskCreate[] = [];

    // Create task objects for selected types
    for (const type of selectedTypes) {
      if (type === 'Custom') continue; // Skip Custom type
      
      const config = FOLLOWUP_CONFIG[type];
      if (!config) continue;

      const scheduledDate = new Date(now);
      scheduledDate.setDate(scheduledDate.getDate() + config.days);
      scheduledDate.setHours(9, 0, 0, 0); // Default to 9 AM

      tasksToCreate.push({
        client_id: clientId,
        followup_type: type as any,
        scheduled_for: scheduledDate.toISOString(),
        priority: config.priority,
        notes: config.description,
      });
    }

    try {
      // Create all tasks
      await Promise.all(tasksToCreate.map((task) => createTask.mutateAsync(task)));

      toast({
        title: 'Tasks created',
        description: `Successfully created ${tasksToCreate.length} follow-up task(s) for ${clientName}.`,
      });

      // Reset and close
      setSelectedTypes(new Set(['Day 1']));
      onOpenChange(false);
    } catch (error: any) {
      toast({
        title: 'Error creating tasks',
        description: error?.response?.data?.detail || 'Some tasks may not have been created. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleCancel = () => {
    setSelectedTypes(new Set(['Day 1']));
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create Follow-up Tasks</DialogTitle>
          <DialogDescription>
            Select which follow-up tasks you'd like to create for {clientName}. You can customize these later.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="flex justify-between items-center">
            <Label className="text-base font-semibold">Select Tasks</Label>
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
                disabled={isCreating}
              >
                Select All
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleDeselectAll}
                disabled={isCreating}
              >
                Deselect All
              </Button>
            </div>
          </div>

          <div className="space-y-3 border rounded-lg p-4">
            {FOLLOWUP_TYPES.filter((type) => type !== 'Custom').map((type) => {
              const config = FOLLOWUP_CONFIG[type];
              const isSelected = selectedTypes.has(type);
              
              return (
                <div
                  key={type}
                  className="flex items-start space-x-3 p-3 rounded-md hover:bg-secondary/10 hover:text-secondary transition-colors cursor-pointer"
                  onClick={() => !isCreating && handleToggle(type)}
                >
                  <Checkbox
                    id={`task-${type}`}
                    checked={isSelected}
                    onCheckedChange={() => handleToggle(type)}
                    disabled={isCreating}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <Label
                      htmlFor={`task-${type}`}
                      className="text-sm font-medium leading-none cursor-pointer"
                    >
                      {type}
                    </Label>
                    {config && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {config.description} • {config.days} day(s) • {config.priority} priority
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {selectedTypes.size === 0 && (
            <p className="text-sm text-muted-foreground text-center py-2">
              No tasks selected. Select at least one task to continue.
            </p>
          )}
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={handleCancel} disabled={isCreating}>
            Skip
          </Button>
          <Button type="button" onClick={handleCreate} disabled={isCreating || selectedTypes.size === 0}>
            {isCreating ? 'Creating...' : `Create ${selectedTypes.size} Task${selectedTypes.size !== 1 ? 's' : ''}`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

