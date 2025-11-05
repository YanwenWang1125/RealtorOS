"""Webhook Service for RealtorOS."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from shared.db.postgresql import init_db, close_db
from shared.utils.logger import setup_logging
from .api.routes.webhooks import webhook_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(title="RealtorOS Webhook Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(webhook_router, prefix="/webhook", tags=["webhooks"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "webhook-service"}

