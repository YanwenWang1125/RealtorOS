# CURSOR PROMPT: RealtorOS - MODULE 1 - CLIENTS

## OBJECTIVE
Build the complete CLIENTS module for RealtorOS CRM. This includes client list, create, detail, edit, and delete functionality. This is a standalone, production-ready module that integrates with the existing backend API.

---

## PREREQUISITES VERIFICATION

Before starting, verify these exist:
- ✅ `src/lib/types/client.types.ts` - Client TypeScript types
- ✅ `src/lib/api/endpoints/clients.ts` - Client API functions
- ✅ `src/lib/schemas/client.schema.ts` - Zod validation schemas
- ✅ `src/lib/constants/client.constants.ts` - Client constants/enums
- ✅ `src/lib/hooks/queries/useClients.ts` - React Query hooks
- ✅ `src/lib/hooks/mutations/useCreateClient.ts` - Mutation hooks
- ✅ Backend API running at `http://localhost:8000`

---

## MODULE 1: CLIENTS - COMPLETE IMPLEMENTATION

### **TASK 1.1: Client List Page**

**File:** `src/app/(dashboard)/clients/page.tsx`

**Requirements:**
Create a comprehensive client list page with the following features:

1. **Page Header:**
   - Heading: "Clients"
   - "Create New Client" button (top right) → navigates to `/clients/new`
   - Total count display: "Showing X clients"

2. **Filters Section:**
   - Stage filter: Multi-select dropdown with all stages from `CLIENT_STAGES`
   - Search input: Search by name, email, or property address (debounced 300ms)
   - Clear filters button (appears when filters active)

3. **Table View (Desktop ≥ 768px):**
   - Columns: Name, Email, Property Address, Property Type, Stage, Last Contacted, Actions
   - Sortable columns (click header to sort)
   - Stage column: Badge with color from `CLIENT_STAGE_COLORS`
   - Property type column: Label from `PROPERTY_TYPE_LABELS`
   - Last Contacted: Relative time (e.g., "2 hours ago") or "Never"
   - Actions column: View button → navigate to `/clients/[id]`
   - Hover effect on rows
   - Empty state: "No clients found. Create your first client!"

4. **Card View (Mobile < 768px):**
   - Card component for each client
   - Show: Name, Email, Property, Stage badge
   - Click card → navigate to detail page

5. **Pagination:**
   - Page size selector: 10, 25, 50, 100
   - Previous/Next buttons
   - Page numbers (show 5 at a time)
   - Total pages display

6. **Loading States:**
   - Skeleton rows while fetching (5 rows)
   - Disable interactions during load

7. **Error States:**
   - Display error message if API fails
   - Retry button

**API Integration:**
```typescript
const [page, setPage] = useState(1);
const [limit, setLimit] = useState(10);
const [stage, setStage] = useState<string | null>(null);
const [search, setSearch] = useState('');

const debouncedSearch = useDebounce(search, 300);

const { data: clients, isLoading, isError, error } = useClients({
  page,
  limit,
  stage: stage || undefined
});

// Client-side filtering by search (or implement backend search)
const filteredClients = useMemo(() => {
  if (!clients || !debouncedSearch) return clients;
  return clients.filter(c =>
    c.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
    c.email.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
    c.property_address.toLowerCase().includes(debouncedSearch.toLowerCase())
  );
}, [clients, debouncedSearch]);
```

**Components to Create:**

1. **`src/components/clients/ClientList.tsx`**
   - Main container component
   - Handles state (filters, pagination)
   - Renders header, filters, table/cards, pagination

2. **`src/components/clients/ClientTable.tsx`**
   - Desktop table view
   - Receives: `clients[]`, `onSort`, `sortColumn`, `sortDirection`
   - Uses shadcn/ui `Table` component
   - Props: `clients: Client[], loading: boolean`

3. **`src/components/clients/ClientCard.tsx`**
   - Mobile card view
   - Props: `client: Client`
   - Clickable card with hover effect
   - Shows key info: name, email, property, stage badge

