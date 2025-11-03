# Tasks Module - RealtorOS CRM

## 📋 Overview

The Tasks module is a comprehensive task management system for RealtorOS that handles follow-up task scheduling, tracking, and automation. It integrates seamlessly with the Clients and Emails modules to provide a complete workflow for real estate client relationship management.

### Purpose

Tasks automate and organize follow-up activities with clients throughout their real estate journey. The system supports:

- **Automated follow-up scheduling**: Automatically creates tasks based on predefined schedules (Day 1, Day 3, Week 1, Week 2, Month 1)
- **Custom task creation**: Allows manual creation of custom follow-up tasks
- **Task management**: View, filter, reschedule, complete, skip, or cancel tasks
- **Visual calendar view**: See all tasks in a monthly calendar format
- **Integration with emails**: Links tasks to sent emails for tracking engagement

---

## 🏗️ Architecture

### Frontend Structure

```
frontend/src/
├── app/(dashboard)/tasks/
│   └── page.tsx                    # Main tasks page with table/calendar views
├── components/tasks/
│   ├── ClientAutocomplete.tsx      # Client search/selection component
│   ├── CreateTaskDialog.tsx        # Form to create custom tasks
│   ├── TaskActionsMenu.tsx         # Dropdown menu with task actions
│   ├── TaskCalendar.tsx            # Calendar view component
│   ├── TaskDetailModal.tsx         # Modal showing full task details
│   ├── TaskFilters.tsx             # Filter controls (status, priority, client)
│   ├── TaskPriorityBadge.tsx       # Priority indicator badge
│   ├── TaskRescheduleDialog.tsx    # Dialog to reschedule tasks
│   ├── TaskStatusBadge.tsx         # Status indicator badge
│   └── TaskTable.tsx               # Table view component
└── lib/
    ├── api/endpoints/tasks.ts      # API client functions
    ├── constants/task.constants.ts # Constants (statuses, priorities, labels)
    ├── hooks/
    │   ├── queries/useTasks.ts     # React Query hook for fetching tasks
    │   └── mutations/
    │       ├── useCreateTask.ts    # Mutation hook for creating tasks
    │       └── useUpdateTask.ts    # Mutation hook for updating tasks
    ├── schemas/task.schema.ts      # Zod validation schemas
    └── types/task.types.ts         # TypeScript type definitions
```

### Backend Structure

```
backend/app/
├── api/routes/tasks.py              # FastAPI task endpoints
├── models/task.py                   # SQLAlchemy Task model
├── schemas/task_schema.py           # Pydantic schemas for validation
└── services/scheduler_service.py    # Business logic for task management
```

---

## 🎯 Features

### 1. **Dual View Modes**

#### Table View (Default)
- Sortable columns (Client, Type, Scheduled For, Status, Priority, Notes)
- Color-coded dates:
  - 🔴 **Red text**: Overdue tasks (past due date)
  - 🟡 **Yellow background**: Tasks due today
  - Normal: Future tasks
- Pagination (10, 25, 50, 100 items per page)
- Click row to open task detail modal
- Quick actions menu on each row

#### Calendar View
- Monthly calendar using `react-big-calendar`
- Tasks displayed as colored events:
  - 🔴 **Red**: High priority
  - 🟠 **Orange**: Medium priority
  - 🔵 **Blue**: Low priority
  - ⚫ **Gray**: Completed or skipped tasks
- Click event to open task detail modal
- Switch between month/week/day views

### 2. **Advanced Filtering**

- **Status Filter**: Multi-select dropdown
  - Pending
  - Completed
  - Skipped
  - Cancelled
  
- **Priority Filter**: Multi-select dropdown
  - High
  - Medium
  - Low
  
- **Client Filter**: Autocomplete search
  - Search by client name or email
  - Shows all clients when cleared

- **Clear All Filters**: One-click button to reset all filters

### 3. **Task Actions**

Available through the actions dropdown menu:

- **View Details**: Opens comprehensive task detail modal
- **Reschedule**: Change the scheduled date and time
- **Mark Complete**: Mark task as completed
- **Skip Task**: Skip this task (keeps it in history)
- **Cancel Task**: Cancel the task permanently
- **Send Email**: (if email not yet sent) Navigate to email sending

### 4. **Task Detail Modal**

Shows complete information about a task:

