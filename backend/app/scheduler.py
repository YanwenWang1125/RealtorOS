"""
APScheduler integration for RealtorOS.

This module replaces Celery Beat for periodic task scheduling.
Uses APScheduler to run background jobs within the FastAPI process.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import datetime

logger = logging.getLogger(__name__)

# Configure APScheduler
jobstores = {
    'default': MemoryJobStore()
}
executors = {
    'default': AsyncIOExecutor()
}
job_defaults = {
    'coalesce': True,          # Combine missed runs into one
    'max_instances': 1,        # Only one instance of each job at a time
    'misfire_grace_time': 60   # Allow 60s grace period for missed jobs
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone='UTC'
)

# Import here to avoid circular dependencies
async def process_due_tasks_job():
    """
    Process all tasks that are due for execution.

    This job runs every 60 seconds and processes tasks where:
    - scheduled_for <= now
    - status = 'pending'

    For each task, it:
    1. Fetches client and agent information
    2. Generates personalized email using AI
    3. Sends email via Amazon SES
    4. Marks task as completed
    """
    from app.db.postgresql import SessionLocal, init_db
    from app.services.scheduler_service import SchedulerService

    try:
        # Ensure database is initialized
        if SessionLocal is None:
            await init_db()
        
        # Create a new database session for this job
        async with SessionLocal() as session:
            svc = SchedulerService(session)
            count = await svc.process_and_send_due_emails()

            if count > 0:
                logger.info(f"✅ Processed {count} due task(s) and sent follow-up emails")
            else:
                logger.debug("No due tasks to process in this cycle")

            return count

    except Exception as e:
        logger.error(f"❌ Error in process_due_tasks_job: {str(e)}", exc_info=True)
        # Don't re-raise - let scheduler continue running
        return 0

def start_scheduler():
    """
    Initialize and start the APScheduler.

    Registers all periodic jobs and starts the scheduler.
    Called during FastAPI application startup.
    """
    try:
        # Register periodic jobs
        scheduler.add_job(
            process_due_tasks_job,
            trigger=IntervalTrigger(seconds=60),
            id='process_due_tasks',
            name='Process due tasks and send automated follow-up emails',
            replace_existing=True,
            next_run_time=datetime.now()  # Run immediately on startup
        )

        # Future: Add more jobs as needed
        # scheduler.add_job(
        #     cleanup_old_tasks_job,
        #     trigger=CronTrigger(hour=2, minute=0),  # Daily at 2 AM
        #     id='cleanup_old_tasks',
        #     name='Clean up old completed tasks',
        #     replace_existing=True
        # )

        scheduler.start()
        logger.info("🚀 APScheduler started successfully")
        logger.info(f"📋 Registered jobs: {[job.id for job in scheduler.get_jobs()]}")

    except Exception as e:
        logger.error(f"❌ Failed to start APScheduler: {str(e)}", exc_info=True)
        raise

def stop_scheduler():
    """
    Gracefully shutdown the APScheduler.

    Called during FastAPI application shutdown.
    Waits for running jobs to complete before stopping.
    """
    try:
        if scheduler.running:
            scheduler.shutdown(wait=True)  # Wait for jobs to finish
            logger.info("🛑 APScheduler stopped gracefully")
        else:
            logger.warning("APScheduler was not running")

    except Exception as e:
        logger.error(f"❌ Error stopping APScheduler: {str(e)}", exc_info=True)

def get_scheduler_status():
    """
    Get current scheduler status and job information.

    Returns:
        dict: Scheduler state, running jobs, and next execution times
    """
    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job in scheduler.get_jobs()
        ]
    }

