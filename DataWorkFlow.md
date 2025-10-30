# RealtorOS - Data Flow & Service Interactions

## 1. NEW CLIENT CREATION FLOW

```
┌──────────────────┐
│   Agent clicks   │
│  "+ New Client"  │
└────────┬─────────┘
         │
         ▼
    ┌─────────────────────────────────────┐
    │   Frontend: ClientForm Component    │
    │  - name, email, phone, property     │
    │  - property_type, stage, notes      │
    └─────────────┬───────────────────────┘
                  │
                  ▼ POST /api/clients
         ┌────────────────────┐
         │  FastAPI Endpoint  │
         │  (routes/clients)  │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  CRM Service       │
         │  - Validate input  │
         │  - Create Client   │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │  MongoDB Insert        │
         │  → clients collection  │
         │  Returns: client_id    │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │ Scheduler Service  │
         │ create_followup_   │
         │ tasks(client_id)   │
         └────────┬───────────┘
                  │
         ┌────────┴──────────┐
         │                   │
         ▼                   ▼
    Create Task 1       Create Task 2
    "Day 1"              "Day 3"
    scheduled_for:       scheduled_for:
    now + 1 day          now + 3 days
    status: pending      status: pending
         │                   │
         └────────┬──────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │  MongoDB Insert (bulk) │
         │  → tasks collection    │
         │  (5 tasks total)       │
         └────────┬───────────────┘
                  │
                  ▼
    ┌──────────────────────────────┐
    │  Response to Frontend        │
    │  HTTP 201 Created            │
    │  { client_id, status: ok }   │
    └──────────────────────────────┘
```

---

## 2. AUTOMATED EMAIL FOLLOW-UP FLOW