- **Task Information**
  - Follow-up type (Day 1, Day 3, Week 1, Week 2, Month 1, Custom)
  - Scheduled date and time
  - Current status and priority
  - Notes (if any)
  - Completion timestamp (if completed)
  
- **Client Information**
  - Client name (clickable link to client page)
  - Email address
  - Property address
  - Current stage in pipeline
  
- **Email Information** (if email was sent)
  - Email subject (clickable link to email page)
  - Email status
  - Sent timestamp
  - Opened timestamp (if opened)
  - Clicked timestamp (if clicked)

### 5. **Create Custom Tasks**

Dialog form to manually create follow-up tasks:

- **Required Fields**
  - Client selection (autocomplete search)
  - Priority level (high, medium, low)
  - Scheduled date (date picker)
  - Scheduled time (time picker)
  
- **Optional Fields**
  - Follow-up type (defaults to "Custom")
  - Notes (up to 500 characters with counter)

- **Validation**
  - Client must be selected
  - Date cannot be in the past
  - All required fields must be filled

### 6. **Automated Task Creation**

Tasks are automatically created by the backend scheduler service:

- **Follow-up Schedule Types**
  - Day 1: First follow-up after client creation
  - Day 3: Follow-up 3 days after creation
  - Week 1: Follow-up 1 week after creation
  - Week 2: Follow-up 2 weeks after creation
  - Month 1: Follow-up 1 month after creation

- **Automatic Scheduling**
  - Tasks are created when clients are added to the system
  - Based on predefined schedules in `followup_schedules.py`
  - All initial tasks start with status "pending"

---

## 📊 Data Model

### Task Entity

```typescript
interface Task {
  id: number;                    // Unique task identifier
  client_id: number;             // Reference to client (required)
  email_sent_id?: number;        // Reference to email log (optional)
  followup_type: FollowupType;  // Day 1 | Day 3 | Week 1 | Week 2 | Month 1 | Custom
  scheduled_for: string;        // ISO 8601 datetime string (UTC)
  status: TaskStatus;           // pending | completed | skipped | cancelled
  priority: Priority;           // high | medium | low
  notes?: string;               // Optional notes (max 500 chars)
  created_at: string;           // ISO 8601 datetime string (UTC)
  updated_at: string;           // ISO 8601 datetime string (UTC)
  completed_at?: string;         // ISO 8601 datetime string (UTC, optional)
}
```

### Task Status Flow

```
pending ──→ completed (when task is done)
   │
   ├──→ skipped (skip this task)
   │
   └──→ cancelled (cancel permanently)
```

### Follow-up Types

| Type | Description | Auto-Generated |
|------|-------------|----------------|
| Day 1 | First follow-up after client creation | ✅ Yes |
| Day 3 | Follow-up 3 days after creation | ✅ Yes |
| Week 1 | Follow-up 1 week after creation | ✅ Yes |
| Week 2 | Follow-up 2 weeks after creation | ✅ Yes |
| Month 1 | Follow-up 1 month after creation | ✅ Yes |
| Custom | Manually created task | ❌ No |

### Priority Levels

| Priority | Color | Use Case |
|----------|-------|-----------|
| High | 🔴 Red | Urgent tasks, time-sensitive follow-ups |
| Medium | 🟠 Orange | Standard follow-ups (default) |
| Low | 🔵 Blue | Low-priority or informational tasks |

---

## 🔌 API Endpoints

### Base URL
```
/api/tasks/
```

### Endpoints

#### 1. List Tasks
```
GET /api/tasks/
```

**Query Parameters:**
- `page` (optional, default: 1): Page number (minimum: 1)
- `limit` (optional, default: 10): Items per page (minimum: 1, maximum: 100)
- `status` (optional): Filter by status (comma-separated, e.g., "pending,completed")
- `client_id` (optional): Filter by client ID

**Response:**
```json
[
  {
    "id": 1,
    "client_id": 5,
    "email_sent_id": null,
    "followup_type": "Day 1",
    "scheduled_for": "2024-01-15T10:00:00Z",
    "status": "pending",
    "priority": "medium",
    "notes": "Initial contact follow-up",
    "created_at": "2024-01-14T08:00:00Z",
    "updated_at": "2024-01-14T08:00:00Z",
    "completed_at": null
  }
]
```

#### 2. Get Task by ID
```
GET /api/tasks/{task_id}
```

**Response:** Single task object (same structure as list item)

