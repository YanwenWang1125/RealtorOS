'use client';

import { Button } from '@/components/ui/Button';
import { MultiSelect } from '@/components/ui/multi-select';
import { ClientAutocomplete } from '@/components/tasks/ClientAutocomplete';
import { TASK_STATUSES, PRIORITY_LEVELS, TASK_STATUS_LABELS, PRIORITY_LABELS } from '@/lib/constants/task.constants';
import { X } from 'lucide-react';

interface TaskFiltersProps {
  statusFilter: string[];
  priorityFilter: string[];
  clientFilter: number | null;
  onStatusChange: (status: string[]) => void;
  onPriorityChange: (priority: string[]) => void;
  onClientChange: (clientId: number | null) => void;
  onClearAll: () => void;
}

export function TaskFilters({
  statusFilter,
  priorityFilter,
  clientFilter,
  onStatusChange,
  onPriorityChange,
  onClientChange,
  onClearAll
}: TaskFiltersProps) {
  const hasActiveFilters = statusFilter.length > 0 || priorityFilter.length > 0 || clientFilter !== null;

  return (
    <div className="flex flex-wrap gap-4 items-end">
      {/* Status Filter */}
      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium mb-2 block">Status</label>
        <MultiSelect
          options={TASK_STATUSES.map(status => ({
            value: status,
            label: TASK_STATUS_LABELS[status]
          }))}
          selected={statusFilter}
          onChange={onStatusChange}
          placeholder="All statuses"
        />
      </div>

      {/* Priority Filter */}
      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium mb-2 block">Priority</label>
        <MultiSelect
          options={PRIORITY_LEVELS.map(priority => ({
            value: priority,
            label: PRIORITY_LABELS[priority]
          }))}
          selected={priorityFilter}
          onChange={onPriorityChange}
          placeholder="All priorities"
        />
      </div>

      {/* Client Filter */}
      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium mb-2 block">Client</label>
        <ClientAutocomplete
          value={clientFilter}
          onChange={onClientChange}
        />
      </div>

      {/* Clear Filters */}
      {hasActiveFilters && (
        <Button variant="outline" onClick={onClearAll}>
          <X className="h-4 w-4 mr-2" />
          Clear Filters
        </Button>
      )}
    </div>
  );
}

