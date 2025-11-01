# RealtorOS - Data Flow & Service Interactions

**Complete documentation of data flows, service interactions, and system architecture for RealtorOS CRM.**

---

## 1. NEW CLIENT CREATION FLOW

```
┌──────────────────┐
│   Agent clicks   │
│  "+ New Client"  │
│  (Frontend UI)   │
└────────┬─────────┘
         │
         ▼
    ┌─────────────────────────────────────┐
    │   Frontend: ClientForm Component    │
    │  - name, email, phone                │
    │  - property_address, property_type │
    │  - stage, notes, custom_fields      │
    └─────────────┬───────────────────────┘
                  │
                  ▼ POST /api/clients
         ┌────────────────────┐
         │  FastAPI Endpoint  │
         │  (routes/clients)  │
         │  POST /api/clients  │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  CRM Service       │
         │  create_client()   │
         │  - Validate input  │
         │  - Create Client   │
         └────────┬───────────┘
                  │
                  ▼ SQLAlchemy Insert
         ┌────────────────────────┐
         │  PostgreSQL: clients   │
         │  INSERT INTO clients   │
         │  Returns: client_id     │
         │  (with created_at)      │
         └────────┬───────────────┘
                  │
                  ▼ Celery Task (async)
         ┌────────────────────┐
         │ create_followup_   │
         │ tasks_task.delay() │
         │ (enqueued to Redis)│
         └────────┬───────────┘
                  │
                  ▼ Redis Queue
         ┌────────────────────┐
         │  Redis Queue       │
         │  (Celery broker)   │
         └────────┬───────────┘
                  │
     ┌────────────┴────────────┐
     │                         │
     ▼ Celery Worker picks up │
┌─────────────────────────────┐
│  Scheduler Service          │
│  create_followup_tasks()    │
│  Uses FOLLOWUP_SCHEDULE     │
└──────────┬──────────────────┘
           │
           ▼ Create 5 Tasks
    ┌──────────────────────────┐
    │  For each schedule:      │
    │  - Day 1 (1 day, high)   │
    │  - Day 3 (3 days, medium)│
    │  - Week 1 (7 days, med)  │
    │  - Week 2 (14 days, low) │
    │  - Month 1 (30 days, low)│
    └──────────┬───────────────┘
               │
               ▼ SQLAlchemy Bulk Insert
    ┌──────────────────────────────┐
    │  PostgreSQL: tasks           │
    │  INSERT INTO tasks (bulk)    │
    │  - client_id (FK)            │
    │  - followup_type             │
    │  - scheduled_for             │
    │  - status = "pending"        │
    │  - priority                  │
    └──────────┬───────────────────┘
               │
               ▼ HTTP 201 Created
    ┌──────────────────────────────┐
    │  Response to Frontend        │
    │  {                           │
    │    id: 123,                  │
    │    name: "John Doe",         │
    │    email: "john@example.com",│
    │    stage: "lead",            │
    │    created_at: "2024-...",   │
    │    ...                        │
    │  }                           │
    └──────────────────────────────┘
```

**Key Points:**
- Client creation is **synchronous** (immediate response)
- Follow-up task creation is **asynchronous** (via Celery)
- 5 tasks automatically created based on `FOLLOWUP_SCHEDULE` constant
- All timestamps in UTC (timezone-aware)

---

## 2. AUTOMATED EMAIL FOLLOW-UP FLOW