4. **`src/components/clients/ClientFilters.tsx`**
   - Filter controls
   - Stage multi-select (shadcn/ui `Select`)
   - Search input (shadcn/ui `Input` with search icon)
   - Clear filters button
   - Props: `onStageChange`, `onSearchChange`, `stage`, `search`

**Styling:**
- Use Tailwind CSS classes
- Match shadcn/ui design system
- Responsive breakpoints: `md:` for desktop, mobile-first

**Example Table Structure:**
```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Email</TableHead>
      <TableHead>Property</TableHead>
      <TableHead>Type</TableHead>
      <TableHead>Stage</TableHead>
      <TableHead>Last Contacted</TableHead>
      <TableHead>Actions</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {filteredClients?.map(client => (
      <TableRow key={client.id}>
        <TableCell className="font-medium">{client.name}</TableCell>
        <TableCell>{client.email}</TableCell>
        {/* ... */}
      </TableRow>
    ))}
  </TableBody>
</Table>
```

---

### **TASK 1.2: Custom Fields Editor Component**

**File:** `src/components/clients/CustomFieldsEditor.tsx`

**Requirements:**
Create a reusable component for editing custom fields (key-value pairs).

**Features:**
1. Display existing fields as editable rows
2. Each row: Key input, Value input, Delete button
3. "Add Field" button at bottom
4. Validation: No duplicate keys, max 20 fields
5. Character limits: Key (50 chars), Value (200 chars)
6. Empty state: "No custom fields. Click 'Add Field' to create one."

**Props:**
```typescript
interface CustomFieldsEditorProps {
  fields: Record<string, any>;
  onChange: (fields: Record<string, any>) => void;
  disabled?: boolean;
}
```

**Implementation:**
```tsx
export function CustomFieldsEditor({ fields, onChange, disabled }: CustomFieldsEditorProps) {
  const [entries, setEntries] = useState<Array<{ key: string; value: any }>>(
    Object.entries(fields || {}).map(([key, value]) => ({ key, value }))
  );

  const handleAdd = () => {
    setEntries([...entries, { key: '', value: '' }]);
  };

  const handleRemove = (index: number) => {
    const newEntries = entries.filter((_, i) => i !== index);
    setEntries(newEntries);
    onChange(Object.fromEntries(newEntries.map(e => [e.key, e.value])));
  };

  const handleChange = (index: number, field: 'key' | 'value', newValue: string) => {
    const newEntries = [...entries];
    newEntries[index][field] = newValue;
    setEntries(newEntries);

    // Convert to object and pass to parent
    const fieldsObject = Object.fromEntries(
      newEntries.filter(e => e.key.trim()).map(e => [e.key, e.value])
    );
    onChange(fieldsObject);
  };

  return (
    <div className="space-y-2">
      {entries.map((entry, index) => (
        <div key={index} className="flex gap-2">
          <Input
            placeholder="Field name"
            value={entry.key}
            onChange={(e) => handleChange(index, 'key', e.target.value)}
            disabled={disabled}
            maxLength={50}
          />
          <Input
            placeholder="Value"
            value={entry.value}
            onChange={(e) => handleChange(index, 'value', e.target.value)}
            disabled={disabled}
            maxLength={200}
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => handleRemove(index)}
            disabled={disabled}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ))}
      <Button
        type="button"
        variant="outline"
        onClick={handleAdd}
        disabled={disabled || entries.length >= 20}
      >
        <Plus className="h-4 w-4 mr-2" />
        Add Field
      </Button>
    </div>
  );
}
```

---

### **TASK 1.3: Client Form Component (Create & Edit)**

**File:** `src/components/clients/ClientForm.tsx`

**Requirements:**
Create a reusable form component for both creating and editing clients.

**Features:**
1. All fields with validation (React Hook Form + Zod)
2. Real-time validation with inline errors
3. Character counters for text fields
4. Dropdown selectors for property type and stage
5. Custom fields editor integration
6. Loading state during submission
7. Cancel + Submit buttons

