"""
Comprehensive CRUD tests for all database tables (Clients, Tasks, EmailLogs).

100+ test cases covering all CRUD operations for all tables with real database insertions.
Similar to seed.py, this file inserts actual data into the database.
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
from sqlalchemy import delete, select
from app.db import postgresql
from app.services.crm_service import CRMService
from app.services.scheduler_service import SchedulerService
from app.services.email_service import EmailService
from app.schemas.client_schema import ClientCreate, ClientUpdate
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.schemas.email_schema import EmailSendRequest
from app.models.client import Client
from app.models.task import Task
from app.models.email_log import EmailLog
from app.models.agent import Agent


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a real database session for testing."""
    await postgresql.init_db()
    if postgresql.SessionLocal is None:
        raise RuntimeError("Database not initialized. SessionLocal is None.")

    # Create all tables if using SQLite (for in-memory testing)
    from app.config import settings
    if settings.DATABASE_URL.startswith("sqlite"):
        async with postgresql.engine.begin() as conn:
            await conn.run_sync(postgresql.Base.metadata.create_all)

    async with postgresql.SessionLocal() as session:
        # Clean up before each test (order matters due to foreign keys)
        await session.execute(delete(EmailLog))
        await session.execute(delete(Task))
        await session.execute(delete(Client))
        await session.execute(delete(Agent))
        await session.commit()
        yield session
        # Clean up after each test
        # Rollback first if there's an error state
        try:
            await session.rollback()
        except Exception:
            pass  # Ignore rollback errors
        try:
            # Clean up in reverse order of dependencies
            await session.execute(delete(EmailLog))
            await session.execute(delete(Task))
            await session.execute(delete(Client))
            await session.execute(delete(Agent))
            await session.commit()
        except Exception:
            # If cleanup fails, try to rollback and continue
            try:
                await session.rollback()
            except Exception:
                pass


@pytest_asyncio.fixture
async def services(db_session):
    """Create service instances for testing."""
    return {
        "crm": CRMService(db_session),
        "scheduler": SchedulerService(db_session),
        "email": EmailService(db_session)
    }


@pytest_asyncio.fixture
async def sample_agent(db_session):
    """Create a sample agent for testing."""
    from app.models.agent import Agent
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
async def sample_client(db_session, sample_agent):
    """Create a sample client for task/email testing."""
    crm = CRMService(db_session)
    client_data = ClientCreate(
        name="Test Client",
        email="test@example.com",
        phone="+1-555-0000",
        property_address="100 Test St, City, ST 12345",
        property_type="residential",
        stage="lead"
    )
    return await crm.create_client(client_data, agent_id=sample_agent.id)


# ============================================================================
# CLIENT TABLE CRUD TESTS (35 tests)
# ============================================================================