#### 3. Create Task
```
POST /api/tasks/
```

**Request Body:**
```json
{
  "client_id": 5,
  "followup_type": "Custom",
  "scheduled_for": "2024-01-20T14:00:00Z",
  "priority": "high",
  "notes": "Custom follow-up task"
}
```

**Response:** Created task object

#### 4. Update Task
```
PATCH /api/tasks/{task_id}
```

**Request Body:**
```json
{
  "status": "completed",
  "scheduled_for": "2024-01-21T15:00:00Z",
  "priority": "low",
  "notes": "Updated notes"
}
```

**Note:** All fields are optional. Only include fields you want to update.

**Response:** Updated task object

---

## 🧩 Component Details

### TaskTable Component

**File:** `TaskTable.tsx`

**Features:**
- Sortable columns (click headers to sort)
- Color-coded date display
- Pagination controls
- Click row to open detail modal
- Loading skeleton state
- Empty state message

**Props:**
```typescript
interface TaskTableProps {
  tasks: Task[];
  isLoading: boolean;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  onLimitChange: (limit: number) => void;
}
```

### TaskCalendar Component

**File:** `TaskCalendar.tsx`

**Features:**
- Monthly calendar view with `react-big-calendar`
- Color-coded events by priority
- Click event to open detail modal
- Today highlighted
- Responsive (switches to week view on mobile)

**Dependencies:**
- `react-big-calendar`
- `date-fns`
- `@types/react-big-calendar`

**Props:**
```typescript
interface TaskCalendarProps {
  tasks: Task[];
  isLoading: boolean;
}
```

### TaskFilters Component

**File:** `TaskFilters.tsx`

**Features:**
- Multi-select status filter
- Multi-select priority filter
- Client autocomplete filter
- Clear all filters button
- Active filter count display

**Props:**
```typescript
interface TaskFiltersProps {
  statusFilter: string[];
  priorityFilter: string[];
  clientFilter: number | null;
  onStatusChange: (status: string[]) => void;
  onPriorityChange: (priority: string[]) => void;
  onClientChange: (clientId: number | null) => void;
  onClearAll: () => void;
}
```

### TaskDetailModal Component

**File:** `TaskDetailModal.tsx`

**Features:**
- Complete task information display
- Client information with link
- Email information with link (if available)
- Task actions menu
- Responsive modal design

**Props:**
```typescript
interface TaskDetailModalProps {
  task: Task;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}
```

### CreateTaskDialog Component

**File:** `CreateTaskDialog.tsx`

**Features:**
- Form validation with Zod
- Client autocomplete
- Date and time pickers
- Notes field with character counter
- Loading state during submission

**Props:**
```typescript
interface CreateTaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultClientId?: number;
}
```

### TaskActionsMenu Component

**File:** `TaskActionsMenu.tsx`

**Features:**
- Dropdown menu with task actions
- Reschedule dialog trigger
- Status change handlers
- Conditional menu items based on task status
- Toast notifications for actions

**Props:**
```typescript
interface TaskActionsMenuProps {
  task: Task;
}
```

### TaskRescheduleDialog Component

**File:** `TaskRescheduleDialog.tsx`

**Features:**
- Calendar date picker
- Time input field
- Validation (prevents past dates)
- Shows current scheduled time
- Updates task via API

**Props:**
```typescript
interface TaskRescheduleDialogProps {
  task: Task;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}
```

---

## 🔗 Integration with Other Modules

### Clients Module

**Relationship:** Tasks belong to clients (one-to-many)

- Clicking a client name in the task table navigates to `/clients/{client_id}`
- Client autocomplete filter uses the clients API endpoint
- Task detail modal shows client information with navigation link

**Data Flow:**
1. Client created → Automatic tasks scheduled
2. Client updated → No impact on existing tasks
3. Client deleted → Tasks remain but client reference may be invalid

### Emails Module

**Relationship:** Tasks can have one associated email (one-to-one)

- When an email is sent for a task, `email_sent_id` is populated
- Task detail modal shows email information if available
- Email engagement tracking (opened, clicked) visible in task details

**Data Flow:**
1. Task created → Email can be sent manually
2. Email sent → Task's `email_sent_id` updated
3. Email opened/clicked → Engagement visible in task detail

### Dashboard Module

**Relationship:** Tasks contribute to dashboard statistics