```
EVERY 60 SECONDS (Celery Beat):
┌──────────────────────────────────────┐
│  Celery Beat (Scheduler)             │
│  - Reads beat_schedule config        │
│  - Runs every 60.0 seconds           │
│  - Task: process_due_tasks           │
└──────────────┬───────────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Periodic Task              │
    │  process_due_tasks()         │
    │  (app.tasks.periodic)        │
    └──────────┬───────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Scheduler Service          │
    │  process_and_send_due_emails()│
    └──────────┬───────────────────┘
               │
               ▼ SQLAlchemy Query
    ┌─────────────────────────────┐
    │  PostgreSQL Query:          │
    │  SELECT * FROM tasks         │
    │  WHERE scheduled_for <= NOW()│
    │  AND status = 'pending'      │
    │  (using SQLAlchemy ORM)      │
    └──────────┬───────────────────┘
               │
        ┌──────┴──────┐
        │             │
   Found 3      Found 0
   tasks        tasks
        │             │
        ▼             ▼
   Process       Log & Return
   tasks         count = 0
        │


FOR EACH DUE TASK:
┌─────────────────────────────────────────┐
│  Loop through each due task             │
│  For task_id=1, client_id=10:           │
└──────────┬──────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────┐
    │  1. Fetch Client            │
    │     SELECT * FROM clients   │
    │     WHERE id = task.client_id│
    └──────────┬──────────────────┘
               │
               ▼ Client found
    ┌─────────────────────────────┐
    │  2. AI Agent Service        │
    │     AIAgent.generate_email()│
    └──────────┬───────────────────┘
               │
               ▼ Build Prompt
    ┌─────────────────────────────┐
    │  Prompt includes:            │
    │  - Client info (name, email, │
    │    property, stage, notes)   │
    │  - Follow-up context         │
    │    (Day 1, Day 3, etc.)      │
    │  - Task priority & notes     │
    │  - Custom instructions       │
    └──────────┬───────────────────┘
               │
               ▼ HTTP POST Request
    ┌─────────────────────────────┐
    │  OpenAI API                 │
    │  POST /v1/chat/completions   │
    │  Model: GPT-3.5-turbo/GPT-4 │
    │  Async call                  │
    └──────────┬───────────────────┘
               │
        ┌──────┴──────┐
        │             │
    Success       Error/Timeout
        │             │
        │             ▼ Fallback Template
        │      ┌──────────────────┐
        │      │ Fallback email   │
        │      │ {subject, body}  │
        │      └──────────────────┘
        │             │
        └──────┬──────┘
               │
               ▼ Parse Response
    ┌─────────────────────────────┐
    │  Extract from OpenAI:       │
    │  {                           │
    │    "subject": "...",        │
    │    "body": "..."             │
    │  }                           │
    │  (handles JSON & text)       │
    └──────────┬───────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  3. Email Service           │
    │     send_email()             │
    └──────────┬───────────────────┘
               │
               ▼ Step 3a: Log Email
    ┌─────────────────────────────┐
    │  PostgreSQL: email_logs    │
    │  INSERT INTO email_logs     │
    │  - task_id, client_id       │
    │  - to_email, subject, body  │
    │  - status = "queued"        │
    │  Returns: email_log_id      │
    └──────────┬───────────────────┘
               │
               ▼ Step 3b: Send via SendGrid
    ┌─────────────────────────────┐
    │  SendGrid API               │
    │  POST /v3/mail/send         │
    │  - from_email (configured)  │
    │  - to_emails (client.email) │
    │  - subject, html_content    │
    └──────────┬───────────────────┘
               │
        ┌──────┴──────┐
        │             │
    Success       Failure
        │             │
        │             ▼
        │      ┌──────────────────┐
        │      │ Update status    │
        │      │ = "failed"       │
        │      │ error_message    │
        │      └──────────────────┘
        │
        ▼ Returns Message ID
    ┌─────────────────────────────┐
    │  Update EmailLog:            │
    │  - status = "sent"           │
    │  - sendgrid_message_id       │
    │  - sent_at = NOW()           │
    └──────────┬───────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  4. Update Task              │
    │     UPDATE tasks             │
    │     SET status = "completed" │
    │     SET email_sent_id = ...  │
    │     SET completed_at = NOW() │
    │     WHERE id = task_id       │
    └──────────┬───────────────────┘
               │
               ▼ Continue to next task
    ┌─────────────────────────────┐
    │  Process next due task       │
    │  (or finish if no more)      │
    └──────────────────────────────┘

    ┌─────────────────────────────┐
    │  Return count                │
    │  logger.info("Processed 3    │
    │              due tasks")     │
    └──────────────────────────────┘
```

**Key Points:**
- **Celery Beat** runs `process_due_tasks` every **60 seconds** (1 minute)
- All processing happens **synchronously within each task** (not queued separately)
- **Error handling**: If one task fails, processing continues for others
- **Transaction safety**: Each task wrapped in try/except with rollback
- **Logging**: All operations logged at INFO level

---

## 3. SENDGRID WEBHOOK EMAIL ENGAGEMENT FLOW