```
MINUTE 0:
┌──────────────────────────────┐
│  Celery Beat (Scheduler)     │
│  Every 1 minute:             │
│  check_and_schedule_emails() │
└──────────────┬───────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │  Query MongoDB:             │
    │  tasks WHERE               │
    │  scheduled_for <= NOW      │
    │  AND status = "pending"    │
    └──────────┬──────────────────┘
               │
        ┌──────┴──────┐
        │             │
   Found 2   Found 0
   tasks    tasks
        │       │
        ▼       ▼
    Process   Sleep
    tasks     1 min


MINUTE 1 (After tasks found):
┌───────────────────────────────────────┐
│  For each task:                       │
│  generate_and_send_email_task.delay() │
│  (Queue Celery task)                  │
└───────────────────┬───────────────────┘
                    │
                    ▼ Send to Redis Queue
    ┌──────────────────────────────────┐
    │  Redis Message Queue             │
    │  (Celery broker)                 │
    │  └─ email_task_1                 │
    │  └─ email_task_2                 │
    └──────────────────┬───────────────┘
                       │
     ┌─────────────────┴─────────────────┐
     │                                   │
     ▼ Celery Worker 1                   ▼ Celery Worker 2
┌─────────────────────────────┐  ┌─────────────────────────────┐
│  Fetch Task & Client        │  │  Fetch Task & Client        │
│  from MongoDB               │  │  from MongoDB               │
└─────────────┬───────────────┘  └────────┬────────────────────┘
              │                            │
              ▼                            ▼
    ┌──────────────────────┐    ┌──────────────────────┐
    │  AI Agent Service:   │    │  AI Agent Service:   │
    │  generate_email()    │    │  generate_email()    │
    └──────────┬───────────┘    └──────────┬───────────┘
               │                            │
               ▼ OpenAI API Call            ▼ OpenAI API Call
    ┌──────────────────────┐    ┌──────────────────────┐
    │  OpenAI GPT-4        │    │  OpenAI GPT-4        │
    │  "Generate email     │    │  "Generate email     │
    │   for John Doe..."   │    │   for Jane Smith..." │
    └──────────┬───────────┘    └──────────┬───────────┘
               │                            │
               ▼ Returns                    ▼ Returns
         {subject, body}              {subject, body}
               │                            │
               ▼                            ▼
    ┌──────────────────────┐    ┌──────────────────────┐
    │  Email Service:      │    │  Email Service:      │
    │  queue_send_email()  │    │  queue_send_email()  │
    │                      │    │                      │
    │ 1. Create EmailLog   │    │ 1. Create EmailLog   │
    │ 2. Queue Celery task │    │ 2. Queue Celery task │
    └──────────┬───────────┘    └──────────┬───────────┘
               │                            │
               ▼ insert_one()               ▼ insert_one()
      ┌─────────────────────────┐ ┌─────────────────────────┐
      │  MongoDB:EmailLog       │ │  MongoDB:EmailLog       │
      │  status: "queued"       │ │  status: "queued"       │
      │  {task_id, client_id,   │ │  {task_id, client_id,   │
      │   email, subject, body} │ │   email, subject, body} │
      └──────────┬──────────────┘ └──────────┬──────────────┘
                 │                            │
                 └────────────┬───────────────┘
                              │
                              ▼ (enqueue)
          ┌────────────────────────────┐
          │  Redis: send_email_tasks   │
          │  └─ send_email_1           │
          │  └─ send_email_2           │
          └───────────────┬────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼ Celery Worker 1              ▼ Celery Worker 2
    ┌───────────────────────┐      ┌───────────────────────┐
    │  send_email_task()    │      │  send_email_task()    │
    │  - Call SendGrid API  │      │  - Call SendGrid API  │
    │  - Send email         │      │  - Send email         │
    └───────────┬───────────┘      └───────────┬───────────┘
                │                              │
                ▼ API Call                     ▼ API Call
          ┌──────────────┐              ┌──────────────┐
          │  SendGrid    │              │  SendGrid    │
          │  /mail/send  │              │  /mail/send  │
          └───────┬──────┘              └───────┬──────┘
                  │                             │
                  ▼ Returns msgid               ▼ Returns msgid
          ┌──────────────────┐          ┌──────────────────┐
          │  MongoDB Update  │          │  MongoDB Update  │
          │  EmailLog:       │          │  EmailLog:       │
          │  status: "sent"  │          │  status: "sent"  │
          │  sent_at: now    │          │  sent_at: now    │
          │  msgid: SG-xxx   │          │  msgid: SG-xxx   │
          └──────────┬───────┘          └──────────┬───────┘
                     │                             │
                     └──────────┬──────────────────┘
                                │
                                ▼ Also Update Task
                         ┌─────────────────┐
                         │  MongoDB:Task   │
                         │  status: sent   │
                         │  updated_at: now│
                         └─────────────────┘


REAL-TIME DASHBOARD UPDATE:
┌─────────────────────────────────────────┐
│  Frontend polls /api/tasks every 5 sec  │
│  - Task status changes from pending     │
│    to completed                         │
│  - Email is now visible in UI           │
│  - Agent sees "Day 1: Sent ✓"           │
└─────────────────────────────────────────┘
```

---

## 3. DATABASE SCHEMA RELATIONSHIPS

