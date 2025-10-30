# RealtorOS - Full-Stack MVP Architecture

## 1. PROJECT FOLDER STRUCTURE

```
realtoros/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Configuration & env vars
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── clients.py      # Client CRUD endpoints
│   │   │   │   ├── tasks.py        # Task/follow-up endpoints
│   │   │   │   ├── emails.py       # Email history endpoints
│   │   │   │   └── dashboard.py    # Analytics/dashboard endpoints
│   │   │   └── dependencies.py     # Auth, DB session injection
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── crm_service.py      # Client data operations
│   │   │   ├── scheduler_service.py # Follow-up scheduling logic
│   │   │   ├── ai_agent.py         # OpenAI integration
│   │   │   └── email_service.py    # SendGrid integration
│   │   │
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py       # Celery config
│   │   │   ├── email_tasks.py      # Celery tasks: generate & send emails
│   │   │   ├── scheduler_tasks.py  # Celery tasks: create follow-ups
│   │   │   └── periodic.py         # Periodic tasks (beat scheduler)
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── client.py           # MongoDB Client schema
│   │   │   ├── task.py             # MongoDB Task schema
│   │   │   └── email_log.py        # MongoDB Email log schema
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── client_schema.py    # Pydantic validation for clients
│   │   │   ├── task_schema.py      # Pydantic validation for tasks
│   │   │   └── email_schema.py     # Pydantic validation for emails
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── mongodb.py          # MongoDB connection & session
│   │   │   └── seed.py             # Demo data seeding
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py           # Structured logging
│   │   │   └── decorators.py       # Custom decorators
│   │   │
│   │   └── constants/
│   │       ├── __init__.py
│   │       ├── followup_schedules.py # Day 1, Day 3, Week 1, Month 1, etc.
│   │       └── email_templates.py  # Email prompt templates
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py             # Pytest fixtures
│   │   ├── test_crm_service.py
│   │   ├── test_scheduler_service.py
│   │   ├── test_ai_agent.py
│   │   └── test_email_service.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml          # For local dev (shared with frontend)
│
├── frontend/
│   ├── public/
│   │   ├── favicon.ico
│   │   └── realtoros-logo.png
│   │
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          # Root layout
│   │   │   ├── page.tsx            # Dashboard home
│   │   │   ├── globals.css         # Global styles
│   │   │   │
│   │   │   ├── clients/
│   │   │   │   ├── page.tsx        # Clients list view
│   │   │   │   ├── [id]/
│   │   │   │   │   ├── page.tsx    # Client detail & edit
│   │   │   │   │   └── tasks/
│   │   │   │   │       └── page.tsx # Client-specific tasks
│   │   │   │   └── new/
│   │   │   │       └── page.tsx    # Create new client
│   │   │   │
│   │   │   ├── tasks/
│   │   │   │   ├── page.tsx        # All tasks/follow-ups view
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx    # Task detail
│   │   │   │
│   │   │   ├── emails/
│   │   │   │   └── page.tsx        # Email history & logs
│   │   │   │
│   │   │   └── api/
│   │   │       └── [...nextauth].ts # NextAuth for future auth
│   │   │
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ClientCard.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   ├── ClientForm.tsx
│   │   │   ├── EmailPreview.tsx
│   │   │   ├── DashboardStats.tsx
│   │   │   └── Modal.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useClients.ts       # SWR/React Query: fetch clients
│   │   │   ├── useTasks.ts         # SWR/React Query: fetch tasks
│   │   │   ├── useEmails.ts        # SWR/React Query: fetch email logs
│   │   │   └── useApi.ts           # Generic API hook
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts              # Axios/fetch client
│   │   │   ├── utils.ts            # Helper functions
│   │   │   └── constants.ts        # Frontend constants
│   │   │
│   │   ├── styles/
│   │   │   ├── colors.css
│   │   │   ├── typography.css
│   │   │   └── components.css
│   │   │
│   │   └── types/
│   │       ├── index.ts            # Shared TypeScript types
│   │       ├── client.ts
│   │       ├── task.ts
│   │       └── email.ts
│   │
│   ├── .env.example
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── .gitignore
├── .dockerignore
├── docker-compose.yml              # Main orchestration file
├── README.md
└── ARCHITECTURE.md                 # This file

```

---

## 2. RECOMMENDED TECH STACK

### Backend
- **FastAPI** (0.109+): Async Python web framework, auto OpenAPI docs
- **MongoDB** (6.0+): NoSQL database for flexible CRM data
- **Celery** (5.3+): Distributed task queue for async jobs
- **Redis** (7.0+): Message broker & cache
- **Python** (3.11+): Main language
- **Pydantic** (v2): Data validation & serialization
- **Motor**: Async MongoDB driver
- **python-dotenv**: Environment variable management