```
┌─────────────────────────────────────────┐
│  SendGrid (External Service)           │
│  - Email delivered to recipient         │
│  - Recipient opens email                │
│  - Recipient clicks link                │
└──────────────┬──────────────────────────┘
               │
               ▼ HTTP POST
    ┌─────────────────────────────┐
    │  SendGrid Webhook           │
    │  POST /webhook/sendgrid     │
    │  (Public endpoint, no /api) │
    │                              │
    │  Headers:                    │
    │  - X-Twilio-Email-Event-     │
    │    Webhook-Signature         │
    │  - X-Twilio-Email-Event-     │
    │    Webhook-Timestamp         │
    │                              │
    │  Body: [                     │
    │    {                         │
    │      "event": "open",        │
    │      "sg_message_id": "...", │
    │      "timestamp": 1234567890,│
    │      "email": "user@...",    │
    │      "ip": "192.168.1.1",    │
    │      "useragent": "..."      │
    │    }                         │
    │  ]                           │
    └──────────┬───────────────────┘
               │
               ▼ Extract Headers
    ┌─────────────────────────────┐
    │  FastAPI Endpoint            │
    │  sendgrid_webhook()          │
    │  (routes/emails.py)          │
    └──────────┬───────────────────┘
               │
               ▼ Read Raw Body
    ┌─────────────────────────────┐
    │  Verify ECDSA Signature     │
    │  verify_sendgrid_signature() │
    │  - Extract signature         │
    │  - Extract timestamp         │
    │  - Load public key (env)     │
    │  - Verify: SHA256(timestamp  │
    │    + payload) → ECDSA verify │
    └──────────┬───────────────────┘
               │
        ┌──────┴──────┐
        │             │
    Valid        Invalid
        │             │
        │             ▼ HTTP 401
        │      ┌──────────────────┐
        │      │ Unauthorized     │
        │      │ Return 401       │
        │      └──────────────────┘
        │
        ▼ Validate Timestamp
    ┌─────────────────────────────┐
    │  Check timestamp age         │
    │  Must be < 10 minutes old    │
    │  (prevent replay attacks)    │
    └──────────┬───────────────────┘
               │
        ┌──────┴──────┐
        │             │
    Fresh        Too Old
        │             │
        │             ▼ HTTP 401
        │      ┌──────────────────┐
        │      │ Reject (replay)  │
        │      └──────────────────┘
        │
        ▼ Parse JSON
    ┌─────────────────────────────┐
    │  Parse webhook payload      │
    │  (array of events)          │
    │  Validate with Pydantic     │
    │  SendGridWebhookEvent       │
    └──────────┬───────────────────┘
               │
               ▼ For Each Event
    ┌─────────────────────────────┐
    │  Email Service              │
    │  process_webhook_event()    │
    └──────────┬───────────────────┘
               │
               ▼ Find EmailLog by Message ID
    ┌─────────────────────────────┐
    │  PostgreSQL Query:          │
    │  SELECT * FROM email_logs    │
    │  WHERE sendgrid_message_id   │
    │  = event.sg_message_id      │
    └──────────┬───────────────────┘
               │
        ┌──────┴──────┐
        │             │
    Found        Not Found
        │             │
        │             ▼ Log Warning
        │      ┌──────────────────┐
        │      │ Continue to next │
        │      │ event             │
        │      └──────────────────┘
        │
        ▼ Parse Event Timestamp
    ┌─────────────────────────────┐
    │  Convert Unix timestamp     │
    │  to datetime (UTC)          │
    └──────────┬───────────────────┘
               │
               ▼ Update EmailLog
    ┌─────────────────────────────┐
    │  Based on event type:       │
    │                              │
    │  If event == "open":         │
    │    - Set opened_at           │
    │      (first open only)      │
    │                              │
    │  If event == "click":        │
    │    - Set clicked_at          │
    │      (first click only)     │
    │                              │
    │  Always:                     │
    │    - Update status           │
    │    - Append to webhook_     │
    │      events JSON array       │
    │                              │
    │  UPDATE email_logs           │
    │  SET opened_at = ...         │
    │  SET clicked_at = ...        │
    │  SET status = event.event    │
    │  SET webhook_events =        │
    │    array_append(...)         │
    └──────────┬───────────────────┘
               │
               ▼ HTTP 200 OK
    ┌─────────────────────────────┐
    │  Response:                   │
    │  {                           │
    │    "status": "success",      │
    │    "processed": 2,          │
    │    "failed": 0,              │
    │    "total": 2                │
    │  }                           │
    │                              │
    │  (Always 200 to prevent      │
    │   SendGrid retries)          │
    └──────────────────────────────┘
```

