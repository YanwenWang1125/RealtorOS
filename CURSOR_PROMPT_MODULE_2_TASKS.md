# CURSOR PROMPT: RealtorOS - MODULE 2 - TASKS

## OBJECTIVE
Build the complete TASKS module for RealtorOS CRM. This includes task list with table/calendar views, task detail modal, task actions (reschedule, complete, skip, cancel), and custom task creation. This module integrates with the Clients and Emails modules.

---

## PREREQUISITES VERIFICATION

Before starting, verify these exist:
- ✅ `src/lib/types/task.types.ts` - Task TypeScript types
- ✅ `src/lib/api/endpoints/tasks.ts` - Task API functions
- ✅ `src/lib/schemas/task.schema.ts` - Zod validation schemas
- ✅ `src/lib/constants/task.constants.ts` - Task constants/enums
- ✅ `src/lib/hooks/queries/useTasks.ts` - React Query hooks
- ✅ `src/lib/hooks/mutations/useUpdateTask.ts` - Mutation hooks
- ✅ **Module 1 (Clients) completed** - Task detail links to clients
- ✅ Backend API running at `http://localhost:8000`

---

## MODULE 2: TASKS - COMPLETE IMPLEMENTATION

### **TASK 2.1: Task List Page with View Toggle**

**File:** `src/app/(dashboard)/tasks/page.tsx`

**Requirements:**
Create a comprehensive task management page with two view modes: Table and Calendar.

1. **Page Header:**
   - Heading: "Tasks"
   - View toggle buttons: Table / Calendar (shadcn/ui `Tabs`)
   - "Create Custom Task" button (top right)
   - Active filter count badge (e.g., "3 filters active")

2. **Filters Section:**
   - Status filter: Multi-select dropdown (pending, completed, skipped, cancelled)
   - Priority filter: Multi-select dropdown (high, medium, low)
   - Client filter: Autocomplete search by client name
   - Date range filter: Date picker (from/to)
   - Clear all filters button

3. **Table View (Default):**
   - Columns: Client, Type, Scheduled For, Status, Priority, Notes, Actions
   - Client column: Clickable name → navigate to `/clients/{id}`
   - Type column: Badge with followup type
   - Scheduled For: Date + time, color-coded:
     - Red text if overdue (past due date)
     - Yellow background if due today
     - Normal if future
   - Status column: Badge with color from `TASK_STATUS_COLORS`
   - Priority column: Badge with color from `PRIORITY_COLORS`
   - Notes column: Truncated to 50 chars with "..." (tooltip shows full)
   - Actions column: Dropdown menu (View, Reschedule, Complete, Skip)
   - Sortable columns (click header)
   - Pagination (10/25/50/100 per page)

