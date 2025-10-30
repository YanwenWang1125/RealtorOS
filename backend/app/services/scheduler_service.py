"""
Scheduler service for task and follow-up management (SQLAlchemy).
"""

from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from app.constants.followup_schedules import FOLLOWUP_SCHEDULE


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

    async def create_followup_tasks(self, client_id: int) -> List[TaskResponse]:
        now = datetime.utcnow()
        created: List[Task] = []
        # FOLLOWUP_SCHEDULE is a dict keyed by label {label: {days, priority, ...}}
        for label, cfg in self.followup_schedule.items():
            scheduled_for = now + timedelta(days=cfg.get("days", 0))
            task = Task(
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

    async def get_task(self, task_id: int) -> Optional[TaskResponse]:
        stmt = select(Task).where(Task.id == task_id)
        result = await self.session.execute(stmt)
        task = result.scalar_one_or_none()
        if task is None:
            return None
        return self._to_response(task)

    async def list_tasks(self, page: int = 1, limit: int = 10, status: Optional[str] = None, client_id: Optional[int] = None) -> List[TaskResponse]:
        offset = (page - 1) * limit
        stmt = select(Task)
        if status:
            stmt = stmt.where(Task.status == status)
        if client_id:
            stmt = stmt.where(Task.client_id == client_id)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        return [self._to_response(t) for t in tasks]

    async def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[TaskResponse]:
        update_data = task_data.model_dump(exclude_unset=True)
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_task(task_id)

    async def create_task(self, task_data: TaskCreate) -> TaskResponse:
        task = Task(
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
        now = datetime.utcnow()
        stmt = select(Task).where(Task.scheduled_for <= now, Task.status == "pending")
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        return [self._to_response(t) for t in tasks]

    async def reschedule_task(self, task_id: int, new_date: datetime) -> Optional[TaskResponse]:
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(scheduled_for=new_date)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_task(task_id)
