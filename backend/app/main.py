"""
FastAPI application entry point for RealtorOS.

This module initializes the FastAPI app with all routes, middleware,
and configuration for the RealtorOS CRM system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import clients, tasks, emails, dashboard

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="RealtorOS CRM API - Automated follow-up system for real estate agents"
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
