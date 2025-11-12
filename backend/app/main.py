"""
FastAPI application entry point for RealtorOS.

This module initializes the FastAPI app with all routes, middleware,
and configuration for the RealtorOS CRM system.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import settings
from app.api.routes import clients, tasks, emails, dashboard, agents
from app.utils.logger import setup_logging, get_logger
from contextlib import asynccontextmanager
from app.db.postgresql import init_db, close_db
from app.scheduler import start_scheduler, stop_scheduler, get_scheduler_status

logger = get_logger(__name__)

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

# CORS middleware - MUST be added before exception handlers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global exception handlers - CORS middleware will add headers automatically
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc) if settings.DEBUG else "An error occurred"}
    )

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
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

@app.get("/health/scheduler")
async def scheduler_health():
    """Scheduler health check endpoint for monitoring."""
    return get_scheduler_status()
