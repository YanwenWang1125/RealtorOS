"""
FastAPI application entry point for RealtorOS.

This module initializes the FastAPI app with all routes, middleware,
and configuration for the RealtorOS CRM system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import clients, tasks, emails, dashboard, agents
from app.utils.logger import setup_logging
from contextlib import asynccontextmanager
from app.db.postgresql import init_db, close_db
from app.scheduler import start_scheduler, stop_scheduler, get_scheduler_status

# Initialize structured logging using LOG_LEVEL from settings
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    # Startup
    await init_db()
    start_scheduler()  # Start APScheduler
    yield
    # Shutdown
    stop_scheduler()   # Stop APScheduler
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
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

# Include webhook router (public endpoint, no /api prefix)
app.include_router(emails.webhook_router, prefix="/webhook", tags=["webhooks"])

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

@app.get("/health/scheduler")
async def scheduler_health():
    """Scheduler health check endpoint for monitoring."""
    return get_scheduler_status()