- Dashboard shows task counts (pending, completed, overdue)
- Task creation/completion updates dashboard stats
- Dashboard queries use task filtering APIs

---

## 💻 Usage Examples

### Fetching Tasks with Filters

```typescript
import { useTasks } from '@/lib/hooks/queries/useTasks';

function MyComponent() {
  const { data: tasks, isLoading } = useTasks({
    page: 1,
    limit: 25,
    status: 'pending',
    client_id: 5
  });

  if (isLoading) return <div>Loading...</div>;
  
  return (
    <div>
      {tasks?.map(task => (
        <div key={task.id}>{task.followup_type}</div>
      ))}
    </div>
  );
}
```

### Creating a Custom Task

```typescript
import { useCreateTask } from '@/lib/hooks/mutations/useCreateTask';

function CreateTask() {
  const createTask = useCreateTask();
  
  const handleCreate = async () => {
    try {
      await createTask.mutateAsync({
        client_id: 5,
        followup_type: 'Custom',
        scheduled_for: new Date().toISOString(),
        priority: 'high',
        notes: 'Custom follow-up task'
      });
      console.log('Task created successfully!');
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };
  
  return (
    <button onClick={handleCreate} disabled={createTask.isPending}>
      {createTask.isPending ? 'Creating...' : 'Create Task'}
    </button>
  );
}
```

### Updating Task Status

```typescript
import { useUpdateTask } from '@/lib/hooks/mutations/useUpdateTask';

function TaskActions({ taskId }: { taskId: number }) {
  const updateTask = useUpdateTask();
  
  const handleComplete = async () => {
    try {
      await updateTask.mutateAsync({
        id: taskId,
        data: { status: 'completed' }
      });
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };
  
  return <button onClick={handleComplete}>Mark Complete</button>;
}
```

---

## 🎨 Styling & UI

### Status Badge Colors

- **Pending**: Yellow (`bg-yellow-100 text-yellow-800`)
- **Completed**: Green (`bg-green-100 text-green-800`)
- **Skipped**: Gray (`bg-gray-100 text-gray-800`)
- **Cancelled**: Red (`bg-red-100 text-red-800`)

### Priority Badge Colors

- **High**: Red (`bg-red-100 text-red-800`)
- **Medium**: Orange (`bg-orange-100 text-orange-800`)
- **Low**: Blue (`bg-blue-100 text-blue-800`)

### Calendar Event Colors

- **High Priority**: Red (`#EF4444`)
- **Medium Priority**: Orange (`#F97316`)
- **Low Priority**: Blue (`#3B82F6`)
- **Completed/Skipped**: Gray (`#9CA3AF`)

### Responsive Design

- **Desktop (> 768px)**: Full table view, monthly calendar
- **Mobile (< 768px)**: Card view, week calendar view

---

## 🔧 Development Notes

### Adding a New Follow-up Type

1. **Backend**: Update `FollowupType` enum in `task_schema.py`:
   ```python
   followup_type: str = Field(..., pattern=r'^(Day 1|Day 3|Week 1|Week 2|Month 1|Custom|New Type)$')
   ```

2. **Frontend**: Update `FollowupType` in `task.types.ts`:
   ```typescript
   export type FollowupType = 'Day 1' | 'Day 3' | 'Week 1' | 'Week 2' | 'Month 1' | 'Custom' | 'New Type';
   ```

3. **Frontend**: Update `FOLLOWUP_TYPES` constant in `task.constants.ts`:
   ```typescript
   export const FOLLOWUP_TYPES: FollowupType[] = [
     // ... existing types
     'New Type'
   ];
   ```

### Adding a New Task Status

1. **Backend**: Update `TaskUpdate` schema in `task_schema.py`:
   ```python
   status: Optional[str] = Field(None, pattern=r'^(pending|completed|skipped|cancelled|new_status)$')
   ```

2. **Frontend**: Update `TaskStatus` type in `task.types.ts`:
   ```typescript
   export type TaskStatus = 'pending' | 'completed' | 'skipped' | 'cancelled' | 'new_status';
   ```

3. **Frontend**: Add to constants in `task.constants.ts`:
   ```typescript
   export const TASK_STATUSES: TaskStatus[] = [
     // ... existing statuses
     'new_status'
   ];
   
   export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
     // ... existing labels
     new_status: 'New Status'
   };
   
   export const TASK_STATUS_COLORS: Record<TaskStatus, string> = {
     // ... existing colors
     new_status: 'bg-purple-100 text-purple-800'
   };
   ```