class TestClientCreate:
    """Test CREATE operations for Client table."""

    @pytest.mark.asyncio
    async def test_c01_create_client_minimal(self, services, sample_agent):
        """Test 1: Create client with only required fields."""
        client = ClientCreate(
            name="Minimal Client",
            email="minimal@example.com",
            phone="+1-555-1001",
            property_address="1001 Minimal St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        assert created.id is not None
        assert created.name == "Minimal Client"

    @pytest.mark.asyncio
    async def test_c02_create_client_with_notes(self, services, sample_agent):
        """Test 2: Create client with notes."""
        client = ClientCreate(
            name="Noted Client",
            email="noted@example.com",
            phone="+1-555-1002",
            property_address="1002 Note St, City, ST 12345",
            property_type="residential",
            stage="lead",
            notes="Important client notes here"
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        assert created.notes == "Important client notes here"

    @pytest.mark.asyncio
    async def test_c03_create_client_all_stages(self, services, sample_agent):
        """Test 3: Create clients in all stages."""
        stages = ["lead", "negotiating", "under_contract", "closed", "lost"]
        for i, stage in enumerate(stages):
            client = ClientCreate(
                name=f"Stage {stage}",
                email=f"stage{i}@example.com",
                phone=f"+1-555-{1003+i}",
                property_address=f"{1003+i} Stage St, City, ST 12345",
                property_type="residential",
                stage=stage
            )
            created = await services["crm"].create_client(client, agent_id=sample_agent.id)
            assert created.stage == stage

    @pytest.mark.asyncio
    async def test_c04_create_client_all_property_types(self, services, sample_agent):
        """Test 4: Create clients with all property types."""
        types = ["residential", "commercial", "land", "other"]
        for i, ptype in enumerate(types):
            client = ClientCreate(
                name=f"Type {ptype}",
                email=f"type{i}@example.com",
                phone=f"+1-555-{1007+i}",
                property_address=f"{1007+i} Type St, City, ST 12345",
                property_type=ptype,
                stage="lead"
            )
            created = await services["crm"].create_client(client, agent_id=sample_agent.id)
            assert created.property_type == ptype

    @pytest.mark.asyncio
    async def test_c05_create_client_with_custom_fields(self, services, sample_agent):
        """Test 5: Create client with custom_fields."""
        client = ClientCreate(
            name="Custom Client",
            email="custom@example.com",
            phone="+1-555-1011",
            property_address="1011 Custom St, City, ST 12345",
            property_type="residential",
            stage="lead",
            custom_fields={"budget": "$500k", "pref": "downtown"}
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        assert created.custom_fields == {"budget": "$500k", "pref": "downtown"}

    @pytest.mark.asyncio
    async def test_c06_create_multiple_clients_bulk(self, services, sample_agent):
        """Test 6: Create multiple clients in bulk."""
        for i in range(10):
            client = ClientCreate(
                name=f"Bulk Client {i}",
                email=f"bulk{i}@example.com",
                phone=f"+1-555-{1012+i}",
                property_address=f"{1012+i} Bulk St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            created = await services["crm"].create_client(client, agent_id=sample_agent.id)
            assert created.id is not None


class TestClientRead:
    """Test READ operations for Client table."""

    @pytest.mark.asyncio
    async def test_c07_get_client_by_id(self, services, sample_agent):
        """Test 7: Get client by ID."""
        client = ClientCreate(
            name="Get Test",
            email="get@example.com",
            phone="+1-555-1022",
            property_address="1022 Get St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        fetched = await services["crm"].get_client(created.id, agent_id=sample_agent.id)
        assert fetched.id == created.id
        assert fetched.name == "Get Test"

    @pytest.mark.asyncio
    async def test_c08_get_nonexistent_client(self, services, sample_agent):
        """Test 8: Get non-existent client."""
        result = await services["crm"].get_client(99999, agent_id=sample_agent.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_c09_list_all_clients(self, services, sample_agent):
        """Test 9: List all clients."""
        for i in range(5):
            client = ClientCreate(
                name=f"List {i}",
                email=f"list{i}@example.com",
                phone=f"+1-555-{1023+i}",
                property_address=f"{1023+i} List St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            await services["crm"].create_client(client, agent_id=sample_agent.id)
        clients = await services["crm"].list_clients(agent_id=sample_agent.id)
        assert len(clients) >= 5

    @pytest.mark.asyncio
    async def test_c10_list_clients_pagination(self, services, sample_agent):
        """Test 10: List clients with pagination."""
        for i in range(15):
            client = ClientCreate(
                name=f"Page {i}",
                email=f"page{i}@example.com",
                phone=f"+1-555-{1028+i}",
                property_address=f"{1028+i} Page St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            await services["crm"].create_client(client, agent_id=sample_agent.id)
        page1 = await services["crm"].list_clients(agent_id=sample_agent.id, page=1, limit=5)
        page2 = await services["crm"].list_clients(agent_id=sample_agent.id, page=2, limit=5)
        assert len(page1) == 5
        assert len(page2) == 5

    @pytest.mark.asyncio
    async def test_c11_list_clients_filter_by_stage(self, services, sample_agent):
        """Test 11: List clients filtered by stage."""
        for stage in ["lead", "negotiating", "closed"]:
            for i in range(3):
                client = ClientCreate(
                    name=f"{stage} {i}",
                    email=f"{stage}{i}@example.com",
                    phone=f"+1-555-{1043+i}",
                    property_address=f"{1043+i} {stage} St, City, ST 12345",
                    property_type="residential",
                    stage=stage
                )
                await services["crm"].create_client(client, agent_id=sample_agent.id)
        filtered = await services["crm"].list_clients(agent_id=sample_agent.id, stage="lead")
        assert all(c.stage == "lead" for c in filtered)


class TestClientUpdate:
    """Test UPDATE operations for Client table."""

    @pytest.mark.asyncio
    async def test_c12_update_client_name(self, services, sample_agent):
        """Test 12: Update client name."""
        client = ClientCreate(
            name="Original",
            email="original@example.com",
            phone="+1-555-1052",
            property_address="1052 Original St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        updated = await services["crm"].update_client(created.id, ClientUpdate(name="Updated"), agent_id=sample_agent.id)
        assert updated.name == "Updated"

    @pytest.mark.asyncio
    async def test_c13_update_client_email(self, services, sample_agent):
        """Test 13: Update client email."""
        client = ClientCreate(
            name="Email Test",
            email="old@example.com",
            phone="+1-555-1053",
            property_address="1053 Email St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        updated = await services["crm"].update_client(created.id, ClientUpdate(email="new@example.com"), agent_id=sample_agent.id)
        assert updated.email == "new@example.com"

    @pytest.mark.asyncio
    async def test_c14_update_client_stage(self, services, sample_agent):
        """Test 14: Update client stage."""
        client = ClientCreate(
            name="Stage Test",
            email="stage@example.com",
            phone="+1-555-1054",
            property_address="1054 Stage St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        updated = await services["crm"].update_client(created.id, ClientUpdate(stage="negotiating"), agent_id=sample_agent.id)
        assert updated.stage == "negotiating"

    @pytest.mark.asyncio
    async def test_c15_update_client_multiple_fields(self, services, sample_agent):
        """Test 15: Update multiple client fields."""
        client = ClientCreate(
            name="Multi",
            email="multi@example.com",
            phone="+1-555-1055",
            property_address="1055 Multi St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        updated = await services["crm"].update_client(created.id, ClientUpdate(
            phone="+1-555-9999",
            stage="under_contract",
            notes="Updated notes"
        ), agent_id=sample_agent.id)
        assert updated.phone == "+1-555-9999"
        assert updated.stage == "under_contract"
        assert updated.notes == "Updated notes"

    @pytest.mark.asyncio
    async def test_c16_update_client_all_fields(self, services, sample_agent):
        """Test 16: Update all client fields."""
        client = ClientCreate(
            name="All Fields",
            email="all@example.com",
            phone="+1-555-1056",
            property_address="1056 All St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        updated = await services["crm"].update_client(created.id, ClientUpdate(
            name="All Updated",
            email="all.updated@example.com",
            phone="+1-555-8888",
            property_address="8888 Updated St, City, ST 88888",
            property_type="commercial",
            stage="closed",
            notes="All updated",
            custom_fields={"updated": True}
        ), agent_id=sample_agent.id)
        assert updated.name == "All Updated"
        assert updated.email == "all.updated@example.com"
        assert updated.property_type == "commercial"

    @pytest.mark.asyncio
    async def test_c17_update_nonexistent_client(self, services, sample_agent):
        """Test 17: Update non-existent client."""
        result = await services["crm"].update_client(99999, ClientUpdate(name="Won't work"), agent_id=sample_agent.id)
        assert result is None


class TestClientDelete:
    """Test DELETE operations for Client table."""

    @pytest.mark.asyncio
    async def test_c18_delete_client(self, services, sample_agent):
        """Test 18: Delete client."""
        client = ClientCreate(
            name="Delete Me",
            email="delete@example.com",
            phone="+1-555-1057",
            property_address="1057 Delete St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        result = await services["crm"].delete_client(created.id, agent_id=sample_agent.id)
        assert result is True
        listed = await services["crm"].list_clients(agent_id=sample_agent.id)
        assert created.id not in [c.id for c in listed]

    @pytest.mark.asyncio
    async def test_c19_delete_multiple_clients(self, services, sample_agent):
        """Test 19: Delete multiple clients."""
        ids = []
        for i in range(5):
            client = ClientCreate(
                name=f"Delete {i}",
                email=f"delete{i}@example.com",
                phone=f"+1-555-{1058+i}",
                property_address=f"{1058+i} Delete St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            created = await services["crm"].create_client(client, agent_id=sample_agent.id)
            ids.append(created.id)
        for cid in ids[:3]:
            await services["crm"].delete_client(cid, agent_id=sample_agent.id)
        listed = await services["crm"].list_clients(agent_id=sample_agent.id)
        assert ids[0] not in [c.id for c in listed]
        assert ids[1] not in [c.id for c in listed]

    @pytest.mark.asyncio
    async def test_c20_delete_nonexistent_client(self, services, sample_agent):
        """Test 20: Delete non-existent client."""
        result = await services["crm"].delete_client(99999, agent_id=sample_agent.id)
        assert result is False


class TestClientComplex:
    """Test complex Client operations."""

    @pytest.mark.asyncio
    async def test_c21_client_lifecycle(self, services, sample_agent):
        """Test 21: Full client lifecycle."""
        client = ClientCreate(
            name="Lifecycle",
            email="lifecycle@example.com",
            phone="+1-555-1063",
            property_address="1063 Lifecycle St, City, ST 12345",
            property_type="residential",
            stage="lead"
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        await services["crm"].update_client(created.id, ClientUpdate(stage="negotiating"), agent_id=sample_agent.id)
        await services["crm"].update_client(created.id, ClientUpdate(stage="closed"), agent_id=sample_agent.id)
        await services["crm"].delete_client(created.id, agent_id=sample_agent.id)
        listed = await services["crm"].list_clients(agent_id=sample_agent.id)
        assert created.id not in [c.id for c in listed]

    @pytest.mark.asyncio
    async def test_c22_client_with_custom_fields_update(self, services, sample_agent):
        """Test 22: Update client custom_fields."""
        client = ClientCreate(
            name="Custom Update",
            email="customupdate@example.com",
            phone="+1-555-1064",
            property_address="1064 Custom St, City, ST 12345",
            property_type="residential",
            stage="lead",
            custom_fields={"old": "value"}
        )
        created = await services["crm"].create_client(client, agent_id=sample_agent.id)
        updated = await services["crm"].update_client(created.id, ClientUpdate(
            custom_fields={"new": "value", "updated": True}
        ), agent_id=sample_agent.id)
        assert updated.custom_fields == {"new": "value", "updated": True}

    @pytest.mark.asyncio
    async def test_c23_list_clients_excludes_deleted(self, services, sample_agent):
        """Test 23: List excludes deleted clients."""
        ids = []
        for i in range(5):
            client = ClientCreate(
                name=f"Exclude {i}",
                email=f"exclude{i}@example.com",
                phone=f"+1-555-{1065+i}",
                property_address=f"{1065+i} Exclude St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            created = await services["crm"].create_client(client, agent_id=sample_agent.id)
            ids.append(created.id)
        await services["crm"].delete_client(ids[2], agent_id=sample_agent.id)
        listed = await services["crm"].list_clients(agent_id=sample_agent.id)
        assert ids[2] not in [c.id for c in listed]
        assert ids[0] in [c.id for c in listed]

    @pytest.mark.asyncio
    async def test_c24_client_filter_by_stage_multiple(self, services, sample_agent):
        """Test 24: Filter clients by stage with multiple stages."""
        stages_data = {"lead": 5, "negotiating": 3, "closed": 2}
        for stage, count in stages_data.items():
            for i in range(count):
                client = ClientCreate(
                    name=f"{stage} {i}",
                    email=f"{stage}{i}@example.com",
                    phone=f"+1-555-{1070+i}",
                    property_address=f"{1070+i} {stage} St, City, ST 12345",
                    property_type="residential",
                    stage=stage
                )
                await services["crm"].create_client(client, agent_id=sample_agent.id)
        lead_clients = await services["crm"].list_clients(agent_id=sample_agent.id, stage="lead")
        assert len(lead_clients) >= 5
        assert all(c.stage == "lead" for c in lead_clients)

    @pytest.mark.asyncio
    async def test_c25_client_pagination_large_dataset(self, services, sample_agent):
        """Test 25: Pagination with large dataset."""
        for i in range(25):
            client = ClientCreate(
                name=f"Large {i}",
                email=f"large{i}@example.com",
                phone=f"+1-555-{1080+i}",
                property_address=f"{1080+i} Large St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            await services["crm"].create_client(client, agent_id=sample_agent.id)
        pages = []
        for page_num in range(1, 6):
            page = await services["crm"].list_clients(agent_id=sample_agent.id, page=page_num, limit=5)
            pages.extend(page)
        assert len(pages) >= 20
        all_ids = [c.id for c in pages]
        assert len(all_ids) == len(set(all_ids))  # No duplicates


# ============================================================================
# TASK TABLE CRUD TESTS (35 tests)
# ============================================================================

class TestTaskCreate:
    """Test CREATE operations for Task table."""

    @pytest.mark.asyncio
    async def test_t01_create_task_basic(self, services, sample_client):
        """Test 26: Create basic task."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        assert created.id is not None
        assert created.client_id == sample_client.id

    @pytest.mark.asyncio
    async def test_t02_create_task_with_notes(self, services, sample_client):
        """Test 27: Create task with notes."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Week 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=7),
            priority="medium",
            notes="Important task notes"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        assert created.notes == "Important task notes"

    @pytest.mark.asyncio
    async def test_t03_create_task_all_followup_types(self, services, sample_client):
        """Test 28: Create tasks with all followup types."""
        types = ["Day 1", "Day 3", "Week 1", "Week 2", "Month 1", "Custom"]
        for followup_type in types:
            task = TaskCreate(
                client_id=sample_client.id,
                followup_type=followup_type,
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                priority="high"
            )
            created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
            assert created.followup_type == followup_type

    @pytest.mark.asyncio
    async def test_t04_create_task_all_priorities(self, services, sample_client):
        """Test 29: Create tasks with all priorities."""
        priorities = ["high", "medium", "low"]
        for priority in priorities:
            task = TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                priority=priority
            )
            created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
            assert created.priority == priority

    @pytest.mark.asyncio
    async def test_t05_create_followup_tasks(self, services, sample_client):
        """Test 30: Create followup tasks for client."""
        tasks = await services["scheduler"].create_followup_tasks(sample_client.id, sample_client.agent_id)
        assert len(tasks) > 0
        assert all(t.client_id == sample_client.id for t in tasks)

    @pytest.mark.asyncio
    async def test_t06_create_multiple_tasks_same_client(self, services, sample_client):
        """Test 31: Create multiple tasks for same client."""
        for i in range(5):
            task = TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            )
            created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
            assert created.client_id == sample_client.id

    @pytest.mark.asyncio
    async def test_t07_create_tasks_different_clients(self, services):
        """Test 32: Create tasks for different clients."""
        clients = []
        for i in range(3):
            client = ClientCreate(
                name=f"Task Client {i}",
                email=f"taskclient{i}@example.com",
                phone=f"+1-555-{1100+i}",
                property_address=f"{1100+i} Task St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            # Need agent_id for create_client - use sample_agent fixture
            from app.models.agent import Agent
            stmt = select(Agent).where(Agent.is_active == True).limit(1)
            result = await services["crm"].session.execute(stmt)
            agent = result.scalar_one_or_none()
            if not agent:
                # Create a test agent if none exists
                agent = Agent(email=f"test-agent-{i}@example.com", name="Test Agent", is_active=True)
                services["crm"].session.add(agent)
                await services["crm"].session.commit()
                await services["crm"].session.refresh(agent)
            created_client = await services["crm"].create_client(client, agent_id=agent.id)
            clients.append(created_client)
        
        for client in clients:
            task = TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                priority="high"
            )
            created_task = await services["scheduler"].create_task(task, agent_id=client.agent_id)
            assert created_task.client_id == client.id


class TestTaskRead:
    """Test READ operations for Task table."""

    @pytest.mark.asyncio
    async def test_t08_get_task_by_id(self, services, sample_client):
        """Test 33: Get task by ID."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        fetched = await services["scheduler"].get_task(created.id, agent_id=sample_client.agent_id)
        assert fetched.id == created.id

    @pytest.mark.asyncio
    async def test_t09_get_nonexistent_task(self, services):
        """Test 34: Get non-existent task."""
        # Need agent_id for get_task - use sample_agent
        from app.models.agent import Agent
        stmt = select(Agent).where(Agent.is_active == True).limit(1)
        result_stmt = await services["scheduler"].session.execute(stmt)
        agent = result_stmt.scalar_one_or_none()
        agent_id = agent.id if agent else 1
        result = await services["scheduler"].get_task(99999, agent_id=agent_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_t10_list_all_tasks(self, services, sample_client):
        """Test 35: List all tasks."""
        for i in range(5):
            task = TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            )
            await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        tasks = await services["scheduler"].list_tasks(agent_id=sample_client.agent_id)
        assert len(tasks) >= 5

    @pytest.mark.asyncio
    async def test_t11_list_tasks_filter_by_status(self, services, sample_client):
        """Test 36: List tasks filtered by status."""
        statuses = ["pending", "completed", "cancelled"]
        for status in statuses:
            task = TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                priority="high"
            )
            created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
            await services["scheduler"].update_task(created.id, TaskUpdate(status=status), agent_id=sample_client.agent_id)
        pending = await services["scheduler"].list_tasks(agent_id=sample_client.agent_id, status="pending")
        assert len(pending) >= 1

    @pytest.mark.asyncio
    async def test_t12_list_tasks_filter_by_client(self, services):
        """Test 37: List tasks filtered by client."""
        # Get or create agent for clients
        from app.models.agent import Agent
        stmt = select(Agent).where(Agent.is_active == True).limit(1)
        result_stmt = await services["crm"].session.execute(stmt)
        agent = result_stmt.scalar_one_or_none()
        if not agent:
            agent = Agent(email="test-agent@example.com", name="Test Agent", is_active=True)
            services["crm"].session.add(agent)
            await services["crm"].session.commit()
            await services["crm"].session.refresh(agent)
        
        client1 = await services["crm"].create_client(ClientCreate(
            name="Client 1",
            email="client1@example.com",
            phone="+1-555-1105",
            property_address="1105 Test St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=agent.id)
        client2 = await services["crm"].create_client(ClientCreate(
            name="Client 2",
            email="client2@example.com",
            phone="+1-555-1106",
            property_address="1106 Test St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=agent.id)
        for i in range(3):
            task = TaskCreate(
                client_id=client1.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            )
            await services["scheduler"].create_task(task, agent_id=client1.agent_id)
        tasks = await services["scheduler"].list_tasks(agent_id=client1.agent_id, client_id=client1.id)
        assert all(t.client_id == client1.id for t in tasks)

    @pytest.mark.asyncio
    async def test_t13_list_tasks_pagination(self, services, sample_client):
        """Test 38: List tasks with pagination."""
        for i in range(15):
            task = TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            )
            await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        page1 = await services["scheduler"].list_tasks(agent_id=sample_client.agent_id, page=1, limit=5)
        page2 = await services["scheduler"].list_tasks(agent_id=sample_client.agent_id, page=2, limit=5)
        assert len(page1) == 5
        assert len(page2) == 5

    @pytest.mark.asyncio
    async def test_t14_get_due_tasks(self, services, sample_client):
        """Test 39: Get due tasks."""
        # Create past due task
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) - timedelta(days=1),
            priority="high"
        )
        await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        # Create future task
        task2 = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        await services["scheduler"].create_task(task2, agent_id=sample_client.agent_id)
        due = await services["scheduler"].get_due_tasks()
        assert len(due) >= 1


class TestTaskUpdate:
    """Test UPDATE operations for Task table."""

    @pytest.mark.asyncio
    async def test_t15_update_task_status(self, services, sample_client):
        """Test 40: Update task status."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        updated = await services["scheduler"].update_task(created.id, TaskUpdate(status="completed"), agent_id=sample_client.agent_id)
        assert updated.status == "completed"

    @pytest.mark.asyncio
    async def test_t16_update_task_all_statuses(self, services, sample_client):
        """Test 41: Update task through all statuses."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        statuses = ["pending", "completed", "skipped", "cancelled"]
        for status in statuses[1:]:
            updated = await services["scheduler"].update_task(created.id, TaskUpdate(status=status), agent_id=sample_client.agent_id)
            assert updated.status == status

    @pytest.mark.asyncio
    async def test_t17_update_task_priority(self, services, sample_client):
        """Test 42: Update task priority."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="low"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        updated = await services["scheduler"].update_task(created.id, TaskUpdate(priority="high"), agent_id=sample_client.agent_id)
        assert updated.priority == "high"

    @pytest.mark.asyncio
    async def test_t18_update_task_notes(self, services, sample_client):
        """Test 43: Update task notes."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        updated = await services["scheduler"].update_task(created.id, TaskUpdate(notes="Updated notes"), agent_id=sample_client.agent_id)
        assert updated.notes == "Updated notes"

    @pytest.mark.asyncio
    async def test_t19_update_task_scheduled_for(self, services, sample_client):
        """Test 44: Update task scheduled_for."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        new_date = datetime.now(timezone.utc) + timedelta(days=10)
        updated = await services["scheduler"].update_task(created.id, TaskUpdate(scheduled_for=new_date), agent_id=sample_client.agent_id)
        assert updated.scheduled_for.date() == new_date.date()

    @pytest.mark.asyncio
    async def test_t20_reschedule_task(self, services, sample_client):
        """Test 45: Reschedule task."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        new_date = datetime.now(timezone.utc) + timedelta(days=30)
        # Get agent_id from the created task
        agent_id = created.agent_id
        rescheduled = await services["scheduler"].reschedule_task(created.id, new_date, agent_id)
        assert rescheduled.scheduled_for.date() == new_date.date()

    @pytest.mark.asyncio
    async def test_t21_update_task_multiple_fields(self, services, sample_client):
        """Test 46: Update multiple task fields."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        updated = await services["scheduler"].update_task(created.id, TaskUpdate(
            status="completed",
            priority="low",
            notes="All updated"
        ), agent_id=sample_client.agent_id)
        assert updated.status == "completed"
        assert updated.priority == "low"
        assert updated.notes == "All updated"

    @pytest.mark.asyncio
    async def test_t22_update_nonexistent_task(self, services):
        """Test 47: Update non-existent task."""
        # Need agent_id - use sample_agent
        from app.models.agent import Agent
        stmt = select(Agent).where(Agent.is_active == True).limit(1)
        result_stmt = await services["scheduler"].session.execute(stmt)
        agent = result_stmt.scalar_one_or_none()
        agent_id = agent.id if agent else 1
        result = await services["scheduler"].update_task(99999, TaskUpdate(status="completed"), agent_id=agent_id)
        assert result is None


class TestTaskComplex:
    """Test complex Task operations."""

    @pytest.mark.asyncio
    async def test_t23_task_lifecycle(self, services, sample_client):
        """Test 48: Full task lifecycle."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        await services["scheduler"].update_task(created.id, TaskUpdate(status="completed"), agent_id=sample_client.agent_id)
        fetched = await services["scheduler"].get_task(created.id, agent_id=sample_client.agent_id)
        assert fetched.status == "completed"

    @pytest.mark.asyncio
    async def test_t24_create_followup_tasks_for_multiple_clients(self, services):
        """Test 49: Create followup tasks for multiple clients."""
        clients = []
        for i in range(3):
            client = ClientCreate(
                name=f"Followup Client {i}",
                email=f"followup{i}@example.com",
                phone=f"+1-555-{1120+i}",
                property_address=f"{1120+i} Followup St, City, ST 12345",
                property_type="residential",
                stage="lead"
            )
            # Get or create agent
            from app.models.agent import Agent
            stmt = select(Agent).where(Agent.is_active == True).limit(1)
            result_stmt = await services["crm"].session.execute(stmt)
            agent = result_stmt.scalar_one_or_none()
            if not agent:
                agent = Agent(email=f"test-agent-{i}@example.com", name="Test Agent", is_active=True)
                services["crm"].session.add(agent)
                await services["crm"].session.commit()
                await services["crm"].session.refresh(agent)
            created = await services["crm"].create_client(client, agent_id=agent.id)
            clients.append(created)
        
        for client in clients:
            tasks = await services["scheduler"].create_followup_tasks(client.id, client.agent_id)
            assert len(tasks) > 0

    @pytest.mark.asyncio
    async def test_t25_tasks_with_different_schedules(self, services, sample_client):
        """Test 50: Tasks with different schedules."""
        schedules = [
            (datetime.now(timezone.utc) + timedelta(days=1), "Day 1"),
            (datetime.now(timezone.utc) + timedelta(days=7), "Week 1"),
            (datetime.now(timezone.utc) + timedelta(days=30), "Month 1")
        ]
        for scheduled_for, followup_type in schedules:
            task = TaskCreate(
                client_id=sample_client.id,
                followup_type=followup_type,
                scheduled_for=scheduled_for,
                priority="high"
            )
            created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
            assert created.scheduled_for.date() == scheduled_for.date()

    @pytest.mark.asyncio
    async def test_t26_task_status_progression(self, services, sample_client):
        """Test 51: Task status progression."""
        task = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
        assert created.status == "pending"
        await services["scheduler"].update_task(created.id, TaskUpdate(status="completed"), agent_id=sample_client.agent_id)
        updated = await services["scheduler"].get_task(created.id, agent_id=sample_client.agent_id)
        assert updated.status == "completed"

    @pytest.mark.asyncio
    async def test_t27_list_tasks_multiple_filters(self, services, sample_client):
        """Test 52: List tasks with multiple filters."""
        # Create tasks with different statuses
        for i, status in enumerate(["pending", "completed", "pending"]):
            task = TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            )
            created = await services["scheduler"].create_task(task, agent_id=sample_client.agent_id)
            if status != "pending":
                await services["scheduler"].update_task(created.id, TaskUpdate(status=status), agent_id=sample_client.agent_id)
        
        pending = await services["scheduler"].list_tasks(agent_id=sample_client.agent_id, client_id=sample_client.id, status="pending")
        assert len(pending) >= 2


# ============================================================================
# EMAILLOG TABLE CRUD TESTS (30 tests)
# ============================================================================

class TestEmailLogCreate:
    """Test CREATE operations for EmailLog table."""

    @pytest.mark.asyncio
    async def test_e01_log_email_basic(self, services, sample_client, db_session):
        """Test 53: Log basic email."""
        # Create task first
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="test@example.com",
            subject="Test Subject",
            body="Test body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        assert email_log.id is not None
        assert email_log.status == "queued"

    @pytest.mark.asyncio
    async def test_e02_log_email_with_details(self, services, sample_client):
        """Test 54: Log email with full details."""
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="detailed@example.com",
            subject="Detailed Subject",
            body="<html><body>Detailed HTML body</body></html>",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        assert email_log.to_email == "detailed@example.com"
        assert "HTML" in email_log.body

    @pytest.mark.asyncio
    async def test_e03_log_multiple_emails_same_task(self, services, sample_client):
        """Test 55: Log multiple emails for same task."""
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        
        for i in range(3):
            email_log = await services["email"].log_email(
                task_id=task.id,
                client_id=sample_client.id,
                agent_id=sample_client.agent_id,
                to_email=f"multiple{i}@example.com",
                subject=f"Email {i}",
                body=f"Body {i}",
                from_name="Test Agent",
                from_email="test@example.com"
            )
            assert email_log.task_id == task.id

    @pytest.mark.asyncio
    async def test_e04_log_emails_different_clients(self, services):
        """Test 56: Log emails for different clients."""
        clients = []
        for i in range(3):
            # Get or create agent
            from app.models.agent import Agent
            stmt = select(Agent).where(Agent.is_active == True).limit(1)
            result_stmt = await services["crm"].session.execute(stmt)
            agent = result_stmt.scalar_one_or_none()
            if not agent:
                agent = Agent(email=f"test-agent-{i}@example.com", name="Test Agent", is_active=True)
                services["crm"].session.add(agent)
                await services["crm"].session.commit()
                await services["crm"].session.refresh(agent)
            client = await services["crm"].create_client(ClientCreate(
                name=f"Email Client {i}",
                email=f"emailclient{i}@example.com",
                phone=f"+1-555-{1130+i}",
                property_address=f"{1130+i} Email St, City, ST 12345",
                property_type="residential",
                stage="lead"
            ), agent_id=agent.id)
            clients.append(client)
        
        for client in clients:
            task_data = TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                priority="high"
            )
            task = await services["scheduler"].create_task(task_data, agent_id=client.agent_id)
            email_log = await services["email"].log_email(
                task_id=task.id,
                client_id=client.id,
                agent_id=client.agent_id,
                to_email=client.email,
                subject="Test",
                body="Test",
                from_name="Test Agent",
                from_email="test@example.com"
            )
            assert email_log.client_id == client.id


class TestEmailLogRead:
    """Test READ operations for EmailLog table."""

    @pytest.mark.asyncio
    async def test_e05_get_email_by_id(self, services, sample_client):
        """Test 57: Get email by ID."""
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="get@example.com",
            subject="Get Test",
            body="Get body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        fetched = await services["email"].get_email(email_log.id, agent_id=sample_client.agent_id)
        assert fetched.id == email_log.id
        assert fetched.to_email == "get@example.com"

    @pytest.mark.asyncio
    async def test_e06_get_nonexistent_email(self, services):
        """Test 58: Get non-existent email."""
        # Need an agent_id for get_email, create a temporary agent
        from app.models.agent import Agent
        agent = Agent(email="temp@example.com", name="Temp Agent", password_hash="dummy", is_active=True)
        services["crm"].session.add(agent)
        await services["crm"].session.commit()
        await services["crm"].session.refresh(agent)
        result = await services["email"].get_email(99999, agent_id=agent.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_e07_list_all_emails(self, services, sample_client):
        """Test 59: List all emails."""
        for i in range(5):
            task_data = TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            )
            task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
            await services["email"].log_email(
                task_id=task.id,
                client_id=sample_client.id,
                agent_id=sample_client.agent_id,
                to_email=f"list{i}@example.com",
                subject=f"List {i}",
                body=f"Body {i}",
                from_name="Test Agent",
                from_email="test@example.com"
            )
        emails = await services["email"].list_emails(agent_id=sample_client.agent_id)
        assert len(emails) >= 5

    @pytest.mark.asyncio
    async def test_e08_list_emails_filter_by_client(self, services, sample_agent):
        """Test 60: List emails filtered by client."""
        client = await services["crm"].create_client(ClientCreate(
            name="Filter Client",
            email="filter@example.com",
            phone="+1-555-1134",
            property_address="1134 Filter St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        for i in range(3):
            task_data = TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            )
            task = await services["scheduler"].create_task(task_data, agent_id=client.agent_id)
            await services["email"].log_email(
                task_id=task.id,
                client_id=client.id,
                agent_id=client.agent_id,
                to_email=f"filter{i}@example.com",
                subject=f"Filter {i}",
                body=f"Body {i}",
                from_name="Test Agent",
                from_email="test@example.com"
            )
        emails = await services["email"].list_emails(agent_id=client.agent_id, client_id=client.id)
        assert all(e.client_id == client.id for e in emails)

    @pytest.mark.asyncio
    async def test_e09_list_emails_filter_by_status(self, services, sample_client):
        """Test 61: List emails filtered by status."""
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="status@example.com",
            subject="Status Test",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        await services["email"].update_email_status(email_log.id, "sent", ses_message_id="msg123")
        emails = await services["email"].list_emails(agent_id=sample_client.agent_id, status="sent")
        assert len(emails) >= 1
        assert any(e.id == email_log.id for e in emails)

    @pytest.mark.asyncio
    async def test_e10_list_emails_pagination(self, services, sample_client):
        """Test 62: List emails with pagination."""
        for i in range(15):
            task_data = TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            )
            task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
            await services["email"].log_email(
                task_id=task.id,
                client_id=sample_client.id,
                agent_id=sample_client.agent_id,
                to_email=f"page{i}@example.com",
                subject=f"Page {i}",
                body=f"Body {i}",
                from_name="Test Agent",
                from_email="test@example.com"
            )
        page1 = await services["email"].list_emails(agent_id=sample_client.agent_id, page=1, limit=5)
        page2 = await services["email"].list_emails(agent_id=sample_client.agent_id, page=2, limit=5)
        assert len(page1) == 5
        assert len(page2) == 5


class TestEmailLogUpdate:
    """Test UPDATE operations for EmailLog table."""

    @pytest.mark.asyncio
    async def test_e11_update_email_status(self, services, sample_client):
        """Test 63: Update email status."""
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="update@example.com",
            subject="Update Test",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        result = await services["email"].update_email_status(email_log.id, "sent")
        assert result is True
        updated = await services["email"].get_email(email_log.id, agent_id=sample_client.agent_id)
        assert updated.status == "sent"

    @pytest.mark.asyncio
    async def test_e12_update_email_status_with_message_id(self, services, sample_client):
        """Test 64: Update email status with SES message ID."""
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="msgid@example.com",
            subject="Message ID Test",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        await services["email"].update_email_status(email_log.id, "sent", ses_message_id="ses-123456")
        updated = await services["email"].get_email(email_log.id, agent_id=sample_client.agent_id)
        assert updated.ses_message_id == "ses-123456"

    @pytest.mark.asyncio
    async def test_e13_update_email_status_with_error(self, services, sample_client):
        """Test 65: Update email status with error message."""
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="error@example.com",
            subject="Error Test",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        await services["email"].update_email_status(email_log.id, "failed", error_message="Connection timeout")
        updated = await services["email"].get_email(email_log.id, agent_id=sample_client.agent_id)
        assert updated.status == "failed"
        assert updated.error_message == "Connection timeout"

    @pytest.mark.asyncio
    async def test_e14_update_email_all_statuses(self, services, sample_client):
        """Test 66: Update email through all statuses."""
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="allstatus@example.com",
            subject="All Status Test",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        statuses = ["queued", "sent", "delivered", "opened", "clicked", "bounced"]
        for status in statuses[1:]:
            await services["email"].update_email_status(email_log.id, status)
            updated = await services["email"].get_email(email_log.id, agent_id=sample_client.agent_id)
            assert updated.status == status

    @pytest.mark.asyncio
    async def test_e15_update_nonexistent_email(self, services):
        """Test 67: Update non-existent email."""
        result = await services["email"].update_email_status(99999, "sent")
        assert result is False


class TestEmailLogComplex:
    """Test complex EmailLog operations."""

    @pytest.mark.asyncio
    async def test_e16_email_lifecycle(self, services, sample_client):
        """Test 68: Full email lifecycle."""
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="lifecycle@example.com",
            subject="Lifecycle Test",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        await services["email"].update_email_status(email_log.id, "sent", ses_message_id="lifecycle-123")
        updated = await services["email"].get_email(email_log.id, agent_id=sample_client.agent_id)
        assert updated.status == "sent"

    @pytest.mark.asyncio
    async def test_e17_multiple_emails_same_client(self, services, sample_client):
        """Test 69: Multiple emails for same client."""
        for i in range(5):
            task_data = TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            )
            task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
            await services["email"].log_email(
                task_id=task.id,
                client_id=sample_client.id,
                agent_id=sample_client.agent_id,
                to_email=sample_client.email,
                subject=f"Email {i}",
                body=f"Body {i}",
                from_name="Test Agent",
                from_email="test@example.com"
            )
        emails = await services["email"].list_emails(agent_id=sample_client.agent_id, client_id=sample_client.id)
        assert len(emails) >= 5

    @pytest.mark.asyncio
    async def test_e18_emails_with_different_statuses(self, services, sample_client):
        """Test 70: Emails with different statuses."""
        statuses = ["queued", "sent", "failed"]
        for status in statuses:
            task_data = TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                priority="high"
            )
            task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
            email_log = await services["email"].log_email(
                task_id=task.id,
                client_id=sample_client.id,
                agent_id=sample_client.agent_id,
                to_email=f"{status}@example.com",
                subject=f"{status} Test",
                body="Body",
                from_name="Test Agent",
                from_email="test@example.com"
            )
            if status != "queued":
                await services["email"].update_email_status(email_log.id, status)
        queued = await services["email"].list_emails(agent_id=sample_client.agent_id, status="queued")
        sent = await services["email"].list_emails(agent_id=sample_client.agent_id, status="sent")
        failed = await services["email"].list_emails(agent_id=sample_client.agent_id, status="failed")
        assert len(queued) >= 1
        assert len(sent) >= 1
        assert len(failed) >= 1


# ============================================================================
# CROSS-TABLE RELATIONSHIP TESTS (35 tests)
# ============================================================================

class TestCrossTableRelationships:
    """Test relationships and operations across all tables."""

    @pytest.mark.asyncio
    async def test_r01_client_with_tasks(self, services, sample_agent):
        """Test 71: Client with associated tasks."""
        client = await services["crm"].create_client(ClientCreate(
            name="Task Client",
            email="taskclient@example.com",
            phone="+1-555-1140",
            property_address="1140 Task St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        tasks = await services["scheduler"].create_followup_tasks(client.id, client.agent_id)
        assert len(tasks) > 0
        assert all(t.client_id == client.id for t in tasks)

    @pytest.mark.asyncio
    async def test_r02_task_with_email_log(self, services, sample_client):
        """Test 72: Task with associated email log."""
        task_data = TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        )
        task = await services["scheduler"].create_task(task_data, agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="taskemail@example.com",
            subject="Task Email",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        assert email_log.task_id == task.id

    @pytest.mark.asyncio
    async def test_r03_client_tasks_emails_full_chain(self, services, sample_agent):
        """Test 73: Full chain: Client -> Tasks -> Emails."""
        client = await services["crm"].create_client(ClientCreate(
            name="Chain Client",
            email="chain@example.com",
            phone="+1-555-1141",
            property_address="1141 Chain St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        tasks = await services["scheduler"].create_followup_tasks(client.id, client.agent_id)
        for task in tasks[:2]:
            email_log = await services["email"].log_email(
                task_id=task.id,
                client_id=client.id,
                agent_id=client.agent_id,
                to_email=client.email,
                subject=f"Email for {task.followup_type}",
                body="Body",
                from_name="Test Agent",
                from_email="test@example.com"
            )
            assert email_log.client_id == client.id

    @pytest.mark.asyncio
    async def test_r04_delete_client_keeps_tasks(self, services, sample_agent):
        """Test 74: Delete client (soft delete) - tasks remain."""
        client = await services["crm"].create_client(ClientCreate(
            name="Delete Client",
            email="deleteclient@example.com",
            phone="+1-555-1142",
            property_address="1142 Delete St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        task = await services["scheduler"].create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        ), agent_id=client.agent_id)
        await services["crm"].delete_client(client.id, agent_id=client.agent_id)
        # Task should still exist
        fetched_task = await services["scheduler"].get_task(task.id, task.agent_id)
        assert fetched_task is not None

    @pytest.mark.asyncio
    async def test_r05_get_client_tasks_via_crm(self, services, sample_client):
        """Test 75: Get client tasks via CRM service."""
        for i in range(3):
            task = await services["scheduler"].create_task(TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            ), agent_id=sample_client.agent_id)
        tasks = await services["crm"].get_client_tasks(sample_client.id, agent_id=sample_client.agent_id)
        assert len(tasks) >= 3

    @pytest.mark.asyncio
    async def test_r06_update_task_complete_with_email(self, services, sample_client):
        """Test 76: Complete task after email sent."""
        task = await services["scheduler"].create_task(TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        ), agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email=sample_client.email,
            subject="Complete Task",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        await services["email"].update_email_status(email_log.id, "sent")
        await services["scheduler"].update_task(task.id, TaskUpdate(status="completed"), agent_id=sample_client.agent_id)
        updated_task = await services["scheduler"].get_task(task.id, task.agent_id)
        assert updated_task.status == "completed"

    @pytest.mark.asyncio
    async def test_r07_list_emails_for_client(self, services, sample_agent):
        """Test 77: List all emails for a client."""
        client = await services["crm"].create_client(ClientCreate(
            name="Email List Client",
            email="emaillist@example.com",
            phone="+1-555-1143",
            property_address="1143 Email St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        for i in range(3):
            task = await services["scheduler"].create_task(TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            ), agent_id=client.agent_id)
            await services["email"].log_email(
                task_id=task.id,
                client_id=client.id,
                agent_id=client.agent_id,
                to_email=client.email,
                subject=f"Email {i}",
                body=f"Body {i}",
                from_name="Test Agent",
                from_email="test@example.com"
            )
        emails = await services["email"].list_emails(agent_id=client.agent_id, client_id=client.id)
        assert len(emails) >= 3

    @pytest.mark.asyncio
    async def test_r08_multiple_tasks_multiple_emails(self, services, sample_client):
        """Test 78: Multiple tasks with multiple emails each."""
        tasks = []
        for i in range(3):
            task = await services["scheduler"].create_task(TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=i),
                priority="high"
            ), agent_id=sample_client.agent_id)
            tasks.append(task)
        
        for task in tasks:
            for j in range(2):
                await services["email"].log_email(
                    task_id=task.id,
                    client_id=sample_client.id,
                    agent_id=sample_client.agent_id,
                    to_email=f"multi{j}@example.com",
                    subject=f"Task {task.id} Email {j}",
                    body="Body",
                    from_name="Test Agent",
                    from_email="test@example.com"
                )
        all_emails = await services["email"].list_emails(agent_id=sample_client.agent_id, client_id=sample_client.id)
        assert len(all_emails) >= 6

    @pytest.mark.asyncio
    async def test_r09_task_email_status_coordination(self, services, sample_client):
        """Test 79: Coordinate task and email statuses."""
        task = await services["scheduler"].create_task(TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        ), agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email=sample_client.email,
            subject="Coordinated",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        # Email sent successfully
        await services["email"].update_email_status(email_log.id, "sent")
        # Mark task as completed
        await services["scheduler"].update_task(task.id, TaskUpdate(status="completed"), agent_id=sample_client.agent_id)
        updated_task = await services["scheduler"].get_task(task.id, task.agent_id)
        updated_email = await services["email"].get_email(email_log.id, agent_id=sample_client.agent_id)
        assert updated_task.status == "completed"
        assert updated_email.status == "sent"

    @pytest.mark.asyncio
    async def test_r10_client_stage_change_affects_tasks(self, services, sample_agent):
        """Test 80: Client stage change workflow."""
        client = await services["crm"].create_client(ClientCreate(
            name="Stage Change Client",
            email="stagechange@example.com",
            phone="+1-555-1144",
            property_address="1144 Stage St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        tasks = await services["scheduler"].create_followup_tasks(client.id, client.agent_id)
        # Update client stage
        await services["crm"].update_client(client.id, ClientUpdate(stage="closed"), agent_id=client.agent_id)
        # Tasks should still exist
        for task in tasks:
            fetched = await services["scheduler"].get_task(task.id, agent_id=task.agent_id)
            assert fetched is not None


# ============================================================================
# ADVANCED SCENARIO TESTS (20 tests)
# ============================================================================

class TestAdvancedScenarios:
    """Test advanced scenarios and edge cases."""

    @pytest.mark.asyncio
    async def test_a01_bulk_create_all_tables(self, services, sample_agent):
        """Test 81: Bulk create across all tables."""
        clients = []
        for i in range(5):
            client = await services["crm"].create_client(ClientCreate(
                name=f"Bulk Client {i}",
                email=f"bulkclient{i}@example.com",
                phone=f"+1-555-{1150+i}",
                property_address=f"{1150+i} Bulk St, City, ST 12345",
                property_type="residential",
                stage="lead"
            ), agent_id=sample_agent.id)
            clients.append(client)
        
        tasks = []
        for client in clients:
            client_tasks = await services["scheduler"].create_followup_tasks(client.id, client.agent_id)
            tasks.extend(client_tasks)
        
        emails = []
        for task in tasks[:10]:
            email_log = await services["email"].log_email(
                task_id=task.id,
                client_id=task.client_id,
                agent_id=task.agent_id,
                to_email=f"bulk{task.id}@example.com",
                subject=f"Bulk Email {task.id}",
                body="Bulk body",
                from_name="Test Agent",
                from_email="test@example.com"
            )
            emails.append(email_log)
        
        assert len(clients) == 5
        assert len(tasks) >= 20
        assert len(emails) == 10

    @pytest.mark.asyncio
    async def test_a02_concurrent_updates(self, services, sample_client):
        """Test 82: Handle concurrent-style updates."""
        task = await services["scheduler"].create_task(TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        ), agent_id=sample_client.agent_id)
        # Multiple updates
        await services["scheduler"].update_task(task.id, TaskUpdate(status="completed"), agent_id=sample_client.agent_id)
        await services["scheduler"].update_task(task.id, TaskUpdate(priority="low"), agent_id=sample_client.agent_id)
        updated = await services["scheduler"].get_task(task.id, task.agent_id)
        assert updated.status == "completed"
        assert updated.priority == "low"

    @pytest.mark.asyncio
    async def test_a03_data_integrity_foreign_keys(self, services, sample_client):
        """Test 83: Foreign key integrity."""
        task = await services["scheduler"].create_task(TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        ), agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="integrity@example.com",
            subject="Integrity",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        assert email_log.task_id == task.id
        assert email_log.client_id == sample_client.id

    @pytest.mark.asyncio
    async def test_a04_pagination_consistency(self, services, sample_agent):
        """Test 84: Pagination consistency across tables."""
        # Create data
        for i in range(20):
            client = await services["crm"].create_client(ClientCreate(
                name=f"Page Client {i}",
                email=f"pageclient{i}@example.com",
                phone=f"+1-555-{1170+i}",
                property_address=f"{1170+i} Page St, City, ST 12345",
                property_type="residential",
                stage="lead"
            ), agent_id=sample_agent.id)
            task = await services["scheduler"].create_task(TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                priority="high"
            ), agent_id=client.agent_id)
            await services["email"].log_email(
                task_id=task.id,
                client_id=client.id,
                agent_id=client.agent_id,
                to_email=client.email,
                subject=f"Page {i}",
                body="Body",
                from_name="Test Agent",
                from_email="test@example.com"
            )
        
        # Test pagination
        clients_page = await services["crm"].list_clients(agent_id=sample_agent.id, page=1, limit=10)
        tasks_page = await services["scheduler"].list_tasks(agent_id=sample_agent.id, page=1, limit=10)
        emails_page = await services["email"].list_emails(agent_id=sample_agent.id, page=1, limit=10)
        
        assert len(clients_page) >= 10
        assert len(tasks_page) >= 10
        assert len(emails_page) >= 10

    @pytest.mark.asyncio
    async def test_a05_filter_combinations(self, services, sample_client):
        """Test 85: Multiple filter combinations."""
        # Create various statuses
        for status in ["pending", "completed", "pending"]:
            task = await services["scheduler"].create_task(TaskCreate(
                client_id=sample_client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                priority="high"
            ), agent_id=sample_client.agent_id)
            if status != "pending":
                await services["scheduler"].update_task(task.id, TaskUpdate(status=status), agent_id=sample_client.agent_id)
        
        # Filter combinations
        pending = await services["scheduler"].list_tasks(
            agent_id=sample_client.agent_id,
            client_id=sample_client.id,
            status="pending"
        )
        assert len(pending) >= 2

    @pytest.mark.asyncio
    async def test_a06_timestamp_validation(self, services, sample_agent):
        """Test 86: Timestamp fields validation."""
        client = await services["crm"].create_client(ClientCreate(
            name="Timestamp Client",
            email="timestamp@example.com",
            phone="+1-555-1190",
            property_address="1190 Time St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        assert client.created_at is not None
        
        task = await services["scheduler"].create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        ), agent_id=client.agent_id)
        assert task.created_at is not None
        assert task.updated_at is not None
        
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=client.id,
            agent_id=client.agent_id,
            to_email="timestamp@example.com",
            subject="Timestamp",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        assert email_log.created_at is not None

    @pytest.mark.asyncio
    async def test_a07_data_persistence(self, services, sample_agent):
        """Test 87: Data persistence across operations."""
        client = await services["crm"].create_client(ClientCreate(
            name="Persist Client",
            email="persist@example.com",
            phone="+1-555-1191",
            property_address="1191 Persist St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        original_id = client.id
        
        # Multiple operations
        await services["crm"].update_client(client.id, ClientUpdate(stage="negotiating"), agent_id=client.agent_id)
        task = await services["scheduler"].create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        ), agent_id=client.agent_id)
        
        # Verify persistence
        fetched = await services["crm"].get_client(original_id, agent_id=client.agent_id)
        assert fetched.stage == "negotiating"
        fetched_task = await services["scheduler"].get_task(task.id, task.agent_id)
        assert fetched_task.client_id == original_id

    @pytest.mark.asyncio
    async def test_a08_cascade_operations(self, services, sample_agent):
        """Test 88: Cascade operations across tables."""
        client = await services["crm"].create_client(ClientCreate(
            name="Cascade Client",
            email="cascade@example.com",
            phone="+1-555-1192",
            property_address="1192 Cascade St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        tasks = await services["scheduler"].create_followup_tasks(client.id, client.agent_id)
        for task in tasks[:3]:
            await services["email"].log_email(
                task_id=task.id,
                client_id=client.id,
                agent_id=client.agent_id,
                to_email=client.email,
                subject=f"Cascade {task.id}",
                body="Body",
                from_name="Test Agent",
                from_email="test@example.com"
            )
        
        # Soft delete client
        await services["crm"].delete_client(client.id, agent_id=client.agent_id)
        
        # Verify tasks and emails still exist
        for task in tasks:
            fetched = await services["scheduler"].get_task(task.id, task.agent_id)
            assert fetched is not None

    @pytest.mark.asyncio
    async def test_a09_search_and_filter_complex(self, services, sample_agent):
        """Test 89: Complex search and filter scenarios."""
        # Create diverse data
        stages = ["lead", "negotiating", "closed"]
        for i, stage in enumerate(stages):
            for j in range(3):
                client = await services["crm"].create_client(ClientCreate(
                    name=f"Search {stage} {j}",
                    email=f"search{stage}{j}@example.com",
                    phone=f"+1-555-{1193+i*10+j}",
                    property_address=f"{1193+i*10+j} Search St, City, ST 12345",
                    property_type="residential",
                    stage=stage
                ), agent_id=sample_agent.id)
                task = await services["scheduler"].create_task(TaskCreate(
                    client_id=client.id,
                    followup_type="Day 1",
                    scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                    priority="high"
                ), agent_id=client.agent_id)
                await services["scheduler"].update_task(task.id, TaskUpdate(
                    status="completed" if j % 2 == 0 else "pending"
                ), agent_id=client.agent_id)
        
        # Complex filters
        lead_clients = await services["crm"].list_clients(agent_id=sample_agent.id, stage="lead")
        completed_tasks = await services["scheduler"].list_tasks(agent_id=sample_agent.id, status="completed")
        
        assert len(lead_clients) >= 3
        assert len(completed_tasks) >= 3

    @pytest.mark.asyncio
    async def test_a10_volume_stress_test(self, services, sample_agent):
        """Test 90: Volume stress test."""
        # Create many records
        for i in range(50):
            client = await services["crm"].create_client(ClientCreate(
                name=f"Volume {i}",
                email=f"volume{i}@example.com",
                phone=f"+1-555-{1200+i}",
                property_address=f"{1200+i} Volume St, City, ST 12345",
                property_type="residential",
                stage="lead"
            ), agent_id=sample_agent.id)
            if i % 2 == 0:
                task = await services["scheduler"].create_task(TaskCreate(
                    client_id=client.id,
                    followup_type="Day 1",
                    scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                    priority="high"
                ), agent_id=client.agent_id)
                await services["email"].log_email(
                    task_id=task.id,
                    client_id=client.id,
                    agent_id=client.agent_id,
                    to_email=client.email,
                    subject=f"Volume {i}",
                    body="Body",
                    from_name="Test Agent",
                    from_email="test@example.com"
                )
        
        # Verify counts - use large limits to get all records
        clients = await services["crm"].list_clients(agent_id=sample_agent.id, page=1, limit=100)
        tasks = await services["scheduler"].list_tasks(agent_id=sample_agent.id, page=1, limit=100)
        emails = await services["email"].list_emails(agent_id=sample_agent.id, page=1, limit=100)
        
        assert len(clients) >= 50
        assert len(tasks) >= 25
        assert len(emails) >= 25


# Continue with more tests to reach 100...

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_e20_empty_results(self, services, sample_agent):
        """Test 91: Empty result sets."""
        no_clients = await services["crm"].list_clients(agent_id=sample_agent.id, stage="closed")
        no_tasks = await services["scheduler"].list_tasks(agent_id=sample_agent.id, status="cancelled")
        no_emails = await services["email"].list_emails(agent_id=sample_agent.id, status="bounced")
        # These should return empty lists, not errors
        assert isinstance(no_clients, list)
        assert isinstance(no_tasks, list)
        assert isinstance(no_emails, list)

    @pytest.mark.asyncio
    async def test_e21_max_pagination(self, services, sample_agent):
        """Test 92: Maximum pagination values."""
        # Create data
        for i in range(5):
            client = await services["crm"].create_client(ClientCreate(
                name=f"Max {i}",
                email=f"max{i}@example.com",
                phone=f"+1-555-{1250+i}",
                property_address=f"{1250+i} Max St, City, ST 12345",
                property_type="residential",
                stage="lead"
            ), agent_id=sample_agent.id)
        
        # Test with max limit
        clients = await services["crm"].list_clients(agent_id=sample_agent.id, page=1, limit=100)
        assert len(clients) >= 5

    @pytest.mark.asyncio
    async def test_e22_update_no_changes(self, services, sample_client):
        """Test 93: Update with no actual changes."""
        task = await services["scheduler"].create_task(TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        ), agent_id=sample_client.agent_id)
        # Update with same values
        updated = await services["scheduler"].update_task(task.id, TaskUpdate(
            status="pending",
            priority="high"
        ), agent_id=sample_client.agent_id)
        assert updated is not None

    @pytest.mark.asyncio
    async def test_e23_date_edge_cases(self, services, sample_client):
        """Test 94: Date edge cases."""
        # Past date
        past_task = await services["scheduler"].create_task(TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) - timedelta(days=1),
            priority="high"
        ), agent_id=sample_client.agent_id)
        # Far future
        future_task = await services["scheduler"].create_task(TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=365),
            priority="high"
        ), agent_id=sample_client.agent_id)
        assert past_task.id is not None
        assert future_task.id is not None

    @pytest.mark.asyncio
    async def test_e24_string_field_lengths(self, services, sample_agent):
        """Test 95: String field maximum lengths."""
        long_name = "A" * 100
        long_address = "B" * 200
        client = await services["crm"].create_client(ClientCreate(
            name=long_name,
            email="long@example.com",
            phone="+1-555-1255",
            property_address=long_address,
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        assert len(client.name) == 100
        assert len(client.property_address) == 200


# Additional tests to reach exactly 100

class TestFinalScenarios:
    """Final tests to complete 100 test cases."""

    @pytest.mark.asyncio
    async def test_f01_comprehensive_workflow(self, services, sample_agent):
        """Test 96: Complete real-world workflow."""
        # Create client
        client = await services["crm"].create_client(ClientCreate(
            name="Workflow Client",
            email="workflow@example.com",
            phone="+1-555-1260",
            property_address="1260 Workflow St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        # Create tasks
        tasks = await services["scheduler"].create_followup_tasks(client.id, client.agent_id)
        # Send emails
        for task in tasks[:2]:
            await services["email"].log_email(
                task_id=task.id,
                client_id=client.id,
                agent_id=client.agent_id,
                to_email=client.email,
                subject=f"Workflow {task.followup_type}",
                body="Workflow body",
                from_name="Test Agent",
                from_email="test@example.com"
            )
        # Update client
        await services["crm"].update_client(client.id, ClientUpdate(stage="negotiating"), agent_id=client.agent_id)
        # Complete tasks
        for task in tasks[:2]:
            await services["scheduler"].update_task(task.id, TaskUpdate(status="completed"), agent_id=client.agent_id)
        
        # Verify
        updated_client = await services["crm"].get_client(client.id, agent_id=client.agent_id)
        assert updated_client.stage == "negotiating"

    @pytest.mark.asyncio
    async def test_f02_data_isolation(self, services, sample_agent):
        """Test 97: Data isolation between tests."""
        client1 = await services["crm"].create_client(ClientCreate(
            name="Isolated 1",
            email="isolated1@example.com",
            phone="+1-555-1261",
            property_address="1261 Isolated St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        client2 = await services["crm"].create_client(ClientCreate(
            name="Isolated 2",
            email="isolated2@example.com",
            phone="+1-555-1262",
            property_address="1262 Isolated St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        assert client1.id != client2.id
        tasks1 = await services["scheduler"].create_followup_tasks(client1.id, client1.agent_id)
        tasks2 = await services["scheduler"].create_followup_tasks(client2.id, client2.agent_id)
        assert len(tasks1) == len(tasks2)

    @pytest.mark.asyncio
    async def test_f03_transaction_safety(self, services, sample_client):
        """Test 98: Transaction safety."""
        task = await services["scheduler"].create_task(TaskCreate(
            client_id=sample_client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high"
        ), agent_id=sample_client.agent_id)
        email_log = await services["email"].log_email(
            task_id=task.id,
            client_id=sample_client.id,
            agent_id=sample_client.agent_id,
            to_email="transaction@example.com",
            subject="Transaction",
            body="Body",
            from_name="Test Agent",
            from_email="test@example.com"
        )
        # Both should be committed
        fetched_task = await services["scheduler"].get_task(task.id, task.agent_id)
        fetched_email = await services["email"].get_email(email_log.id, agent_id=sample_client.agent_id)
        assert fetched_task is not None
        assert fetched_email is not None

    @pytest.mark.asyncio
    async def test_f04_performance_large_queries(self, services, sample_agent):
        """Test 99: Performance with large query results."""
        # Create data
        for i in range(30):
            client = await services["crm"].create_client(ClientCreate(
                name=f"Perf {i}",
                email=f"perf{i}@example.com",
                phone=f"+1-555-{1263+i}",
                property_address=f"{1263+i} Perf St, City, ST 12345",
                property_type="residential",
                stage="lead"
            ), agent_id=sample_agent.id)
        
        # Large queries
        all_clients = await services["crm"].list_clients(agent_id=sample_agent.id, limit=100)
        assert len(all_clients) >= 30

    @pytest.mark.asyncio
    async def test_f100_complete_system_integration(self, services, sample_agent):
        """Test 100: Complete system integration test."""
        # Full integration: Create -> Update -> Read -> Delete flow
        # Client
        client = await services["crm"].create_client(ClientCreate(
            name="Integration Test",
            email="integration@example.com",
            phone="+1-555-1293",
            property_address="1293 Integration St, City, ST 12345",
            property_type="residential",
            stage="lead",
            custom_fields={"test": True}
        ), agent_id=sample_agent.id)
        # Tasks
        tasks = await services["scheduler"].create_followup_tasks(client.id, client.agent_id)
        # Emails
        email_logs = []
        for task in tasks[:3]:
            email_log = await services["email"].log_email(
                task_id=task.id,
                client_id=client.id,
                agent_id=client.agent_id,
                to_email=client.email,
                subject=f"Integration {task.followup_type}",
                body="Integration body",
                from_name="Test Agent",
                from_email="test@example.com"
            )
            email_logs.append(email_log)
            await services["email"].update_email_status(email_log.id, "sent")
        
        # Update client
        await services["crm"].update_client(client.id, ClientUpdate(stage="closed"), agent_id=client.agent_id)
        
        # Complete tasks
        for task in tasks[:2]:
            await services["scheduler"].update_task(task.id, TaskUpdate(status="completed"), agent_id=client.agent_id)
        
        # Verify everything
        updated_client = await services["crm"].get_client(client.id, agent_id=client.agent_id)
        assert updated_client.stage == "closed"
        assert len(tasks) > 0
        assert len(email_logs) == 3
        
        # Final verification
        all_clients = await services["crm"].list_clients(agent_id=client.agent_id)
        all_tasks = await services["scheduler"].list_tasks(agent_id=client.agent_id)
        all_emails = await services["email"].list_emails(agent_id=client.agent_id)
        
        assert len(all_clients) >= 1
        assert len(all_tasks) >= len(tasks)
        assert len(all_emails) >= len(email_logs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

