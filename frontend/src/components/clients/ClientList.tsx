'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { ClientFilters } from './ClientFilters';
import { ClientTable } from './ClientTable';
import { ClientCard } from './ClientCard';
import { useClients } from '@/lib/hooks/queries/useClients';
import { useDebounce } from '@/lib/hooks/ui/useDebounce';
import { Client, ClientStage } from '@/lib/types/client.types';
import { Plus, Users } from 'lucide-react';

type SortColumn = 'name' | 'email' | 'property_address' | 'property_type' | 'stage' | 'last_contacted';
type SortDirection = 'asc' | 'desc';

export function ClientList() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [stage, setStage] = useState<ClientStage | null>(null);
  const [search, setSearch] = useState('');
  const [sortColumn, setSortColumn] = useState<SortColumn>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const debouncedSearch = useDebounce(search, 300);

  const { data: clients, isLoading, isError, error } = useClients({
    page,
    limit,
    stage: stage || undefined,
  });

  // Client-side filtering by search
  const filteredClients = useMemo(() => {
    if (!clients || !debouncedSearch) return clients || [];
    const searchLower = debouncedSearch.toLowerCase();
    return clients.filter(
      (c) =>
        c.name.toLowerCase().includes(searchLower) ||
        c.email.toLowerCase().includes(searchLower) ||
        c.property_address.toLowerCase().includes(searchLower)
    );
  }, [clients, debouncedSearch]);

  // Client-side sorting
  const sortedClients = useMemo(() => {
    if (!filteredClients) return [];
    
    return [...filteredClients].sort((a, b) => {
      let aValue: any;
      let bValue: any;

      if (sortColumn === 'name') {
        aValue = a.name.toLowerCase();
        bValue = b.name.toLowerCase();
      } else if (sortColumn === 'email') {
        aValue = a.email.toLowerCase();
        bValue = b.email.toLowerCase();
      } else if (sortColumn === 'property_address') {
        aValue = a.property_address.toLowerCase();
        bValue = b.property_address.toLowerCase();
      } else if (sortColumn === 'property_type') {
        aValue = a.property_type;
        bValue = b.property_type;
      } else if (sortColumn === 'stage') {
        aValue = a.stage;
        bValue = b.stage;
      } else if (sortColumn === 'last_contacted') {
        aValue = a.last_contacted ? new Date(a.last_contacted).getTime() : 0;
        bValue = b.last_contacted ? new Date(b.last_contacted).getTime() : 0;
      } else {
        return 0;
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredClients, sortColumn, sortDirection]);

  const handleSort = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const totalClients = sortedClients.length;
  const totalPages = Math.ceil(totalClients / limit);
  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + limit;
  const paginatedClients = sortedClients.slice(startIndex, endIndex);

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleLimitChange = (newLimit: number) => {
    setLimit(newLimit);
    setPage(1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Clients</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Showing {totalClients} {totalClients === 1 ? 'client' : 'clients'}
          </p>
        </div>
        <Button onClick={() => router.push('/clients/new')}>
          <Plus className="h-4 w-4 mr-2" />
          Create New Client
        </Button>
      </div>

      {/* Filters */}
      <ClientFilters
        stage={stage}
        search={search}
        onStageChange={setStage}
        onSearchChange={setSearch}
      />

      {/* Error State */}
      {isError && (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4">
          <p className="text-sm text-destructive">
            Error loading clients: {error instanceof Error ? error.message : 'Unknown error'}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.location.reload()}
            className="mt-2"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !isError && sortedClients.length === 0 && (
        <EmptyState
          icon={Users}
          title="No clients found"
          description={
            debouncedSearch || stage
              ? "Try adjusting your filters to see more results."
              : "Create your first client to get started!"
          }
          action={
            !debouncedSearch && !stage
              ? {
                  label: 'Create New Client',
                  onClick: () => router.push('/clients/new'),
                }
              : undefined
          }
        />
      )}

      {/* Desktop Table View */}
      <div className="hidden md:block">
        <ClientTable
          clients={paginatedClients}
          loading={isLoading}
          sortColumn={sortColumn}
          sortDirection={sortDirection}
          onSort={handleSort}
        />
      </div>

      {/* Mobile Card View */}
      <div className="md:hidden space-y-4">
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-32 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        ) : (
          paginatedClients.map((client) => (
            <ClientCard key={client.id} client={client} />
          ))
        )}
      </div>

      {/* Pagination */}
      {!isLoading && sortedClients.length > 0 && (
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Page size:</span>
            <select
              value={limit}
              onChange={(e) => handleLimitChange(Number(e.target.value))}
              className="rounded-md border border-input bg-background px-3 py-1 text-sm"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
            >
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {page} of {totalPages || 1}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(page + 1)}
              disabled={page >= totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

