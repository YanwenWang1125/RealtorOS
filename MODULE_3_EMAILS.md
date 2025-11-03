# CURSOR PROMPT: RealtorOS - MODULE 3 - EMAILS

## OBJECTIVE
Build the complete EMAILS module for RealtorOS CRM. This includes AI-powered email preview, email composition with rich text editing, email sending, email history with engagement tracking, and real-time webhook integration. This is the most complex module involving OpenAI integration and SendGrid webhook processing.

---

## PREREQUISITES VERIFICATION

Before starting, verify these exist:
- ✅ `src/lib/types/email.types.ts` - Email TypeScript types
- ✅ `src/lib/api/endpoints/emails.ts` - Email API functions
- ✅ `src/lib/schemas/email.schema.ts` - Zod validation schemas
- ✅ `src/lib/constants/email.constants.ts` - Email constants/enums
- ✅ `src/lib/hooks/queries/useEmails.ts` - React Query hooks
- ✅ `src/lib/hooks/mutations/useSendEmail.ts` - Mutation hooks
- ✅ **Module 1 (Clients) completed** - Email detail links to clients
- ✅ **Module 2 (Tasks) completed** - Email preview triggered from tasks
- ✅ Backend API running at `http://localhost:8000`
- ✅ OpenAI API key configured in backend
- ✅ SendGrid API key configured in backend

---

## MODULE 3: EMAILS - COMPLETE IMPLEMENTATION

### **TASK 3.1: Email List Page**

**File:** `src/app/(dashboard)/emails/page.tsx`

**Requirements:**
Comprehensive email history page with filters and engagement metrics.

1. **Page Header:**
   - Heading: "Emails"
   - Total count display: "Showing X emails"
   - Refresh button (manual refresh for latest engagement data)

2. **Filters Section:**
   - Status filter: Multi-select dropdown (queued, sent, failed, delivered, opened, clicked, bounced)
   - Client filter: Autocomplete search by client name
   - Date range filter: From/To date pickers
   - Clear all filters button

3. **Table View:**
   - Columns: Client, Subject, To, Status, Sent At, Engagement, Actions
   - Client column: Clickable name → navigate to `/clients/{id}`
   - Subject column: Truncated to 60 chars with tooltip
   - Status column: Badge with color from `EMAIL_STATUS_COLORS`
   - Sent At column: Relative time (e.g., "2 hours ago")
   - Engagement column: Icons for opened (eye) and clicked (cursor) with tooltips
   - Actions column: View button → navigate to `/emails/{id}`
   - Sortable columns (sent_at, opened_at, status)
   - Pagination (10/25/50/100 per page)

4. **Mobile View:**
   - Card view showing key info
   - Engagement icons visible
   - Tap card → navigate to detail

5. **Loading States:**
   - Skeleton rows (5 rows)

6. **Empty States:**
   - "No emails found. Emails will appear here once follow-up tasks are completed."

**Implementation:**
```tsx
'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { useEmails } from '@/lib/hooks/queries/useEmails';
import { useClients } from '@/lib/hooks/queries/useClients';
import { Button } from '@/components/ui/button';
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
    status: statusFilter.join(',') || undefined,
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
```

---

### **TASK 3.2: Email Filters Component**

**File:** `src/components/emails/EmailFilters.tsx`