**Props:**
```typescript
interface ClientFormProps {
  client?: Client; // If editing, pass existing client
  onSubmit: (data: ClientCreateFormData | ClientUpdateFormData) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}
```

**Implementation:**
```tsx
'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { clientCreateSchema, ClientCreateFormData } from '@/lib/schemas/client.schema';
import { PROPERTY_TYPES, CLIENT_STAGES } from '@/lib/constants/client.constants';
import { CustomFieldsEditor } from './CustomFieldsEditor';

export function ClientForm({ client, onSubmit, onCancel, isLoading }: ClientFormProps) {
  const form = useForm<ClientCreateFormData>({
    resolver: zodResolver(clientCreateSchema),
    defaultValues: client || {
      name: '',
      email: '',
      phone: '',
      property_address: '',
      property_type: 'residential',
      stage: 'lead',
      notes: '',
      custom_fields: {}
    }
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Name Field */}
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name *</FormLabel>
              <FormControl>
                <Input placeholder="John Doe" {...field} maxLength={100} />
              </FormControl>
              <FormDescription>
                {field.value?.length || 0}/100 characters
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Email Field */}
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email *</FormLabel>
              <FormControl>
                <Input type="email" placeholder="john@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Phone Field */}
        <FormField
          control={form.control}
          name="phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Phone</FormLabel>
              <FormControl>
                <Input placeholder="+1 (555) 123-4567" {...field} maxLength={20} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Property Address Field */}
        <FormField
          control={form.control}
          name="property_address"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Property Address *</FormLabel>
              <FormControl>
                <Input placeholder="123 Main St, City, State 12345" {...field} maxLength={200} />
              </FormControl>
              <FormDescription>
                {field.value?.length || 0}/200 characters
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Property Type Dropdown */}
        <FormField
          control={form.control}
          name="property_type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Property Type *</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select property type" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {PROPERTY_TYPES.map(type => (
                    <SelectItem key={type} value={type}>
                      {PROPERTY_TYPE_LABELS[type]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Stage Dropdown */}
        <FormField
          control={form.control}
          name="stage"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Stage *</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select stage" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {CLIENT_STAGES.map(stage => (
                    <SelectItem key={stage} value={stage}>
                      {CLIENT_STAGE_LABELS[stage]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Notes Textarea */}
        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Notes</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Additional notes about this client..."
                  className="resize-none"
                  rows={4}
                  {...field}
                  maxLength={1000}
                />
              </FormControl>
              <FormDescription>
                {field.value?.length || 0}/1000 characters
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Custom Fields */}
        <FormField
          control={form.control}
          name="custom_fields"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Custom Fields</FormLabel>
              <FormControl>
                <CustomFieldsEditor
                  fields={field.value || {}}
                  onChange={field.onChange}
                  disabled={isLoading}
                />
              </FormControl>
              <FormDescription>
                Add custom fields to track additional information
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {client ? 'Update Client' : 'Create Client'}
          </Button>
        </div>
      </form>
    </Form>
  );
}
```

---

### **TASK 1.4: Client Create Page**

**File:** `src/app/(dashboard)/clients/new/page.tsx`

**Requirements:**
Create page for adding new clients.

**Implementation:**
```tsx
'use client';

import { useRouter } from 'next/navigation';
import { ClientForm } from '@/components/clients/ClientForm';
import { useCreateClient } from '@/lib/hooks/mutations/useCreateClient';
import { useToast } from '@/lib/hooks/ui/useToast';
import { ClientCreateFormData } from '@/lib/schemas/client.schema';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function ClientCreatePage() {
  const router = useRouter();
  const { toast } = useToast();
  const createClient = useCreateClient();

  const handleSubmit = async (data: ClientCreateFormData) => {
    try {
      const newClient = await createClient.mutateAsync(data);

      toast({
        title: "Client created!",
        description: "Follow-up tasks are being scheduled in the background.",
      });

      // Navigate to client detail page
      router.push(`/clients/${newClient.id}`);
    } catch (error: any) {
      toast({
        title: "Error creating client",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleCancel = () => {
    router.push('/clients');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Create New Client</CardTitle>
          <CardDescription>
            Add a new client to your CRM. Follow-up tasks will be automatically created.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ClientForm
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={createClient.isPending}
          />
        </CardContent>
      </Card>
    </div>
  );
}
```

