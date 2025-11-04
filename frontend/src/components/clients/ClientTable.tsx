'use client';

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
import { Client } from '@/lib/types/client.types';
import { CLIENT_STAGE_COLORS, CLIENT_STAGE_LABELS, PROPERTY_TYPE_LABELS } from '@/lib/constants/client.constants';
import { formatRelativeTime } from '@/lib/utils/format';
import { Eye } from 'lucide-react';

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
    <Table>
      <TableHeader>
        <TableRow>
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
          <TableRow key={client.id} className="hover:bg-secondary/10 hover:text-secondary cursor-pointer transition-colors">
            <TableCell className="font-medium">{client.name}</TableCell>
            <TableCell>{client.email}</TableCell>
            <TableCell>{client.property_address}</TableCell>
            <TableCell>{PROPERTY_TYPE_LABELS[client.property_type]}</TableCell>
            <TableCell>
              <Badge className={CLIENT_STAGE_COLORS[client.stage]}>
                {CLIENT_STAGE_LABELS[client.stage]}
              </Badge>
            </TableCell>
            <TableCell>
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
  );
}