```
┌─────────────────────────────────────────────────────────┐
│                     MONGODB                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────┐                              │
│  │    clients           │                              │
│  ├──────────────────────┤                              │
│  │ _id: ObjectId (PK)   │                              │
│  │ name: string         │                              │
│  │ email: string        │◄─────────────┐               │
│  │ phone: string        │              │               │
│  │ property_address     │              │               │
│  │ property_type        │              │               │
│  │ stage: string        │              │               │
│  │ notes: string        │              │               │
│  │ custom_fields: dict  │              │               │
│  │ created_at           │              │               │
│  │ updated_at           │              │               │
│  │ last_contacted       │              │               │
│  └──────────────────────┘              │ (Foreign Key)
│           ▲                            │
│           │ (References)               │
│           │                            │
│  ┌────────┴──────────────┐             │
│  │     tasks             │             │
│  ├───────────────────────┤             │
│  │ _id: ObjectId (PK)    │             │
│  │ client_id: ObjectId ◄─┼─────────────┘
│  │ followup_type: string │
│  │ scheduled_for: date   │
│  │ status: string        │
│  │ email_sent_id ◄───────┼─────────┐
│  │ created_at            │         │
│  │ updated_at            │         │
│  │ notes: string         │         │ (Foreign Key)
│  └───────────────────────┘         │
│           ▲                         │
│           │ (References)            │
│           │                         │
│  ┌────────┴──────────────────┐      │
│  │     email_logs            │      │
│  ├───────────────────────────┤      │
│  │ _id: ObjectId (PK)        │      │
│  │ task_id: ObjectId ◄───────┼──────┘
│  │ client_id: ObjectId       │
│  │ to_email: string          │
│  │ subject: string           │
│  │ body: string              │
│  │ status: string            │
│  │ sendgrid_message_id       │
│  │ opened_at: date           │
│  │ clicked_at: date          │
│  │ sent_at: date             │
│  │ error_message: string     │
│  │ created_at: date          │
│  └───────────────────────────┘
│                                                         │
└─────────────────────────────────────────────────────────┘

INDICES for Performance:
- clients._id (default, clustered)
- clients.email (unique, for lookups)
- tasks.client_id + tasks.scheduled_for (compound, for checking pending)
- tasks.status + tasks.scheduled_for (for filtering)
- email_logs.status + email_logs.created_at (for analytics)
```

---

## 4. REQUEST/RESPONSE CYCLE

```
┌────────────────────────────────────────────────────────────┐
│                  FRONTEND (Next.js)                        │
│  React Component: Dashboard                               │
│  Calls: useFetch('/api/tasks?status=pending')             │
└────────────────┬─────────────────────────────────────────┘
                 │ HTTP GET
                 │ Accept: application/json
                 ▼
        ┌────────────────────────────────────┐
        │  BACKEND (FastAPI)                 │
        │  Route: GET /api/tasks             │
        │  Handler: tasks.py                 │
        └────────┬─────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────┐
        │  Scheduler Service                 │
        │  get_pending_tasks(               │
        │    status="pending",               │
        │    limit=20,                       │
        │    page=1                          │
        │  )                                 │
        └────────┬─────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────┐
        │  MongoDB Query                     │
        │  db.tasks.find({                  │
        │    status: "pending",              │
        │    scheduled_for: { $lte: now }    │
        │  })                                │
        └────────┬─────────────────────────┘
                 │ Returns 5 documents
                 │
                 ▼
        ┌────────────────────────────────────┐
        │  Format Response (Pydantic)        │
        │  [                                 │
        │    {                               │
        │      _id: "...",                   │
        │      client_id: "...",             │
        │      followup_type: "Day 1",       │
        │      scheduled_for: "2025-10-30",  │
        │      status: "pending"             │
        │    },                              │
        │    ...                             │
        │  ]                                 │
        └────────┬─────────────────────────┘
                 │ HTTP 200 OK
                 │ Content-Type: application/json
                 ▼
        ┌────────────────────────────────────┐
        │  FRONTEND (React)                  │
        │  useFetch updates state            │
        │  Component re-renders with tasks   │
        │  UI displays:                      │
        │  - Day 1: John Doe (pending)       │
        │  - Day 1: Jane Smith (pending)     │
        │  ...                               │
        └────────────────────────────────────┘
```

---

