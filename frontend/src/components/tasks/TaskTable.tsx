'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { Task } from '@/lib/types/task.types';
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
import { TaskStatusBadge } from '@/components/tasks/TaskStatusBadge';
import { TaskPriorityBadge } from '@/components/tasks/TaskPriorityBadge';
import { TaskActionsMenu } from '@/components/tasks/TaskActionsMenu';
import { TaskDetailModal } from '@/components/tasks/TaskDetailModal';
import { formatDateTime } from '@/lib/utils/format';
import { truncateText } from '@/lib/utils/formatters';
import { cn } from '@/lib/utils/index';
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { useClients } from '@/lib/hooks/queries/useClients';

interface TaskTableProps {
  tasks: Task[];
  isLoading: boolean;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  onLimitChange: (limit: number) => void;
}

export function TaskTable({
  tasks,
  isLoading,
  page,
  limit,
  onPageChange,
  onLimitChange
}: TaskTableProps) {
  const [sortColumn, setSortColumn] = useState<keyof Task>('scheduled_for');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  // Fetch clients for name mapping (or include in task response)
  // Backend enforces limit <= 100
  const { data: clients } = useClients({ limit: 100 });
  const clientMap = useMemo(() => {
    if (!clients) return {};
    return Object.fromEntries(clients.map(c => [c.id, c]));
  }, [clients]);

  const handleSort = (column: keyof Task) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const sortedTasks = useMemo(() => {
    if (!tasks) return [];
    return [...tasks].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];
      const multiplier = sortDirection === 'asc' ? 1 : -1;

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return aVal.localeCompare(bVal) * multiplier;
      }
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return (aVal - bVal) * multiplier;
      }
      return 0;
    });
  }, [tasks, sortColumn, sortDirection]);

  // Determine if task is overdue or due today
  const getTaskDateStatus = (scheduledFor: string) => {
    const taskDate = new Date(scheduledFor);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (taskDate < today) return 'overdue';
    if (taskDate >= today && taskDate < tomorrow) return 'today';
    return 'future';
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <EmptyState
        icon={Calendar}
        title="No tasks found"
        description="Adjust your filters or create a custom task to get started."
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
                onClick={() => handleSort('followup_type')}
              >
                Type
              </TableHead>
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort('scheduled_for')}
              >
                Scheduled For
              </TableHead>
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort('status')}
              >
                Status
              </TableHead>
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort('priority')}
              >
                Priority
              </TableHead>
              <TableHead>Notes</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedTasks.map((task) => {
              const client = clientMap[task.client_id];
              const dateStatus = getTaskDateStatus(task.scheduled_for);

              return (
                <TableRow
                  key={task.id}
                  className={cn(
                    'cursor-pointer',
                    dateStatus === 'overdue' && task.status === 'pending' && 'hover:bg-red-50',
                    dateStatus === 'today' && task.status === 'pending' && 'hover:bg-yellow-50',
                    !(dateStatus === 'overdue' && task.status === 'pending') && 
                    !(dateStatus === 'today' && task.status === 'pending') && 
                    'hover:bg-muted/50'
                  )}
                  onClick={() => setSelectedTask(task)}
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
                      `Client #${task.client_id}`
                    )}
                  </TableCell>
                  <TableCell>
                    <span className="text-sm font-medium">
                      {task.followup_type}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className={cn(
                      dateStatus === 'overdue' && task.status === 'pending' && 'text-red-600 font-medium',
                      dateStatus === 'today' && task.status === 'pending' && 'text-yellow-700 font-medium'
                    )}>
                      {formatDateTime(task.scheduled_for)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <TaskStatusBadge status={task.status} />
                  </TableCell>
                  <TableCell>
                    <TaskPriorityBadge priority={task.priority} />
                  </TableCell>
                  <TableCell className="max-w-xs">
                    {task.notes ? (
                      <span className="text-sm text-muted-foreground" title={task.notes}>
                        {truncateText(task.notes, 50)}
                      </span>
                    ) : (
                      <span className="text-sm text-muted-foreground italic">No notes</span>
                    )}
                  </TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <TaskActionsMenu task={task} />
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
            disabled={tasks.length < limit}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Task Detail Modal */}
      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          open={!!selectedTask}
          onOpenChange={(open) => !open && setSelectedTask(null)}
        />
      )}
    </>
  );
}

