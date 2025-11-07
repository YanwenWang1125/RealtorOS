'use client';

import { Button } from '@/components/ui/Button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ClientAutocomplete } from '@/components/tasks/ClientAutocomplete';
import { EMAIL_STATUS_LABELS } from '@/lib/constants/email.constants';
import { EmailStatus } from '@/lib/types/email.types';
import { X } from 'lucide-react';

// Engagement statuses shown in the timeline: Sent, Delivered, Opened, Clicked, and Failed
const ENGAGEMENT_STATUSES: EmailStatus[] = ['sent', 'delivered', 'opened', 'clicked', 'failed'];

interface EmailFiltersProps {
  statusFilter: string | null;
  clientFilter: number | null;
  onStatusChange: (status: string | null) => void;
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
  const hasActiveFilters = statusFilter !== null || clientFilter !== null;

  return (
    <div className="flex flex-wrap gap-4 items-end">
      {/* Status Filter */}
      <div className="flex-1 min-w-[250px]">
        <label className="text-sm font-medium mb-2 block">Status</label>
        <Select 
          value={statusFilter || 'all'} 
          onValueChange={(value) => onStatusChange(value === 'all' ? null : value)}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="All statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {ENGAGEMENT_STATUSES.map(status => (
              <SelectItem key={status} value={status}>
                {EMAIL_STATUS_LABELS[status]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
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