4. **Calendar View:**
   - Monthly calendar using `react-big-calendar`
   - Tasks displayed as events
   - Event color based on priority:
     - High priority: Red (#EF4444)
     - Medium priority: Orange (#F97316)
     - Low priority: Blue (#3B82F6)
   - Event text: Client name + Task type
   - Click event → open Task Detail Modal
   - Drag-and-drop to reschedule (optional enhancement)
   - Today highlighted

5. **Loading States:**
   - Skeleton rows for table view (5 rows)
   - Skeleton calendar for calendar view

6. **Empty States:**
   - Table: "No tasks found. Adjust your filters or create a custom task."
   - Calendar: "No tasks scheduled this month."

7. **Mobile Responsiveness:**
   - Card view instead of table on mobile (< 768px)
   - Calendar switches to week view on mobile

**API Integration:**
```typescript
'use client';

import { useState, useMemo } from 'react';
import { useTasks } from '@/lib/hooks/queries/useTasks';
import { useDebounce } from '@/lib/hooks/ui/useDebounce';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
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

  const { data: tasks, isLoading, isError } = useTasks({
    page,
    limit,
    status: statusFilter.join(',') || undefined,
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
```

---

### **TASK 2.2: Task Filters Component**

**File:** `src/components/tasks/TaskFilters.tsx`

**Requirements:**
Comprehensive filter controls for tasks.

**Implementation:**
```tsx
'use client';

import { Button } from '@/components/ui/button';
import { MultiSelect } from '@/components/ui/multi-select';
import { ClientAutocomplete } from '@/components/tasks/ClientAutocomplete';
import { TASK_STATUSES, PRIORITY_LEVELS, TASK_STATUS_LABELS, PRIORITY_LABELS } from '@/lib/constants/task.constants';
import { X } from 'lucide-react';

interface TaskFiltersProps {
  statusFilter: string[];
  priorityFilter: string[];
  clientFilter: number | null;
  onStatusChange: (status: string[]) => void;
  onPriorityChange: (priority: string[]) => void;
  onClientChange: (clientId: number | null) => void;
  onClearAll: () => void;
}

export function TaskFilters({
  statusFilter,
  priorityFilter,
  clientFilter,
  onStatusChange,
  onPriorityChange,
  onClientChange,
  onClearAll
}: TaskFiltersProps) {
  const hasActiveFilters = statusFilter.length > 0 || priorityFilter.length > 0 || clientFilter !== null;

  return (
    <div className="flex flex-wrap gap-4 items-end">
      {/* Status Filter */}
      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium mb-2 block">Status</label>
        <MultiSelect
          options={TASK_STATUSES.map(status => ({
            value: status,
            label: TASK_STATUS_LABELS[status]
          }))}
          selected={statusFilter}
          onChange={onStatusChange}
          placeholder="All statuses"
        />
      </div>

      {/* Priority Filter */}
      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium mb-2 block">Priority</label>
        <MultiSelect
          options={PRIORITY_LEVELS.map(priority => ({
            value: priority,
            label: PRIORITY_LABELS[priority]
          }))}
          selected={priorityFilter}
          onChange={onPriorityChange}
          placeholder="All priorities"
        />
      </div>

      {/* Client Filter */}
      <div className="flex-1 min-w-[200px]">
        <label className="text-sm font-medium mb-2 block">Client</label>
        <ClientAutocomplete
          value={clientFilter}
          onChange={onClientChange}
        />
      </div>

      {/* Clear Filters */}
      {hasActiveFilters && (
        <Button variant="outline" onClick={onClearAll}>
          <X className="h-4 w-4 mr-2" />
          Clear Filters
        </Button>
      )}
    </div>
  );
}
```

---

### **TASK 2.3: Multi-Select Component**

**File:** `src/components/ui/multi-select.tsx`

**Requirements:**
Reusable multi-select dropdown component.

**Implementation:**
```tsx
'use client';

import * as React from 'react';
import { Check, ChevronsUpDown, X } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';

interface MultiSelectProps {
  options: { value: string; label: string }[];
  selected: string[];
  onChange: (selected: string[]) => void;
  placeholder?: string;
}

export function MultiSelect({
  options,
  selected,
  onChange,
  placeholder = 'Select...'
}: MultiSelectProps) {
  const [open, setOpen] = React.useState(false);

  const handleSelect = (value: string) => {
    if (selected.includes(value)) {
      onChange(selected.filter(v => v !== value));
    } else {
      onChange([...selected, value]);
    }
  };

  const handleRemove = (value: string) => {
    onChange(selected.filter(v => v !== value));
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between"
        >
          <div className="flex gap-1 flex-wrap">
            {selected.length === 0 && (
              <span className="text-muted-foreground">{placeholder}</span>
            )}
            {selected.map(value => {
              const option = options.find(o => o.value === value);
              return (
                <Badge key={value} variant="secondary" className="mr-1">
                  {option?.label}
                  <button
                    className="ml-1 ring-offset-background rounded-full outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleRemove(value);
                      }
                    }}
                    onMouseDown={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemove(value);
                    }}
                  >
                    <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                  </button>
                </Badge>
              );
            })}
          </div>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0">
        <Command>
          <CommandInput placeholder="Search..." />
          <CommandEmpty>No option found.</CommandEmpty>
          <CommandGroup className="max-h-64 overflow-auto">
            {options.map((option) => (
              <CommandItem
                key={option.value}
                value={option.value}
                onSelect={() => handleSelect(option.value)}
              >
                <Check
                  className={cn(
                    'mr-2 h-4 w-4',
                    selected.includes(option.value) ? 'opacity-100' : 'opacity-0'
                  )}
                />
                {option.label}
              </CommandItem>
            ))}
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
```

---

### **TASK 2.4: Client Autocomplete Component**

**File:** `src/components/tasks/ClientAutocomplete.tsx`

**Requirements:**
Searchable client selector with autocomplete.

**Implementation:**
```tsx
'use client';

import * as React from 'react';
import { Check, ChevronsUpDown } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { useClients } from '@/lib/hooks/queries/useClients';

interface ClientAutocompleteProps {
  value: number | null;
  onChange: (clientId: number | null) => void;
}

export function ClientAutocomplete({ value, onChange }: ClientAutocompleteProps) {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState('');

  // Fetch all clients (or implement search API)
  const { data: clients, isLoading } = useClients({ limit: 100 });

  const selectedClient = clients?.find(c => c.id === value);

  // Client-side search
  const filteredClients = React.useMemo(() => {
    if (!clients) return [];
    if (!search) return clients;
    return clients.filter(c =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.email.toLowerCase().includes(search.toLowerCase())
    );
  }, [clients, search]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between"
        >
          {value && selectedClient
            ? selectedClient.name
            : "All clients"}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0">
        <Command>
          <CommandInput
            placeholder="Search clients..."
            value={search}
            onValueChange={setSearch}
          />
          <CommandEmpty>
            {isLoading ? 'Loading...' : 'No client found.'}
          </CommandEmpty>
          <CommandGroup className="max-h-64 overflow-auto">
            <CommandItem
              value="all"
              onSelect={() => {
                onChange(null);
                setOpen(false);
              }}
            >
              <Check
                className={cn(
                  'mr-2 h-4 w-4',
                  !value ? 'opacity-100' : 'opacity-0'
                )}
              />
              All clients
            </CommandItem>
            {filteredClients.map((client) => (
              <CommandItem
                key={client.id}
                value={client.id.toString()}
                onSelect={() => {
                  onChange(client.id);
                  setOpen(false);
                }}
              >
                <Check
                  className={cn(
                    'mr-2 h-4 w-4',
                    value === client.id ? 'opacity-100' : 'opacity-0'
                  )}
                />
                <div>
                  <div className="font-medium">{client.name}</div>
                  <div className="text-sm text-muted-foreground">{client.email}</div>
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
```

---

### **TASK 2.5: Task Table Component**

**File:** `src/components/tasks/TaskTable.tsx`

**Requirements:**
Table view with all task columns, sorting, and actions.

**Implementation:**
```tsx
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
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import { TaskStatusBadge } from '@/components/tasks/TaskStatusBadge';
import { TaskPriorityBadge } from '@/components/tasks/TaskPriorityBadge';
import { TaskActionsMenu } from '@/components/tasks/TaskActionsMenu';
import { TaskDetailModal } from '@/components/tasks/TaskDetailModal';
import { formatDate, formatDateTime } from '@/lib/utils/date';
import { truncateText } from '@/lib/utils/formatters';
import { cn } from '@/lib/utils/cn';
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
  const { data: clients } = useClients({ limit: 1000 });
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
                    'cursor-pointer hover:bg-muted/50',
                    dateStatus === 'overdue' && task.status === 'pending' && 'bg-red-50',
                    dateStatus === 'today' && task.status === 'pending' && 'bg-yellow-50'
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
```

---

### **TASK 2.6: Task Status and Priority Badges**

**File:** `src/components/tasks/TaskStatusBadge.tsx`

```tsx
import { Badge } from '@/components/ui/badge';
import { TaskStatus } from '@/lib/types/task.types';
import { TASK_STATUS_LABELS, TASK_STATUS_COLORS } from '@/lib/constants/task.constants';
import { cn } from '@/lib/utils/cn';

interface TaskStatusBadgeProps {
  status: TaskStatus;
}

export function TaskStatusBadge({ status }: TaskStatusBadgeProps) {
  return (
    <Badge className={cn(TASK_STATUS_COLORS[status])}>
      {TASK_STATUS_LABELS[status]}
    </Badge>
  );
}
```

**File:** `src/components/tasks/TaskPriorityBadge.tsx`

```tsx
import { Badge } from '@/components/ui/badge';
import { Priority } from '@/lib/types/task.types';
import { PRIORITY_LABELS, PRIORITY_COLORS } from '@/lib/constants/task.constants';
import { cn } from '@/lib/utils/cn';

interface TaskPriorityBadgeProps {
  priority: Priority;
}

export function TaskPriorityBadge({ priority }: TaskPriorityBadgeProps) {
  return (
    <Badge className={cn(PRIORITY_COLORS[priority])}>
      {PRIORITY_LABELS[priority]}
    </Badge>
  );
}
```

---

### **TASK 2.7: Task Calendar Component**

**File:** `src/components/tasks/TaskCalendar.tsx`

**Requirements:**
Monthly calendar view with tasks as events.

**Installation:**
```bash
npm install react-big-calendar date-fns
npm install -D @types/react-big-calendar
```

**Implementation:**
```tsx
'use client';

import { useMemo, useState } from 'react';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { Task } from '@/lib/types/task.types';
import { TaskDetailModal } from '@/components/tasks/TaskDetailModal';
import { useClients } from '@/lib/hooks/queries/useClients';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const locales = {
  'en-US': enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

interface TaskCalendarProps {
  tasks: Task[];
  isLoading: boolean;
}

export function TaskCalendar({ tasks, isLoading }: TaskCalendarProps) {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const { data: clients } = useClients({ limit: 1000 });

  const clientMap = useMemo(() => {
    if (!clients) return {};
    return Object.fromEntries(clients.map(c => [c.id, c]));
  }, [clients]);

  const events = useMemo(() => {
    return tasks.map(task => {
      const client = clientMap[task.client_id];
      return {
        id: task.id,
        title: `${client?.name || 'Unknown'} - ${task.followup_type}`,
        start: new Date(task.scheduled_for),
        end: new Date(task.scheduled_for),
        resource: task,
      };
    });
  }, [tasks, clientMap]);

  const eventStyleGetter = (event: any) => {
    const task = event.resource as Task;
    let backgroundColor = '#3B82F6'; // blue (low priority)

    if (task.priority === 'high') {
      backgroundColor = '#EF4444'; // red
    } else if (task.priority === 'medium') {
      backgroundColor = '#F97316'; // orange
    }

    // Grey out completed tasks
    if (task.status === 'completed' || task.status === 'skipped') {
      backgroundColor = '#9CA3AF'; // gray
    }

    return {
      style: {
        backgroundColor,
        borderRadius: '4px',
        opacity: 0.8,
        color: 'white',
        border: '0',
        display: 'block',
      },
    };
  };

  if (isLoading) {
    return <div className="h-[600px] flex items-center justify-center">
      <p className="text-muted-foreground">Loading calendar...</p>
    </div>;
  }

  return (
    <>
      <div className="h-[600px] bg-white p-4 rounded-lg border">
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: '100%' }}
          eventPropGetter={eventStyleGetter}
          onSelectEvent={(event) => setSelectedTask(event.resource)}
          views={['month', 'week', 'day']}
          defaultView="month"
        />
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
```

**Add Calendar Styles:** `src/app/globals.css`

```css
/* React Big Calendar custom styles */
.rbc-calendar {
  font-family: inherit;
}

.rbc-header {
  padding: 10px 3px;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
}

.rbc-today {
  background-color: #fef3c7;
}

.rbc-event {
  padding: 2px 5px;
  font-size: 0.875rem;
  cursor: pointer;
}

.rbc-event:hover {
  opacity: 1 !important;
}
```

---

### **TASK 2.8: Task Detail Modal**

**File:** `src/components/tasks/TaskDetailModal.tsx`

**Requirements:**
Modal showing complete task details with actions.

**Implementation:**
```tsx
'use client';

import { Task } from '@/lib/types/task.types';
import { useClient } from '@/lib/hooks/queries/useClients';
import { useEmail } from '@/lib/hooks/queries/useEmails';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { TaskStatusBadge } from '@/components/tasks/TaskStatusBadge';
import { TaskPriorityBadge } from '@/components/tasks/TaskPriorityBadge';
import { TaskActionsMenu } from '@/components/tasks/TaskActionsMenu';
import { formatDateTime } from '@/lib/utils/date';
import { Calendar, User, Mail, FileText } from 'lucide-react';
import Link from 'next/link';

interface TaskDetailModalProps {
  task: Task;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TaskDetailModal({ task, open, onOpenChange }: TaskDetailModalProps) {
  const { data: client, isLoading: clientLoading } = useClient(task.client_id);
  const { data: email, isLoading: emailLoading } = useEmail(
    task.email_sent_id || 0,
    { enabled: !!task.email_sent_id }
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex justify-between items-start">
            <div>
              <DialogTitle className="text-2xl">{task.followup_type}</DialogTitle>
              <DialogDescription>Task #{task.id}</DialogDescription>
            </div>
            <TaskActionsMenu task={task} />
          </div>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Task Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Task Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Scheduled:</span>
                <span className="text-sm">{formatDateTime(task.scheduled_for)}</span>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Status:</span>
                <TaskStatusBadge status={task.status} />
              </div>

              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Priority:</span>
                <TaskPriorityBadge priority={task.priority} />
              </div>

              {task.notes && (
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Notes:</span>
                  </div>
                  <p className="text-sm text-muted-foreground pl-6">{task.notes}</p>
                </div>
              )}

              {task.completed_at && (
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Completed:</span>
                  <span className="text-sm">{formatDateTime(task.completed_at)}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Client Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Client</CardTitle>
            </CardHeader>
            <CardContent>
              {clientLoading ? (
                <Skeleton className="h-20 w-full" />
              ) : client ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <Link
                      href={`/clients/${client.id}`}
                      className="font-medium hover:underline"
                    >
                      {client.name}
                    </Link>
                  </div>
                  <p className="text-sm text-muted-foreground pl-6">{client.email}</p>
                  <p className="text-sm text-muted-foreground pl-6">{client.property_address}</p>
                  <p className="text-sm text-muted-foreground pl-6">Stage: {client.stage}</p>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Client not found</p>
              )}
            </CardContent>
          </Card>

          {/* Email Info (if sent) */}
          {task.email_sent_id && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Email Sent</CardTitle>
              </CardHeader>
              <CardContent>
                {emailLoading ? (
                  <Skeleton className="h-20 w-full" />
                ) : email ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <Link
                        href={`/emails/${email.id}`}
                        className="font-medium hover:underline"
                      >
                        {email.subject}
                      </Link>
                    </div>
                    <p className="text-sm text-muted-foreground pl-6">
                      Status: {email.status}
                    </p>
                    {email.sent_at && (
                      <p className="text-sm text-muted-foreground pl-6">
                        Sent: {formatDateTime(email.sent_at)}
                      </p>
                    )}
                    {email.opened_at && (
                      <p className="text-sm text-green-600 pl-6">
                        ✓ Opened: {formatDateTime(email.opened_at)}
                      </p>
                    )}
                    {email.clicked_at && (
                      <p className="text-sm text-purple-600 pl-6">
                        ✓ Clicked: {formatDateTime(email.clicked_at)}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Email not found</p>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

---

### **TASK 2.9: Task Actions Menu**

**File:** `src/components/tasks/TaskActionsMenu.tsx`

**Requirements:**
Dropdown menu with task actions.

**Implementation:**
```tsx
'use client';

import { useState } from 'react';
import { Task } from '@/lib/types/task.types';
import { useUpdateTask } from '@/lib/hooks/mutations/useUpdateTask';
import { useToast } from '@/lib/hooks/ui/useToast';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { TaskRescheduleDialog } from '@/components/tasks/TaskRescheduleDialog';
import { MoreVertical, Calendar, CheckCircle, XCircle, SkipForward, Mail } from 'lucide-react';

interface TaskActionsMenuProps {
  task: Task;
}

export function TaskActionsMenu({ task }: TaskActionsMenuProps) {
  const { toast } = useToast();
  const updateTask = useUpdateTask();
  const [rescheduleOpen, setRescheduleOpen] = useState(false);

  const handleStatusChange = async (status: 'completed' | 'skipped' | 'cancelled') => {
    try {
      await updateTask.mutateAsync({
        id: task.id,
        data: { status }
      });
      toast({
        title: "Task updated",
        description: `Task marked as ${status}`,
      });
    } catch (error: any) {
      toast({
        title: "Error updating task",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => setRescheduleOpen(true)}>
            <Calendar className="h-4 w-4 mr-2" />
            Reschedule
          </DropdownMenuItem>

          {task.status === 'pending' && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleStatusChange('completed')}>
                <CheckCircle className="h-4 w-4 mr-2" />
                Mark Complete
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleStatusChange('skipped')}>
                <SkipForward className="h-4 w-4 mr-2" />
                Skip Task
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => handleStatusChange('cancelled')}
                className="text-destructive"
              >
                <XCircle className="h-4 w-4 mr-2" />
                Cancel Task
              </DropdownMenuItem>

              {!task.email_sent_id && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <Mail className="h-4 w-4 mr-2" />
                    Send Email
                  </DropdownMenuItem>
                </>
              )}
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>

      <TaskRescheduleDialog
        task={task}
        open={rescheduleOpen}
        onOpenChange={setRescheduleOpen}
      />
    </>
  );
}
```

---

### **TASK 2.10: Task Reschedule Dialog**

**File:** `src/components/tasks/TaskRescheduleDialog.tsx`

**Requirements:**
Dialog with date/time picker to reschedule tasks.

**Installation:**
```bash
npx shadcn-ui@latest add calendar popover
npm install react-day-picker date-fns
```

**Implementation:**
```tsx
'use client';

import { useState } from 'react';
import { Task } from '@/lib/types/task.types';
import { useUpdateTask } from '@/lib/hooks/mutations/useUpdateTask';
import { useToast } from '@/lib/hooks/ui/useToast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { formatDate } from '@/lib/utils/date';

interface TaskRescheduleDialogProps {
  task: Task;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TaskRescheduleDialog({ task, open, onOpenChange }: TaskRescheduleDialogProps) {
  const currentDate = new Date(task.scheduled_for);
  const [selectedDate, setSelectedDate] = useState<Date>(currentDate);
  const [selectedTime, setSelectedTime] = useState<string>(
    currentDate.toTimeString().slice(0, 5) // HH:MM
  );

  const { toast } = useToast();
  const updateTask = useUpdateTask();

  const handleReschedule = async () => {
    try {
      // Combine date and time
      const [hours, minutes] = selectedTime.split(':');
      const newDate = new Date(selectedDate);
      newDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      await updateTask.mutateAsync({
        id: task.id,
        data: { scheduled_for: newDate.toISOString() }
      });

      toast({
        title: "Task rescheduled",
        description: `Task scheduled for ${formatDate(newDate, 'PPP p')}`,
      });

      onOpenChange(false);
    } catch (error: any) {
      toast({
        title: "Error rescheduling task",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Reschedule Task</DialogTitle>
          <DialogDescription>
            Choose a new date and time for this task
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>Date</Label>
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={(date) => date && setSelectedDate(date)}
              disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
              className="rounded-md border"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="time">Time</Label>
            <Input
              id="time"
              type="time"
              value={selectedTime}
              onChange={(e) => setSelectedTime(e.target.value)}
            />
          </div>

          <div className="text-sm text-muted-foreground">
            Current: {formatDate(currentDate, 'PPP p')}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleReschedule} disabled={updateTask.isPending}>
            {updateTask.isPending ? 'Rescheduling...' : 'Reschedule'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

---

### **TASK 2.11: Create Custom Task Dialog**

**File:** `src/components/tasks/CreateTaskDialog.tsx`

**Requirements:**
Dialog form to create custom tasks.

**Implementation:**
```tsx
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { taskCreateSchema, TaskCreateFormData } from '@/lib/schemas/task.schema';
import { useCreateTask } from '@/lib/hooks/mutations/useCreateTask';
import { useToast } from '@/lib/hooks/ui/useToast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Calendar } from '@/components/ui/calendar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ClientAutocomplete } from '@/components/tasks/ClientAutocomplete';
import { PRIORITY_LEVELS, PRIORITY_LABELS } from '@/lib/constants/task.constants';

interface CreateTaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultClientId?: number;
}

export function CreateTaskDialog({ open, onOpenChange, defaultClientId }: CreateTaskDialogProps) {
  const { toast } = useToast();
  const createTask = useCreateTask();
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [selectedTime, setSelectedTime] = useState<string>('09:00');

  const form = useForm<TaskCreateFormData>({
    resolver: zodResolver(taskCreateSchema),
    defaultValues: {
      client_id: defaultClientId || 0,
      followup_type: 'Custom',
      scheduled_for: new Date().toISOString(),
      priority: 'medium',
      notes: ''
    }
  });

  const handleSubmit = async (data: TaskCreateFormData) => {
    try {
      // Combine date and time
      const [hours, minutes] = selectedTime.split(':');
      const scheduledDate = new Date(selectedDate);
      scheduledDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      await createTask.mutateAsync({
        ...data,
        scheduled_for: scheduledDate.toISOString()
      });

      toast({
        title: "Task created",
        description: "Custom task has been added successfully.",
      });

      form.reset();
      onOpenChange(false);
    } catch (error: any) {
      toast({
        title: "Error creating task",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Custom Task</DialogTitle>
          <DialogDescription>
            Add a custom follow-up task for a client
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            {/* Client Selection */}
            <FormField
              control={form.control}
              name="client_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Client *</FormLabel>
                  <FormControl>
                    <ClientAutocomplete
                      value={field.value || null}
                      onChange={(id) => field.onChange(id || 0)}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Priority */}
            <FormField
              control={form.control}
              name="priority"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Priority *</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {PRIORITY_LEVELS.map(priority => (
                        <SelectItem key={priority} value={priority}>
                          {PRIORITY_LABELS[priority]}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Date */}
            <div className="space-y-2">
              <FormLabel>Scheduled Date *</FormLabel>
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={(date) => date && setSelectedDate(date)}
                disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
                className="rounded-md border"
              />
            </div>

            {/* Time */}
            <div className="space-y-2">
              <FormLabel>Scheduled Time *</FormLabel>
              <Input
                type="time"
                value={selectedTime}
                onChange={(e) => setSelectedTime(e.target.value)}
              />
            </div>

            {/* Notes */}
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Add notes about this task..."
                      className="resize-none"
                      rows={3}
                      {...field}
                      maxLength={500}
                    />
                  </FormControl>
                  <FormDescription>
                    {field.value?.length || 0}/500 characters
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={createTask.isPending}>
                {createTask.isPending ? 'Creating...' : 'Create Task'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
```

---

### **TASK 2.12: Add Create Task Mutation Hook**

**File:** `src/lib/hooks/mutations/useCreateTask.ts`

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi } from '@/lib/api/endpoints/tasks';
import { TaskCreate } from '@/lib/types/task.types';

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (task: TaskCreate) => tasksApi.create(task),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
```

---

## TESTING CHECKLIST

After implementing all tasks, verify:

### **Functionality:**
- [ ] Task list loads with all tasks
- [ ] Filter by status (pending, completed, skipped, cancelled)
- [ ] Filter by priority (high, medium, low)
- [ ] Filter by client (autocomplete search)
- [ ] Clear all filters button works
- [ ] Switch between table and calendar views
- [ ] Table sorting works (click column headers)
- [ ] Overdue tasks highlighted in red
- [ ] Tasks due today highlighted in yellow
- [ ] Click task row opens detail modal
- [ ] Calendar displays tasks as events
- [ ] Click calendar event opens detail modal
- [ ] Calendar events color-coded by priority
- [ ] Task detail modal shows all information
- [ ] Reschedule task dialog works
- [ ] Mark task as complete/skip/cancel works
- [ ] Create custom task dialog works
- [ ] Client autocomplete search works
- [ ] Pagination works

### **UI/UX:**
- [ ] Loading skeletons appear while fetching
- [ ] Empty states display correctly
- [ ] Toast notifications for all actions
- [ ] Modal animations smooth
- [ ] Responsive on mobile (card view)
- [ ] Calendar responsive (week view on mobile)
- [ ] Date picker prevents past dates
- [ ] Time picker format correct (24-hour)
- [ ] Character counters work

### **Performance:**
- [ ] Page loads in < 2 seconds
- [ ] Calendar renders smoothly with 100+ tasks
- [ ] Filter changes are instant
- [ ] No layout shift

---

## COMMON ISSUES & SOLUTIONS

### **Issue: "Calendar not rendering"**
**Solution:** Ensure CSS is imported in component:
```tsx
import 'react-big-calendar/lib/css/react-big-calendar.css';
```

### **Issue: "Client autocomplete not working"**
**Solution:** Increase client limit or implement backend search:
```typescript
const { data: clients } = useClients({ limit: 1000 });
```

### **Issue: "Date picker allows past dates"**
**Solution:** Add disabled prop to Calendar:
```tsx
disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
```

### **Issue: "Task status not updating in list"**
**Solution:** Ensure mutation invalidates queries:
```typescript
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: ['tasks'] });
}
```

---

## SUCCESS CRITERIA

Module 2 (Tasks) is complete when:
- ✅ Task list page with table/calendar views working
- ✅ All filters functional (status, priority, client)
- ✅ Task detail modal displays complete information
- ✅ All task actions work (reschedule, complete, skip, cancel)
- ✅ Create custom task functional
- ✅ Client autocomplete search works
- ✅ Calendar view displays tasks correctly
- ✅ Responsive on all screen sizes
- ✅ All error states handled
- ✅ Toast notifications for all actions

---

## NEXT STEPS

After completing Module 2, proceed to:
- **Module 3: Emails** (Email preview, send, engagement tracking)
- **Module 4: Dashboard** (Stats, activity feed, charts)

---

**START IMPLEMENTING MODULE 2 NOW!** Follow the tasks in order (2.1 → 2.12). Test each component thoroughly before moving to the next. Good luck! 🚀
