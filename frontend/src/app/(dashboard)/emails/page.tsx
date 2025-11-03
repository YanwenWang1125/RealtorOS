'use client';

import { useState, useMemo } from 'react';
import { useEmails } from '@/lib/hooks/queries/useEmails';
import { useClients } from '@/lib/hooks/queries/useClients';
import { Button } from '@/components/ui/Button';
import { EmailFilters } from '@/components/emails/EmailFilters';
import { EmailTable } from '@/components/emails/EmailTable';
import { RefreshCw } from 'lucide-react';

export default function EmailsPage() {
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(25);
  const [statusFilter, setStatusFilter] = useState<string[]>([]);
  const [clientFilter, setClientFilter] = useState<number | null>(null);

  const { data: emails, isLoading, isError, refetch, isFetching } = useEmails({
    page,
    limit,
    status: statusFilter.length > 0 ? statusFilter.join(',') : undefined,
    client_id: clientFilter || undefined
  });

  const { data: clients } = useClients({ limit: 1000 });

  const clientMap = useMemo(() => {
    if (!clients) return {};
    return Object.fromEntries(clients.map(c => [c.id, c]));
  }, [clients]);

  const activeFilterCount = statusFilter.length + (clientFilter ? 1 : 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Emails</h1>
          {emails && (
            <p className="text-sm text-muted-foreground mt-1">
              Showing {emails.length} email{emails.length !== 1 ? 's' : ''}
              {activeFilterCount > 0 && ` (${activeFilterCount} filter${activeFilterCount !== 1 ? 's' : ''} active)`}
            </p>
          )}
        </div>
        <Button
          variant="outline"
          onClick={() => refetch()}
          disabled={isFetching}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <EmailFilters
        statusFilter={statusFilter}
        clientFilter={clientFilter}
        onStatusChange={setStatusFilter}
        onClientChange={setClientFilter}
        onClearAll={() => {
          setStatusFilter([]);
          setClientFilter(null);
        }}
      />

      {/* Email Table */}
      <EmailTable
        emails={emails || []}
        clientMap={clientMap}
        isLoading={isLoading}
        page={page}
        limit={limit}
        onPageChange={setPage}
        onLimitChange={setLimit}
      />
    </div>
  );
}
