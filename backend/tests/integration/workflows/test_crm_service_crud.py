"""
Comprehensive CRUD tests for CRM service with real database operations.

This test file inserts actual data into the database and tests all CRUD operations
similar to how seed.py works with database connections.
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent.parent.parent
backend_dir_str = str(backend_dir)
if backend_dir_str not in sys.path:
    sys.path.insert(0, backend_dir_str)

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

try:
    import app
except ImportError as e:
    raise ImportError(
        f"Cannot import 'app' module. Backend dir: {backend_dir_str}, "
        f"Python path: {sys.path[:3]}, Error: {e}"
    ) from e

import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete
from app.db import postgresql
from app.services.crm_service import CRMService
from app.schemas.client_schema import ClientCreate, ClientUpdate
from app.models.client import Client
from app.models.task import Task
from app.models.agent import Agent


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a real database session for testing."""
    await postgresql.init_db()
    if postgresql.SessionLocal is None:
        raise RuntimeError("Database not initialized. SessionLocal is None.")
    
    async with postgresql.SessionLocal() as session:
        # Clean up before each test
        await session.execute(delete(Task))
        await session.execute(delete(Client))
        await session.commit()
        yield session
        # Clean up after each test
        await session.execute(delete(Task))
        await session.execute(delete(Client))
        await session.commit()


