"""
FastAPI application entry point for Auth Service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from shared.db.postgresql import init_db, close_db
from shared.utils.logger import setup_logging
from .api.routes.auth import router

# Initialize structured logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="RealtorOS Auth Service",
    version="1.0.0",
    description="Authentication service for RealtorOS",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "RealtorOS Auth Service",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "auth-service"}