## 5. DEPLOYMENT ARCHITECTURE (Production)

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
    │ (Vercel)   │          │ Proxy (VPS)    │
    │ Next.js    │          │ Port 80/443    │
    │ Deployed   │          └────────┬───────┘
    └────────────┘                   │
                        ┌────────────┴───────────┐
                        │                        │
                        ▼                        ▼
                  ┌──────────────┐       ┌──────────────┐
                  │  FastAPI     │       │  FastAPI     │
                  │  Gunicorn    │       │  Gunicorn    │
                  │  (AWS ECS    │       │  (AWS ECS    │
                  │   Task 1)    │       │   Task 2)    │
                  └──────┬───────┘       └──────┬───────┘
                         │                      │
                         └──────────┬───────────┘
                                    │
                        ┌───────────┴───────────┐
                        │                       │
                        ▼                       ▼
                  ┌──────────────┐      ┌──────────────┐
                  │ MongoDB Atlas│      │  Redis Cloud │
                  │  (Managed)   │      │  (Managed)   │
                  └──────────────┘      └──────┬───────┘
                                               │
                        ┌──────────────────────┘
                        │
        ┌───────────────┴────────────────┐
        │                                │
        ▼                                ▼
    ┌─────────────┐            ┌──────────────────┐
    │ Celery      │            │  Celery Workers  │
    │ Beat        │            │  (AWS ECS Tasks) │
    │ (Scheduler) │            │  - Generate      │
    │ (1 instance)│            │  - Send          │
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
    └──────────────┘        └────────────────┘
```

---

## 6. ERROR HANDLING & RETRY LOGIC

```
┌─────────────────────────────────────┐
│  Task: Generate Email               │
└────────────────┬────────────────────┘
                 │
                 ▼ Attempt 1
        ┌─────────────────────┐
        │ OpenAI API Call     │
        └────────┬────────────┘
                 │
         ┌───────┴────────┐
         │                │
    Success          Error
         │                │
         │ (Log: 200)     │ (Log: 500)
         │                │
         │                ▼
         │        ┌──────────────────────┐
         │        │ Retry logic:         │
         │        │ countdown = 60 * 2^0 │
         │        │ = 60 sec             │
         │        └────────┬─────────────┘
         │                 │
         │                 ▼ Wait 60 sec
         │        ┌──────────────────────┐
         │        │ Attempt 2 (Retry)    │
         │        │ max_retries=3        │
         │        └────────┬─────────────┘
         │                 │
         │         ┌───────┴────────┐
         │         │                │
         │     Success         Error (AGAIN)
         │         │                │
         │         │ (Log: 200)    │ (Log: 500)
         │         │                │
         │         │                ▼
         │         │       ┌──────────────────────┐
         │         │       │ Retry logic:         │
         │         │       │ countdown = 60 * 2^1 │
         │         │       │ = 120 sec            │
         │         │       └────────┬─────────────┘
         │         │                │
         │         │                ▼ Wait 120 sec
         │         │       ┌──────────────────────┐
         │         │       │ Attempt 3 (Retry)    │
         │         │       └────────┬─────────────┘
         │         │                │
         │         │         ┌──────┴──────┐
         │         │         │             │
         │         │     Success       Error
         │         │         │             │
         │         │         │    ┌────────┴────────────┐
         │         │         │    │ Max retries (3)     │
         │         │         │    │ FAILED              │
         │         │         │    │ - Log error         │
         │         │         │    │ - Mark task "failed"│
         │         │         │    │ - Alert admin       │
         │         │         │    └─────────────────────┘
         │         │         │
         └─────────┴─────────┴──────→ Continue to Send Email
                                      (Or fail gracefully)
```

---

## 7. SERVICE COMMUNICATION SUMMARY

| Communication | Protocol | Sync/Async | Example |
|---|---|---|---|
| Frontend ↔ Backend | HTTP REST | Sync | GET /api/clients |
| Backend → MongoDB | MongoDB protocol | Async | Motor query |
| Backend → Redis | TCP | Async | Celery publish |
| Backend → Celery | Redis | Async | Task queue |
| Worker ↔ Worker | (via Redis queue) | Async | Share results |
| Worker → OpenAI | HTTP REST | Sync (blocking) | generate_email() |
| Worker → SendGrid | HTTP REST | Sync (blocking) | send email |
| Frontend → Dashboard | WebSocket (optional) | Real-time | Live updates |

---

This completes the full data flow and architecture documentation for RealtorOS!