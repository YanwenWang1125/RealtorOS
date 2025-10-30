# MongoDB to PostgreSQL Migration Guide for RealtorOS

## 🎯 Quick Answer: What to Pass to Cursor

**Connection String Format:**
```
postgresql+asyncpg://username:password@host:port/database_name
```

**Real World Examples:**
```
# Local Development
postgresql+asyncpg://postgres:mypassword@localhost:5432/realtoros

# Docker Container
postgresql+asyncpg://postgres:mypassword@postgres:5432/realtoros

# Remote Server
postgresql+asyncpg://postgres:mypassword@db.example.com:5432/realtoros
```

---

## Connection String Breakdown

| Part | Value | Example |
|------|-------|---------|
| **Protocol** | postgresql+asyncpg:// | For async database operations |
| **Username** | Your DB user | postgres |
| **Password** | Your DB password | mypassword |
| **Host** | Where PostgreSQL runs | localhost or postgres or db.example.com |
| **Port** | PostgreSQL port | 5432 (default) |
| **Database** | Your database name | realtoros |

---

## Complete Migration Steps

### Step 1: Update requirements.txt

**Remove:**
```
motor==3.3.2
```

**Add:**
```
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.13.1
psycopg2-binary==2.9.9
```

### Step 2: Update config.py

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # FastAPI
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_TITLE: str = "RealtorOS API"
    API_VERSION: str = "0.1.0"
    
    # PostgreSQL Connection (CHANGED FROM MONGODB)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/realtoros"
    
    # Redis & Celery (unchanged)
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 500
    
    # SendGrid
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "agent@realtoros.app"
    SENDGRID_FROM_NAME: str = "RealtorOS"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Step 3: Create db/postgresql.py

Replace `db/mongodb.py` with this file:

```python
"""
PostgreSQL connection and configuration.

This module handles PostgreSQL connection, database initialization,
and provides database session management for the RealtorOS system.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager."""
    engine = None
    async_session_maker = None

db = Database()

async def init_db():
    """Initialize database connection and create tables."""
    try:
        db.engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connection before using
        )
        
        db.async_session_maker = sessionmaker(
            db.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        
        # Test the connection
        async with db.engine.begin() as conn:
            await conn.exec_driver_sql("SELECT 1")
        
        logger.info("Connected to PostgreSQL successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise

async def close_db():
    """Close database connection."""
    if db.engine:
        await db.engine.dispose()
        logger.info("Disconnected from PostgreSQL")

async def get_session() -> AsyncSession:
    """Get a database session for dependency injection."""
    async with db.async_session_maker() as session:
        yield session
```

### Step 4: Create/Update Models (models/client.py)

```python
"""
Client model for PostgreSQL and SQLAlchemy ORM.

This module defines the Client table model for storing
real estate client information in PostgreSQL.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Client(Base):
    """Client table model."""
    __tablename__ = "clients"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Client Information
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20))
    
    # Property Information
    property_address = Column(String(200), nullable=False)
    property_type = Column(String(50), nullable=False)
    stage = Column(String(50), nullable=False, index=True)
    
    # Additional Information
    notes = Column(Text)
    custom_fields = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted = Column(DateTime)
    
    # Status
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_client_stage_deleted', 'stage', 'is_deleted'),
        Index('idx_client_email_deleted', 'email', 'is_deleted'),
    )
```

### Step 5: Create/Update Models (models/task.py)

```python
"""
Task model for PostgreSQL and SQLAlchemy ORM.

This module defines the Task table model for storing
follow-up task information in PostgreSQL.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Task(Base):
    """Task table model."""
    __tablename__ = "tasks"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    email_sent_id = Column(Integer, ForeignKey("email_logs.id"))
    
    # Task Information
    followup_type = Column(String(50), nullable=False)
    scheduled_for = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), default="pending", index=True)
    priority = Column(String(20), nullable=False)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_task_client_status', 'client_id', 'status'),
        Index('idx_task_scheduled_status', 'scheduled_for', 'status'),
    )
```

### Step 6: Create/Update Models (models/email_log.py)

```python
"""
Email log model for PostgreSQL and SQLAlchemy ORM.

This module defines the EmailLog table model for storing
email sending history and tracking in PostgreSQL.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class EmailLog(Base):
    """Email log table model."""
    __tablename__ = "email_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Email Information
    to_email = Column(String(255), nullable=False)
    subject = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, index=True)
    
    # SendGrid Integration
    sendgrid_message_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    # Error Tracking
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Webhook Events
    webhook_events = Column(JSON, default=list)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_email_status_client', 'status', 'client_id'),
        Index('idx_email_sendgrid_id', 'sendgrid_message_id'),
    )
```

### Step 7: Update Services (services/crm_service.py)

