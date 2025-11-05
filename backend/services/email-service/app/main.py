"""
FastAPI application entry point for Email Service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from shared.db.postgresql import init_db, close_db
from shared.utils.logger import setup_logging
from .api.routes.emails import router as emails_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(
    title="RealtorOS Email Service",
    version="1.0.0",
    description="Email service for RealtorOS",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(emails_router, prefix="/api/emails", tags=["emails"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "email-service"}

