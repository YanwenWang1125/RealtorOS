# RealtorOS - AI-Powered CRM for Real Estate Agents

> **An intelligent CRM system that automates client follow-ups, generates personalized emails using AI, and tracks email engagement in real-time.**

RealtorOS helps real estate agents never miss a follow-up by automatically scheduling tasks, generating personalized emails with OpenAI, sending them via AWS SES, and tracking engagement through secure webhooks. Built with tenant isolation and multi-agent support.

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
9. [Development Guide](#-development-guide)
10. [Testing](#-testing)
11. [Deployment](#-deployment)
12. [Troubleshooting](#-troubleshooting)
13. [Roadmap](#-roadmap)

---

## ✨ Key Features

- 🏠 **Complete Client Management** - Full CRUD operations with pipeline stages (lead → closed)
- 🤖 **AI-Powered Email Generation** - Personalized follow-up emails using OpenAI GPT models
- ⏰ **Automated Follow-Up System** - Intelligent scheduling with predefined sequences (Day 1, Day 3, Week 1, Week 2, Month 1)
- 📧 **Email Automation** - AWS SES integration with real-time engagement tracking
- 📊 **Dashboard Analytics** - KPIs, open rates, click rates, conversion metrics (tenant-scoped)
- 🔒 **Secure Authentication** - JWT-based authentication with Google OAuth support
- 🎯 **Task Management** - Track, reschedule, and manage follow-up tasks
- 📈 **Real-Time Updates** - Live engagement tracking (opens, clicks, bounces, deliveries)
- 👥 **Multi-Agent Support** - Tenant isolation with agent-scoped data and operations
- 🔐 **Tenant Scoping** - All operations are scoped by agent_id for data security

---

## 🏗️ Architecture

### Tech Stack

**Backend (FastAPI + Python)**
- **FastAPI** - Modern, async web framework with automatic OpenAPI documentation
- **PostgreSQL** - Production-grade relational database with SQLAlchemy ORM
- **APScheduler** - In-process task scheduling for automated follow-ups
- **OpenAI API** - AI-powered email content generation (GPT-3.5/GPT-4)
- **AWS SES** - Reliable email delivery via boto3
- **Alembic** - Database migrations and version control
- **JWT** - Token-based authentication
- **Google OAuth** - Social authentication support

**Frontend (Next.js + React)**
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling framework
- **TanStack Query (React Query)** - Data fetching and caching
- **Axios** - HTTP client for API communication
- **TipTap** - Rich text editor for email composition
- **Radix UI** - Accessible component primitives

**Infrastructure**
- **Docker & Docker Compose** - Containerization and orchestration
- **PostgreSQL** - Relational database (production-ready)

### Service Architecture

```
Frontend (Next.js) → FastAPI Backend → PostgreSQL
                          ↓
                    APScheduler (in-process)
                          ↓
              OpenAI API | AWS SES
```

### Key Services

1. **CRM Service** - Client data operations (CRUD) with agent scoping
2. **Scheduler Service** - Follow-up scheduling and task management
3. **AI Agent Service** - OpenAI email generation
4. **Email Service** - AWS SES integration and email logging (async, non-blocking)
5. **Dashboard Service** - Analytics and KPI aggregation (agent-scoped)
6. **Agent Service** - Authentication and agent management

### Tenant Isolation

All operations are scoped by `agent_id` to ensure:
- Data isolation between agents
- Secure multi-tenant architecture
- Proper authorization checks
- Scoped dashboard statistics

---

## 📁 Project Structure

```
realtoros/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes and dependencies
│   │   │   └── routes/     # Endpoint handlers (clients, tasks, emails, dashboard, agents)
│   │   ├── services/       # Business logic services
│   │   │   ├── crm_service.py          # Client management
│   │   │   ├── scheduler_service.py    # Task & follow-up automation
│   │   │   ├── email_service.py        # Email logging & sending (async)
│   │   │   ├── ai_agent.py             # OpenAI email generation
│   │   │   ├── dashboard_service.py    # Analytics & KPIs (agent-scoped)
│   │   │   └── agent_service.py       # Agent management & auth
│   │   ├── models/         # SQLAlchemy ORM models
│   │   │   ├── client.py   # Client model (with agent_id)
│   │   │   ├── task.py     # Task model (with agent_id)
│   │   │   ├── email_log.py # EmailLog model (with agent_id)
│   │   │   └── agent.py    # Agent model
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── scheduler.py    # APScheduler configuration
│   │   ├── db/             # Database configuration
│   │   │   └── postgresql.py   # Async PostgreSQL setup
│   │   ├── utils/          # Utility functions
│   │   │   ├── auth.py     # JWT authentication
│   │   │   ├── google_oauth.py  # Google OAuth integration
│   │   │   └── logger.py
│   │   ├── config.py       # Configuration & settings
│   │   └── main.py        # FastAPI application
│   ├── alembic/            # Database migrations
│   ├── tests/              # Unit and integration tests
│   │   ├── unit/           # Unit tests
│   │   ├── integration/    # Integration tests
│   │   └── fixtures/       # Test fixtures
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container config
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/     # React components
│   │   ├── lib/           # Utility libraries
│   │   │   ├── api/       # API client & endpoints
│   │   │   ├── hooks/     # Custom React hooks
│   │   │   ├── types/     # TypeScript types
│   │   │   ├── utils/     # Utility functions
│   │   │   └── constants/ # Constants
│   │   ├── providers/     # Context providers
│   │   └── styles/        # CSS and styling
│   ├── package.json       # Node.js dependencies
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

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd realtoros
   ```

2. **Set up environment variables**
   
   Create `backend/.env` file:
   ```bash
   # Copy from example if available, or create new
   # Edit backend/.env with your configuration
   ```
   
   Required variables (see [Configuration](#-configuration) section):
   - `DATABASE_URL` - PostgreSQL connection string
   - `OPENAI_API_KEY` - OpenAI API key for email generation
   - `AWS_REGION` - AWS region for SES
   - `AWS_ACCESS_KEY_ID` - AWS access key for SES
   - `AWS_SECRET_ACCESS_KEY` - AWS secret key for SES
   - `SES_FROM_EMAIL` - Verified sender email in SES
   - `SES_FROM_NAME` - Display name for emails
   - `SECRET_KEY` - Secret key for JWT encryption (minimum 32 characters)
   - `GOOGLE_CLIENT_ID` - Google OAuth client ID (optional)
   - `GOOGLE_CLIENT_SECRET` - Google OAuth client secret (optional)

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
   - FastAPI backend (http://localhost:8000)
   - Next.js frontend (http://localhost:3000)
   - APScheduler runs in-process with FastAPI

2. **Run database migrations**
   ```bash
   docker exec realtoros-backend alembic upgrade head
   ```

3. **Create initial agent** (required for authentication)
   ```bash
   docker exec realtoros-backend python -m app.db.ensure_agent
   ```

4. **Seed demo data (optional)**
   ```bash
   docker exec realtoros-backend python -m app.db.seed
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation (Swagger): http://localhost:8000/docs
   - API Documentation (ReDoc): http://localhost:8000/redoc

6. **View logs**
   ```bash
   docker-compose logs -f backend
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
   
   # Create initial agent
   python -m app.db.ensure_agent
   
   # Start server (APScheduler runs in-process)
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

# OpenAI (for email generation)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=500

# Amazon SES (for email delivery)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
SES_FROM_EMAIL=agent@yourdomain.com
SES_FROM_NAME=Your Real Estate Team

# Authentication
SECRET_KEY=your-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
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

### Database Schema

**Agents Table**
- `id` (Primary Key)
- `email` (unique, indexed)
- `name`, `password_hash`
- `is_active`, `created_at`, `updated_at`

**Clients Table**
- `id` (Primary Key)
- `agent_id` (Foreign Key → agents.id, indexed for tenant scoping)
- `name`, `email` (indexed), `phone`
- `property_address`, `property_type`
- `stage` (lead, negotiating, under_contract, closed, lost)
- `notes`, `custom_fields` (JSON)
- `created_at`, `updated_at`, `last_contacted`
- `is_deleted` (soft delete flag)

**Tasks Table**
- `id` (Primary Key)
- `agent_id` (Foreign Key → agents.id, indexed for tenant scoping)
- `client_id` (Foreign Key → clients.id)
- `email_sent_id` (Foreign Key → email_logs.id, optional)
- `followup_type` (Day 1, Day 3, Week 1, Week 2, Month 1, Custom)
- `scheduled_for` (timestamp, indexed, timezone-aware)
- `status` (pending, completed, skipped, cancelled)
- `priority` (high, medium, low)
- `notes`, `email_preview` (JSON), `created_at`, `updated_at`, `completed_at`

**Email Logs Table**
- `id` (Primary Key)
- `agent_id` (Foreign Key → agents.id, indexed for tenant scoping)
- `task_id` (Foreign Key → tasks.id)
- `client_id` (Foreign Key → clients.id, indexed)
- `to_email`, `subject`, `body`
- `from_name`, `from_email`
- `status` (queued, sent, delivered, opened, clicked, bounced, failed, etc.)
- `ses_message_id` (indexed for webhook lookups)
- `created_at`, `sent_at`, `opened_at`, `clicked_at`
- `error_message`, `webhook_events` (JSON array)

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

### Authentication

All API endpoints (except `/api/auth/*`) require JWT authentication:
- Include `Authorization: Bearer <token>` header
- Tokens expire after 30 minutes (configurable)
- Google OAuth supported for login

### Key Endpoints

#### Authentication
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/google` - Login with Google OAuth
- `POST /api/auth/register` - Register new agent
- `GET /api/auth/me` - Get current agent info

#### Clients
- `GET /api/clients` - List clients (agent-scoped, with pagination & filtering)
- `POST /api/clients` - Create new client (auto-creates follow-up tasks)
- `GET /api/clients/{id}` - Get client details
- `PATCH /api/clients/{id}` - Update client information
- `DELETE /api/clients/{id}` - Soft delete client
- `GET /api/clients/{id}/tasks` - Get all tasks for a client

#### Tasks
- `GET /api/tasks` - List tasks (agent-scoped, with pagination & filtering)
- `POST /api/tasks` - Manually create a new task
- `GET /api/tasks/{id}` - Get task details
- `PATCH /api/tasks/{id}` - Update task (status, schedule, notes, priority, email_preview)
- `POST /api/tasks/{id}/reschedule` - Reschedule a task

#### Emails
- `GET /api/emails` - List email history (agent-scoped, with pagination & filtering)
- `GET /api/emails/{id}` - Get email details (with engagement data)
- `POST /api/emails/preview` - Preview AI-generated email (no send)
- `POST /api/emails/send` - Generate and send email

#### Dashboard
- `GET /api/dashboard/stats` - Get dashboard KPIs and statistics (agent-scoped)
- `GET /api/dashboard/recent-activity` - Get recent activity feed

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
- **All operations are agent-scoped** for tenant isolation

### Task & Follow-Up Automation

**Automated Task Creation**
When a new client is created, the system automatically creates 5 follow-up tasks:
- **Day 1** (High Priority): 1 day after client creation
- **Day 3** (Medium Priority): 3 days after
- **Week 1** (Medium Priority): 7 days after
- **Week 2** (Low Priority): 14 days after
- **Month 1** (Low Priority): 30 days after

**Task Management**
- View all tasks with pagination (agent-scoped)
- Filter by status (pending, completed, skipped, cancelled) or client
- Reschedule tasks
- Update priority and notes
- Manual task creation
- Automatic status update to "completed" after email send
- Email preview storage in task record

**Automated Processing**
- APScheduler runs every 60 seconds
- Processes all due tasks automatically
- Generates AI emails and sends via AWS SES
- Updates task and email status

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
- Store preview in task record
- Edit before sending
- No email log created on preview

**Fallback Templates**
- Automatic fallback if OpenAI API fails
- Ensures email delivery even during API issues

### Email Management & Tracking

**AWS SES Integration**
- Reliable email delivery via boto3
- HTML email support
- Automatic message ID tracking
- **Async, non-blocking** email sending (uses `asyncio.to_thread`)

**Email Status Tracking**
- `queued` → `sent` → `delivered` → `opened` → `clicked`
- Also tracks: `bounced`, `failed`, `dropped`, `spamreport`, `deferred`
- First open and first click tracked with timestamps

**Webhook Integration** (Future)
- Secure webhook processing for engagement events
- Automatic status updates from SES events
- Full event history stored in JSON array

### Dashboard & Analytics

**KPIs and Statistics** (Agent-Scoped)
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

## 🛠️ Development Guide

### Code Style

- **Backend**: Follow PEP 8, use type hints, async/await patterns
- **Frontend**: Follow React best practices, use TypeScript strictly

### Key Implementation Details

**Tenant Scoping**
- All database queries filter by `agent_id`
- Service methods require `agent_id` parameter
- API endpoints extract `agent_id` from JWT token
- Dashboard statistics are agent-scoped

**Timezone Safety**
- All timestamps use `datetime.now(timezone.utc)` (timezone-aware)
- No naive datetime objects in production code
- Database stores UTC timestamps

**Async Email Sending**
- Email sending is non-blocking using `asyncio.to_thread`
- Prevents blocking the FastAPI event loop
- Proper error handling and logging

**Authentication**
- JWT tokens required for all API endpoints
- Google OAuth supported
- No development fallbacks (strict auth in all environments)

### Adding New Features

1. Create database model in `app/models/` (include `agent_id` for tenant scoping)
2. Create Pydantic schemas in `app/schemas/`
3. Add business logic in `app/services/` (ensure agent scoping)
4. Create API routes in `app/api/routes/` (use `get_current_agent` dependency)
5. Add tests in `tests/` (include `agent_id` in all test calls)
6. Create migration: `alembic revision --autogenerate -m "Description"`
7. Apply migration: `alembic upgrade head`

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

### Test Coverage

- **Unit Tests**: Service layer logic, utilities
- **Integration Tests**: API endpoints, database operations, workflows
- **Fixtures**: Reusable test data (agents, clients, tasks)

### Database Testing

For tests, the system uses a test PostgreSQL database configured via environment variables. All tests are properly scoped with `agent_id`.

---

## 📦 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production` and `DEBUG=false`
- [ ] Use strong `SECRET_KEY` (minimum 32 characters)
- [ ] Configure production PostgreSQL database
- [ ] Set up AWS SES (verify sender email, configure credentials)
- [ ] Configure OpenAI API key
- [ ] Configure CORS origins for production domain
- [ ] Run database migrations (`alembic upgrade head`)
- [ ] Create initial agent account
- [ ] Set up logging/monitoring (e.g., Sentry, CloudWatch)
- [ ] Configure SSL/TLS certificates
- [ ] Set up health check endpoints
- [ ] Configure backup strategy for PostgreSQL

### Deployment Platforms

#### Backend (FastAPI)
- **Platforms**: AWS ECS, DigitalOcean App Platform, Railway, Render, Fly.io, Azure Container Apps
- **Requirements**: PostgreSQL database
- **Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000` (with Gunicorn for production)
- **Note**: APScheduler runs in-process, so only one replica should run scheduled tasks

#### Frontend (Next.js)
- **Platforms**: Vercel (recommended), Netlify, AWS S3 + CloudFront
- **Build**: `npm run build`
- **Environment**: Set `NEXT_PUBLIC_API_URL` to production backend URL

#### Database
- **PostgreSQL**: AWS RDS, Supabase, DigitalOcean Managed Database, Heroku Postgres, Azure Database for PostgreSQL
- **Migrations**: Run `alembic upgrade head` on deployment

#### Email
- **AWS SES**: Configure verified sender email, set up credentials
- **Alternative**: Can migrate to Azure Communication Services Email or other providers

See [DEPLOY.md](DEPLOY.md) for detailed Azure deployment instructions.

---

## 🔍 Troubleshooting

### Common Issues

**Issue: Authentication errors**
- **Solution**: Ensure JWT token is included in `Authorization` header. Check `SECRET_KEY` is set correctly.

**Issue: Tasks not being created automatically for new clients**
- **Solution**: Ensure the client creation endpoint is calling `scheduler_service.create_followup_tasks()` with `agent_id`. Check backend logs.

**Issue: Database connection errors**
- **Solution**: Verify `DATABASE_URL` format: `postgresql+asyncpg://username:password@host:port/database_name`
- Check PostgreSQL is running and accessible
- Verify network connectivity in Docker containers

**Issue: Email sending fails**
- **Solution**: Verify AWS SES credentials are correct. Ensure sender email is verified in SES. Check AWS region matches configuration.

**Issue: Module not found errors in frontend**
- **Solution**: Run `npm install` in the frontend directory. Ensure all dependencies are installed.

**Issue: TypeScript errors in frontend**
- **Solution**: Run `npm run type-check` to identify issues. Ensure all types are properly defined in `src/lib/types/`.

---

## 🗺️ Roadmap

### ✅ Phase 1 (Completed - MVP)
- [x] Client management (CRUD operations) with tenant scoping
- [x] Automated follow-up task creation
- [x] AI-powered email generation (OpenAI)
- [x] Email sending via AWS SES (async, non-blocking)
- [x] Dashboard analytics and KPIs (agent-scoped)
- [x] Task management and scheduling (APScheduler)
- [x] JWT authentication with Google OAuth support
- [x] Multi-agent tenant isolation
- [x] Timezone-aware timestamps
- [x] Email preview functionality

### 🚧 Phase 2 (In Progress)
- [ ] AWS SES webhook integration for engagement tracking
- [ ] Advanced email analytics (charts, trends)
- [ ] Bulk operations (import clients, bulk email)
- [ ] Custom email templates
- [ ] Data export (CSV, PDF)
- [ ] Email engagement timeline visualization

### 🔮 Phase 3 (Future)
- [ ] Multi-user/team support within agent accounts
- [ ] SMS follow-ups
- [ ] Calendar integration
- [ ] Mobile application
- [ ] Advanced reporting
- [ ] Client activity timeline
- [ ] Document management
- [ ] Email A/B testing

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- All database operations must include `agent_id` for tenant scoping
- Use timezone-aware datetimes (`datetime.now(timezone.utc)`)
- Write tests for new features
- Update API documentation
- Follow existing code style

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs` and `/redoc`
- Review this README for setup and troubleshooting
- See [DEPLOY.md](DEPLOY.md) for deployment guidance

---

**Built with ❤️ for real estate professionals**

*RealtorOS helps you never miss a follow-up and build stronger relationships with your clients through automated, personalized communication!*