**Key Points:**
- **ECDSA signature verification** required on every request
- **Timestamp validation** prevents replay attacks (10-minute window)
- **Idempotent processing**: Multiple events for same email handled correctly
- **Always returns 200**: Even if some events fail (to prevent SendGrid retries)
- **Full event history**: All webhook events stored in JSON array

---

## 4. DATABASE SCHEMA & RELATIONSHIPS

```
┌─────────────────────────────────────────────────────────┐
│                  POSTGRESQL DATABASE                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────┐                              │
│  │    clients           │                              │
│  ├──────────────────────┤                              │
│  │ id: INTEGER (PK)     │                              │
│  │ name: VARCHAR(100)   │                              │
│  │ email: VARCHAR(255) ◄─┼─────────────┐               │
│  │ phone: VARCHAR(20)    │             │               │
│  │ property_address      │             │               │
│  │ property_type         │             │               │
│  │ stage: VARCHAR(50)    │             │               │
│  │ notes: TEXT           │             │               │
│  │ custom_fields: JSON   │             │               │
│  │ created_at: TIMESTAMP │             │               │
│  │ updated_at: TIMESTAMP  │             │               │
│  │ last_contacted        │             │               │
│  │ is_deleted: BOOLEAN   │             │               │
│  └──────────────────────┘             │               │
│           ▲                            │               │
│           │ FOREIGN KEY                │               │
│           │ client_id                  │               │
│  ┌────────┴──────────────┐             │               │
│  │     tasks             │             │               │
│  ├───────────────────────┤             │               │
│  │ id: INTEGER (PK)      │             │               │
│  │ client_id: INTEGER ◄──┼─────────────┘               │
│  │ email_sent_id: INT ◄──┼─────────────┐               │
│  │ followup_type         │             │               │
│  │ scheduled_for         │             │               │
│  │ status: VARCHAR(50)   │             │               │
│  │ priority              │             │               │
│  │ notes: TEXT           │             │               │
│  │ created_at            │             │               │
│  │ updated_at             │             │               │
│  │ completed_at           │             │               │
│  └───────────────────────┘             │               │
│           ▲                             │               │
│           │ FOREIGN KEY                  │               │
│           │ task_id                      │               │
│  ┌────────┴──────────────────┐          │               │
│  │     email_logs            │          │               │
│  ├───────────────────────────┤          │               │
│  │ id: INTEGER (PK)          │          │               │
│  │ task_id: INTEGER ◄───────┼──────────┘               │
│  │ client_id: INTEGER       │          │               │
│  │ to_email: VARCHAR(255)   │          │               │
│  │ subject: VARCHAR(200)     │          │               │
│  │ body: TEXT                │          │               │
│  │ status: VARCHAR(50)       │          │               │
│  │ sendgrid_message_id       │          │               │
│  │ created_at                │          │               │
│  │ sent_at                   │          │               │
│  │ opened_at                 │          │               │
│  │ clicked_at                │          │               │
│  │ error_message: TEXT       │          │               │
│  │ retry_count: INTEGER      │          │               │
│  │ webhook_events: JSON      │          │               │
│  └───────────────────────────┘          │               │
│                                           │               │
└───────────────────────────────────────────┼───────────────┘
                                            │
                                            │ References
                                            │ (no FK constraint,
                                            │ but logical)
```

**Database Relationships:**
- **Clients → Tasks**: One-to-Many (one client has many tasks)
- **Tasks → EmailLogs**: One-to-One (one task has one email log)
- **Clients → EmailLogs**: One-to-Many (one client has many emails)

**Indexes for Performance:**
```sql
-- Clients
CREATE INDEX ix_clients_stage_is_deleted ON clients(stage, is_deleted);
CREATE INDEX ix_clients_email_is_deleted ON clients(email, is_deleted);

-- Tasks
CREATE INDEX ix_tasks_client_status ON tasks(client_id, status);
CREATE INDEX ix_tasks_scheduled_status ON tasks(scheduled_for, status);

-- Email Logs
CREATE INDEX ix_email_logs_status_client ON email_logs(status, client_id);
-- (sendgrid_message_id indexed for webhook lookups)
```