---

### **TASK 1.5: Client Detail Page**

**File:** `src/app/(dashboard)/clients/[id]/page.tsx`

**Requirements:**
Comprehensive client detail view with all related data.

**Sections:**
1. **Header:** Name, email, phone, Edit/Delete buttons
2. **Stage Pipeline:** Visual progress indicator
3. **Info Card:** All client details
4. **Tasks Section:** Timeline of follow-up tasks
5. **Emails Section:** Email history with engagement
6. **Quick Actions:** Send Email, Create Task

**Implementation:**
```tsx
'use client';

import { useParams, useRouter } from 'next/navigation';
import { useClient } from '@/lib/hooks/queries/useClients';
import { useClientTasks } from '@/lib/hooks/queries/useClients';
import { useEmails } from '@/lib/hooks/queries/useEmails';
import { Button } from '@/components/ui/button';
import { ClientHeader } from '@/components/clients/ClientHeader';
import { ClientStagePipeline } from '@/components/clients/ClientStagePipeline';
import { ClientInfoCard } from '@/components/clients/ClientInfoCard';
import { ClientTimeline } from '@/components/clients/ClientTimeline';
import { ClientEmailHistory } from '@/components/clients/ClientEmailHistory';
import { Skeleton } from '@/components/ui/skeleton';
import { Mail, Plus, Pencil } from 'lucide-react';

export default function ClientDetailPage() {
  const params = useParams();
  const router = useRouter();
  const clientId = parseInt(params.id as string);

  const { data: client, isLoading: clientLoading } = useClient(clientId);
  const { data: tasks, isLoading: tasksLoading } = useClientTasks(clientId);
  const { data: emails, isLoading: emailsLoading } = useEmails({ client_id: clientId });

  if (clientLoading) {
    return <div className="space-y-6">
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-64 w-full" />
    </div>;
  }

  if (!client) {
    return <div className="text-center py-12">
      <h2 className="text-2xl font-bold">Client not found</h2>
      <Button onClick={() => router.push('/clients')} className="mt-4">
        Back to Clients
      </Button>
    </div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <ClientHeader client={client} />
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => router.push(`/clients/${clientId}/edit`)}
          >
            <Pencil className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="outline">
            <Mail className="h-4 w-4 mr-2" />
            Send Email
          </Button>
        </div>
      </div>

      {/* Stage Pipeline */}
      <ClientStagePipeline client={client} />

      {/* Info Card */}
      <ClientInfoCard client={client} />

      {/* Tasks Section */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Follow-up Tasks</h2>
          <Button variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Create Custom Task
          </Button>
        </div>
        {tasksLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : (
          <ClientTimeline tasks={tasks || []} />
        )}
      </div>

      {/* Emails Section */}
      <div>
        <h2 className="text-xl font-bold mb-4">Email History</h2>
        {emailsLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : (
          <ClientEmailHistory emails={emails || []} />
        )}
      </div>
    </div>
  );
}
```

---

### **TASK 1.6: Supporting Client Detail Components**

Create these components for the detail page:

**1. `src/components/clients/ClientHeader.tsx`**
```tsx
export function ClientHeader({ client }: { client: Client }) {
  return (
    <div>
      <h1 className="text-3xl font-bold">{client.name}</h1>
      <div className="flex gap-4 mt-2 text-muted-foreground">
        <div className="flex items-center gap-1">
          <Mail className="h-4 w-4" />
          {client.email}
        </div>
        {client.phone && (
          <div className="flex items-center gap-1">
            <Phone className="h-4 w-4" />
            {client.phone}
          </div>
        )}
      </div>
      {client.last_contacted && (
        <p className="text-sm text-muted-foreground mt-1">
          Last contacted {formatRelativeTime(client.last_contacted)}
        </p>
      )}
    </div>
  );
}
```

