# RealtorOS - AI-Powered CRM for Real Estate Agents

> **An intelligent CRM system that automates client follow-ups, generates personalized emails using AI, and tracks email engagement in real-time.**

RealtorOS helps real estate agents never miss a follow-up by automatically scheduling tasks, generating personalized emails with OpenAI, sending them via SendGrid, and tracking opens, clicks, and engagement through secure webhooks.

---

## Table of Contents

1. [Key Features](#-key-features)
2. [Architecture](#-architecture)
3. [Project Structure](#-project-structure)
4. [Quick Start](#-quick-start)
5. [Configuration](#-configuration)
6. [Database Setup](#-database-setup)
7. [API Documentation](#-api-documentation)
8. [Features & Capabilities](#-features--capabilities)
9. [Data Flow & System Design](#-data-flow--system-design)
10. [Development Guide](#-development-guide)
11. [Testing](#-testing)
12. [Deployment](#-deployment)
13. [Troubleshooting](#-troubleshooting)
14. [Roadmap](#-roadmap)

---

## ✨ Key Features

- 🏠 **Complete Client Management** - Full CRUD operations with pipeline stages (lead → closed)
- 🤖 **AI-Powered Email Generation** - Personalized follow-up emails using OpenAI GPT models
- ⏰ **Automated Follow-Up System** - Intelligent scheduling with predefined sequences (Day 1, Day 3, Week 1, Week 2, Month 1)
- 📧 **Email Automation** - SendGrid integration with real-time engagement tracking
- 📊 **Dashboard Analytics** - KPIs, open rates, click rates, conversion metrics
- 🔒 **Secure Webhook Processing** - ECDSA signature verification for SendGrid webhooks
- 🎯 **Task Management** - Track, reschedule, and manage follow-up tasks
- 📈 **Real-Time Updates** - Live engagement tracking (opens, clicks, bounces, deliveries)

---

## 🏗️ Architecture

### Tech Stack

**Backend (FastAPI + Python)**
- **FastAPI** - Modern, async web framework with automatic OpenAPI documentation
- **PostgreSQL** - Production-grade relational database with SQLAlchemy ORM
- **Celery + Redis** - Asynchronous task processing and message queuing
- **OpenAI API** - AI-powered email content generation (GPT-3.5/GPT-4)
- **SendGrid** - Reliable email delivery with webhook engagement tracking
- **Alembic** - Database migrations and version control

**Frontend (Next.js + React)**
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling framework
- **TanStack Query (React Query)** - Data fetching and caching
- **Axios** - HTTP client for API communication
- **TipTap** - Rich text editor for email composition

**Infrastructure**
- **Docker & Docker Compose** - Containerization and orchestration
- **PostgreSQL** - Relational database (production-ready)
- **Redis** - Message broker and cache for Celery

### Service Architecture

```
Frontend (Next.js) → FastAPI Backend → PostgreSQL
                          ↓
                    Celery Workers
                          ↓
              OpenAI API | SendGrid API
                          ↓
                  SendGrid Webhooks → FastAPI
```

### Key Services

1. **CRM Service** - Client data operations (CRUD)
2. **Scheduler Service** - Follow-up scheduling and task management
3. **AI Agent Service** - OpenAI email generation
4. **Email Service** - SendGrid integration and email logging
5. **Dashboard Service** - Analytics and KPI aggregation

---

## 📁 Project Structure

```
realtoros/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes and dependencies
│   │   │   └── routes/     # Endpoint handlers (clients, tasks, emails, dashboard)
│   │   ├── services/       # Business logic services
│   │   │   ├── crm_service.py          # Client management
│   │   │   ├── scheduler_service.py    # Task & follow-up automation
│   │   │   ├── email_service.py        # Email logging & sending
│   │   │   ├── ai_agent.py             # OpenAI email generation
│   │   │   └── dashboard_service.py    # Analytics & KPIs
│   │   ├── models/         # SQLAlchemy ORM models
│   │   │   ├── client.py   # Client model
│   │   │   ├── task.py     # Task model
│   │   │   └── email_log.py # EmailLog model
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── tasks/          # Celery task definitions
│   │   │   ├── celery_app.py    # Celery configuration
│   │   │   ├── scheduler_tasks.py
│   │   │   ├── email_tasks.py
│   │   │   └── periodic.py      # Scheduled tasks (Celery Beat)
│   │   ├── db/             # Database configuration
│   │   │   └── postgresql.py   # Async PostgreSQL setup
│   │   ├── utils/          # Utility functions
│   │   │   ├── webhook_security.py  # ECDSA signature verification
│   │   │   └── logger.py
│   │   ├── constants/      # Application constants
│   │   │   └── followup_schedules.py
│   │   ├── config.py       # Configuration & settings
│   │   └── main.py        # FastAPI application
│   ├── alembic/            # Database migrations
│   ├── tests/              # Unit and integration tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container config
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/     # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utility libraries
│   │   ├── styles/        # CSS and styling
│   │   └── types/         # TypeScript type definitions
│   ├── package.json       # Node.js dependencies
│   ├── package-lock.json  # Locked dependency versions (DO NOT DELETE)
│   └── Dockerfile         # Frontend container config
├── docker-compose.yml     # Multi-container orchestration
└── README.md             # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker and Docker Compose** (recommended)
- **Node.js 18+** (for local frontend development)
- **Python 3.11+** (for local backend development)
- **PostgreSQL 16+** (if running locally)
- **Redis 7+** (if running locally)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd realtoros
   ```

2. **Set up environment variables**
   
   Create `backend/.env` file:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```
   
   Required variables (see [Configuration](#-configuration) section):
   - `DATABASE_URL` - PostgreSQL connection string
   - `OPENAI_API_KEY` - OpenAI API key for email generation
   - `SENDGRID_API_KEY` - SendGrid API key for email delivery
   - `SENDGRID_WEBHOOK_VERIFICATION_KEY` - SendGrid webhook public key (optional in development)
   - `SECRET_KEY` - Secret key for encryption/JWT

3. **Create `frontend/.env.local`** (if developing frontend locally)
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Docker Development (Recommended)

1. **Start all services**
   ```bash
   docker-compose up -d
   ```
   
   This starts:
   - PostgreSQL database
   - Redis cache/queue
   - FastAPI backend (http://localhost:8000)
   - Next.js frontend (http://localhost:3000)
   - Celery worker (background tasks)
   - Celery Beat (scheduled tasks)

2. **Run database migrations**
   ```bash
   docker exec realtoros-backend alembic upgrade head
   ```

3. **Seed demo data (optional)**
   ```bash
   docker exec realtoros-backend python -m app.db.seed
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation (Swagger): http://localhost:8000/docs
   - API Documentation (ReDoc): http://localhost:8000/redoc

5. **View logs**
   ```bash
   docker-compose logs -f backend celery_worker celery_beat
   ```

### Local Development

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Run migrations
   alembic upgrade head
   
   # Start server
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Start supporting services** (Docker)
   ```bash
   # PostgreSQL
   docker run -d -p 5432:5432 \
     -e POSTGRES_PASSWORD=dev_password \
     -e POSTGRES_DB=realtoros \
     --name postgres postgres:16-alpine
   
   # Redis
   docker run -d -p 6379:6379 \
     --name redis redis:7.0-alpine
   ```

4. **Start Celery workers** (separate terminal)
   ```bash
   cd backend
   source venv/bin/activate
   celery -A app.tasks.celery_app worker --loglevel=info
   ```

5. **Start Celery Beat** (separate terminal)
   ```bash
   cd backend
   source venv/bin/activate
   celery -A app.tasks.celery_app beat --loglevel=info
   ```

---

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```env
# FastAPI
ENVIRONMENT=development
DEBUG=true
API_TITLE=RealtorOS API
API_VERSION=1.0.0

# PostgreSQL Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/realtoros

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# OpenAI (for email generation)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=500

# SendGrid (for email delivery)
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=agent@yourdomain.com
SENDGRID_FROM_NAME=Your Real Estate Team
SENDGRID_WEBHOOK_VERIFICATION_KEY=-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----
# Note: SENDGRID_WEBHOOK_VERIFICATION_KEY is optional in development

# Logging
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Connection String Format:**
```
postgresql+asyncpg://username:password@host:port/database_name
```

**Examples:**
- Local: `postgresql+asyncpg://postgres:mypassword@localhost:5432/realtoros`
- Docker: `postgresql+asyncpg://postgres:mypassword@postgres:5432/realtoros`
- Remote: `postgresql+asyncpg://postgres:mypassword@db.example.com:5432/realtoros`

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 💾 Database Setup

### PostgreSQL Connection

The system uses **PostgreSQL** with **SQLAlchemy ORM** and **asyncpg** driver for async operations.

**Connection String Components:**
| Part | Value | Example |
|------|-------|---------|
| **Protocol** | postgresql+asyncpg:// | For async database operations |
| **Username** | Your DB user | postgres |
| **Password** | Your DB password | mypassword |
| **Host** | Where PostgreSQL runs | localhost or postgres or db.example.com |
| **Port** | PostgreSQL port | 5432 (default) |
| **Database** | Your database name | realtoros |

### Database Schema

**Clients Table**
- `id` (Primary Key)
- `name`, `email` (unique, indexed), `phone`
- `property_address`, `property_type`
- `stage` (lead, negotiating, under_contract, closed, lost)
- `notes`, `custom_fields` (JSON)
- `created_at`, `updated_at`, `last_contacted`
- `is_deleted` (soft delete flag)

**Tasks Table**
- `id` (Primary Key)
- `client_id` (Foreign Key → clients.id)
- `email_sent_id` (Foreign Key → email_logs.id, optional)
- `followup_type` (Day 1, Day 3, Week 1, Week 2, Month 1, Custom)
- `scheduled_for` (timestamp, indexed)
- `status` (pending, completed, skipped, cancelled)
- `priority` (high, medium, low)
- `notes`, `created_at`, `updated_at`, `completed_at`

**Email Logs Table**
- `id` (Primary Key)
- `task_id` (Foreign Key → tasks.id)
- `client_id` (Foreign Key → clients.id, indexed)
- `to_email`, `subject`, `body`
- `status` (queued, sent, delivered, opened, clicked, bounced, failed, etc.)
- `sendgrid_message_id` (indexed for webhook lookups)
- `created_at`, `sent_at`, `opened_at`, `clicked_at`
- `error_message`, `retry_count`
- `webhook_events` (JSON array of all webhook events)

### Database Migrations

RealtorOS uses **Alembic** for database migrations.

**Create a new migration:**
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback migration:**
```bash
alembic downgrade -1
```

---

## 📚 API Documentation

The API documentation is automatically generated using FastAPI's OpenAPI integration:

- **Swagger UI**: http://localhost:8000/docs (interactive API explorer)
- **ReDoc**: http://localhost:8000/redoc (beautiful API documentation)

### Key Endpoints

#### Clients
- `GET /api/clients` - List clients (with pagination & filtering by stage)
- `POST /api/clients` - Create new client (auto-creates follow-up tasks)
- `GET /api/clients/{id}` - Get client details
- `PATCH /api/clients/{id}` - Update client information
- `DELETE /api/clients/{id}` - Soft delete client
- `GET /api/clients/{id}/tasks` - Get all tasks for a client

#### Tasks
- `GET /api/tasks` - List tasks (with pagination & filtering by status/client)
- `POST /api/tasks` - Manually create a new task
- `GET /api/tasks/{id}` - Get task details
- `PATCH /api/tasks/{id}` - Update task (status, schedule, notes, priority)

#### Emails
- `GET /api/emails` - List email history (with pagination & filtering)
- `GET /api/emails/{id}` - Get email details (with engagement data)
- `POST /api/emails/preview` - Preview AI-generated email (no send)
- `POST /api/emails/send` - Generate and send email

#### Dashboard
- `GET /api/dashboard/stats` - Get dashboard KPIs and statistics
- `GET /api/dashboard/recent-activity` - Get recent activity feed

#### Webhooks (Public Endpoint)
- `POST /webhook/sendgrid` - SendGrid webhook endpoint (signature verified)
- `GET /webhook/sendgrid/test` - Test endpoint to verify webhook accessibility

---

## 🎯 Features & Capabilities

### Client Management

**Complete CRUD Operations**
- Create, read, update, and soft-delete clients
- Pipeline stages: `lead`, `negotiating`, `under_contract`, `closed`, `lost`
- Filter by stage, search by email
- Pagination support (default 10 per page, up to 100)
- Custom fields (JSON) for flexible data tracking
- Full audit trail with timestamps

**Client Data Fields**
- Basic: name, email (unique), phone
- Property: address, type (residential, commercial, land, other)
- Pipeline: stage, notes, custom fields
- Timestamps: created_at, updated_at, last_contacted

### Task & Follow-Up Automation

**Automated Task Creation**
When a new client is created, the system automatically creates 5 follow-up tasks:
- **Day 1** (High Priority): 1 day after client creation
- **Day 3** (Medium Priority): 3 days after
- **Week 1** (Medium Priority): 7 days after
- **Week 2** (Low Priority): 14 days after
- **Month 1** (Low Priority): 30 days after

**Task Management**
- View all tasks with pagination
- Filter by status (pending, completed, skipped, cancelled) or client
- Reschedule tasks
- Update priority and notes
- Manual task creation
- Automatic status update to "completed" after email send

### AI-Powered Email Generation

**OpenAI Integration**
- Uses GPT-3.5-turbo or GPT-4 (configurable)
- Async processing for fast generation
- Configurable max tokens

**Personalization**
- Client-specific content (name, property, stage, notes)
- Follow-up context awareness (Day 1 vs Month 1)
- Dynamic prompt engineering based on timing
- Custom instructions support (up to 500 characters)

**Email Preview**
- Preview AI-generated emails before sending
- No email log created on preview
- Edit before sending

**Fallback Templates**
- Automatic fallback if OpenAI API fails
- Ensures email delivery even during API issues

### Email Management & Tracking

**SendGrid Integration**
- Reliable email delivery
- HTML email support
- Automatic message ID tracking

**Email Status Tracking**
- `queued` → `sent` → `delivered` → `opened` → `clicked`
- Also tracks: `bounced`, `failed`, `dropped`, `spamreport`, `deferred`
- First open and first click tracked with timestamps

**Webhook Integration**
- Secure ECDSA signature verification
- Timestamp validation (10-minute window, replay attack protection)
- Automatic status updates from SendGrid events
- Full event history stored in JSON array

### Dashboard & Analytics

**KPIs and Statistics**
- Client metrics: Total, Active (lead/negotiating/under_contract)
- Task metrics: Pending, Completed
- Email activity: Sent today, Sent this week
- Engagement: Open rate, Click rate, Conversion rate

**Pipeline Metrics**
- Stage distribution counts
- Active vs total clients

**Recent Activity Feed**
- Email sent events
- Client and task information
- Timestamp tracking

---

## 🔄 Data Flow & System Design

### New Client Creation Flow

1. Agent creates client via Frontend → POST `/api/clients`
2. Backend creates client in PostgreSQL
3. System **synchronously** creates 5 follow-up tasks
4. Tasks stored in PostgreSQL with scheduled dates
5. Frontend receives client data response

**Key Points:**
- Client creation is **synchronous** (immediate response)
- Follow-up task creation happens **immediately** (not via Celery)
- All timestamps in UTC (timezone-aware)

### Automated Email Follow-Up Flow

**Celery Beat Schedule:** Every 60 seconds

1. **Celery Beat** triggers `process_due_tasks`
2. **Scheduler Service** queries PostgreSQL for due tasks:
   - `scheduled_for <= NOW()`
   - `status = 'pending'`
3. **For each due task:**
   - Fetch client information
   - Generate email via **AI Agent** (OpenAI API)
   - Log email in `email_logs` table (status: `queued`)
   - Send email via **SendGrid API**
   - Update email log (status: `sent`, `sendgrid_message_id`, `sent_at`)
   - Update task (status: `completed`, `email_sent_id`, `completed_at`)
4. Continue processing all due tasks

**Error Handling:**
- Individual task failures don't stop processing
- Fallback email template if OpenAI fails
- Database rollbacks for failed tasks
- Comprehensive logging

### SendGrid Webhook Engagement Flow

1. **SendGrid** sends HTTP POST to `/webhook/sendgrid`
   - Headers: ECDSA signature, timestamp
   - Body: Array of event objects

2. **Backend** verifies signature:
   - Extract signature and timestamp
   - Verify ECDSA signature using public key
   - Validate timestamp (< 10 minutes old)

3. **For each event:**
   - Find `EmailLog` by `sendgrid_message_id`
   - Update status based on event type:
     - `open` → Set `opened_at` (first open only)
     - `click` → Set `clicked_at` (first click only)
   - Append event to `webhook_events` JSON array
   - Update email status

4. **Response:** Always returns 200 OK (to prevent SendGrid retries)

**Key Points:**
- ECDSA signature verification required (bypassed in development mode if no signature)
- Idempotent processing (can handle duplicate events)
- Full event history preserved
- Timestamp validation prevents replay attacks

### Database Relationships

```
clients (1) ──→ (N) tasks
tasks (1) ──→ (1) email_logs
clients (1) ──→ (N) email_logs
```

**Indexes for Performance:**
- `clients`: `stage`, `email`, `is_deleted` (composite indexes)
- `tasks`: `client_id`, `status`, `scheduled_for` (composite indexes)
- `email_logs`: `status`, `client_id`, `sendgrid_message_id`

---

## 🛠️ Development Guide

### Code Style

- **Backend**: Follow PEP 8, use type hints, async/await patterns
- **Frontend**: Follow React best practices, use TypeScript strictly

### Adding New Features

1. Create database model in `app/models/`
2. Create Pydantic schemas in `app/schemas/`
3. Add business logic in `app/services/`
4. Create API routes in `app/api/routes/`
5. Add tests in `tests/`
6. Create migration: `alembic revision --autogenerate -m "Description"`
7. Apply migration: `alembic upgrade head`

### SendGrid Webhook Setup

For **local development**, use **ngrok** to expose your local server:

1. **Install ngrok**
   ```bash
   # Download from https://ngrok.com/download
   # Or use: brew install ngrok / choco install ngrok
   ```

2. **Start ngrok tunnel**
   ```bash
   ngrok http 8000
   # Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
   ```

3. **Configure SendGrid Webhook**
   - Go to SendGrid Dashboard → Settings → Mail Settings → Event Webhook
   - Set HTTP POST URL: `https://abc123.ngrok.io/webhook/sendgrid`
   - Enable events: Delivered, Opened, Clicked, Bounced, Dropped, Spam Reports
   - Copy the verification key (ECDSA public key) to `SENDGRID_WEBHOOK_VERIFICATION_KEY`

4. **Test webhook**
   ```bash
   curl https://abc123.ngrok.io/webhook/sendgrid/test
   # Should return: {"status": "ok", "message": "Webhook endpoint is accessible"}
   ```

**Note:** In development mode, signature verification is bypassed if no signature is provided. In production, always use proper signature verification.

---

## 🧪 Testing

### Backend Tests

Run all tests:
```bash
cd backend
pytest
```

Run specific test categories:
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Specific test file
pytest tests/unit/services/test_email_service.py -v
```

### Database Testing

For tests, the system uses an in-memory SQLite database or a test PostgreSQL database configured via environment variables.

---

## 📦 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production` and `DEBUG=false`
- [ ] Use strong `SECRET_KEY` (minimum 32 characters)
- [ ] Configure production PostgreSQL database
- [ ] Set up Redis for Celery
- [ ] Configure SendGrid webhook URL (public HTTPS URL)
- [ ] Set up SendGrid webhook verification key
- [ ] Configure CORS origins for production domain
- [ ] Run database migrations (`alembic upgrade head`)
- [ ] Set up logging/monitoring (e.g., Sentry, CloudWatch)
- [ ] Configure SSL/TLS certificates
- [ ] Set up health check endpoints
- [ ] Configure backup strategy for PostgreSQL

### Deployment Platforms

#### Backend (FastAPI)
- **Platforms**: AWS ECS, DigitalOcean App Platform, Railway, Render, Fly.io
- **Requirements**: PostgreSQL database, Redis instance
- **Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000` (with Gunicorn for production)

#### Frontend (Next.js)
- **Platforms**: Vercel (recommended), Netlify, AWS S3 + CloudFront
- **Build**: `npm run build`
- **Environment**: Set `NEXT_PUBLIC_API_URL` to production backend URL

#### Database
- **PostgreSQL**: AWS RDS, Supabase, DigitalOcean Managed Database, Heroku Postgres
- **Migrations**: Run `alembic upgrade head` on deployment

#### Redis
- **Providers**: Redis Cloud, AWS ElastiCache, DigitalOcean Managed Redis
- **Usage**: Celery broker and result backend

#### Celery Workers
- **Deployment**: Same platform as backend or separate worker containers
- **Command**: `celery -A app.tasks.celery_app worker --loglevel=info`
- **Scaling**: Run multiple workers for parallel processing

#### Celery Beat
- **Deployment**: Single instance (required for scheduling)
- **Command**: `celery -A app.tasks.celery_app beat --loglevel=info`

---

## 🔍 Troubleshooting

### Common Issues

**Issue: SendGrid webhooks not received in local development**
- **Solution**: Use ngrok to expose local server to SendGrid. See [SendGrid Webhook Setup](#sendgrid-webhook-setup)

**Issue: Tasks not being created automatically for new clients**
- **Solution**: Ensure the client creation endpoint is calling `scheduler_service.create_followup_tasks()` synchronously. Check backend logs.

**Issue: Email engagement timeline showing nothing**
- **Solution**: Ensure `sent_at` timestamp is set when email is sent. Check `email_service.py` - should refresh email_log after updating status.

**Issue: Module not found errors (e.g., @tiptap/react)**
- **Solution**: Run `npm install` in the frontend directory. Ensure `package-lock.json` is committed to version control.

**Issue: SSR/Hydration errors with TipTap editor**
- **Solution**: Set `immediatelyRender: false` in `useEditor` hook configuration.

**Issue: Database connection errors**
- **Solution**: Verify `DATABASE_URL` format: `postgresql+asyncpg://username:password@host:port/database_name`
- Check PostgreSQL is running and accessible
- Verify network connectivity in Docker containers

---

## 🗺️ Roadmap

### ✅ Phase 1 (Completed)
- [x] Client management (CRUD operations)
- [x] Automated follow-up task creation
- [x] AI-powered email generation (OpenAI)
- [x] Email sending via SendGrid
- [x] Email engagement tracking (webhooks)
- [x] Dashboard analytics and KPIs
- [x] Secure webhook signature verification
- [x] Task management and scheduling

### 🚧 Phase 2 (In Progress)
- [ ] User authentication and authorization
- [ ] Advanced email analytics (charts, trends)
- [ ] Bulk operations (import clients, bulk email)
- [ ] Custom email templates
- [ ] Data export (CSV, PDF)

### 🔮 Phase 3 (Future)
- [ ] Multi-user/team support
- [ ] SMS follow-ups
- [ ] Calendar integration
- [ ] Mobile application
- [ ] Advanced reporting
- [ ] Client activity timeline
- [ ] Document management

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs` and `/redoc`
- Review this README for setup and troubleshooting

---

**Built with ❤️ for real estate professionals**

*RealtorOS helps you never miss a follow-up and build stronger relationships with your clients through automated, personalized communication!*