**SQLAlchemy ORM:**
- Uses **declarative Base** for models
- **AsyncSession** for async database operations
- **Foreign Key constraints** defined in models
- **Timezone-aware timestamps** (UTC)

---

## 5. REQUEST/RESPONSE CYCLE (Example: List Tasks)

```
┌────────────────────────────────────────────────────────────┐
│                  FRONTEND (Next.js)                        │
│  React Component: TaskList                                │
│  Hook: useTasks()                                         │
│  Calls: GET /api/tasks?status=pending                     │
└────────────────┬─────────────────────────────────────────┘
                 │ HTTP GET
                 │ Accept: application/json
                 │ Authorization: (if implemented)
                 ▼
        ┌────────────────────────────────────┐
        │  BACKEND (FastAPI)                 │
        │  Route: GET /api/tasks             │
        │  Handler: list_tasks()             │
        │  (routes/tasks.py)                 │
        └────────┬─────────────────────────┘
                 │
                 ▼ Extract Query Params
        ┌────────────────────────────────────┐
        │  Query Parameters:                 │
        │  - page: 1 (default)               │
        │  - limit: 10 (default)              │
        │  - status: "pending" (optional)     │
        │  - client_id: 5 (optional)          │
        └────────┬─────────────────────────┘
                 │
                 ▼ Dependency Injection
        ┌────────────────────────────────────┐
        │  Scheduler Service                 │
        │  (via get_scheduler_service)       │
        │  list_tasks(                       │
        │    page=1,                          │
        │    limit=10,                        │
        │    status="pending",                │
        │    client_id=None                   │
        │  )                                 │
        └────────┬─────────────────────────┘
                 │
                 ▼ SQLAlchemy Query Builder
        ┌────────────────────────────────────┐
        │  Build SQL Query:                  │
        │  SELECT * FROM tasks               │
        │  WHERE status = 'pending'          │
        │  ORDER BY scheduled_for ASC        │
        │  LIMIT 10 OFFSET 0                 │
        └────────┬─────────────────────────┘
                 │
                 ▼ Execute Async Query
        ┌────────────────────────────────────┐
        │  PostgreSQL Database               │
        │  (via asyncpg driver)              │
        │  Returns: Task objects              │
        └────────┬─────────────────────────┘
                 │ Returns 5 Task records
                 │
                 ▼ Transform to Response
        ┌────────────────────────────────────┐
        │  Format Response (Pydantic)        │
        │  List[TaskResponse]:               │
        │  [                                 │
        │    {                               │
        │      id: 1,                        │
        │      client_id: 10,                │
        │      followup_type: "Day 1",       │
        │      scheduled_for: "2024-...",   │
        │      status: "pending",            │
        │      priority: "high",            │
        │      created_at: "2024-...",       │
        │      ...                           │
        │    },                              │
        │    ... (4 more)                    │
        │  ]                                 │
        └────────┬─────────────────────────┘
                 │ HTTP 200 OK
                 │ Content-Type: application/json
                 ▼
        ┌────────────────────────────────────┐
        │  FRONTEND (React)                  │
        │  useTasks() hook updates state     │
        │  Component re-renders with data    │
        │  UI displays:                      │
        │  - Task 1: Day 1 (pending)       │
        │  - Task 2: Day 1 (pending)       │
        │  - Task 3: Day 3 (pending)       │
        │  ...                              │
        └────────────────────────────────────┘
```

**Key Points:**
- **FastAPI async/await** for non-blocking I/O
- **Pydantic validation** ensures type safety
- **SQLAlchemy ORM** handles query building
- **Automatic serialization** via Pydantic models
- **Pagination** via LIMIT/OFFSET

---

## 6. DEPLOYMENT ARCHITECTURE (Production)

