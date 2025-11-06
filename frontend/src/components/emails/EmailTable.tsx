'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Email } from '@/lib/types/email.types';
import { Client } from '@/lib/types/client.types';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import { EmailStatusBadge } from '@/components/emails/EmailStatusBadge';
import { EmailEngagementIcons } from '@/components/emails/EmailEngagementIcons';
import { formatRelativeTime } from '@/lib/utils/format';
import { truncateText } from '@/lib/utils/formatters';
import { Mail, ChevronLeft, ChevronRight, Eye } from 'lucide-react';

interface EmailTableProps {
  emails: Email[];
  clientMap: Record<number, Client>;
  isLoading: boolean;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  onLimitChange: (limit: number) => void;
}

export function EmailTable({
  emails,
  clientMap,
  isLoading,
  page,
  limit,
  onPageChange,
  onLimitChange
}: EmailTableProps) {
  const router = useRouter();
  const [sortColumn, setSortColumn] = useState<keyof Email>('created_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const handleSort = (column: keyof Email) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  const sortedEmails = useMemo(() => {
    if (!emails) return [];
    return [...emails].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];
      const multiplier = sortDirection === 'asc' ? 1 : -1;

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return aVal.localeCompare(bVal) * multiplier;
      }
      if (!aVal && bVal) return 1;
      if (aVal && !bVal) return -1;
      return 0;
    });
  }, [emails, sortColumn, sortDirection]);

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (emails.length === 0) {
    return (
      <EmptyState
        icon={Mail}
        title="No emails found"
        description="Emails will appear here once follow-up tasks are completed or you send manual emails."
      />
    );
  }

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort('client_id')}
              >
                Client
              </TableHead>
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort('subject')}
              >
                Subject
              </TableHead>
              <TableHead>To</TableHead>
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort('status')}
              >
                Status
              </TableHead>
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort('sent_at')}
              >
                Sent At
              </TableHead>
              <TableHead>Engagement</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedEmails.map((email) => {
              const client = clientMap[email.client_id];

              return (
                <TableRow
                  key={email.id}
                  className="cursor-pointer hover:bg-secondary/10 hover:text-secondary transition-colors"
                  onClick={() => router.push(`/emails/${email.id}`)}
                >
                  <TableCell className="font-medium">
                    {client ? (
                      <Link
                        href={`/clients/${client.id}`}
                        className="hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {client.name}
                      </Link>
                    ) : (
                      `Client #${email.client_id}`
                    )}
                  </TableCell>
                  <TableCell className="max-w-md">
                    <span title={email.subject}>
                      {truncateText(email.subject, 60)}
                    </span>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {email.to_email}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <EmailStatusBadge status={email.status} />
                      {email.status === 'failed' && email.error_message && (
                        <span 
                          className="text-xs text-muted-foreground cursor-help" 
                          title={email.error_message}
                        >
                          ⚠️
                        </span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    {email.sent_at ? (
                      <span className="text-sm">
                        {formatRelativeTime(email.sent_at)}
                      </span>
                    ) : (
                      <span className="text-sm text-muted-foreground">Not sent</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <EmailEngagementIcons email={email} />
                  </TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => router.push(`/emails/${email.id}`)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Rows per page:</span>
          <select
            value={limit}
            onChange={(e) => onLimitChange(Number(e.target.value))}
            className="border rounded px-2 py-1 text-sm"
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
            onClick={() => onPageChange(page - 1)}
            disabled={page === 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm">Page {page}</span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page + 1)}
            disabled={emails.length < limit}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </>
  );
}