### Testing Components

Each component should be tested for:

- **Rendering**: Component renders without errors
- **User Interactions**: Buttons, clicks, form submissions work
- **Loading States**: Skeleton loaders appear during data fetching
- **Empty States**: Empty state message shows when no data
- **Error Handling**: Error messages display on API failures
- **Responsiveness**: Component works on mobile and desktop

---

## 🐛 Common Issues & Solutions

### Issue: Calendar Not Rendering

**Symptom:** Calendar view shows blank or error

**Solution:**
1. Ensure `react-big-calendar` CSS is imported:
   ```typescript
   import 'react-big-calendar/lib/css/react-big-calendar.css';
   ```
2. Check that `date-fns` is installed: `npm install date-fns`
3. Verify calendar height is set: `className="h-[600px]"`

### Issue: Client Autocomplete Not Working

**Symptom:** Client filter dropdown empty or not searching

**Solution:**
1. Increase client fetch limit:
   ```typescript
   const { data: clients } = useClients({ limit: 1000 });
   ```
2. Check that clients API endpoint is responding
3. Verify search logic in `ClientAutocomplete.tsx`

### Issue: Date Picker Allows Past Dates

**Symptom:** Can select dates in the past when creating/rescheduling tasks

**Solution:** Ensure `disabled` prop is set on Calendar:
```typescript
<Calendar
  disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
/>
```

### Issue: Task Status Not Updating in List

**Symptom:** After updating task, list doesn't refresh

**Solution:** Ensure mutation invalidates queries:
```typescript
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: ['tasks'] });
}
```

### Issue: Overdue Tasks Not Highlighted

**Symptom:** Past due tasks don't show red text

**Solution:** Check date comparison logic:
```typescript
const taskDate = new Date(task.scheduled_for);
const today = new Date();
today.setHours(0, 0, 0, 0);
const isOverdue = taskDate < today && task.status === 'pending';
```

---

## 📚 Related Documentation

- **Module 1: Clients** - `CURSOR_PROMPT_MODULE_1_CLIENTS.md`
- **Module 2: Tasks** - `CURSOR_PROMPT_MODULE_2_TASKS.md` (this document's source)
- **Backend API Documentation** - FastAPI auto-generated docs at `/docs`
- **Architecture Overview** - `REALTOROS_ARCHITECTURE.md`
- **Features List** - `FEATURES.md`
- **Database Schema** - `DataWorkFlow.md`

---

## ✅ Success Criteria

The Tasks module is considered complete when:

- ✅ Task list page loads with table/calendar views working
- ✅ All filters functional (status, priority, client)
- ✅ Task detail modal displays complete information
- ✅ All task actions work (reschedule, complete, skip, cancel)
- ✅ Create custom task functional
- ✅ Client autocomplete search works
- ✅ Calendar view displays tasks correctly with color coding
- ✅ Responsive on all screen sizes (mobile, tablet, desktop)
- ✅ All error states handled with user-friendly messages
- ✅ Toast notifications for all actions
- ✅ Loading states implemented
- ✅ Empty states display correctly
- ✅ Integration with Clients module working
- ✅ Integration with Emails module working

---

## 🚀 Future Enhancements

Potential improvements for future iterations:

1. **Recurring Tasks**: Support for tasks that repeat on a schedule
2. **Task Templates**: Save common task configurations as templates
3. **Bulk Actions**: Select multiple tasks and perform actions in bulk
4. **Task Comments**: Add comments/notes history to tasks
5. **Task Assignments**: Assign tasks to different team members
6. **Task Reminders**: Email/SMS reminders before task due date
7. **Task Analytics**: Charts and reports on task completion rates
8. **Drag-and-Drop Rescheduling**: Reschedule tasks by dragging on calendar
9. **Task Dependencies**: Link tasks that depend on other tasks
10. **Task Time Tracking**: Track time spent on tasks

---

## 📝 Changelog

### Version 1.0.0 (Current)
- Initial implementation of Tasks module
- Table and calendar views
- Complete filtering and search
- Task creation and management
- Integration with Clients and Emails modules

---

**Last Updated:** January 2025  
**Module Version:** 1.0.0  
**Status:** ✅ Production Ready

