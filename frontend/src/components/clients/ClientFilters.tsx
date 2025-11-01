'use client';

import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Search, X } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { CLIENT_STAGES, CLIENT_STAGE_LABELS } from '@/lib/constants/client.constants';
import { ClientStage } from '@/lib/types/client.types';

interface ClientFiltersProps {
  stage: ClientStage | null;
  search: string;
  onStageChange: (stage: ClientStage | null) => void;
  onSearchChange: (search: string) => void;
}

export function ClientFilters({ stage, search, onStageChange, onSearchChange }: ClientFiltersProps) {
  const hasActiveFilters = stage !== null || search !== '';

  const handleClearFilters = () => {
    onStageChange(null);
    onSearchChange('');
  };

  return (
    <div className="flex flex-col sm:flex-row gap-4 mb-6">
      <div className="flex-1">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name, email, or property address..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>
      <Select value={stage || 'all'} onValueChange={(value) => onStageChange(value === 'all' ? null : value as ClientStage)}>
        <SelectTrigger className="w-full sm:w-[200px]">
          <SelectValue placeholder="Filter by stage" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Stages</SelectItem>
          {CLIENT_STAGES.map(s => (
            <SelectItem key={s} value={s}>
              {CLIENT_STAGE_LABELS[s]}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {hasActiveFilters && (
        <Button
          variant="outline"
          onClick={handleClearFilters}
          className="whitespace-nowrap"
        >
          <X className="h-4 w-4 mr-2" />
          Clear Filters
        </Button>
      )}
    </div>
  );
}

