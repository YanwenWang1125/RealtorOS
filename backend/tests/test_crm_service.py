"""
Tests for CRM service (SQLAlchemy + AsyncSession).
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path so we can import app
# This works when running directly with python or with pytest
backend_dir = Path(__file__).resolve().parent.parent
backend_dir_str = str(backend_dir)  # Already resolved, convert to string

# Add both the backend directory and parent directory to path
if backend_dir_str not in sys.path:
    sys.path.insert(0, backend_dir_str)

# Also add current working directory if it's different
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

# Verify we can import app module
try:
    import app
except ImportError as e:
    raise ImportError(
        f"Cannot import 'app' module. Backend dir: {backend_dir_str}, "
        f"Python path: {sys.path[:3]}, Error: {e}"
    ) from e

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

    @pytest.mark.asyncio
    async def test_create_client_with_custom_fields(self, test_session):
        """Test creating a client with custom fields for additional metadata."""
        service = CRMService(test_session)
        client_data = {
            "name": "Custom Fields Client",
            "email": "custom@example.com",
            "phone": "+1-555-9999",
            "property_address": "456 Custom St, City, ST 54321",
            "property_type": "commercial",
            "stage": "lead",
            "notes": "Client with custom metadata",
            "custom_fields": {
                "budget_range": "500k-750k",
                "preferred_contact_time": "evening",
                "referral_source": "website"
            }
        }
        created = await service.create_client(ClientCreate(**client_data))
        assert created.id is not None
        assert created.custom_fields == client_data["custom_fields"]
        assert created.custom_fields["budget_range"] == "500k-750k"

    @pytest.mark.asyncio
    async def test_get_nonexistent_client(self, test_session):
        """Test retrieving a client that doesn't exist returns None."""
        service = CRMService(test_session)
        result = await service.get_client(99999)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_client_partial_fields(self, test_session, sample_client_data):
        """Test updating only some fields of a client (partial update)."""
        service = CRMService(test_session)
        created = await service.create_client(ClientCreate(**sample_client_data))
        original_name = created.name
        original_email = created.email

        # Update only phone and stage
        update_data = ClientUpdate(phone="+1-555-9999", stage="negotiating")
        updated = await service.update_client(created.id, update_data)
        
        assert updated is not None
        assert updated.name == original_name  # Unchanged
        assert updated.email == original_email  # Unchanged
        assert updated.phone == "+1-555-9999"  # Changed
        assert updated.stage == "negotiating"  # Changed

    @pytest.mark.asyncio
    async def test_update_nonexistent_client(self, test_session):
        """Test updating a client that doesn't exist returns None."""
        service = CRMService(test_session)
        update_data = ClientUpdate(notes="This won't work")
        result = await service.update_client(99999, update_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_list_clients_pagination(self, test_session, sample_client_data):
        """Test listing clients with pagination (page and limit)."""
        service = CRMService(test_session)
        
        # Create 5 clients
        for i in range(5):
            client_data = sample_client_data.copy()
            client_data["email"] = f"client{i}@example.com"
            client_data["name"] = f"Client {i}"
            await service.create_client(ClientCreate(**client_data))

        # First page with limit 2
        page1 = await service.list_clients(page=1, limit=2)
        assert len(page1) == 2

        # Second page with limit 2
        page2 = await service.list_clients(page=2, limit=2)
        assert len(page2) == 2

        # Third page should have remaining clients
        page3 = await service.list_clients(page=3, limit=2)
        assert len(page3) >= 1

        # Verify no duplicate clients across pages
        all_ids = [c.id for c in page1 + page2 + page3]
        assert len(all_ids) == len(set(all_ids))  # No duplicates

    @pytest.mark.asyncio
    async def test_list_clients_filter_by_stage(self, test_session, sample_client_data):
        """Test filtering clients by different stages."""
        service = CRMService(test_session)
        
        # Create clients in different stages
        stages = ["lead", "negotiating", "under_contract", "closed", "lost"]
        created_clients = {}
        
        for stage in stages:
            client_data = sample_client_data.copy()
            client_data["email"] = f"{stage}@example.com"
            client_data["stage"] = stage
            created = await service.create_client(ClientCreate(**client_data))
            created_clients[stage] = created.id

        # Filter by each stage
        for stage in stages:
            filtered = await service.list_clients(stage=stage)
            assert len(filtered) >= 1
            assert all(c.stage == stage for c in filtered)
            assert created_clients[stage] in [c.id for c in filtered]

    @pytest.mark.asyncio
    async def test_delete_client_soft_delete(self, test_session, sample_client_data):
        """Test that delete_client performs soft delete (sets is_deleted flag)."""
        service = CRMService(test_session)
        created = await service.create_client(ClientCreate(**sample_client_data))
        client_id = created.id

        # Delete the client
        result = await service.delete_client(client_id)
        assert result is True

        # Client should still exist in database but marked as deleted
        # get_client should return None for deleted clients (based on soft delete logic)
        # But let's verify it's not in the list
        listed = await service.list_clients()
        assert client_id not in [c.id for c in listed]

    @pytest.mark.asyncio
    async def test_delete_nonexistent_client(self, test_session):
        """Test deleting a client that doesn't exist returns False."""
        service = CRMService(test_session)
        result = await service.delete_client(99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_client_tasks_multiple_statuses(self, test_session, sample_client_data):
        """Test retrieving tasks for a client with tasks in different statuses."""
        service = CRMService(test_session)
        created = await service.create_client(ClientCreate(**sample_client_data))

        # Create tasks with different statuses and priorities
        tasks_data = [
            {"followup_type": "Day 1", "status": "pending", "priority": "high", "days_offset": 1},
            {"followup_type": "Week 1", "status": "completed", "priority": "medium", "days_offset": 7},
            {"followup_type": "Week 2", "status": "pending", "priority": "low", "days_offset": 14},
            {"followup_type": "Month 1", "status": "cancelled", "priority": "low", "days_offset": 30},
        ]

        for task_info in tasks_data:
            task = Task(
                client_id=created.id,
                followup_type=task_info["followup_type"],
                scheduled_for=datetime.utcnow() + timedelta(days=task_info["days_offset"]),
                status=task_info["status"],
                priority=task_info["priority"],
                notes=f"Task for {task_info['followup_type']}"
            )
            test_session.add(task)
        await test_session.commit()

        # Retrieve all tasks
        tasks = await service.get_client_tasks(created.id)
        assert len(tasks) == 4

        # Verify task data structure
        for task in tasks:
            assert "id" in task
            assert "followup_type" in task
            assert "scheduled_for" in task
            assert "status" in task
            assert "priority" in task

        # Verify specific tasks exist
        followup_types = [t["followup_type"] for t in tasks]
        assert "Day 1" in followup_types
        assert "Week 1" in followup_types
        assert "Week 2" in followup_types
        assert "Month 1" in followup_types

    @pytest.mark.asyncio
    async def test_update_client_all_fields(self, test_session, sample_client_data):
        """Test updating all fields of a client."""
        service = CRMService(test_session)
        created = await service.create_client(ClientCreate(**sample_client_data))

        # Update all fields
        update_data = ClientUpdate(
            name="Updated Name",
            email="updated@example.com",
            phone="+1-555-UPDATED",
            property_address="789 Updated St, New City, ST 99999",
            property_type="land",
            stage="under_contract",
            notes="Updated notes",
            custom_fields={"new_field": "new_value"}
        )
        updated = await service.update_client(created.id, update_data)

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.email == "updated@example.com"
        assert updated.phone == "+1-555-UPDATED"
        assert updated.property_address == "789 Updated St, New City, ST 99999"
        assert updated.property_type == "land"
        assert updated.stage == "under_contract"
        assert updated.notes == "Updated notes"
        assert updated.custom_fields == {"new_field": "new_value"}


if __name__ == "__main__":
    # Allow running tests directly with: python tests/test_crm_service.py
    # But recommended: pytest tests/test_crm_service.py
    pytest.main([__file__, "-v"])
