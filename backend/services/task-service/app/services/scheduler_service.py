"""
Scheduler service for task and follow-up management (SQLAlchemy).
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.task import Task
from shared.models.client import Client
from shared.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from ..constants.followup_schedules import FOLLOWUP_SCHEDULE

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.followup_schedule = FOLLOWUP_SCHEDULE

    def _as_aware_utc(self, dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        # Ensure timezone-aware UTC
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)

    def _to_response(self, task: Task) -> TaskResponse:
        return TaskResponse(
            id=task.id,
            agent_id=task.agent_id,
            client_id=task.client_id,
            followup_type=task.followup_type,
            scheduled_for=self._as_aware_utc(task.scheduled_for),
            status=task.status,
            priority=task.priority,
            notes=task.notes,
            created_at=self._as_aware_utc(task.created_at),
            updated_at=self._as_aware_utc(task.updated_at),
            completed_at=self._as_aware_utc(task.completed_at),
            email_sent_id=task.email_sent_id,
        )

    async def create_followup_tasks(self, client_id: int, agent_id: int) -> List[TaskResponse]:
        now = datetime.now(timezone.utc)
        created: List[Task] = []
        # FOLLOWUP_SCHEDULE is a dict keyed by label {label: {days, priority, ...}}
        for label, cfg in self.followup_schedule.items():
            scheduled_for = now + timedelta(days=cfg.get("days", 0))
            task = Task(
                agent_id=agent_id,
                client_id=client_id,
                followup_type=label,
                scheduled_for=scheduled_for,
                status="pending",
                priority=cfg.get("priority", "medium"),
            )
            self.session.add(task)
            created.append(task)
        await self.session.commit()
        for t in created:
            await self.session.refresh(t)
        return [self._to_response(t) for t in created]

    async def get_task(self, task_id: int, agent_id: int) -> Optional[TaskResponse]:
        stmt = select(Task).where(Task.id == task_id, Task.agent_id == agent_id)
        result = await self.session.execute(stmt)
        task = result.scalar_one_or_none()
        if task is None:
            return None
        return self._to_response(task)

    async def list_tasks(self, agent_id: int, page: int = 1, limit: int = 10, status: Optional[str] = None, client_id: Optional[int] = None) -> List[TaskResponse]:
        offset = (page - 1) * limit
        stmt = select(Task).where(Task.agent_id == agent_id)
        if status:
            stmt = stmt.where(Task.status == status)
        if client_id:
            stmt = stmt.where(Task.client_id == client_id)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        return [self._to_response(t) for t in tasks]

    async def update_task(self, task_id: int, task_data: TaskUpdate, agent_id: int) -> Optional[TaskResponse]:
        update_data = task_data.model_dump(exclude_unset=True)
        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.agent_id == agent_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_task(task_id, agent_id)

    async def create_task(self, task_data: TaskCreate, agent_id: int) -> TaskResponse:
        task = Task(
            agent_id=agent_id,
            client_id=task_data.client_id,
            followup_type=task_data.followup_type,
            scheduled_for=task_data.scheduled_for,
            status="pending",
            priority=task_data.priority,
            notes=task_data.notes,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return self._to_response(task)

    async def get_due_tasks(self) -> List[TaskResponse]:
        now = datetime.now(timezone.utc)
        stmt = select(Task).where(Task.scheduled_for <= now, Task.status == "pending")
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        return [self._to_response(t) for t in tasks]

    async def reschedule_task(self, task_id: int, new_date: datetime, agent_id: int) -> Optional[TaskResponse]:
        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.agent_id == agent_id)
            .values(scheduled_for=new_date)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_task(task_id, agent_id)

    async def process_and_send_due_emails(self) -> int:
        """
        Process all due tasks and send automated follow-up emails.
        This method will be called by Celery periodic tasks.
        It should communicate with email-service to send emails.
        
        Returns:
            int: Count of successfully processed tasks
        """
        now = datetime.now(timezone.utc)
        
        # Query all due tasks
        stmt = select(Task).where(
            Task.scheduled_for <= now,
            Task.status == "pending"
        )
        result = await self.session.execute(stmt)
        due_tasks = result.scalars().all()
        
        logger.info(f"Found {len(due_tasks)} due task(s) to process")
        
        if not due_tasks:
            return 0
        
        # For now, just return count - actual email sending will be handled by email-service
        # In a full microservices architecture, this would call email-service via HTTP
        success_count = 0
        
        for task in due_tasks:
            try:
                # Here you would call email-service API to send the email
                # For now, we'll just mark as processed
                logger.info(f"Processing task_id={task.id}, client_id={task.client_id}, followup_type={task.followup_type}")
                success_count += 1
            except Exception as e:
                logger.error(f"Error processing task_id={task.id}: {str(e)}", exc_info=True)
                continue
        
        logger.info(f"Processed {success_count} out of {len(due_tasks)} due task(s) successfully")
        return success_count