**2. `src/components/clients/ClientStagePipeline.tsx`**
```tsx
export function ClientStagePipeline({ client }: { client: Client }) {
  const stages: ClientStage[] = ['lead', 'negotiating', 'under_contract', 'closed'];
  const currentIndex = stages.indexOf(client.stage);

  return (
    <div className="flex items-center gap-2">
      {stages.map((stage, index) => (
        <React.Fragment key={stage}>
          <div className={cn(
            "flex-1 rounded-lg p-4 text-center transition-colors",
            index <= currentIndex
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-muted-foreground"
          )}>
            {CLIENT_STAGE_LABELS[stage]}
          </div>
          {index < stages.length - 1 && (
            <ChevronRight className="h-5 w-5 text-muted-foreground" />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
```

**3. `src/components/clients/ClientInfoCard.tsx`**
```tsx
export function ClientInfoCard({ client }: { client: Client }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Client Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium">Property Address</label>
          <p className="text-sm text-muted-foreground">{client.property_address}</p>
        </div>
        <div>
          <label className="text-sm font-medium">Property Type</label>
          <p className="text-sm text-muted-foreground">
            {PROPERTY_TYPE_LABELS[client.property_type]}
          </p>
        </div>
        {client.notes && (
          <div>
            <label className="text-sm font-medium">Notes</label>
            <p className="text-sm text-muted-foreground">{client.notes}</p>
          </div>
        )}
        {client.custom_fields && Object.keys(client.custom_fields).length > 0 && (
          <div>
            <label className="text-sm font-medium">Custom Fields</label>
            <dl className="mt-2 space-y-2">
              {Object.entries(client.custom_fields).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">{key}:</dt>
                  <dd className="font-medium">{String(value)}</dd>
                </div>
              ))}
            </dl>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

**4. `src/components/clients/ClientTimeline.tsx`**
```tsx
export function ClientTimeline({ tasks }: { tasks: Task[] }) {
  if (tasks.length === 0) {
    return <EmptyState
      icon={Calendar}
      title="No tasks yet"
      description="Follow-up tasks are being created in the background."
    />;
  }

  const sortedTasks = [...tasks].sort((a, b) =>
    new Date(a.scheduled_for).getTime() - new Date(b.scheduled_for).getTime()
  );

  return (
    <div className="space-y-4">
      {sortedTasks.map((task, index) => (
        <div key={task.id} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div className={cn(
              "w-3 h-3 rounded-full",
              task.status === 'completed' ? "bg-green-500" :
              task.status === 'pending' ? "bg-yellow-500" :
              "bg-gray-300"
            )} />
            {index < sortedTasks.length - 1 && (
              <div className="w-px h-full bg-border mt-1" />
            )}
          </div>
          <Card className="flex-1">
            <CardContent className="pt-6">
              <div className="flex justify-between">
                <div>
                  <h3 className="font-semibold">{task.followup_type}</h3>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(task.scheduled_for)}
                  </p>
                </div>
                <Badge variant={
                  task.status === 'completed' ? 'success' :
                  task.status === 'pending' ? 'warning' :
                  'secondary'
                }>
                  {TASK_STATUS_LABELS[task.status]}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      ))}
    </div>
  );
}
```

**5. `src/components/clients/ClientEmailHistory.tsx`**
```tsx
export function ClientEmailHistory({ emails }: { emails: Email[] }) {
  if (emails.length === 0) {
    return <EmptyState
      icon={Mail}
      title="No emails yet"
      description="Email history will appear here once follow-up emails are sent."
    />;
  }

  return (
    <div className="space-y-2">
      {emails.map(email => (
        <Card key={email.id} className="hover:bg-accent cursor-pointer">
          <CardContent className="pt-6">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="font-semibold">{email.subject}</h3>
                <p className="text-sm text-muted-foreground">
                  {formatRelativeTime(email.sent_at || email.created_at)}
                </p>
              </div>
              <div className="flex gap-2">
                <Badge variant={EMAIL_STATUS_COLORS[email.status]}>
                  {EMAIL_STATUS_LABELS[email.status]}
                </Badge>
                {email.opened_at && <Eye className="h-4 w-4 text-green-500" />}
                {email.clicked_at && <MousePointer className="h-4 w-4 text-purple-500" />}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

---

### **TASK 1.7: Client Edit Page**

**File:** `src/app/(dashboard)/clients/[id]/edit/page.tsx`

```tsx
'use client';

import { useParams, useRouter } from 'next/navigation';
import { useClient } from '@/lib/hooks/queries/useClients';
import { useUpdateClient } from '@/lib/hooks/mutations/useUpdateClient';
import { ClientForm } from '@/components/clients/ClientForm';
import { useToast } from '@/lib/hooks/ui/useToast';
import { ClientUpdateFormData } from '@/lib/schemas/client.schema';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export default function ClientEditPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const clientId = parseInt(params.id as string);

  const { data: client, isLoading } = useClient(clientId);
  const updateClient = useUpdateClient();

  const handleSubmit = async (data: ClientUpdateFormData) => {
    try {
      await updateClient.mutateAsync({ id: clientId, data });

      toast({
        title: "Client updated!",
        description: "Changes have been saved successfully.",
      });

      router.push(`/clients/${clientId}`);
    } catch (error: any) {
      toast({
        title: "Error updating client",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleCancel = () => {
    router.push(`/clients/${clientId}`);
  };

  if (isLoading) {
    return <Skeleton className="h-96 w-full" />;
  }

  if (!client) {
    return <div className="text-center py-12">
      <h2 className="text-2xl font-bold">Client not found</h2>
    </div>;
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Edit Client</CardTitle>
        </CardHeader>
        <CardContent>
          <ClientForm
            client={client}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={updateClient.isPending}
          />
        </CardContent>
      </Card>
    </div>
  );
}
```

---

### **TASK 1.8: Client Delete Dialog**

**File:** `src/components/clients/ClientDeleteDialog.tsx`

```tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useDeleteClient } from '@/lib/hooks/mutations/useDeleteClient';
import { useToast } from '@/lib/hooks/ui/useToast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/button';
import { Trash2 } from 'lucide-react';
import { Client } from '@/lib/types/client.types';

interface ClientDeleteDialogProps {
  client: Client;
  taskCount?: number;
  emailCount?: number;
}

export function ClientDeleteDialog({ client, taskCount, emailCount }: ClientDeleteDialogProps) {
  const router = useRouter();
  const { toast } = useToast();
  const deleteClient = useDeleteClient();
  const [open, setOpen] = useState(false);

  const handleDelete = async () => {
    try {
      await deleteClient.mutateAsync(client.id);

      toast({
        title: "Client deleted",
        description: `${client.name} has been removed from your CRM.`,
      });

      router.push('/clients');
    } catch (error: any) {
      toast({
        title: "Error deleting client",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        <Button variant="destructive" size="sm">
          <Trash2 className="h-4 w-4 mr-2" />
          Delete
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This will permanently delete <strong>{client.name}</strong> and cannot be undone.
            {(taskCount || emailCount) && (
              <div className="mt-4 p-3 bg-muted rounded-md">
                <p className="text-sm">This client has:</p>
                <ul className="text-sm list-disc list-inside mt-1">
                  {taskCount > 0 && <li>{taskCount} task(s)</li>}
                  {emailCount > 0 && <li>{emailCount} email(s)</li>}
                </ul>
              </div>
            )}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleDelete}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            Delete Client
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
```

Integrate into ClientDetailPage by adding delete button:
```tsx
import { ClientDeleteDialog } from '@/components/clients/ClientDeleteDialog';

// In the header actions
<ClientDeleteDialog
  client={client}
  taskCount={tasks?.length}
  emailCount={emails?.length}
/>
```

---

### **TASK 1.9: Add Delete Mutation Hook**

**File:** `src/lib/hooks/mutations/useDeleteClient.ts`

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clientsApi } from '@/lib/api/endpoints/clients';

export function useDeleteClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => clientsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
```

---

### **TASK 1.10: Shared UI Components**

Create these reusable components:

**1. `src/components/ui/EmptyState.tsx`**
```tsx
import { LucideIcon } from 'lucide-react';
import { Button } from './button';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <Icon className="h-12 w-12 text-muted-foreground mb-4" />
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground mb-4 max-w-sm">{description}</p>
      {action && (
        <Button onClick={action.onClick}>{action.label}</Button>
      )}
    </div>
  );
}
```

---

## TESTING CHECKLIST

After implementing all tasks, verify:

### **Functionality:**
- [ ] Create new client with all fields (including custom fields)
- [ ] Client appears in list immediately after creation
- [ ] Navigate to client detail page
- [ ] See "Tasks are being scheduled" message
- [ ] Wait 5 seconds, refresh → see 5 tasks created (Day 1, Day 3, Week 1, Week 2, Month 1)
- [ ] Edit client → update name, stage, notes → verify changes saved
- [ ] Delete client → confirm deletion → verify redirect to list
- [ ] Filter clients by stage → verify results
- [ ] Search clients by name/email → verify results (debounced)
- [ ] Paginate through client list
- [ ] All validation errors display correctly

### **UI/UX:**
- [ ] Loading skeletons appear while fetching data
- [ ] Error states display with retry button
- [ ] Toast notifications appear for all actions
- [ ] Forms have inline validation with error messages
- [ ] Character counters work on text fields
- [ ] Responsive on mobile (cards instead of table)
- [ ] Keyboard navigation works (tab through form)
- [ ] Focus styles visible

### **Performance:**
- [ ] Page loads in < 2 seconds
- [ ] Search is debounced (300ms)
- [ ] No layout shift during load
- [ ] Smooth animations

---

## COMMON ISSUES & SOLUTIONS

### **Issue: "Property 'toast' does not exist"**
**Solution:** Ensure toast hook is properly exported:
```typescript
// src/lib/hooks/ui/useToast.ts
import { useToast as useToastPrimitive } from '@/components/ui/use-toast';
export { useToastPrimitive as useToast };
```

### **Issue: "Module not found: Can't resolve 'lucide-react'"**
**Solution:** Install lucide-react:
```bash
npm install lucide-react
```

### **Issue: "Tasks not appearing after client creation"**
**Solution:** Tasks are created asynchronously by Celery. Implement polling:
```typescript
// After client creation, poll for tasks
useEffect(() => {
  if (!client) return;

  const interval = setInterval(async () => {
    queryClient.invalidateQueries(['client', client.id, 'tasks']);
  }, 2000);

  // Stop after 10 seconds
  setTimeout(() => clearInterval(interval), 10000);

  return () => clearInterval(interval);
}, [client?.id]);
```

### **Issue: "Custom fields not saving"**
**Solution:** Ensure empty keys are filtered:
```typescript
const fieldsObject = Object.fromEntries(
  entries.filter(e => e.key.trim()).map(e => [e.key, e.value])
);
```

---

## SUCCESS CRITERIA

Module 1 (Clients) is complete when:
- ✅ All 5 pages working (list, create, detail, edit, delete)
- ✅ All CRUD operations functional
- ✅ Custom fields editor working
- ✅ Stage pipeline visualization
- ✅ Task timeline display
- ✅ Email history display
- ✅ Responsive on all screen sizes
- ✅ All error states handled
- ✅ All loading states implemented
- ✅ Toast notifications for all actions

---

## NEXT STEPS

After completing Module 1, proceed to:
- **Module 2: Tasks** (Task list, calendar, detail, actions)
- **Module 3: Emails** (Email preview, send, engagement tracking)
- **Module 4: Dashboard** (Stats, activity feed, charts)

---

**START IMPLEMENTING MODULE 1 NOW!** Follow the tasks in order (1.1 → 1.10). Test each component thoroughly before moving to the next. Good luck! 🚀