```
┌─────────────────────────────────────────────────────────┐
│                 CloudFlare / CDN                         │
│            (Static assets, caching)                      │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴──────────────┐
         │                          │
         ▼                          ▼
    ┌────────────┐          ┌────────────────┐
    │ Frontend   │          │ Nginx Reverse  │
    │ (Vercel/   │          │ Proxy (VPS)    │
    │  Netlify)  │          │ Port 80/443    │
    │ Next.js    │          │ SSL/TLS        │
    │ Static/SSG │          └────────┬───────┘
    └────────────┘                   │
                        ┌────────────┴───────────┐
                        │                        │
                        ▼                        ▼
                  ┌──────────────┐       ┌──────────────┐
                  │  FastAPI    │       │  FastAPI     │
                  │  Uvicorn    │       │  Uvicorn     │
                  │  (ECS/      │       │  (ECS/       │
                  │   Railway)  │       │   Railway)  │
                  │  Workers    │       │  Workers    │
                  └──────┬───────┘       └──────┬───────┘
                         │                      │
                         └──────────┬───────────┘
                                    │
                        ┌───────────┴───────────┐
                        │                       │
                        ▼                       ▼
                  ┌──────────────┐      ┌──────────────┐
                  │ PostgreSQL    │      │  Redis Cloud │
                  │ (AWS RDS/     │      │  (ElastiCache│
                  │  Supabase/    │      │   /Managed)   │
                  │  Managed)     │      └──────┬───────┘
                  └──────────────┘             │
                                               │
                        ┌──────────────────────┘
                        │
        ┌───────────────┴────────────────┐
        │                                │
        ▼                                ▼
    ┌─────────────┐            ┌──────────────────┐
    │ Celery      │            │  Celery Workers  │
    │ Beat        │            │  (ECS Tasks/     │
    │ (Scheduler) │            │   Kubernetes)    │
    │ (1 instance)│            │  - Process due   │
    │             │            │  - Generate     │
    │             │            │  - Send emails  │
    └─────────────┘            └──────────────────┘
        │                                │
        └────────────┬──────────────────┘
                     │
        ┌────────────┴──────────────┐
        │                           │
        ▼                           ▼
    ┌──────────────┐        ┌────────────────┐
    │  OpenAI API  │        │  SendGrid API  │
    │  (External)  │        │  (External)    │
    │  HTTPS        │        │  HTTPS          │
    └──────────────┘        └────────────────┘

WEBHOOK FLOW:
        ┌────────────────┐
        │  SendGrid      │
        │  (External)    │
        └────────┬───────┘
                 │ HTTP POST
                 │ /webhook/sendgrid
                 ▼
        ┌────────────────┐
        │  FastAPI       │
        │  (Same workers)│
        │  Verify        │
        │  signature     │
        └────────────────┘
```

**Key Components:**
- **Load Balancing**: Multiple FastAPI workers behind Nginx
- **Database**: Managed PostgreSQL (RDS, Supabase, etc.)
- **Cache/Queue**: Managed Redis (ElastiCache, Redis Cloud)
- **Celery**: Separate workers for background processing
- **Celery Beat**: Single instance for scheduling
- **Webhooks**: Received directly by FastAPI workers

---

## 7. ERROR HANDLING & RETRY LOGIC

```
┌─────────────────────────────────────┐
│  Task: Process Due Email            │
│  (SchedulerService.process_and_     │
│   send_due_emails())                │
└────────────────┬────────────────────┘
                 │
                 ▼ For Each Task
        ┌─────────────────────┐
        │ Fetch Client       │
        │ from PostgreSQL     │
        └────────┬────────────┘
                 │
         ┌───────┴────────┐
         │                │
    Success          Client Not Found
         │                │
         │                ▼ Log Error
         │        ┌──────────────────────┐
         │        │ logger.error()       │
         │        │ Continue next task   │
         │        └──────────────────────┘
         │
         ▼
    ┌─────────────────────┐
    │ Generate Email      │
    │ (OpenAI API Call)    │
    └────────┬────────────┘
             │
     ┌───────┴────────┐
     │                │
 Success          Error/Timeout
     │                │
     │                ▼ Fallback
     │        ┌──────────────────────┐
     │        │ Use fallback template│
     │        │ Continue with email  │
     │        └──────────────────────┘
     │
     ▼
┌─────────────────────┐
│ Send Email          │
│ (SendGrid API)      │
└────────┬────────────┘
         │
 ┌───────┴────────┐
 │                │
Success       Failure
 │                │
 │                ▼
 │        ┌──────────────────────┐
 │        │ Update EmailLog:     │
 │        │ status = "failed"    │
 │        │ error_message = ...  │
 │        │ Log error            │
 │        │ Continue next task   │
 │        └──────────────────────┘
 │
 ▼
┌─────────────────────┐
│ Update Task         │
│ status = "completed"│
│ email_sent_id = ...  │
└─────────────────────┘

EXCEPTION HANDLING:
┌─────────────────────────────────────┐
│  try:                               │
│    # Process task                   │
│  except Exception as e:            │
│    logger.error(                    │
│      f"Error: {e}",                 │
│      exc_info=True                  │
│    )                                │
│    await session.rollback()         │
│    continue  # Next task            │
└─────────────────────────────────────┘
```