**Implementation:**
```tsx
'use client';

import { Button } from '@/components/ui/button';
import { MultiSelect } from '@/components/ui/multi-select';
import { ClientAutocomplete } from '@/components/tasks/ClientAutocomplete';
import { EMAIL_STATUSES, EMAIL_STATUS_LABELS } from '@/lib/constants/email.constants';
import { X } from 'lucide-react';

interface EmailFiltersProps {
  statusFilter: string[];
  clientFilter: number | null;
  onStatusChange: (status: string[]) => void;
  onClientChange: (clientId: number | null) => void;
  onClearAll: () => void;
}

export function EmailFilters({
  statusFilter,
  clientFilter,
  onStatusChange,
  onClientChange,
  onClearAll
}: EmailFiltersProps) {
  const hasActiveFilters = statusFilter.length > 0 || clientFilter !== null;

  return (
    <div className="flex flex-wrap gap-4 items-end">
      {/* Status Filter */}
      <div className="flex-1 min-w-[250px]">
        <label className="text-sm font-medium mb-2 block">Status</label>
        <MultiSelect
          options={EMAIL_STATUSES.map(status => ({
            value: status,
            label: EMAIL_STATUS_LABELS[status]
          }))}
          selected={statusFilter}
          onChange={onStatusChange}
          placeholder="All statuses"
        />
      </div>

      {/* Client Filter */}
      <div className="flex-1 min-w-[250px]">
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

### **TASK 3.3: Email Table Component**

**File:** `src/components/emails/EmailTable.tsx`

**Implementation:**
```tsx
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
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import { EmailStatusBadge } from '@/components/emails/EmailStatusBadge';
import { EmailEngagementIcons } from '@/components/emails/EmailEngagementIcons';
import { formatRelativeTime } from '@/lib/utils/date';
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
                  className="cursor-pointer hover:bg-muted/50"
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
                    <EmailStatusBadge status={email.status} />
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
```

---

### **TASK 3.4: Email Status Badge**

**File:** `src/components/emails/EmailStatusBadge.tsx`

```tsx
import { Badge } from '@/components/ui/badge';
import { EmailStatus } from '@/lib/types/email.types';
import { EMAIL_STATUS_LABELS, EMAIL_STATUS_COLORS } from '@/lib/constants/email.constants';
import { cn } from '@/lib/utils/cn';

interface EmailStatusBadgeProps {
  status: EmailStatus;
}

export function EmailStatusBadge({ status }: EmailStatusBadgeProps) {
  return (
    <Badge className={cn(EMAIL_STATUS_COLORS[status])}>
      {EMAIL_STATUS_LABELS[status]}
    </Badge>
  );
}
```

---

### **TASK 3.5: Email Engagement Icons**

**File:** `src/components/emails/EmailEngagementIcons.tsx`

```tsx
import { Email } from '@/lib/types/email.types';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Eye, MousePointer } from 'lucide-react';
import { formatRelativeTime } from '@/lib/utils/date';

interface EmailEngagementIconsProps {
  email: Email;
}

export function EmailEngagementIcons({ email }: EmailEngagementIconsProps) {
  return (
    <TooltipProvider>
      <div className="flex gap-2">
        {email.opened_at && (
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex items-center">
                <Eye className="h-4 w-4 text-green-600" />
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p>Opened {formatRelativeTime(email.opened_at)}</p>
            </TooltipContent>
          </Tooltip>
        )}

        {email.clicked_at && (
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex items-center">
                <MousePointer className="h-4 w-4 text-purple-600" />
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p>Clicked {formatRelativeTime(email.clicked_at)}</p>
            </TooltipContent>
          </Tooltip>
        )}

        {!email.opened_at && !email.clicked_at && email.status === 'sent' && (
          <span className="text-xs text-muted-foreground">No engagement yet</span>
        )}
      </div>
    </TooltipProvider>
  );
}
```

---

### **TASK 3.6: Email Detail Page**

**File:** `src/app/(dashboard)/emails/[id]/page.tsx`

**Requirements:**
Comprehensive email detail view with HTML rendering and engagement tracking.

**Implementation:**
```tsx
'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEmail } from '@/lib/hooks/queries/useEmails';
import { useClient } from '@/lib/hooks/queries/useClients';
import { useTask } from '@/lib/hooks/queries/useTasks';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { EmailStatusBadge } from '@/components/emails/EmailStatusBadge';
import { EmailBodyRenderer } from '@/components/emails/EmailBodyRenderer';
import { EmailEngagementTimeline } from '@/components/emails/EmailEngagementTimeline';
import { EmailWebhookLog } from '@/components/emails/EmailWebhookLog';
import { formatDateTime } from '@/lib/utils/date';
import { ArrowLeft, User, Calendar } from 'lucide-react';
import Link from 'next/link';