### Frontend
- **Next.js** (14+): React framework with SSR/SSG
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui** or **Ant Design**: Component library
- **SWR** or **React Query**: Data fetching & caching
- **Axios**: HTTP client
- **React Hook Form**: Form management
- **date-fns**: Date manipulation

### DevOps & Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Local orchestration
- **Redis**: In-memory store for Celery
- **MongoDB Atlas** (production) or local MongoDB

### External APIs
- **OpenAI API**: GPT-4/3.5-Turbo for email generation
- **SendGrid API**: Email delivery service

---

## 3. SERVICE BOUNDARIES & RESPONSIBILITIES

### A. CRM Service (`crm_service.py`)
**Responsibilities:**
- Create, read, update, delete clients
- Manage client properties (name, email, phone, property info, stage)
- Track client interactions (notes, last contact)
- Retrieve client list with filters & pagination

**Endpoints:**
```
POST   /api/clients              # Create client
GET    /api/clients              # List clients (with pagination)
GET    /api/clients/{id}         # Get client detail
PATCH  /api/clients/{id}         # Update client
DELETE /api/clients/{id}         # Soft delete client
GET    /api/clients/{id}/tasks   # Get client's tasks
```

**Database Model:**
```python
Client:
  - id: ObjectId
  - name: str
  - email: str
  - phone: str
  - property_address: str
  - property_type: str (e.g., "residential", "commercial")
  - stage: str (e.g., "lead", "negotiating", "closed")
  - notes: str
  - created_at: datetime
  - updated_at: datetime
  - last_contacted: datetime
  - custom_fields: dict
```

---

### B. Scheduler Service (`scheduler_service.py`)
**Responsibilities:**
- Define follow-up schedules (Day 1, Day 3, Week 1, Month 1, etc.)
- Create tasks on client creation
- Reschedule tasks based on agent interaction
- Determine which clients need follow-ups

**Constants (followup_schedules.py):**
```python
FOLLOWUP_SCHEDULE = {
    "Day 1": {"days": 1, "priority": "high"},
    "Day 3": {"days": 3, "priority": "medium"},
    "Week 1": {"days": 7, "priority": "medium"},
    "Week 2": {"days": 14, "priority": "low"},
    "Month 1": {"days": 30, "priority": "low"},
}
```

**Endpoints:**
```
GET    /api/tasks                # List all tasks (filtered)
GET    /api/tasks/{id}           # Get task detail
PATCH  /api/tasks/{id}           # Mark task complete / reschedule
POST   /api/tasks                # Manually create task
```

**Database Model:**
```python
Task:
  - id: ObjectId
  - client_id: ObjectId (reference)
  - followup_type: str (e.g., "Day 1", "Week 1")
  - scheduled_for: datetime
  - status: str (e.g., "pending", "completed", "skipped")
  - email_sent_id: ObjectId (reference to EmailLog) - nullable
  - created_at: datetime
  - updated_at: datetime
  - notes: str
```

---

### C. AI Agent (`ai_agent.py`)
**Responsibilities:**
- Take client data + task context
- Construct prompt for OpenAI
- Generate personalized email copy
- Cache results (optional)
- Handle API errors & retries

**Endpoints:**
```
POST   /api/emails/preview       # Generate & preview email
POST   /api/emails/send          # Generate & queue for sending
```

**Function Signature:**
```python
async def generate_email(
    client: ClientModel,
    task: TaskModel,
    agent_instructions: str = None
) -> dict:
    # Returns: {"subject": str, "body": str, "preview": str}
```

**Prompt Template Example:**
```
You are a friendly, professional real estate agent following up with a client.

Client Profile:
- Name: {client.name}
- Property: {client.property_address}
- Stage: {client.stage}
- Last Note: {client.notes}

Follow-up Type: {task.followup_type}
Current Date: {today}

Generate a personalized, concise email (under 200 words) that:
1. References their property or interest
2. Provides value or next steps
3. Encourages a response

Format: {"subject": "...", "body": "..."}
```

---

### D. Email Service (`email_service.py`)
**Responsibilities:**
- Queue emails via Celery
- Send via SendGrid API
- Log all sends (success, failure, bounce)
- Track opens & clicks (webhook integration)

**Celery Tasks:**
```python
@celery_app.task(bind=True, max_retries=3)
async def send_email_task(
    self,
    email_log_id: str,
    to_email: str,
    subject: str,
    body: str
):
    # Attempt send, retry on failure
    # Update EmailLog with status

@celery_app.task
async def process_sendgrid_webhook(event_type, email_log_id):
    # Handle opens, clicks, bounces
```

**Database Model:**
```python
EmailLog:
  - id: ObjectId
  - task_id: ObjectId (reference)
  - client_id: ObjectId (reference)
  - to_email: str
  - subject: str
  - body: str
  - status: str (e.g., "queued", "sent", "failed", "bounced")
  - sendgrid_message_id: str
  - opened_at: datetime - nullable
  - clicked_at: datetime - nullable
  - created_at: datetime
  - sent_at: datetime - nullable
  - error_message: str - nullable
```