**Error Handling Strategy:**
- **Individual task failures** don't stop processing
- **Database rollbacks** for failed tasks
- **Comprehensive logging** with stack traces
- **Fallback templates** if OpenAI fails
- **Error messages** stored in EmailLog
- **Graceful degradation**: System continues even if some operations fail

---

## 8. SERVICE COMMUNICATION SUMMARY

| Communication | Protocol | Sync/Async | Example |
|---|---|---|---|
| Frontend ↔ Backend | HTTP REST | Sync (await) | GET /api/clients |
| Backend → PostgreSQL | PostgreSQL (asyncpg) | Async | SQLAlchemy query |
| Backend → Redis | Redis Protocol | Async | Celery publish |
| Backend → Celery Task | Redis Queue | Async | Task.delay() |
| Celery Worker → PostgreSQL | PostgreSQL (asyncpg) | Async | SQLAlchemy query |
| Celery Worker → OpenAI | HTTP REST | Async (await) | generate_email() |
| Celery Worker → SendGrid | HTTP REST | Sync (requests) | send_email() |
| SendGrid → Backend | HTTP POST | Sync | Webhook callback |

**Service Dependencies:**
- **CRM Service**: Manages clients (CRUD operations)
- **Scheduler Service**: Manages tasks and email processing
- **Email Service**: Handles email logging and sending
- **Dashboard Service**: Aggregates statistics
- **AI Agent Service**: Generates email content via OpenAI

---

## 9. DATA CONSISTENCY & TRANSACTIONS

```
TRANSACTION BOUNDARIES:

Client Creation:
  BEGIN TRANSACTION
    INSERT INTO clients ...
    COMMIT
  END TRANSACTION
  (Then async: create followup tasks)

Task Processing:
  BEGIN TRANSACTION
    SELECT tasks ...
    (For each task:)
      INSERT INTO email_logs ...
      UPDATE tasks SET status='completed' ...
    COMMIT
  END TRANSACTION

Webhook Processing:
  BEGIN TRANSACTION
    UPDATE email_logs SET ...
      opened_at = ...
      webhook_events = array_append(...)
    COMMIT
  END TRANSACTION

CONCURRENCY HANDLING:
- PostgreSQL transactions ensure ACID
- Celery workers process tasks independently
- No race conditions on task status (single worker per task)
- Webhook events are idempotent (can be processed multiple times)
```

**ACID Guarantees:**
- **Atomicity**: All or nothing (transactions)
- **Consistency**: Foreign keys enforce integrity
- **Isolation**: Transaction isolation levels
- **Durability**: Committed data persists

---

## 10. CELERY TASK FLOW SUMMARY

```
PERIODIC TASKS (Celery Beat):
┌──────────────────────────────┐
│ process_due_tasks            │
│ Schedule: Every 60 seconds    │
│ Task: process_and_send_      │
│       due_emails()            │
└──────────────────────────────┘

ASYNC TASKS (Triggered):
┌──────────────────────────────┐
│ create_followup_tasks_task    │
│ Trigger: Client creation      │
│ Action: Create 5 follow-up    │
│         tasks                 │
└──────────────────────────────┘

TASK EXECUTION:
1. Task enqueued to Redis
2. Celery worker picks up task
3. Worker initializes database session
4. Worker calls service method
5. Service performs database operations
6. Service calls external APIs (OpenAI, SendGrid)
7. Worker commits transaction
8. Worker returns result
```

**Task Configuration:**
- **Serialization**: JSON
- **Timezone**: UTC
- **Time Limits**: 30 minutes (hard), 25 minutes (soft)
- **Max Retries**: 3 (for email tasks)
- **Prefetch Multiplier**: 1 (fair distribution)

---

This completes the comprehensive data flow documentation for RealtorOS!

**Last Updated**: Based on current codebase implementation (PostgreSQL, SQLAlchemy, FastAPI, Celery)
