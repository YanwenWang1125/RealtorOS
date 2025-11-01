"""
Celery application configuration.

This module configures the Celery application for background task processing
in the RealtorOS system.
"""

import logging
from celery import Celery
from celery.signals import setup_logging
from app.config import settings
from app.utils.logger import setup_logging as setup_app_logging, StructuredFormatter

# Initialize structured logging for the application
setup_app_logging()

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
log_level = settings.LOG_LEVEL.upper()
valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
if log_level not in valid_levels:
    log_level = "INFO"

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
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)

@setup_logging.connect
def config_celery_logging(*args, **kwargs):
    """Configure Celery to use structured logging from settings."""
    # Get the realtoros logger
    logger = logging.getLogger("realtoros")
    log_level = settings.LOG_LEVEL.upper()
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        log_level = "INFO"
    
    # Configure Celery's logger to use our structured formatter
    celery_logger = logging.getLogger("celery")
    celery_logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    for handler in celery_logger.handlers[:]:
        celery_logger.removeHandler(handler)
    
    # Add structured formatter to Celery logger
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, log_level))
    handler.setFormatter(StructuredFormatter())
    celery_logger.addHandler(handler)
    
    # Also configure task loggers
    task_logger = logging.getLogger("celery.task")
    task_logger.setLevel(getattr(logging, log_level))
    task_logger.addHandler(handler)

# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    "process-due-tasks": {
        "task": "app.tasks.periodic.process_due_tasks",
        "schedule": 60.0,  # Run every minute
    },
}
