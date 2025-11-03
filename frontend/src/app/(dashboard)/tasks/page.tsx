'use client';

import { useState, useMemo } from 'react';
import { useTasks } from '@/lib/hooks/queries/useTasks';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/Button';
import { Plus } from 'lucide-react';
import { TaskTable } from '@/components/tasks/TaskTable';
import { TaskCalendar } from '@/components/tasks/TaskCalendar';
import { TaskFilters } from '@/components/tasks/TaskFilters';
import { CreateTaskDialog } from '@/components/tasks/CreateTaskDialog';

export default function TasksPage() {
  const [view, setView] = useState<'table' | 'calendar'>('table');
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(25);
  const [statusFilter, setStatusFilter] = useState<string[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<string[]>([]);
  const [clientFilter, setClientFilter] = useState<number | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const { data: tasks = [], isLoading, isError } = useTasks({
    page,
    limit,
    status: statusFilter.length > 0 ? statusFilter.join(',') : undefined,
    client_id: clientFilter || undefined
  });

  // Client-side filtering by priority (if backend doesn't support)
  const filteredTasks = useMemo(() => {
    if (!tasks) return [];
    if (priorityFilter.length === 0) return tasks;
    return tasks.filter(t => priorityFilter.includes(t.priority));
  }, [tasks, priorityFilter]);

  const activeFilterCount =
    statusFilter.length +
    priorityFilter.length +
    (clientFilter ? 1 : 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Tasks</h1>
          {activeFilterCount > 0 && (
            <p className="text-sm text-muted-foreground mt-1">
              {activeFilterCount} filter{activeFilterCount !== 1 ? 's' : ''} active
            </p>
          )}
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Custom Task
        </Button>
      </div>

      {/* Filters */}
      <TaskFilters
        statusFilter={statusFilter}
        priorityFilter={priorityFilter}
        clientFilter={clientFilter}
        onStatusChange={setStatusFilter}
        onPriorityChange={setPriorityFilter}
        onClientChange={setClientFilter}
        onClearAll={() => {
          setStatusFilter([]);
          setPriorityFilter([]);
          setClientFilter(null);
        }}
      />

      {/* View Toggle */}
      <Tabs value={view} onValueChange={(v) => setView(v as 'table' | 'calendar')}>
        <TabsList>
          <TabsTrigger value="table">Table</TabsTrigger>
          <TabsTrigger value="calendar">Calendar</TabsTrigger>
        </TabsList>

        <TabsContent value="table" className="mt-6">
          <TaskTable
            tasks={filteredTasks}
            isLoading={isLoading}
            page={page}
            limit={limit}
            onPageChange={setPage}
            onLimitChange={setLimit}
          />
        </TabsContent>

        <TabsContent value="calendar" className="mt-6">
          <TaskCalendar
            tasks={filteredTasks}
            isLoading={isLoading}
          />
        </TabsContent>
      </Tabs>

      {/* Create Task Dialog */}
      <CreateTaskDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />
    </div>
  );
}