```python
"""
CRM service for client management with PostgreSQL.

This module handles all client-related business logic including CRUD operations,
data validation, and client lifecycle management.
"""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.client import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse

class CRMService:
    """Service for managing client data and operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize CRM service with database session."""
        self.session = session
    
    async def create_client(self, client_data: ClientCreate) -> ClientResponse:
        """Create a new client in the database."""
        client = Client(**client_data.dict())
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return client
    
    async def get_client(self, client_id: int) -> ClientResponse:
        """Get a client by ID."""
        stmt = select(Client).where(Client.id == client_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_clients(
        self, 
        page: int = 1, 
        limit: int = 10, 
        stage: str = None
    ) -> list:
        """List clients with pagination and filtering."""
        offset = (page - 1) * limit
        stmt = select(Client).offset(offset).limit(limit)
        
        if stage:
            stmt = stmt.where(Client.stage == stage)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update_client(self, client_id: int, client_data: ClientUpdate) -> ClientResponse:
        """Update a client's information."""
        update_data = client_data.dict(exclude_unset=True)
        stmt = update(Client).where(Client.id == client_id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_client(client_id)
    
    async def delete_client(self, client_id: int) -> bool:
        """Soft delete a client."""
        stmt = update(Client).where(Client.id == client_id).values(is_deleted=True)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
    
    async def get_client_tasks(self, client_id: int) -> list:
        """Get all tasks for a specific client."""
        # Import here to avoid circular imports
        from app.models.task import Task
        stmt = select(Task).where(Task.client_id == client_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

### Step 8: Update Dependencies (api/dependencies.py)

```python
"""
API dependencies for RealtorOS with PostgreSQL.

This module provides dependency injection for services and database connections
used throughout the API routes.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgresql import get_session
from app.services.crm_service import CRMService
from app.services.scheduler_service import SchedulerService
from app.services.ai_agent import AIAgent
from app.services.email_service import EmailService
from app.services.dashboard_service import DashboardService

async def get_crm_service(session: AsyncSession = Depends(get_session)) -> CRMService:
    """Get CRM service instance."""
    return CRMService(session)

async def get_scheduler_service(session: AsyncSession = Depends(get_session)) -> SchedulerService:
    """Get scheduler service instance."""
    return SchedulerService(session)

async def get_ai_agent() -> AIAgent:
    """Get AI agent service instance."""
    return AIAgent()

async def get_email_service(session: AsyncSession = Depends(get_session)) -> EmailService:
    """Get email service instance."""
    return EmailService(session)

async def get_dashboard_service(session: AsyncSession = Depends(get_session)) -> DashboardService:
    """Get dashboard service instance."""
    return DashboardService(session)
```

### Step 9: Update main.py

```python
"""
FastAPI application entry point for RealtorOS with PostgreSQL.

This module initializes the FastAPI app with all routes, middleware,
and configuration for the RealtorOS CRM system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.db.postgresql import init_db, close_db
from app.api.routes import clients, tasks, emails, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown."""
    # Startup
    await init_db()
    
    yield
    
    # Shutdown
    await close_db()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="RealtorOS CRM API - Automated follow-up system for real estate agents",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "RealtorOS API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}
```

### Step 10: Update docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL (replaces MongoDB)
  postgres:
    image: postgres:16-alpine
    container_name: realtoros-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: realtoros
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - realtoros-network

  # Redis (unchanged)
  redis:
    image: redis:7-alpine
    container_name: realtoros-redis
    ports:
      - "6379:6379"
    networks:
      - realtoros-network

  # Backend API
  backend:
    build: ./backend
    container_name: realtoros-backend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:your_secure_password@postgres:5432/realtoros
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SENDGRID_API_KEY: ${SENDGRID_API_KEY}
      ENVIRONMENT: development
      DEBUG: "true"
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    networks:
      - realtoros-network

volumes:
  postgres_data:

networks:
  realtoros-network:
    driver: bridge
```

### Step 11: Update .env File

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:your_secure_password@localhost:5432/realtoros

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# OpenAI
OPENAI_API_KEY=your_openai_key

# SendGrid
SENDGRID_API_KEY=your_sendgrid_key

# App
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your_secret_key
```

---

## Query Syntax Comparison

### MongoDB → PostgreSQL

| Operation | MongoDB | PostgreSQL + SQLAlchemy |
|-----------|---------|-------------------------|
| **Insert** | `db.clients.insert_one()` | `session.add(client); session.commit()` |
| **Find One** | `db.clients.find_one({"_id": id})` | `select(Client).where(Client.id == id)` |
| **Find All** | `db.clients.find({})` | `select(Client)` |
| **Filter** | `db.clients.find({"stage": "lead"})` | `select(Client).where(Client.stage == "lead")` |
| **Update** | `db.clients.update_one({"_id": id}, {"$set": data})` | `update(Client).where(Client.id == id).values(**data)` |
| **Delete** | `db.clients.delete_one({"_id": id})` | `delete(Client).where(Client.id == id)` |
| **Pagination** | `db.clients.find().skip(10).limit(10)` | `select(Client).offset(10).limit(10)` |

---

## Summary

**Connection String for PostgreSQL cursor:**

```
postgresql+asyncpg://username:password@host:port/database_name
```

**Replace in your code:**
- `MONGODB_URL` → `DATABASE_URL`
- `motor` → `sqlalchemy + asyncpg`
- `get_database()` → `get_session()`
- MongoDB queries → SQLAlchemy ORM queries
- `ObjectId` → Integer IDs

This migration provides better performance, simpler queries, and more robust data integrity compared to MongoDB.