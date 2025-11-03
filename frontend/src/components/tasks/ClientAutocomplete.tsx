'use client';

import * as React from 'react';
import { useState, useMemo, useEffect, useRef } from 'react';
import { ChevronsUpDown, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from '@/components/ui/popover';
import { Input } from '@/components/ui/Input';
import { useClients } from '@/lib/hooks/queries/useClients';
import { useDebounce } from '@/lib/hooks/ui/useDebounce';

/**
 * A stable Client search + select component (no cmdk)
 * Works safely inside Dialog
 */
interface ClientAutocompleteProps {
  id?: string;
  value: number | string | null;
  onChange: (id: number | null) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

export function ClientAutocomplete({
  id,
  value,
  onChange,
  disabled = false,
  placeholder = 'Select client...',
  className,
}: ClientAutocompleteProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const debouncedSearch = useDebounce(search, 300);

  const { data: clientsRaw, isLoading } = useClients({
    limit: 1000,
    search: debouncedSearch || undefined,
  });
  const clients = clientsRaw ?? [];

  // 统一 value 类型处理（兼容 react-hook-form 可能传入的 string）
  const numericValue = useMemo<number | null>(() => {
    if (value === null || value === undefined) return null;
    if (typeof value === 'number') return Number.isFinite(value) ? value : null;
    const n = parseInt(value as string, 10);
    return Number.isFinite(n) ? n : null;
  }, [value]);

  const selectedClient = useMemo(
    () => (numericValue != null ? clients.find((c) => c.id === numericValue) : undefined),
    [clients, numericValue]
  );

  // 当打开时自动聚焦输入框
  useEffect(() => {
    if (open && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  const filtered = useMemo(() => {
    const term = search.toLowerCase().trim();
    if (!term) return clients;
    return clients.filter(
      (c) =>
        c.name.toLowerCase().includes(term) ||
        c.email.toLowerCase().includes(term)
    );
  }, [clients, search]);

  return (
    <Popover open={open} onOpenChange={setOpen} modal={false}>
      <PopoverTrigger asChild>
        <Button
          id={id}
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className={cn('w-full justify-between', className)}
        >
          {selectedClient ? selectedClient.name : placeholder}
          <ChevronsUpDown className="ml-2 h-4 w-4 opacity-50" />
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
          placeholder="Search clients..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="mb-2"
        />

        <div className="max-h-64 overflow-auto rounded-sm border bg-white">
          <button
            type="button"
            onClick={() => {
              onChange(null);
              setOpen(false);
            }}
            className={cn(
              'flex w-full items-center justify-start gap-2 px-3 py-2 text-left text-sm hover:bg-accent',
              numericValue === null && 'bg-accent/30'
            )}
          >
            <Check
              className={cn('h-4 w-4', numericValue === null ? 'opacity-100' : 'opacity-0')}
            />
            All clients
          </button>

          {isLoading && (
            <div className="px-3 py-2 text-muted-foreground text-sm">
              Loading...
            </div>
          )}

          {!isLoading && filtered.length === 0 && (
            <div className="px-3 py-2 text-muted-foreground text-sm">
              No clients found
            </div>
          )}

          {!isLoading &&
            filtered.map((client) => (
              <button
                key={client.id}
                type="button"
                onClick={() => {
                  onChange(client.id);
                  setOpen(false);
                }}
                className={cn(
                  'flex w-full items-center justify-start gap-2 px-3 py-2 text-left text-sm hover:bg-accent',
                  numericValue === client.id && 'bg-accent/30'
                )}
              >
                <Check
                  className={cn(
                    'h-4 w-4',
                    numericValue === client.id ? 'opacity-100' : 'opacity-0'
                  )}
                />
                <div>
                  <div className="font-medium">{client.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {client.email}
                  </div>
                </div>
              </button>
            ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}
