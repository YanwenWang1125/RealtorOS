"""
Celery application configuration.

This module configures the Celery application for background task processing
in the RealtorOS system.
"""

from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "realtoros",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.scheduler_tasks",
        "app.tasks.periodic"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    "process-due-tasks": {
        "task": "app.tasks.periodic.process_due_tasks",
        "schedule": 60.0,  # Run every minute
    },
}