@pytest_asyncio.fixture
async def test_agent(db_session):
    """Create a test agent for use in tests."""
    agent = Agent(
        email="test-agent@example.com",
        name="Test Agent",
        password_hash="dummy_hash",
        is_active=True
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


@pytest_asyncio.fixture
async def crm_service(db_session):
    """Create CRMService instance with test session."""
    return CRMService(db_session)


class TestCRMCreate:
    """Test CREATE operations for CRM service."""

    @pytest.mark.asyncio
    async def test_create_client_basic(self, crm_service, test_agent):
        """Test 1: Create a basic client with required fields."""
        client_data = ClientCreate(
            name="John Doe",
            email="john.doe@example.com",
            phone="+1-555-0100",
            property_address="100 Main St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        assert created.id is not None
        assert created.name == "John Doe"
        assert created.email == "john.doe@example.com"
        assert created.stage == "lead"
        assert created.created_at is not None

    @pytest.mark.asyncio
    async def test_create_client_with_custom_fields(self, crm_service, test_agent):
        """Test 2: Create client with custom_fields metadata."""
        client_data = ClientCreate(
            name="Jane Smith",
            email="jane.smith@example.com",
            phone="+1-555-0101",
            property_address="101 Oak Ave, City, ST 12345",
            property_type="commercial",
            stage="negotiating",
            notes="Interested in office space",
            custom_fields={
                "budget": "$500k",
                "sqft_needed": 5000,
                "parking": True
            }
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        assert created.custom_fields == client_data.custom_fields
        assert created.custom_fields["budget"] == "$500k"
        assert created.custom_fields["sqft_needed"] == 5000

    @pytest.mark.asyncio
    async def test_create_client_all_stages(self, crm_service, test_agent):
        """Test 3: Create clients in all possible stages."""
        stages = ["lead", "negotiating", "under_contract", "closed", "lost"]
        created_ids = []
        
        for i, stage in enumerate(stages):
            client_data = ClientCreate(
                name=f"Client {stage}",
                email=f"{stage}@example.com",
                phone=f"+1-555-{1000+i}",
                property_address=f"{100+i} Street, City, ST 12345",
                property_type="residential",
                stage=stage
            )
            created = await crm_service.create_client(client_data, agent_id=test_agent.id)
            created_ids.append(created.id)
            assert created.stage == stage
        
        assert len(created_ids) == 5
        assert len(set(created_ids)) == 5  # All unique IDs

    @pytest.mark.asyncio
    async def test_create_client_all_property_types(self, crm_service, test_agent):
        """Test 4: Create clients with all property types."""
        property_types = ["residential", "commercial", "land", "other"]
        created_clients = []
        
        for prop_type in property_types:
            client_data = ClientCreate(
                name=f"Client {prop_type}",
                email=f"{prop_type}@example.com",
                phone="+1-555-0200",
                property_address="200 Test St, City, ST 12345",
                property_type=prop_type,
                stage="lead"
            )
            created = await crm_service.create_client(client_data, agent_id=test_agent.id)
            created_clients.append(created)
            assert created.property_type == prop_type
        
        assert len(created_clients) == 4

    @pytest.mark.asyncio
    async def test_create_multiple_clients_bulk(self, crm_service, test_agent):
        """Test 5: Create multiple clients in bulk operation."""
        clients_to_create = []
        for i in range(10):
            clients_to_create.append(ClientCreate(
                name=f"Bulk Client {i}",
                email=f"bulk{i}@example.com",
                phone=f"+1-555-{3000+i}",
                property_address=f"{300+i} Bulk St, City, ST 12345",
                property_type="residential",
                stage="lead",
                notes=f"Bulk test client number {i}"
            ))
        
        created_ids = []
        for client_data in clients_to_create:
            created = await crm_service.create_client(client_data, agent_id=test_agent.id)
            created_ids.append(created.id)
        
        assert len(created_ids) == 10
        # Verify all are retrievable
        for client_id in created_ids:
            fetched = await crm_service.get_client(client_id)
            assert fetched is not None
            assert fetched.id == client_id


class TestCRMRead:
    """Test READ operations for CRM service."""

    @pytest.mark.asyncio
    async def test_get_client_by_id(self, crm_service, test_agent):
        """Test 6: Get a specific client by ID."""
        # Create client
        client_data = ClientCreate(
            name="Get Test Client",
            email="get@example.com",
            phone="+1-555-0400",
            property_address="400 Get St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        # Retrieve it
        fetched = await crm_service.get_client(created.id)
        
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Get Test Client"
        assert fetched.email == "get@example.com"

    @pytest.mark.asyncio
    async def test_get_nonexistent_client(self, crm_service, test_agent):
        """Test 7: Attempt to get a client that doesn't exist."""
        result = await crm_service.get_client(99999)
        assert result is None

    @pytest.mark.asyncio
    async def test_list_all_clients(self, crm_service, test_agent):
        """Test 8: List all clients without filters."""
        # Create 5 clients
        for i in range(5):
            client_data = ClientCreate(
                name=f"List Client {i}",
                email=f"list{i}@example.com",
                phone=f"+1-555-{5000+i}",
                property_address=f"{500+i} List St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            await crm_service.create_client(client_data)
        
        # List all
        clients = await crm_service.list_clients()
        assert len(clients) >= 5

    @pytest.mark.asyncio
    async def test_list_clients_with_pagination(self, crm_service, test_agent):
        """Test 9: List clients with pagination."""
        # Create 15 clients
        for i in range(15):
            client_data = ClientCreate(
                name=f"Page Client {i}",
                email=f"page{i}@example.com",
                phone=f"+1-555-{6000+i}",
                property_address=f"{600+i} Page St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            await crm_service.create_client(client_data)
        
        # Test pagination
        page1 = await crm_service.list_clients(page=1, limit=5)
        page2 = await crm_service.list_clients(page=2, limit=5)
        page3 = await crm_service.list_clients(page=3, limit=5)
        
        assert len(page1) == 5
        assert len(page2) == 5
        assert len(page3) == 5
        
        # Verify no duplicates
        all_ids = [c.id for c in page1 + page2 + page3]
        assert len(all_ids) == len(set(all_ids))

    @pytest.mark.asyncio
    async def test_list_clients_filter_by_stage(self, crm_service, test_agent):
        """Test 10: List clients filtered by stage."""
        # Create clients in different stages
        stages_data = [
            ("lead", 3),
            ("negotiating", 2),
            ("under_contract", 2),
            ("closed", 1),
            ("lost", 1)
        ]
        
        created_by_stage = {}
        for stage, count in stages_data:
            created_by_stage[stage] = []
            for i in range(count):
                client_data = ClientCreate(
                    name=f"{stage.title()} Client {i}",
                    email=f"{stage}{i}@example.com",
                    phone=f"+1-555-{7000+i}",
                    property_address=f"{700+i} {stage} St, City, ST 12345",
                    property_type="residential",
                    stage=stage
                )
                created = await crm_service.create_client(client_data, agent_id=test_agent.id)
                created_by_stage[stage].append(created.id)
        
        # Verify filtering
        for stage, expected_ids in created_by_stage.items():
            filtered = await crm_service.list_clients(stage=stage)
            filtered_ids = [c.id for c in filtered]
            for expected_id in expected_ids:
                assert expected_id in filtered_ids
            assert all(c.stage == stage for c in filtered)

    @pytest.mark.asyncio
    async def test_get_client_tasks(self, crm_service, test_agent):
        """Test 11: Get tasks associated with a client."""
        # Create client
        client_data = ClientCreate(
            name="Task Client",
            email="task@example.com",
            phone="+1-555-0800",
            property_address="800 Task St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        # Add tasks directly to database
        tasks_data = [
            ("Day 1", 1, "high", "pending"),
            ("Week 1", 7, "medium", "pending"),
            ("Week 2", 14, "low", "completed"),
        ]
        
        for followup_type, days, priority, status in tasks_data:
            task = Task(
                client_id=created.id,
                followup_type=followup_type,
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=days),
                priority=priority,
                status=status,
                notes=f"Test task: {followup_type}"
            )
            crm_service.session.add(task)
        await crm_service.session.commit()
        
        # Retrieve tasks
        tasks = await crm_service.get_client_tasks(created.id)
        
        assert len(tasks) == 3
        assert all("id" in t for t in tasks)
        assert all("followup_type" in t for t in tasks)
        assert all("status" in t for t in tasks)


class TestCRMUpdate:
    """Test UPDATE operations for CRM service."""

    @pytest.mark.asyncio
    async def test_update_client_name(self, crm_service, test_agent):
        """Test 12: Update client name only."""
        # Create client
        client_data = ClientCreate(
            name="Original Name",
            email="original@example.com",
            phone="+1-555-0900",
            property_address="900 Original St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        # Update name
        update_data = ClientUpdate(name="Updated Name")
        updated = await crm_service.update_client(created.id, update_data)
        
        assert updated.name == "Updated Name"
        assert updated.email == "original@example.com"  # Unchanged

    @pytest.mark.asyncio
    async def test_update_client_email(self, crm_service, test_agent):
        """Test 13: Update client email."""
        client_data = ClientCreate(
            name="Email Client",
            email="old@example.com",
            phone="+1-555-1000",
            property_address="1000 Email St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        update_data = ClientUpdate(email="new@example.com")
        updated = await crm_service.update_client(created.id, update_data)
        
        assert updated.email == "new@example.com"
        assert updated.name == "Email Client"  # Unchanged

    @pytest.mark.asyncio
    async def test_update_client_stage_progression(self, crm_service, test_agent):
        """Test 14: Update client stage (progression through pipeline)."""
        client_data = ClientCreate(
            name="Stage Client",
            email="stage@example.com",
            phone="+1-555-1100",
            property_address="1100 Stage St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        # Progress through stages
        stages = ["lead", "negotiating", "under_contract", "closed"]
        for stage in stages[1:]:  # Skip first (already lead)
            update_data = ClientUpdate(stage=stage)
            updated = await crm_service.update_client(created.id, update_data)
            assert updated.stage == stage

    @pytest.mark.asyncio
    async def test_update_client_multiple_fields(self, crm_service, test_agent):
        """Test 15: Update multiple fields at once."""
        client_data = ClientCreate(
            name="Multi Client",
            email="multi@example.com",
            phone="+1-555-1200",
            property_address="1200 Multi St, City, ST 12345",
            property_type="residential",
            stage="lead",
            notes="Original notes"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        # Update multiple fields
        update_data = ClientUpdate(
            phone="+1-555-9999",
            property_address="9999 Updated St, New City, ST 99999",
            stage="negotiating",
            notes="Updated notes",
            custom_fields={"key": "value"}
        )
        updated = await crm_service.update_client(created.id, update_data)
        
        assert updated.phone == "+1-555-9999"
        assert updated.property_address == "9999 Updated St, New City, ST 99999"
        assert updated.stage == "negotiating"
        assert updated.notes == "Updated notes"
        assert updated.custom_fields == {"key": "value"}

    @pytest.mark.asyncio
    async def test_update_client_all_fields(self, crm_service, test_agent):
        """Test 16: Update all client fields."""
        client_data = ClientCreate(
            name="All Fields",
            email="all@example.com",
            phone="+1-555-1300",
            property_address="1300 All St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        update_data = ClientUpdate(
            name="All Updated",
            email="all.updated@example.com",
            phone="+1-555-8888",
            property_address="8888 Updated St, Updated City, ST 88888",
            property_type="commercial",
            stage="under_contract",
            notes="All fields updated",
            custom_fields={"all": "updated", "test": True}
        )
        updated = await crm_service.update_client(created.id, update_data)
        
        assert updated.name == "All Updated"
        assert updated.email == "all.updated@example.com"
        assert updated.phone == "+1-555-8888"
        assert updated.property_address == "8888 Updated St, Updated City, ST 88888"
        assert updated.property_type == "commercial"
        assert updated.stage == "under_contract"
        assert updated.notes == "All fields updated"
        assert updated.custom_fields == {"all": "updated", "test": True}

    @pytest.mark.asyncio
    async def test_update_nonexistent_client(self, crm_service, test_agent):
        """Test 17: Attempt to update non-existent client."""
        update_data = ClientUpdate(name="Won't Work")
        result = await crm_service.update_client(99999, update_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_with_empty_data(self, crm_service, test_agent):
        """Test 18: Update with empty update data (should return existing)."""
        client_data = ClientCreate(
            name="Empty Update",
            email="empty@example.com",
            phone="+1-555-1400",
            property_address="1400 Empty St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        # Update with empty ClientUpdate
        update_data = ClientUpdate()
        updated = await crm_service.update_client(created.id, update_data)
        
        assert updated is not None
        assert updated.name == "Empty Update"  # Unchanged


class TestCRMDelete:
    """Test DELETE operations for CRM service."""

    @pytest.mark.asyncio
    async def test_delete_client_soft_delete(self, crm_service, test_agent):
        """Test 19: Delete client (soft delete - sets is_deleted flag)."""
        client_data = ClientCreate(
            name="Delete Client",
            email="delete@example.com",
            phone="+1-555-1500",
            property_address="1500 Delete St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        client_id = created.id
        
        # Delete client
        result = await crm_service.delete_client(client_id)
        assert result is True
        
        # Verify it's not in the list
        listed = await crm_service.list_clients()
        assert client_id not in [c.id for c in listed]

    @pytest.mark.asyncio
    async def test_delete_multiple_clients(self, crm_service, test_agent):
        """Test 20: Delete multiple clients."""
        # Create 5 clients
        created_ids = []
        for i in range(5):
            client_data = ClientCreate(
                name=f"Delete Client {i}",
                email=f"delete{i}@example.com",
                phone=f"+1-555-{1600+i}",
                property_address=f"{1600+i} Delete St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            created = await crm_service.create_client(client_data, agent_id=test_agent.id)
            created_ids.append(created.id)
        
        # Delete first 3
        for client_id in created_ids[:3]:
            result = await crm_service.delete_client(client_id)
            assert result is True
        
        # Verify deleted ones are not in list
        listed = await crm_service.list_clients()
        listed_ids = [c.id for c in listed]
        assert created_ids[0] not in listed_ids
        assert created_ids[1] not in listed_ids
        assert created_ids[2] not in listed_ids
        # Verify remaining ones are still there
        assert created_ids[3] in listed_ids
        assert created_ids[4] in listed_ids

    @pytest.mark.asyncio
    async def test_delete_nonexistent_client(self, crm_service, test_agent):
        """Test 21: Attempt to delete non-existent client."""
        result = await crm_service.delete_client(99999)
        assert result is False


class TestCRMComplexScenarios:
    """Test complex scenarios combining multiple CRUD operations."""

    @pytest.mark.asyncio
    async def test_full_client_lifecycle(self, crm_service, test_agent):
        """Test 22: Complete client lifecycle - create, update, delete."""
        # Create
        client_data = ClientCreate(
            name="Lifecycle Client",
            email="lifecycle@example.com",
            phone="+1-555-1700",
            property_address="1700 Lifecycle St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        original_id = created.id
        
        # Read
        fetched = await crm_service.get_client(original_id)
        assert fetched is not None
        assert fetched.stage == "lead"
        
        # Update - progress through stages
        await crm_service.update_client(original_id, ClientUpdate(stage="negotiating"))
        await crm_service.update_client(original_id, ClientUpdate(stage="under_contract"))
        updated = await crm_service.update_client(original_id, ClientUpdate(stage="closed"))
        assert updated.stage == "closed"
        
        # Delete
        deleted = await crm_service.delete_client(original_id)
        assert deleted is True
        
        # Verify deleted
        listed = await crm_service.list_clients()
        assert original_id not in [c.id for c in listed]

    @pytest.mark.asyncio
    async def test_client_with_multiple_task_updates(self, crm_service, test_agent):
        """Test 23: Client with tasks, then update client and verify tasks remain."""
        # Create client
        client_data = ClientCreate(
            name="Task Update Client",
            email="taskupdate@example.com",
            phone="+1-555-1800",
            property_address="1800 Task St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await crm_service.create_client(client_data, agent_id=test_agent.id)
        
        # Add tasks
        task1 = Task(
            client_id=created.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            status="pending",
            priority="high"
        )
        task2 = Task(
            client_id=created.id,
            followup_type="Week 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=7),
            status="pending",
            priority="medium"
        )
        crm_service.session.add_all([task1, task2])
        await crm_service.session.commit()
        
        # Update client
        await crm_service.update_client(created.id, ClientUpdate(stage="negotiating"))
        
        # Verify tasks still exist
        tasks = await crm_service.get_client_tasks(created.id)
        assert len(tasks) == 2

    @pytest.mark.asyncio
    async def test_pagination_with_deleted_clients(self, crm_service, test_agent):
        """Test 24: Pagination works correctly when some clients are deleted."""
        # Create 10 clients
        created_ids = []
        for i in range(10):
            client_data = ClientCreate(
                name=f"Page Delete {i}",
                email=f"pagedelete{i}@example.com",
                phone=f"+1-555-{1900+i}",
                property_address=f"{1900+i} Page St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            created = await crm_service.create_client(client_data, agent_id=test_agent.id)
            created_ids.append(created.id)
        
        # Delete some clients (every other one)
        for client_id in created_ids[::2]:  # Delete indices 0, 2, 4, 6, 8
            await crm_service.delete_client(client_id)
        
        # Paginate - should only get non-deleted clients
        page1 = await crm_service.list_clients(page=1, limit=5)
        page2 = await crm_service.list_clients(page=2, limit=5)
        
        all_listed_ids = [c.id for c in page1 + page2]
        # Verify deleted clients are not in the list
        for deleted_id in created_ids[::2]:
            assert deleted_id not in all_listed_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