---

## 4. INTEGRATION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                         │
│  Dashboard | Clients List | Tasks | Email History              │
└───────────────────┬─────────────────────────────────────────────┘
                    │ HTTP/REST
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│  Routes: /api/clients, /api/tasks, /api/emails                │
└──┬──────────────────────────────────────────────────────────────┘
   │
   ├─────────────────────────────────────────┐
   │                                         │
   ▼                                         ▼
┌──────────────┐                    ┌──────────────────┐
│   MongoDB    │                    │  Redis + Celery  │
│              │                    │   Task Queue     │
│ - Clients    │                    │                  │
│ - Tasks      │                    │ Workers:         │
│ - EmailLogs  │                    │ - Generate Email │
│              │                    │ - Send Email     │
│              │                    │ - Schedule Tasks │
└──────────────┘                    └────────┬─────────┘
                                             │
                                             ▼
                                   ┌──────────────────┐
                                   │   OpenAI API     │
                                   │   Generate Email │
                                   └──────────────────┘
                                             │
                                             ▼
                                   ┌──────────────────┐
                                   │  SendGrid API    │
                                   │  Send Email      │
                                   └──────────────────┘
```

### Typical Flow: New Client → Automatic Follow-ups

1. **Agent creates client** via dashboard
   - Frontend: POST /api/clients
   - Backend: CRM Service stores client in MongoDB

2. **Scheduler triggers** (on client creation)
   - FastAPI route calls `scheduler_service.create_followup_tasks(client_id)`
   - Creates 5 Task records in MongoDB (Day 1, Day 3, Week 1, Week 2, Month 1)

3. **Celery Beat** (periodic scheduler)
   - Every minute, checks for tasks with `scheduled_for <= now` and `status == "pending"`
   - Enqueues `generate_and_send_email_task` for each

4. **Celery Worker: Generate Email**
   - Fetches Client + Task from MongoDB
   - Calls `ai_agent.generate_email(client, task)`
   - OpenAI generates personalized copy
   - Stores preview in cache (Redis)

5. **Celery Worker: Send Email**
   - Calls `email_service.send_via_sendgrid(email_log)`
   - SendGrid API sends
   - Updates EmailLog status to "sent"
   - Updates Task status to "completed"

6. **Dashboard Reflects**
   - Frontend polls /api/tasks, /api/emails
   - Agent sees "Day 1 Follow-up: Sent to john@example.com"
   - Can view email content, mark as done, or reschedule

---

## 5. ENVIRONMENT VARIABLES

### Backend (.env)

```env
# FastAPI
ENVIRONMENT=development
DEBUG=true
API_TITLE=RealtorOS API
API_VERSION=0.1.0

# MongoDB
MONGODB_URL=mongodb://mongo:27017
MONGODB_DB=realtoros

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# OpenAI
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=500

# SendGrid
SENDGRID_API_KEY=SG.xxxxx
SENDGRID_FROM_EMAIL=agent@realtoros.app
SENDGRID_FROM_NAME=RealtorOS

# Logging
LOG_LEVEL=INFO

# Security (for future)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=RealtorOS
```

---

## 6. DOCKER COMPOSE SETUP

```yaml
version: "3.9"

services:
  # MongoDB
  mongo:
    image: mongo:6.0
    container_name: realtoros-mongo
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: rootpassword
    volumes:
      - mongo_data:/data/db
    networks:
      - realtoros-network

  # Redis
  redis:
    image: redis:7.0-alpine
    container_name: realtoros-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - realtoros-network

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: realtoros-backend
    ports:
      - "8000:8000"
    environment:
      MONGODB_URL: mongodb://root:rootpassword@mongo:27017/realtoros?authSource=admin
      REDIS_URL: redis://redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SENDGRID_API_KEY: ${SENDGRID_API_KEY}
    depends_on:
      - mongo
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - realtoros-network

  # Celery Worker
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: realtoros-celery-worker
    environment:
      MONGODB_URL: mongodb://root:rootpassword@mongo:27017/realtoros?authSource=admin
      REDIS_URL: redis://redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SENDGRID_API_KEY: ${SENDGRID_API_KEY}
    depends_on:
      - mongo
      - redis
    volumes:
      - ./backend:/app
    command: celery -A app.tasks.celery_app worker --loglevel=info
    networks:
      - realtoros-network

  # Celery Beat (Scheduler)
  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: realtoros-celery-beat
    environment:
      MONGODB_URL: mongodb://root:rootpassword@mongo:27017/realtoros?authSource=admin
      REDIS_URL: redis://redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SENDGRID_API_KEY: ${SENDGRID_API_KEY}
    depends_on:
      - mongo
      - redis
    volumes:
      - ./backend:/app
    command: celery -A app.tasks.celery_app beat --loglevel=info
    networks:
      - realtoros-network

  # Next.js Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: realtoros-frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
    command: npm run dev
    networks:
      - realtoros-network

