'use client';

import * as React from 'react';
import { useState, useMemo, useEffect, useRef } from 'react';
import { ChevronsUpDown, Check, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from '@/components/ui/popover';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/badge';
import { TASK_STATUSES, TASK_STATUS_LABELS } from '@/lib/constants/task.constants';

interface StatusSelectProps {
  value: string[];
  onChange: (values: string[]) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

export function StatusSelect({
  value,
  onChange,
  disabled = false,
  placeholder = 'All statuses',
  className,
}: StatusSelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // When popover opens, auto-focus the input
  useEffect(() => {
    if (open && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  const filtered = useMemo(() => {
    const term = search.toLowerCase().trim();
    if (!term) return TASK_STATUSES;
    return TASK_STATUSES.filter((status) =>
      TASK_STATUS_LABELS[status].toLowerCase().includes(term)
    );
  }, [search]);

  const handleToggle = (status: string) => {
    if (value.includes(status)) {
      onChange(value.filter((v) => v !== status));
    } else {
      onChange([...value, status]);
    }
  };

  const handleRemove = (status: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(value.filter((v) => v !== status));
  };

  return (
    <Popover open={open} onOpenChange={setOpen} modal={false}>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className={cn('w-full justify-between', className)}
        >
          <div className="flex gap-1 flex-wrap flex-1 min-w-0">
            {value.length === 0 ? (
              <span className="text-muted-foreground">{placeholder}</span>
            ) : (
              value.map((status) => (
                <Badge
                  key={status}
                  variant="secondary"
                  className="mr-1"
                >
                  {TASK_STATUS_LABELS[status]}
                  <span
                    tabIndex={0}
                    className="ml-1 ring-offset-background rounded-full outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 cursor-pointer inline-flex items-center"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        e.stopPropagation();
                        handleRemove(status, e as any);
                      }
                    }}
                    onMouseDown={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemove(status, e);
                    }}
                  >
                    <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                  </span>
                </Badge>
              ))
            )}
          </div>
          <ChevronsUpDown className="ml-2 h-4 w-4 opacity-50 shrink-0" />
        </Button>
      </PopoverTrigger>

      <PopoverContent
        align="start"
        sideOffset={4}
        className="z-[9999] w-[var(--radix-popover-trigger-width)] p-2 bg-white border rounded-md shadow-md"
        side="bottom"
        style={{ pointerEvents: 'auto' }}
      >
        <Input
          ref={inputRef}
          placeholder="Search statuses..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="mb-2"
        />

        <div className="max-h-64 overflow-auto rounded-sm border bg-white">
          {filtered.map((status) => {
            const isSelected = value.includes(status);
            return (
              <button
                key={status}
                type="button"
                onClick={() => handleToggle(status)}
                className={cn(
                  'flex w-full items-center justify-start gap-2 px-3 py-2 text-left text-sm hover:bg-secondary/10',
                  isSelected && 'bg-secondary/10'
                )}
              >
                <Check
                  className={cn('h-4 w-4', isSelected ? 'opacity-100' : 'opacity-0')}
                />
                {TASK_STATUS_LABELS[status]}
              </button>
            );
          })}
        </div>
      </PopoverContent>
    </Popover>
  );
}

