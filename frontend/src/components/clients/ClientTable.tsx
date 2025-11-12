'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Checkbox } from '@/components/ui/checkbox';
import { Client } from '@/lib/types/client.types';
import { CLIENT_STAGE_COLORS, CLIENT_STAGE_LABELS, PROPERTY_TYPE_LABELS } from '@/lib/constants/client.constants';
import { formatRelativeTime } from '@/lib/utils/format';
import { normalizeClientStage } from '@/lib/utils/formatters';
import { useBulkDeleteClients } from '@/lib/hooks/mutations';
import { useToast } from '@/lib/hooks/ui/useToast';
import { Eye, Trash2 } from 'lucide-react';

interface ClientTableProps {
  clients: Client[];
  loading: boolean;
}

type SortColumn = 'name' | 'email' | 'property_address' | 'property_type' | 'stage' | 'last_contacted';
type SortDirection = 'asc' | 'desc';

interface ClientTableWithSortProps extends ClientTableProps {
  sortColumn?: SortColumn;
  sortDirection?: SortDirection;
  onSort?: (column: SortColumn) => void;
}

export function ClientTable({ clients, loading, sortColumn, sortDirection, onSort }: ClientTableWithSortProps) {
  const router = useRouter();
  const { toast } = useToast();
  const bulkDeleteClients = useBulkDeleteClients();
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(new Set(clients.map(c => c.id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelectOne = (id: number, checked: boolean) => {
    const newSelected = new Set(selectedIds);
    if (checked) {
      newSelected.add(id);
    } else {
      newSelected.delete(id);
    }
    setSelectedIds(newSelected);
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    
    if (!confirm(`Are you sure you want to delete ${selectedIds.size} client(s)? This will also delete all associated tasks and emails.`)) {
      return;
    }

    try {
      const result = await bulkDeleteClients.mutateAsync(Array.from(selectedIds));
      toast({
        title: "Clients deleted",
        description: `Successfully deleted ${result.deleted_count} client(s).${result.failed_ids.length > 0 ? ` ${result.failed_ids.length} failed.` : ''}`,
      });
      setSelectedIds(new Set());
    } catch (error: any) {
      toast({
        title: "Error deleting clients",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  const allSelected = clients.length > 0 && selectedIds.size === clients.length;
  const someSelected = selectedIds.size > 0 && selectedIds.size < clients.length;

  const handleSort = (column: SortColumn) => {
    if (onSort) {
      onSort(column);
    }
  };

  const SortButton = ({ column, children }: { column: SortColumn; children: React.ReactNode }) => {
    if (!onSort) return <>{children}</>;
    
    return (
      <button
        onClick={() => handleSort(column)}
        className="flex items-center gap-1 hover:text-foreground transition-colors"
      >
        {children}
        {sortColumn === column && (
          <span className="text-xs">
            {sortDirection === 'asc' ? '↑' : '↓'}
          </span>
        )}
      </button>
    );
  };

  if (loading) {
    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12"></TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Property Address</TableHead>
            <TableHead>Property Type</TableHead>
            <TableHead>Stage</TableHead>
            <TableHead>Last Contacted</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {[...Array(5)].map((_, i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-32" /></TableCell>
              <TableCell><Skeleton className="h-4 w-40" /></TableCell>
              <TableCell><Skeleton className="h-4 w-48" /></TableCell>
              <TableCell><Skeleton className="h-4 w-24" /></TableCell>
              <TableCell><Skeleton className="h-4 w-20" /></TableCell>
              <TableCell><Skeleton className="h-4 w-24" /></TableCell>
              <TableCell><Skeleton className="h-4 w-16" /></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );
  }

  if (clients.length === 0) {
    return null; // Empty state handled by parent
  }

  return (
    <div className="space-y-4">
      {selectedIds.size > 0 && (
        <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
          <span className="text-sm font-medium">
            {selectedIds.size} client(s) selected
          </span>
          <Button
            variant="destructive"
            size="sm"
            onClick={handleBulkDelete}
            disabled={bulkDeleteClients.isPending}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            {bulkDeleteClients.isPending ? 'Deleting...' : `Delete ${selectedIds.size}`}
          </Button>
        </div>
      )}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12">
              <Checkbox
                checked={allSelected}
                onCheckedChange={handleSelectAll}
                aria-label="Select all"
              />
            </TableHead>
            <TableHead>
              <SortButton column="name">Name</SortButton>
            </TableHead>
          <TableHead>
            <SortButton column="email">Email</SortButton>
          </TableHead>
          <TableHead>
            <SortButton column="property_address">Property Address</SortButton>
          </TableHead>
          <TableHead>
            <SortButton column="property_type">Property Type</SortButton>
          </TableHead>
          <TableHead>
            <SortButton column="stage">Stage</SortButton>
          </TableHead>
          <TableHead>
            <SortButton column="last_contacted">Last Contacted</SortButton>
          </TableHead>
          <TableHead>Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {clients.map((client) => (
          <TableRow 
            key={client.id} 
            className="hover:bg-secondary/10 hover:text-secondary transition-colors"
          >
            <TableCell onClick={(e) => e.stopPropagation()}>
              <Checkbox
                checked={selectedIds.has(client.id)}
                onCheckedChange={(checked) => handleSelectOne(client.id, checked as boolean)}
                aria-label={`Select ${client.name}`}
              />
            </TableCell>
            <TableCell 
              className="font-medium cursor-pointer"
              onClick={() => router.push(`/clients/${client.id}`)}
            >
              {client.name}
            </TableCell>
            <TableCell 
              className="cursor-pointer"
              onClick={() => router.push(`/clients/${client.id}`)}
            >
              {client.email}
            </TableCell>
            <TableCell 
              className="cursor-pointer"
              onClick={() => router.push(`/clients/${client.id}`)}
            >
              {client.property_address}
            </TableCell>
            <TableCell 
              className="cursor-pointer"
              onClick={() => router.push(`/clients/${client.id}`)}
            >
              {PROPERTY_TYPE_LABELS[client.property_type]}
            </TableCell>
            <TableCell 
              className="cursor-pointer"
              onClick={() => router.push(`/clients/${client.id}`)}
            >
              {(() => {
                // Normalize the stage value
                const normalizedStage = normalizeClientStage(client.stage);
                
                // Get color and label with fallbacks
                const stageColor = CLIENT_STAGE_COLORS[normalizedStage] ?? 'bg-gray-100 text-gray-700';
                const stageLabel = CLIENT_STAGE_LABELS[normalizedStage] ?? client.stage;
                
                return (
                  <span 
                    className={`inline-flex items-center rounded-full px-2 py-1 text-sm font-medium ${stageColor}`}
                  >
                    {stageLabel}
                  </span>
                );
              })()}
            </TableCell>
            <TableCell 
              className="cursor-pointer"
              onClick={() => router.push(`/clients/${client.id}`)}
            >
              {client.last_contacted
                ? formatRelativeTime(client.last_contacted)
                : 'Never'}
            </TableCell>
            <TableCell>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  router.push(`/clients/${client.id}`);
                }}
              >
                <Eye className="h-4 w-4 mr-1" />
                View
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
    </div>
  );
}

