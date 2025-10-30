"""
Tests for CRM service (SQLAlchemy + AsyncSession).
"""

import pytest
from datetime import datetime, timedelta
from app.services.crm_service import CRMService
from app.schemas.client_schema import ClientCreate, ClientUpdate
from app.models.task import Task


class TestCRMService:
    """Test cases for CRM service."""

    @pytest.mark.asyncio
    async def test_create_and_get_client(self, test_session, sample_client_data):
        service = CRMService(test_session)
        created = await service.create_client(ClientCreate(**sample_client_data))
        assert isinstance(created.id, int)
        assert created.email == sample_client_data["email"]

        fetched = await service.get_client(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    @pytest.mark.asyncio
    async def test_list_update_delete_client(self, test_session, sample_client_data):
        service = CRMService(test_session)
        # seed two clients
        await service.create_client(ClientCreate(**sample_client_data))
        other = sample_client_data.copy()
        other["email"] = "other@example.com"
        other["stage"] = "negotiating"
        c2 = await service.create_client(ClientCreate(**other))

        # list
        items = await service.list_clients(page=1, limit=10)
        assert len(items) >= 2

        # filter by stage
        filtered = await service.list_clients(stage="negotiating")
        assert any(c.id == c2.id for c in filtered)

        # update
        updated = await service.update_client(c2.id, ClientUpdate(notes="updated"))
        assert updated is not None and updated.notes == "updated"

        # delete
        ok = await service.delete_client(c2.id)
        assert ok is True
        # ensure not listed after delete
        listed = await service.list_clients()
        assert all(c.id != c2.id for c in listed)

    @pytest.mark.asyncio
    async def test_get_client_tasks(self, test_session, sample_client_data):
        service = CRMService(test_session)
        created = await service.create_client(ClientCreate(**sample_client_data))

        # add tasks directly
        t1 = Task(
            client_id=created.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high",
        )
        t2 = Task(
            client_id=created.id,
            followup_type="Week 1",
            scheduled_for=datetime.utcnow() + timedelta(days=7),
            status="pending",
            priority="medium",
        )
        test_session.add_all([t1, t2])
        await test_session.commit()

        tasks = await service.get_client_tasks(created.id)
        assert len(tasks) == 2
