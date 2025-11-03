'use client';

import { Button } from '@/components/ui/Button';
import { MultiSelect } from '@/components/ui/multi-select';
import { ClientAutocomplete } from '@/components/tasks/ClientAutocomplete';
import { EMAIL_STATUSES, EMAIL_STATUS_LABELS } from '@/lib/constants/email.constants';
import { X } from 'lucide-react';

interface EmailFiltersProps {
  statusFilter: string[];
  clientFilter: number | null;
  onStatusChange: (status: string[]) => void;
  onClientChange: (clientId: number | null) => void;
  onClearAll: () => void;
}

export function EmailFilters({
  statusFilter,
  clientFilter,
  onStatusChange,
  onClientChange,
  onClearAll
}: EmailFiltersProps) {
  const hasActiveFilters = statusFilter.length > 0 || clientFilter !== null;

  return (
    <div className="flex flex-wrap gap-4 items-end">
      {/* Status Filter */}
      <div className="flex-1 min-w-[250px]">
        <label className="text-sm font-medium mb-2 block">Status</label>
        <MultiSelect
          options={EMAIL_STATUSES.map(status => ({
            value: status,
            label: EMAIL_STATUS_LABELS[status]
          }))}
          selected={statusFilter}
          onChange={onStatusChange}
          placeholder="All statuses"
        />
      </div>

      {/* Client Filter */}
      <div className="flex-1 min-w-[250px]">
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

