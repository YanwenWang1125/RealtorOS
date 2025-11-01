"""
Tests for Scheduler service (SQLAlchemy + AsyncSession).
"""

import pytest
from datetime import datetime, timedelta, timezone
from app.services.scheduler_service import SchedulerService
from app.schemas.task_schema import TaskCreate, TaskUpdate


class TestSchedulerService:
    """Test cases for scheduler service."""

    @pytest.mark.asyncio
    async def test_create_list_get_update_task(self, test_session):
        svc = SchedulerService(test_session)
        # create task
        tc = TaskCreate(
            client_id=1,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high",
            notes="note",
        )
        created = await svc.create_task(tc)
        assert isinstance(created.id, int)
        assert created.status == "pending"

        # list
        listed = await svc.list_tasks(client_id=1)
        assert any(t.id == created.id for t in listed)

        # get
        got = await svc.get_task(created.id)
        assert got is not None and got.id == created.id

        # update
        updated = await svc.update_task(created.id, TaskUpdate(status="completed"))
        assert updated is not None and updated.status == "completed"

    @pytest.mark.asyncio
    async def test_get_due_and_reschedule(self, test_session):
        svc = SchedulerService(test_session)
        past = TaskCreate(
            client_id=2,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) - timedelta(hours=1),
            priority="medium",
        )
        created = await svc.create_task(past)
        due = await svc.get_due_tasks()
        assert any(t.id == created.id for t in due)

        new_date = datetime.now(timezone.utc) + timedelta(days=2)
        res = await svc.reschedule_task(created.id, new_date)
        assert res is not None and res.scheduled_for == new_date
