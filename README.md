# RealtorOS - AI-Powered CRM for Real Estate Agents

> **An intelligent CRM system that automates client follow-ups, generates personalized emails using AI, and tracks email engagement in real-time.**

RealtorOS helps real estate agents never miss a follow-up by automatically scheduling tasks, generating personalized emails with OpenAI, sending them via SendGrid, and tracking opens, clicks, and engagement through secure webhooks.

## ✨ Key Features

- 🏠 **Complete Client Management** - Full CRUD operations with pipeline stages (lead → closed)
- 🤖 **AI-Powered Email Generation** - Personalized follow-up emails using OpenAI GPT models
- ⏰ **Automated Follow-Up System** - Intelligent scheduling with predefined sequences (Day 1, Day 3, Week 1, Week 2, Month 1)
- 📧 **Email Automation** - SendGrid integration with real-time engagement tracking
- 📊 **Dashboard Analytics** - KPIs, open rates, click rates, conversion metrics
- 🔒 **Secure Webhook Processing** - ECDSA signature verification for SendGrid webhooks
- 🎯 **Task Management** - Track, reschedule, and manage follow-up tasks
- 📈 **Real-Time Updates** - Live engagement tracking (opens, clicks, bounces, deliveries)

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **FastAPI** - Modern, async web framework with automatic OpenAPI documentation
- **PostgreSQL** - Production-grade relational database with SQLAlchemy ORM
- **Celery + Redis** - Asynchronous task processing and message queuing
- **OpenAI API** - AI-powered email content generation (GPT-3.5/GPT-4)
- **SendGrid** - Reliable email delivery with webhook engagement tracking
- **Alembic** - Database migrations and version control

### Frontend (Next.js + React)
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling framework
- **SWR** - Data fetching and caching
- **Axios** - HTTP client for API communication

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
│   │   │   ├── client_schema.py
│   │   │   ├── task_schema.py
│   │   │   ├── email_schema.py
│   │   │   ├── dashboard_schema.py
│   │   │   └── webhook_schema.py
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
│   └── Dockerfile         # Frontend container config
├── docker-compose.yml     # Multi-container orchestration
├── FEATURES.md           # Complete feature documentation
├── DataWorkFlow.md       # Data flow and architecture diagrams
└── README.md             # This file
```

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
   
   Required variables (see Configuration section below):
   - `DATABASE_URL` - PostgreSQL connection string
   - `OPENAI_API_KEY` - OpenAI API key for email generation
   - `SENDGRID_API_KEY` - SendGrid API key for email delivery
   - `SENDGRID_WEBHOOK_VERIFICATION_KEY` - SendGrid webhook public key
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

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

Required variables:

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

**SendGrid Webhook Setup:**
1. Go to SendGrid Dashboard → Settings → Mail Settings → Event Webhook
2. Set HTTP POST URL: `https://yourdomain.com/webhook/sendgrid`
3. Enable events: Delivered, Opened, Clicked, Bounced, Dropped, Spam Reports
4. Copy the verification key (ECDSA public key) to `SENDGRID_WEBHOOK_VERIFICATION_KEY`

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

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

## 📦 Deployment

### Production Docker Compose

```bash
# Use production environment variables
docker-compose -f docker-compose.prod.yml up -d
```

### Individual Service Deployment

#### Backend (FastAPI)
- **Platforms**: AWS ECS, DigitalOcean App Platform, Railway, Render, Fly.io
- **Requirements**: PostgreSQL database, Redis instance
- **Environment**: Set all required environment variables
- **Process**: Run `uvicorn app.main:app --host 0.0.0.0 --port 8000` (with Gunicorn for production)

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

### Production Checklist

- [ ] Set `ENVIRONMENT=production` and `DEBUG=false`
- [ ] Use strong `SECRET_KEY` (minimum 32 characters)
- [ ] Configure production PostgreSQL database
- [ ] Set up Redis for Celery
- [ ] Configure SendGrid webhook URL
- [ ] Set up SendGrid webhook verification key
- [ ] Configure CORS origins for production domain
- [ ] Run database migrations (`alembic upgrade head`)
- [ ] Set up logging/monitoring (e.g., Sentry, CloudWatch)
- [ ] Configure SSL/TLS certificates
- [ ] Set up health check endpoints
- [ ] Configure backup strategy for PostgreSQL

## 📖 Documentation

- **[FEATURES.md](FEATURES.md)** - Complete feature documentation from a realtor's perspective
- **[DataWorkFlow.md](DataWorkFlow.md)** - Data flow diagrams, architecture, and service interactions
- **API Documentation** - Auto-generated at `/docs` and `/redoc` endpoints

## 🔄 How It Works

1. **Add a Client**: When you create a client, the system automatically creates 5 follow-up tasks (Day 1, Day 3, Week 1, Week 2, Month 1)

2. **Automated Processing**: Celery Beat runs every minute, checking for due tasks

3. **AI Email Generation**: For each due task, the system:
   - Fetches client information
   - Generates personalized email using OpenAI
   - Sends email via SendGrid
   - Updates task status to "completed"

4. **Engagement Tracking**: SendGrid sends webhooks when emails are:
   - Delivered
   - Opened (first open tracked)
   - Clicked (first click tracked)
   - Bounced or marked as spam

5. **Dashboard Updates**: Real-time metrics update as events are received

## 🛠️ Development

### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

### Code Style

- **Backend**: Follow PEP 8, use type hints, async/await patterns
- **Frontend**: Follow React best practices, use TypeScript strictly

### Adding New Features

1. Create database model in `app/models/`
2. Create Pydantic schemas in `app/schemas/`
3. Add business logic in `app/services/`
4. Create API routes in `app/api/routes/`
5. Add tests in `tests/`
6. Create migration: `alembic revision --autogenerate`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation at `/docs`
- Review [FEATURES.md](FEATURES.md) for feature details
- Review [DataWorkFlow.md](DataWorkFlow.md) for architecture

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

**Built with ❤️ for real estate professionals**

*RealtorOS helps you never miss a follow-up and build stronger relationships with your clients through automated, personalized communication.*