export default function EmailDetailPage() {
  const params = useParams();
  const router = useRouter();
  const emailId = parseInt(params.id as string);

  // Poll for engagement updates every 10 seconds
  const { data: email, isLoading } = useEmail(emailId, {
    refetchInterval: (data) => {
      // Stop polling if opened or email is older than 24 hours
      if (!data) return false;
      if (data.opened_at) return false;

      const sentAt = data.sent_at ? new Date(data.sent_at) : null;
      if (sentAt && (Date.now() - sentAt.getTime()) > 24 * 60 * 60 * 1000) {
        return false;
      }

      return 10000; // Poll every 10 seconds
    }
  });

  const { data: client } = useClient(email?.client_id || 0, { enabled: !!email });
  const { data: task } = useTask(email?.task_id || 0, { enabled: !!email?.task_id });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!email) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold">Email not found</h2>
        <Button onClick={() => router.push('/emails')} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Emails
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Button variant="outline" onClick={() => router.push('/emails')}>
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Emails
      </Button>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">{email.subject}</h1>
        <div className="flex gap-4 mt-2 text-muted-foreground">
          <span>To: {email.to_email}</span>
          <span>•</span>
          <span>{email.sent_at ? formatDateTime(email.sent_at) : 'Not sent yet'}</span>
          <span>•</span>
          <EmailStatusBadge status={email.status} />
        </div>
      </div>

      {/* Breadcrumbs */}
      <div className="flex gap-2 text-sm text-muted-foreground">
        {client && (
          <>
            <Link href={`/clients/${client.id}`} className="hover:underline">
              {client.name}
            </Link>
            <span>→</span>
          </>
        )}
        {task && (
          <>
            <Link href={`/tasks/${task.id}`} className="hover:underline">
              {task.followup_type}
            </Link>
            <span>→</span>
          </>
        )}
        <span>Email</span>
      </div>

      {/* Engagement Timeline */}
      <EmailEngagementTimeline email={email} />

      {/* Email Body */}
      <Card>
        <CardHeader>
          <CardTitle>Email Content</CardTitle>
        </CardHeader>
        <CardContent>
          <EmailBodyRenderer body={email.body} />
        </CardContent>
      </Card>

      {/* Related Items */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Client Card */}
        {client && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <User className="h-5 w-5" />
                Client
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Link
                href={`/clients/${client.id}`}
                className="font-medium hover:underline block"
              >
                {client.name}
              </Link>
              <p className="text-sm text-muted-foreground mt-1">{client.email}</p>
              <p className="text-sm text-muted-foreground">{client.property_address}</p>
              <p className="text-sm text-muted-foreground mt-2">Stage: {client.stage}</p>
            </CardContent>
          </Card>
        )}

        {/* Task Card */}
        {task && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Related Task
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Link
                href={`/tasks/${task.id}`}
                className="font-medium hover:underline block"
              >
                {task.followup_type}
              </Link>
              <p className="text-sm text-muted-foreground mt-1">
                Scheduled: {formatDateTime(task.scheduled_for)}
              </p>
              <p className="text-sm text-muted-foreground">Status: {task.status}</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Webhook Events Log */}
      <EmailWebhookLog email={email} />
    </div>
  );
}
```

---

### **TASK 3.7: Email Body Renderer**

**File:** `src/components/emails/EmailBodyRenderer.tsx`

**Installation:**
```bash
npm install dompurify
npm install -D @types/dompurify
```

**Implementation:**
```tsx
'use client';

import { useEffect, useRef, useState } from 'react';
import DOMPurify from 'dompurify';

interface EmailBodyRendererProps {
  body: string;
}

export function EmailBodyRenderer({ body }: EmailBodyRendererProps) {
  const [sanitizedHtml, setSanitizedHtml] = useState('');

  useEffect(() => {
    // Sanitize HTML to prevent XSS attacks
    const clean = DOMPurify.sanitize(body, {
      ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'img', 'div', 'span', 'blockquote', 'pre', 'code'
      ],
      ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'style']
    });
    setSanitizedHtml(clean);
  }, [body]);

  return (
    <div
      className="prose prose-sm max-w-none"
      dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
    />
  );
}
```

Add prose styles to `tailwind.config.ts`:
```typescript
plugins: [require("tailwindcss-animate"), require("@tailwindcss/typography")],
```

Install typography plugin:
```bash
npm install -D @tailwindcss/typography
```

---

### **TASK 3.8: Email Engagement Timeline**

**File:** `src/components/emails/EmailEngagementTimeline.tsx`

```tsx
import { Email } from '@/lib/types/email.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatDateTime } from '@/lib/utils/date';
import { Check, Clock, Eye, MousePointer, Send } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