volumes:
  mongo_data:
  redis_data:

networks:
  realtoros-network:
    driver: bridge
```

---

## 7. BACKEND REQUIREMENTS.TXT

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
motor==3.3.2
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
celery==5.3.4
redis==5.0.1
requests==2.31.0
openai==1.3.8
python-sendgrid==6.10.0
pytest==7.4.3
pytest-asyncio==0.23.1
httpx==0.25.2
```

---

## 8. KEY ARCHITECTURAL DECISIONS

### Why Celery + Redis?
- **Async email generation & sending**: Don't block API responses
- **Scalability**: Add workers horizontally
- **Reliability**: Retries, dead-letter queues
- **Task persistence**: Tasks survive worker crashes

### Why MongoDB?
- **Flexibility**: CRM data varies (custom fields)
- **Schemaless**: Easy to add agent preferences, property types
- **Horizontal scaling**: Built-in sharding support

### Why FastAPI?
- **Performance**: Async-first, fast startup
- **Developer experience**: Auto OpenAPI/Swagger docs
- **Validation**: Pydantic integration
- **Type hints**: Better IDE support

### Why Next.js?
- **SSR/SSG**: Better SEO, performance
- **Full-stack**: Can add API routes for auth
- **TypeScript**: Type safety across stack
- **Deployment**: Easy to Vercel, Docker

---

## 9. DEPLOYMENT CONSIDERATIONS

### Production MongoDB
- Use **MongoDB Atlas** (managed cloud)
- Enable auth, backups, monitoring
- Connection string: `mongodb+srv://user:pass@cluster.mongodb.net/realtoros`

### Production Redis
- Use **Redis Cloud** or **AWS ElastiCache**
- Enable persistence, encryption
- Backup regularly

### Production FastAPI
- Deploy to **AWS ECS**, **DigitalOcean App Platform**, or **Railway.app**
- Use **Gunicorn** with Uvicorn workers: `gunicorn -k uvicorn.workers.UvicornWorker app.main:app`
- Enable CORS properly for frontend domain

### Production Frontend
- Deploy to **Vercel** (native Next.js) or **AWS CloudFront + S3**
- Set `NEXT_PUBLIC_API_URL` to production backend
- Enable CI/CD via GitHub Actions

### Monitoring & Logging
- **Sentry**: Error tracking (backend + frontend)
- **DataDog** or **New Relic**: APM
- **ELK Stack**: Centralized logging
- **Celery Flower**: Monitor Celery tasks

---

## 10. MVP SCOPE & ROADMAP

### Phase 1 (Week 1-2): MVP Core
- [x] Client CRUD
- [x] Basic task scheduling
- [x] Email generation (OpenAI)
- [x] Email sending (SendGrid)
- [x] Simple dashboard

### Phase 2 (Week 3-4): Polish
- [ ] Email analytics (opens, clicks)
- [ ] Task rescheduling
- [ ] Bulk actions
- [ ] Export to CSV
- [ ] Search & filters

### Phase 3 (Future): Scale
- [ ] Authentication (NextAuth + OAuth)
- [ ] Multi-user support (teams)
- [ ] Custom templates
- [ ] SMS follow-ups
- [ ] Calendar integration
- [ ] Mobile app (React Native)

---

## 11. LOCAL DEVELOPMENT QUICKSTART

```bash
# Clone repo
git clone <repo>
cd realtoros

# Set up env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Start services
docker-compose up -d

# Seed demo data (in another terminal)
docker exec realtoros-backend python -m app.db.seed

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Swagger Docs: http://localhost:8000/docs

# Watch logs
docker-compose logs -f backend celery_worker
```

---

## 12. API ENDPOINT SUMMARY

### Clients
```
POST   /api/clients              Create client
GET    /api/clients?page=1       List clients
GET    /api/clients/{id}         Get client
PATCH  /api/clients/{id}         Update client
DELETE /api/clients/{id}         Delete client
```

### Tasks / Follow-ups
```
GET    /api/tasks?status=pending List tasks
GET    /api/tasks/{id}           Get task
PATCH  /api/tasks/{id}           Mark complete / reschedule
```

### Emails
```
GET    /api/emails?client_id={id} Email history
POST   /api/emails/preview       Preview generated email
POST   /api/emails/send          Send email manually
```

### Dashboard
```
GET    /api/dashboard/stats      Get KPIs (clients, tasks, emails)
```

---

This architecture is production-ready, scalable, and follows industry best practices. Start building! 🚀
