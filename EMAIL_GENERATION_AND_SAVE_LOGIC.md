# Email Generation and Preview Save Logic

This document explains the complete flow of AI email generation and how email previews are saved to the database.

## Table of Contents
1. [Overview](#overview)
2. [Frontend Flow](#frontend-flow)
3. [Backend Flow](#backend-flow)
4. [Database Storage](#database-storage)
5. [State Management](#state-management)
6. [Key Components](#key-components)

---

## Overview

The email generation system uses OpenAI to create personalized emails for real estate clients. The generated preview can be edited, saved to the database, and later sent. The preview is stored in the `tasks.email_preview` JSON field.

### Key Features
- **AI Generation**: Uses OpenAI to generate personalized emails
- **Preview Storage**: Saves preview to database in `tasks.email_preview` JSON field
- **Auto-save**: Automatically saves changes after 1 second of inactivity
- **Manual Save**: User can manually save using the "Save" button
- **Persistence**: Saved previews are loaded when reopening the modal

---

## Frontend Flow

### 1. Modal Opening (`EmailPreviewModal.tsx`)

When the modal opens, the `useEffect` hook (lines 183-301) runs:

```typescript
useEffect(() => {
  // 1. Reset flags when modal closes
  if (!open) {
    hasAttemptedGenerate.current = false;
    isGeneratingRef.current = false;
    isSavingRef.current = false;
    return;
  }
  
  // 2. Prevent loading during save operation
  if (isSavingRef.current) {
    return;
  }
  
  // 3. Skip if content already loaded
  if (hasGenerated && subject && body && hasAttemptedGenerate.current) {
    return;
  }
  
  // 4. Load preview from database or generate new
  loadPreview();
}, [open, taskId, task]);
```

### 2. Preview Loading Logic

The `loadPreview()` function (lines 210-283) follows this priority:

1. **Database (`task.email_preview`)**:
   - Checks if `task.email_preview` exists
   - If found, loads `subject`, `body`, and `custom_instructions`
   - Updates state: `setSubject()`, `setBody()`, `setHasGenerated(true)`

2. **localStorage (Fallback)**:
   - Key: `email_preview_{taskId}`
   - Only used if database preview doesn't exist
   - Expires after 24 hours
   - Same structure: `{ subject, body, custom_instructions, timestamp }`

3. **Generate New**:
   - If no saved preview exists, calls `handleGenerate()`
   - Generates new email using AI

### 3. AI Email Generation (`handleGenerate`)

```typescript
const handleGenerate = async () => {
  // 1. Prevent duplicate calls
  if (isGeneratingRef.current) return;
  
  // 2. Set generating flag
  isGeneratingRef.current = true;
  setHasGenerated(true);
  
  // 3. Call API to generate preview
  const preview = await previewEmail.mutateAsync({
    client_id: clientId,
    task_id: taskId,
    agent_instructions: customInstructions || undefined
  });
  
  // 4. Update state with generated content
  setSubject(preview.subject);
  setBody(preview.body);
  
  // 5. Auto-save to database (skip invalidation to prevent regeneration)
  await savePreviewToDatabase({
    subject: preview.subject,
    body: preview.body,
    custom_instructions: customInstructions || undefined
  }, true); // skipInvalidation = true
};
```

**API Call Flow:**
- Frontend → `POST /api/emails/preview`
- Backend validates client and task
- Backend calls `ai_agent.generate_email_preview()`
- Returns `{ subject, body, preview }`

### 4. Saving Preview (`savePreviewToDatabase`)

```typescript
const savePreviewToDatabase = async (preview, skipInvalidation = false) => {
  // 1. Set saving flags
  setIsSaving(true);
  isSavingRef.current = true;
  
  // 2. Prepare preview data with timestamp
  const previewData = {
    ...preview,
    timestamp: Date.now()
  };
  
  // 3. Update task via API
  const result = await tasksApi.update(taskId, {
    email_preview: previewData
  });
  
  // 4. Update React Query cache
  if (skipInvalidation) {
    // Silent update (no query invalidation)
    queryClient.setQueryData(['task', taskId], (oldData) => ({
      ...oldData,
      email_preview: previewData
    }));
  } else {
    // Update cache and invalidate query
    queryClient.setQueryData(['task', taskId], (oldData) => ({
      ...oldData,
      email_preview: previewData
    }));
    queryClient.invalidateQueries({ queryKey: ['task', taskId] });
  }
  
  // 5. Reset flags after delay
  setTimeout(() => {
    isSavingRef.current = false;
  }, 1000);
};
```

**Save Scenarios:**

1. **Auto-save (Debounced)**:
   - Triggered by `useEffect` (lines 305-318)
   - Runs 1 second after user stops editing
   - Uses `skipInvalidation = true` to prevent regeneration

2. **Manual Save (Button Click)**:
   - Triggered by `handleSave()` (lines 380-406)
   - Uses `skipInvalidation = false` to refresh data
   - Shows success toast

3. **After Generation**:
   - Automatically saves after AI generation
   - Uses `skipInvalidation = true` to prevent regeneration

### 5. State Flags

The component uses several refs to prevent race conditions:

- **`hasAttemptedGenerate`**: Prevents duplicate generation attempts
- **`isGeneratingRef`**: Tracks if email is currently being generated
- **`isSavingRef`**: Tracks if preview is currently being saved (prevents regeneration during save)

---

## Backend Flow

### 1. Preview Endpoint (`/api/emails/preview`)

**Location**: `backend/app/api/routes/emails.py` (lines 37-69)

```python
@router.post("/preview")
async def preview_email(
    request: EmailPreviewRequest,
    agent: Agent = Depends(get_current_agent),
    ai_agent: AIAgent = Depends(get_ai_agent),
    crm_service: CRMService = Depends(get_crm_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    # 1. Validate client belongs to agent
    client = await get_client(request.client_id, agent.id)
    
    # 2. Validate task belongs to agent
    task = await get_task(request.task_id, agent.id)
    
    # 3. Generate preview using AI
    preview = await ai_agent.generate_email_preview(
        client, task, agent, request.agent_instructions
    )
    
    # 4. Return { subject, body, preview }
    return preview
```

### 2. AI Email Generation (`AIAgent.generate_email_preview`)

**Location**: `backend/app/services/ai_agent.py` (lines 404-521)

**Process:**

1. **Build Prompt** (`_build_prompt`):
   - Includes client information (name, email, property, stage, notes)
   - Includes agent information (name, title, company, phone, email)
   - Includes follow-up type context (Day 1, Day 3, Week 1, etc.)
   - Includes custom agent instructions (if provided)
   - Includes formatting instructions

2. **Call OpenAI API**:
   - Model: Configured via `OPENAI_MODEL` (default: gpt-4o-mini)
   - Max tokens: 500-800 for preview (faster response)
   - Temperature: 0.7 (balanced creativity)
   - JSON mode: If model supports it

3. **Parse Response** (`_parse_openai_response`):
   - Extracts `subject` and `body` from JSON response
   - Handles markdown code blocks if present
   - Falls back to text parsing if JSON fails
   - Generates preview (first 200 chars of body)

4. **Error Handling**:
   - If API fails, returns fallback email template
   - Logs errors for debugging

### 3. Task Update (Save Preview)

**Location**: `backend/app/api/routes/tasks.py` (update endpoint)

The frontend calls `tasksApi.update(taskId, { email_preview: previewData })` which:

1. Validates task belongs to agent
2. Updates `tasks.email_preview` JSON field
3. Returns updated task object

**Database Schema:**
```python
# backend/app/models/task.py
class Task(Base):
    email_preview = Column(JSON, nullable=True)  # Stores: { subject, body, custom_instructions, timestamp }
```

---

## Database Storage

### Structure

The `email_preview` field in the `tasks` table stores:

```json
{
  "subject": "Checking In on 884 Saddle St Negotiations",
  "body": "<p>Hello 884 Saddle Street...</p>",
  "custom_instructions": "Be more friendly",
  "timestamp": 1705123456789
}
```

### Migration

**File**: `backend/alembic/versions/20250116_add_email_preview_to_tasks.py`

```python
def upgrade():
    op.add_column('tasks', sa.Column('email_preview', postgresql.JSON(astext_type=sa.Text()), nullable=True))
```

### Access Pattern

1. **Save**: `UPDATE tasks SET email_preview = {...} WHERE id = ?`
2. **Load**: `SELECT email_preview FROM tasks WHERE id = ?`
3. **Clear**: `UPDATE tasks SET email_preview = NULL WHERE id = ?` (after sending)

---

## State Management

### React Query Cache

The task data is cached using React Query:

```typescript
const { data: task } = useTask(taskId, { enabled: open });
```

**Cache Key**: `['task', taskId]`

**Cache Updates:**
- After save: Cache is updated directly, then optionally invalidated
- After load: Cache contains `task.email_preview`

### Local State

```typescript
const [subject, setSubject] = useState('');
const [body, setBody] = useState('');
const [customInstructions, setCustomInstructions] = useState('');
const [hasGenerated, setHasGenerated] = useState(false);
const [isEditMode, setIsEditMode] = useState(false);
const [isSaving, setIsSaving] = useState(false);
```

### Refs (Prevent Race Conditions)

```typescript
const hasAttemptedGenerate = useRef(false);  // Prevent duplicate generation
const isGeneratingRef = useRef(false);       // Track generation in progress
const isSavingRef = useRef(false);           // Track save in progress
```

---

## Key Components

### Frontend

1. **`EmailPreviewModal.tsx`**: Main component handling preview and save
2. **`EmailComposer.tsx`**: Rich text editor for email body
3. **`usePreviewEmail`**: React Query mutation for generating preview
4. **`tasksApi.update`**: API client for updating task

### Backend

1. **`/api/emails/preview`**: Endpoint for generating email preview
2. **`AIAgent.generate_email_preview()`**: AI generation logic
3. **`AIAgent._build_prompt()`**: Prompt construction
4. **`AIAgent._parse_openai_response()`**: Response parsing
5. **`/api/tasks/{id}` (PATCH)**: Endpoint for updating task (including email_preview)

---

## Flow Diagrams

### Generation Flow

```
User Opens Modal
    ↓
Check task.email_preview
    ↓
[Exists?] → Yes → Load from DB → Display
    ↓ No
Check localStorage
    ↓
[Exists?] → Yes → Load from localStorage → Display
    ↓ No
Call handleGenerate()
    ↓
POST /api/emails/preview
    ↓
AIAgent.generate_email_preview()
    ↓
OpenAI API Call
    ↓
Parse Response
    ↓
Return { subject, body }
    ↓
Update State
    ↓
Auto-save to DB (skipInvalidation=true)
```

### Save Flow

```
User Edits Email
    ↓
State Updates (subject/body)
    ↓
[1 second debounce]
    ↓
Auto-save OR User Clicks Save
    ↓
savePreviewToDatabase()
    ↓
Set isSavingRef = true
    ↓
PATCH /api/tasks/{id} { email_preview: {...} }
    ↓
Update Database
    ↓
Update React Query Cache
    ↓
[skipInvalidation?]
    ↓
Yes → Silent update
No → Invalidate query
    ↓
Reset isSavingRef after 1s
```

---

## Important Notes

### Preventing Regeneration

The system uses several mechanisms to prevent unwanted regeneration:

1. **`isSavingRef`**: Prevents `useEffect` from running during save
2. **`hasAttemptedGenerate`**: Prevents duplicate generation attempts
3. **`skipInvalidation`**: Prevents query invalidation from triggering regeneration
4. **Content Comparison**: Only updates state if content differs

### Auto-save vs Manual Save

- **Auto-save**: Debounced (1s), silent, `skipInvalidation=true`
- **Manual Save**: Immediate, shows toast, `skipInvalidation=false`

### Error Handling

- **API Errors**: Falls back to localStorage, shows warning toast
- **Generation Errors**: Uses fallback template, allows editing
- **Save Errors**: Saves to localStorage as backup

### Data Persistence

- **Database**: Primary storage, persists across sessions
- **localStorage**: Fallback only, expires after 24 hours
- **Cache**: React Query cache for fast access

---

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=1000
```

### Database

```sql
ALTER TABLE tasks ADD COLUMN email_preview JSON;
```

---

## Testing Scenarios

1. **Open modal with saved preview**: Should load from database
2. **Open modal without preview**: Should generate new email
3. **Edit and auto-save**: Should save after 1 second
4. **Edit and manual save**: Should save immediately
5. **Save during generation**: Should not regenerate
6. **Close and reopen**: Should load saved preview
7. **Regenerate**: Should clear old preview and generate new
8. **Send email**: Should clear preview after sending

---

## Troubleshooting

### Preview Not Loading

- Check `task.email_preview` in database
- Check browser console for errors
- Verify task query is loading correctly

### Regeneration After Save

- Check `isSavingRef.current` is set correctly
- Verify `skipInvalidation` flag usage
- Check `useEffect` dependencies

### Save Not Working

- Check API endpoint is accessible
- Verify task belongs to agent
- Check database connection
- Review error logs

---

## Future Improvements

1. **Version History**: Store multiple versions of preview
2. **Draft Auto-save**: More frequent auto-saves
3. **Conflict Resolution**: Handle concurrent edits
4. **Preview Expiration**: Auto-expire old previews
5. **Template Library**: Pre-built email templates