interface EmailEngagementTimelineProps {
  email: Email;
}

export function EmailEngagementTimeline({ email }: EmailEngagementTimelineProps) {
  const steps = [
    {
      label: 'Sent',
      timestamp: email.sent_at,
      icon: Send,
      completed: !!email.sent_at
    },
    {
      label: 'Delivered',
      timestamp: email.status === 'delivered' || email.status === 'opened' || email.status === 'clicked' ? email.sent_at : null,
      icon: Check,
      completed: ['delivered', 'opened', 'clicked'].includes(email.status)
    },
    {
      label: 'Opened',
      timestamp: email.opened_at,
      icon: Eye,
      completed: !!email.opened_at
    },
    {
      label: 'Clicked',
      timestamp: email.clicked_at,
      icon: MousePointer,
      completed: !!email.clicked_at
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Engagement Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.label} className="flex-1">
                <div className="flex items-center">
                  {/* Step Circle */}
                  <div
                    className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center',
                      step.completed
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-400'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                  </div>

                  {/* Connecting Line */}
                  {index < steps.length - 1 && (
                    <div
                      className={cn(
                        'flex-1 h-1 mx-2',
                        step.completed && steps[index + 1].completed
                          ? 'bg-green-500'
                          : 'bg-gray-200'
                      )}
                    />
                  )}
                </div>

                {/* Label and Timestamp */}
                <div className="mt-2 text-center">
                  <p className="text-sm font-medium">{step.label}</p>
                  {step.timestamp ? (
                    <p className="text-xs text-muted-foreground">
                      {formatDateTime(step.timestamp)}
                    </p>
                  ) : (
                    <p className="text-xs text-muted-foreground">-</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
```

---

### **TASK 3.9: Email Webhook Log**

**File:** `src/components/emails/EmailWebhookLog.tsx`

```tsx
'use client';

import { useState } from 'react';
import { Email } from '@/lib/types/email.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { formatDateTime } from '@/lib/utils/date';

interface EmailWebhookLogProps {
  email: Email;
}

export function EmailWebhookLog({ email }: EmailWebhookLogProps) {
  // Type guard for webhook_events
  const webhookEvents = Array.isArray(email.webhook_events) ? email.webhook_events : [];

  if (webhookEvents.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Webhook Events ({webhookEvents.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible>
          {webhookEvents.map((event: any, index: number) => (
            <AccordionItem key={index} value={`event-${index}`}>
              <AccordionTrigger>
                <div className="flex justify-between w-full pr-4">
                  <span className="font-medium">{event.event || 'Unknown Event'}</span>
                  <span className="text-sm text-muted-foreground">
                    {event.timestamp ? formatDateTime(new Date(event.timestamp * 1000).toISOString()) : '-'}
                  </span>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <pre className="bg-muted p-4 rounded-md text-xs overflow-x-auto">
                  {JSON.stringify(event, null, 2)}
                </pre>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </CardContent>
    </Card>
  );
}
```

---

### **TASK 3.10: Email Preview Modal (AI-Powered)**

**File:** `src/components/emails/EmailPreviewModal.tsx`

**Requirements:**
This is the most complex component - AI email generation with preview and editing.

**Implementation:**
```tsx
'use client';

import { useState, useEffect } from 'react';
import { usePreviewEmail } from '@/lib/hooks/mutations/usePreviewEmail';
import { useSendEmail } from '@/lib/hooks/mutations/useSendEmail';
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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '@/components/ui/skeleton';
import { EmailComposer } from '@/components/emails/EmailComposer';
import { CustomInstructionsInput } from '@/components/emails/CustomInstructionsInput';
import { AlertCircle, Loader2, RefreshCw, Send } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useRouter } from 'next/navigation';

interface EmailPreviewModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  clientId: number;
  clientEmail: string;
  clientName: string;
  taskId: number;
}

export function EmailPreviewModal({
  open,
  onOpenChange,
  clientId,
  clientEmail,
  clientName,
  taskId
}: EmailPreviewModalProps) {
  const router = useRouter();
  const { toast } = useToast();
  const previewEmail = usePreviewEmail();
  const sendEmail = useSendEmail();

  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [isEditMode, setIsEditMode] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);

  // Generate preview on open
  useEffect(() => {
    if (open && !hasGenerated) {
      handleGenerate();
    }
  }, [open]);

  const handleGenerate = async () => {
    try {
      setHasGenerated(true);
      const preview = await previewEmail.mutateAsync({
        client_id: clientId,
        task_id: taskId,
        agent_instructions: customInstructions || undefined
      });

      setSubject(preview.subject);
      setBody(preview.body);
      setIsEditMode(false);
    } catch (error: any) {
      toast({
        title: "Error generating email",
        description: error.response?.data?.detail || "AI service may be unavailable. Please try again.",
        variant: "destructive",
      });
      // Set fallback template on error
      setSubject(`Follow-up: ${clientName}`);
      setBody(`<p>Hi ${clientName},</p><p>I wanted to follow up with you regarding your property search. Please let me know if you have any questions or would like to schedule a viewing.</p><p>Best regards</p>`);
    }
  };

  const handleRegenerate = () => {
    setHasGenerated(false);
    handleGenerate();
  };

  const handleSend = async () => {
    try {
      const sentEmail = await sendEmail.mutateAsync({
        client_id: clientId,
        task_id: taskId,
        to_email: clientEmail,
        subject,
        body,
        agent_instructions: customInstructions || undefined
      });

      toast({
        title: "Email sent!",
        description: `Email successfully sent to ${clientEmail}`,
      });

      onOpenChange(false);
      router.push(`/emails/${sentEmail.id}`);
    } catch (error: any) {
      toast({
        title: "Error sending email",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleClose = () => {
    setSubject('');
    setBody('');
    setCustomInstructions('');
    setHasGenerated(false);
    setIsEditMode(false);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Email Preview</DialogTitle>
          <DialogDescription>
            AI-generated email for {clientName}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Loading State */}
          {previewEmail.isPending && !hasGenerated && (
            <div className="space-y-4">
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
                  <p className="text-lg font-medium">Generating personalized email...</p>
                  <p className="text-sm text-muted-foreground">
                    This may take a few seconds
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error State */}
          {previewEmail.isError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Failed to generate email. Using fallback template. You can edit it below.
              </AlertDescription>
            </Alert>
          )}

          {/* Preview/Edit State */}
          {hasGenerated && !previewEmail.isPending && (
            <>
              {/* To Field (Read-only) */}
              <div className="space-y-2">
                <Label>To</Label>
                <Input value={clientEmail} disabled />
              </div>

              {/* Subject Field */}
              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Input
                  id="subject"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Email subject"
                />
              </div>

              {/* Body Field */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label>Email Body</Label>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditMode(!isEditMode)}
                  >
                    {isEditMode ? 'Preview' : 'Edit'}
                  </Button>
                </div>
                <EmailComposer
                  value={body}
                  onChange={setBody}
                  readOnly={!isEditMode}
                />
              </div>

              {/* Custom Instructions (Collapsible) */}
              <CustomInstructionsInput
                value={customInstructions}
                onChange={setCustomInstructions}
              />
            </>
          )}
        </div>

        <DialogFooter className="flex justify-between">
          <div className="flex gap-2">
            {hasGenerated && (
              <Button
                variant="outline"
                onClick={handleRegenerate}
                disabled={previewEmail.isPending}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${previewEmail.isPending ? 'animate-spin' : ''}`} />
                Regenerate
              </Button>
            )}
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button
              onClick={handleSend}
              disabled={!hasGenerated || sendEmail.isPending || !subject || !body}
            >
              {sendEmail.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Send Email
                </>
              )}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

---

### **TASK 3.11: Email Composer (Rich Text Editor)**

**File:** `src/components/emails/EmailComposer.tsx`

**Installation:**
```bash
npm install @tiptap/react @tiptap/starter-kit
```

**Implementation:**
```tsx
'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { Button } from '@/components/ui/button';
import { Bold, Italic, List, ListOrdered, Undo, Redo } from 'lucide-react';
import { useEffect } from 'react';

interface EmailComposerProps {
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
}

export function EmailComposer({ value, onChange, readOnly = false }: EmailComposerProps) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: value,
    editable: !readOnly,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });

  // Update editor content when value changes externally
  useEffect(() => {
    if (editor && value !== editor.getHTML()) {
      editor.commands.setContent(value);
    }
  }, [value, editor]);

  if (!editor) {
    return null;
  }

  return (
    <div className="border rounded-md">
      {/* Toolbar */}
      {!readOnly && (
        <div className="border-b p-2 flex gap-1 flex-wrap">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleBold().run()}
            className={editor.isActive('bold') ? 'bg-muted' : ''}
          >
            <Bold className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleItalic().run()}
            className={editor.isActive('italic') ? 'bg-muted' : ''}
          >
            <Italic className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            className={editor.isActive('bulletList') ? 'bg-muted' : ''}
          >
            <List className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            className={editor.isActive('orderedList') ? 'bg-muted' : ''}
          >
            <ListOrdered className="h-4 w-4" />
          </Button>
          <div className="w-px h-6 bg-border mx-1" />
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().undo()}
          >
            <Undo className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().redo()}
          >
            <Redo className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Editor */}
      <EditorContent
        editor={editor}
        className={`prose prose-sm max-w-none p-4 ${
          readOnly ? 'min-h-[300px]' : 'min-h-[400px]'
        }`}
      />
    </div>
  );
}
```

Add Tiptap styles to `src/app/globals.css`:
```css
/* Tiptap Editor Styles */
.ProseMirror {
  outline: none;
}

.ProseMirror p {
  margin: 0.5em 0;
}

.ProseMirror ul,
.ProseMirror ol {
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.ProseMirror strong {
  font-weight: 600;
}

.ProseMirror em {
  font-style: italic;
}
```

---

### **TASK 3.12: Custom Instructions Input**

**File:** `src/components/emails/CustomInstructionsInput.tsx`

```tsx
'use client';

import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Lightbulb } from 'lucide-react';

interface CustomInstructionsInputProps {
  value: string;
  onChange: (value: string) => void;
}

export function CustomInstructionsInput({ value, onChange }: CustomInstructionsInputProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const examples = [
    "Mention the new construction in the area",
    "Keep it very brief, max 3 sentences",
    "Focus on investment potential",
    "Emphasize family-friendly features"
  ];

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label className="flex items-center gap-2">
          <Lightbulb className="h-4 w-4" />
          Custom AI Instructions (Optional)
        </Label>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? (
            <>
              <ChevronUp className="h-4 w-4 mr-1" />
              Hide
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4 mr-1" />
              Show
            </>
          )}
        </Button>
      </div>

      {isExpanded && (
        <>
          <Textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="e.g., Mention the nearby park, keep it brief..."
            rows={3}
            maxLength={500}
          />
          <div className="flex justify-between text-xs">
            <div className="text-muted-foreground">
              {value.length}/500 characters
            </div>
          </div>

          {/* Examples */}
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Examples:</p>
            <div className="flex flex-wrap gap-2">
              {examples.map((example, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="text-xs h-auto py-1"
                  onClick={() => onChange(example)}
                >
                  {example}
                </Button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
```

---

### **TASK 3.13: Add Email Preview/Send Mutation Hooks**

**File:** `src/lib/hooks/mutations/usePreviewEmail.ts`

```typescript
import { useMutation } from '@tanstack/react-query';
import { emailsApi } from '@/lib/api/endpoints/emails';
import { EmailPreviewRequest } from '@/lib/types/email.types';

export function usePreviewEmail() {
  return useMutation({
    mutationFn: (request: EmailPreviewRequest) => emailsApi.preview(request),
    retry: 1, // Retry once on failure
  });
}
```

**File:** `src/lib/hooks/mutations/useSendEmail.ts` (Update if needed)

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { emailsApi } from '@/lib/api/endpoints/emails';
import { EmailSendRequest } from '@/lib/types/email.types';

export function useSendEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: EmailSendRequest) => emailsApi.send(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
```

---

### **TASK 3.14: Update Query Hook with Polling**

**File:** `src/lib/hooks/queries/useEmails.ts` (Update)

```typescript
import { useQuery } from '@tanstack/react-query';
import { emailsApi } from '@/lib/api/endpoints/emails';

export function useEmails(params?: { page?: number; limit?: number; client_id?: number; status?: string }) {
  return useQuery({
    queryKey: ['emails', params],
    queryFn: () => emailsApi.list(params),
  });
}

export function useEmail(id: number, options?: { enabled?: boolean; refetchInterval?: number | ((data: any) => number | false) }) {
  return useQuery({
    queryKey: ['email', id],
    queryFn: () => emailsApi.getById(id),
    enabled: options?.enabled !== false && id > 0,
    refetchInterval: options?.refetchInterval,
  });
}
```

---

## TESTING CHECKLIST

After implementing all tasks, verify:

### **Functionality:**
- [ ] Email list loads with all emails
- [ ] Filter by status works
- [ ] Filter by client works
- [ ] Engagement icons show correctly (opened, clicked)
- [ ] Click email row navigates to detail page
- [ ] Email detail page shows complete information
- [ ] HTML body renders correctly (sanitized)
- [ ] Engagement timeline updates in real-time (polling every 10s)
- [ ] Webhook events log displays correctly
- [ ] Open email preview modal from task/client page
- [ ] AI generates email preview (2-5 seconds)
- [ ] Preview shows subject and body
- [ ] Edit mode works (rich text editor)
- [ ] Regenerate button works with custom instructions
- [ ] Send email button sends successfully
- [ ] After send, navigates to email detail page
- [ ] Toast notifications appear for all actions
- [ ] Breadcrumbs link to client and task
- [ ] Pagination works

### **AI Integration:**
- [ ] Email preview generates personalized content
- [ ] Custom instructions affect generated content
- [ ] Fallback template appears on AI failure
- [ ] Loading state shows during generation
- [ ] Error handling works (rate limits, API down)

### **UI/UX:**
- [ ] Loading skeletons appear while fetching
- [ ] Empty states display correctly
- [ ] Rich text editor toolbar works
- [ ] Subject line editable
- [ ] Custom instructions collapsible
- [ ] Engagement icons have tooltips
- [ ] Responsive on mobile
- [ ] Modal animations smooth
- [ ] Email body sanitized (no XSS)

### **Performance:**
- [ ] Email list loads in < 2 seconds
- [ ] AI preview generates in < 5 seconds
- [ ] Polling doesn't impact performance
- [ ] Rich text editor responsive (no lag)

---

## COMMON ISSUES & SOLUTIONS

### **Issue: "AI email generation fails"**
**Solution:** Check backend logs for OpenAI API errors:
```
- API key invalid
- Rate limit exceeded
- Model not accessible
```
Implement fallback template in frontend.

### **Issue: "Webhook events not updating"**
**Solution:** Ensure polling is working:
```typescript
refetchInterval: 10000 // 10 seconds
```
Check network tab for refetch requests.

### **Issue: "Rich text editor not rendering"**
**Solution:** Ensure Tiptap styles are imported:
```css
/* In globals.css */
.ProseMirror { outline: none; }
```

### **Issue: "XSS vulnerability in email body"**
**Solution:** Ensure DOMPurify is sanitizing:
```typescript
const clean = DOMPurify.sanitize(body, { ALLOWED_TAGS: [...] });
```

### **Issue: "Email send fails silently"**
**Solution:** Check mutation error handling:
```typescript
onError: (error) => {
  console.error('Send error:', error);
  toast({ title: "Error", variant: "destructive" });
}
```

---

## SUCCESS CRITERIA

Module 3 (Emails) is complete when:
- ✅ Email list page with filters working
- ✅ Email detail page with engagement timeline
- ✅ AI-powered email preview functional
- ✅ Rich text editor working (bold, italic, lists)
- ✅ Custom instructions affecting AI generation
- ✅ Email send functional
- ✅ Engagement tracking visible (opened, clicked)
- ✅ Real-time polling for engagement updates
- ✅ Webhook events log displaying
- ✅ All error states handled
- ✅ Toast notifications for all actions
- ✅ HTML sanitization working (no XSS)
- ✅ Responsive on all screen sizes

---

## NEXT STEPS

After completing Module 3, proceed to:
- **Module 4: Dashboard** (Stats, activity feed, charts, KPIs)

---

**START IMPLEMENTING MODULE 3 NOW!** This is the most complex module. Follow tasks in order (3.1 → 3.14). Test AI integration thoroughly. Good luck! 🚀
