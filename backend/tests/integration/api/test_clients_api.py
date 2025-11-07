"""
Integration tests for Client API routes.

This module contains comprehensive integration tests for all client API endpoints,
testing both success cases and error scenarios.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.models.client import Client
from app.models.task import Task


class TestCreateClient:
    """Test POST /api/clients/ - Create client endpoint."""

    @pytest.mark.asyncio
    async def test_create_client_success(self, authenticated_client: AsyncClient):
        """Test creating a client with valid data."""
        client_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0100",
            "property_address": "100 Main St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        response = await authenticated_client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["stage"] == "lead"
        assert "id" in data
        assert "created_at" in data
        assert isinstance(data["id"], int)

    @pytest.mark.asyncio
    async def test_create_client_with_notes(self, authenticated_client: AsyncClient):
        """Test creating a client with notes field."""
        client_data = {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+1-555-0101",
            "property_address": "101 Oak Ave, City, ST 12345",
            "property_type": "commercial",
            "stage": "negotiating",
            "notes": "Interested in office space"
        }
        response = await authenticated_client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Interested in office space"
        assert data["stage"] == "negotiating"

    @pytest.mark.asyncio
    async def test_create_client_with_custom_fields(self, authenticated_client: AsyncClient):
        """Test creating a client with custom_fields."""
        client_data = {
            "name": "Custom Client",
            "email": "custom@example.com",
            "phone": "+1-555-0102",
            "property_address": "102 Custom St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead",
            "custom_fields": {
                "budget": "$500k",
                "preferred_contact_time": "evening",
                "referral_source": "website"
            }
        }
        response = await authenticated_client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["custom_fields"]["budget"] == "$500k"
        assert data["custom_fields"]["referral_source"] == "website"

    @pytest.mark.asyncio
    async def test_create_client_missing_required_fields(self, authenticated_client: AsyncClient):
        """Test creating a client with missing required fields."""
        client_data = {
            "name": "Incomplete Client",
            "email": "incomplete@example.com"
            # Missing: property_address, property_type, stage
        }
        response = await authenticated_client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_client_invalid_email(self, authenticated_client: AsyncClient):
        """Test creating a client with invalid email format."""
        client_data = {
            "name": "Invalid Email",
            "email": "not-an-email",
            "phone": "+1-555-0103",
            "property_address": "103 Invalid St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        response = await authenticated_client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_client_invalid_stage(self, authenticated_client: AsyncClient):
        """Test creating a client with invalid stage value."""
        client_data = {
            "name": "Invalid Stage",
            "email": "invalid.stage@example.com",
            "phone": "+1-555-0104",
            "property_address": "104 Invalid St, City, ST 12345",
            "property_type": "residential",
            "stage": "invalid_stage"  # Invalid value
        }
        response = await authenticated_client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_client_invalid_property_type(self, authenticated_client: AsyncClient):
        """Test creating a client with invalid property_type value."""
        client_data = {
            "name": "Invalid Property",
            "email": "invalid.property@example.com",
            "phone": "+1-555-0105",
            "property_address": "105 Invalid St, City, ST 12345",
            "property_type": "invalid_type",  # Invalid value
            "stage": "lead"
        }
        response = await authenticated_client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_client_all_stages(self, authenticated_client: AsyncClient):
        """Test creating clients in all valid stages."""
        stages = ["lead", "negotiating", "under_contract", "closed", "lost"]
        created_ids = []
        
        for i, stage in enumerate(stages):
            client_data = {
                "name": f"Client {stage}",
                "email": f"{stage}{i}@example.com",
                "phone": f"+1-555-{1000+i}",
                "property_address": f"{100+i} {stage} St, City, ST 12345",
                "property_type": "residential",
                "stage": stage
            }
            response = await authenticated_client.post("/api/clients/", json=client_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["stage"] == stage
            created_ids.append(data["id"])
        
        assert len(created_ids) == 5
        assert len(set(created_ids)) == 5  # All unique IDs

    @pytest.mark.asyncio
    async def test_create_client_triggers_task_creation(self, authenticated_client: AsyncClient, db_session):
        """Test that creating a client automatically triggers follow-up task creation."""
        client_data = {
            "name": "Task Trigger Client",
            "email": "tasktrigger@example.com",
            "phone": "+1-555-0200",
            "property_address": "200 Task St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        response = await authenticated_client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 200
        data = response.json()
        client_id = data["id"]
        
        # Verify that follow-up tasks were created automatically
        from sqlalchemy import select
        from app.models.task import Task
        
        stmt = select(Task).where(Task.client_id == client_id)
        result = await db_session.execute(stmt)
        tasks = result.scalars().all()
        
        # Should have 5 tasks based on follow-up schedule
        assert len(tasks) == 5

    @pytest.mark.asyncio
    async def test_create_client_creates_followup_tasks(self, authenticated_client: AsyncClient, db_session):
        """Test that creating a client results in follow-up tasks being created in database."""
        client_data = {
            "name": "Follow-up Client",
            "email": "followup@example.com",
            "phone": "+1-555-0201",
            "property_address": "201 Follow St, City, ST 12345",
            "property_type": "commercial",
            "stage": "lead"
        }
        response = await authenticated_client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 200
        data = response.json()
        client_id = data["id"]
        
        # Verify tasks were created automatically
        from sqlalchemy import select
        from app.models.task import Task
        
        stmt = select(Task).where(Task.client_id == client_id)
        result = await db_session.execute(stmt)
        tasks = result.scalars().all()
        
        # Should have 5 tasks based on follow-up schedule
        assert len(tasks) == 5
        
        # Verify all expected follow-up types are present
        followup_types = {task.followup_type for task in tasks}
        expected_types = {"Day 1", "Day 3", "Week 1", "Week 2", "Month 1"}
        assert followup_types == expected_types
        
        # Verify all tasks are pending
        assert all(task.status == "pending" for task in tasks)
        
        # Verify priorities are set correctly
        priorities = {task.followup_type: task.priority for task in tasks}
        assert priorities["Day 1"] == "high"
        assert priorities["Day 3"] == "medium"
        assert priorities["Week 1"] == "medium"
        assert priorities["Week 2"] == "low"
        assert priorities["Month 1"] == "low"

    @pytest.mark.asyncio
    async def test_create_client_task_creation_all_stages(self, authenticated_client: AsyncClient, db_session):
        """Test that task creation works for clients in all stages."""
        from sqlalchemy import select
        from app.models.task import Task
        
        stages = ["lead", "negotiating", "under_contract", "closed", "lost"]
        client_ids = []
        
        for i, stage in enumerate(stages):
            client_data = {
                "name": f"Stage {stage} Client",
                "email": f"stage{stage}{i}@example.com",
                "phone": f"+1-555-{2000+i}",
                "property_address": f"{200+i} {stage} St, City, ST 12345",
                "property_type": "residential",
                "stage": stage
            }
            response = await authenticated_client.post("/api/clients/", json=client_data)
            
            assert response.status_code == 200
            data = response.json()
            client_id = data["id"]
            client_ids.append(client_id)
            
            # Verify tasks were created for each client
            stmt = select(Task).where(Task.client_id == client_id)
            result = await db_session.execute(stmt)
            tasks = result.scalars().all()
            assert len(tasks) == 5  # Should have 5 tasks per client
        
        # Verify all clients got tasks
        assert len(client_ids) == 5


class TestListClients:
    """Test GET /api/clients/ - List clients endpoint."""

    @pytest.mark.asyncio
    async def test_list_clients_empty(self, authenticated_client: AsyncClient):
        """Test listing clients when database is empty."""
        response = await authenticated_client.get("/api/clients/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_list_clients_basic(self, authenticated_client: AsyncClient):
        """Test listing clients with basic request."""
        # Create multiple clients
        for i in range(5):
            client_data = {
                "name": f"List Client {i}",
                "email": f"list{i}@example.com",
                "phone": f"+1-555-{2000+i}",
                "property_address": f"{200+i} List St, City, ST 12345",
                "property_type": "residential",
                "stage": "lead"
            }
            await authenticated_client.post("/api/clients/", json=client_data)
        
        response = await authenticated_client.get("/api/clients/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 5
        assert all("id" in item for item in data)
        assert all("email" in item for item in data)

    @pytest.mark.asyncio
    async def test_list_clients_pagination(self, authenticated_client: AsyncClient):
        """Test listing clients with pagination."""
        # Create 15 clients
        for i in range(15):
            client_data = {
                "name": f"Page Client {i}",
                "email": f"page{i}@example.com",
                "phone": f"+1-555-{3000+i}",
                "property_address": f"{300+i} Page St, City, ST 12345",
                "property_type": "residential",
                "stage": "lead"
            }
            await authenticated_client.post("/api/clients/", json=client_data)
        
        # Test first page
        response1 = await authenticated_client.get("/api/clients/?page=1&limit=5")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 5
        
        # Test second page
        response2 = await authenticated_client.get("/api/clients/?page=2&limit=5")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 5
        
        # Verify no duplicates across pages
        ids1 = {item["id"] for item in data1}
        ids2 = {item["id"] for item in data2}
        assert ids1.isdisjoint(ids2)

    @pytest.mark.asyncio
    async def test_list_clients_filter_by_stage(self, authenticated_client: AsyncClient):
        """Test filtering clients by stage."""
        # Create clients in different stages
        stages_data = [
            ("lead", 3),
            ("negotiating", 2),
            ("closed", 2)
        ]
        
        for stage, count in stages_data:
            for i in range(count):
                client_data = {
                    "name": f"{stage.title()} Client {i}",
                    "email": f"{stage}{i}@example.com",
                    "phone": f"+1-555-{4000+i}",
                    "property_address": f"{400+i} {stage} St, City, ST 12345",
                    "property_type": "residential",
                    "stage": stage
                }
                await authenticated_client.post("/api/clients/", json=client_data)
        
        # Filter by lead stage
        response = await authenticated_client.get("/api/clients/?stage=lead")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        assert all(item["stage"] == "lead" for item in data)
        
        # Filter by negotiating stage
        response = await authenticated_client.get("/api/clients/?stage=negotiating")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(item["stage"] == "negotiating" for item in data)

    @pytest.mark.asyncio
    async def test_list_clients_pagination_defaults(self, authenticated_client: AsyncClient):
        """Test pagination with default parameters."""
        # Create a few clients
        for i in range(3):
            client_data = {
                "name": f"Default Client {i}",
                "email": f"default{i}@example.com",
                "phone": f"+1-555-{5000+i}",
                "property_address": f"{500+i} Default St, City, ST 12345",
                "property_type": "residential",
                "stage": "lead"
            }
            await authenticated_client.post("/api/clients/", json=client_data)
        
        response = await authenticated_client.get("/api/clients/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_list_clients_invalid_page(self, authenticated_client: AsyncClient):
        """Test pagination with invalid page number."""
        response = await authenticated_client.get("/api/clients/?page=0")
        assert response.status_code == 422  # Validation error for ge=1

    @pytest.mark.asyncio
    async def test_list_clients_invalid_limit(self, authenticated_client: AsyncClient):
        """Test pagination with invalid limit value."""
        response = await authenticated_client.get("/api/clients/?limit=0")
        assert response.status_code == 422  # Validation error for ge=1
        
        response = await authenticated_client.get("/api/clients/?limit=101")
        assert response.status_code == 422  # Validation error for le=100


class TestGetClient:
    """Test GET /api/clients/{client_id} - Get single client endpoint."""

    @pytest.mark.asyncio
    async def test_get_client_success(self, authenticated_client: AsyncClient):
        """Test getting a client by ID."""
        # Create a client first
        client_data = {
            "name": "Get Test Client",
            "email": "get@example.com",
            "phone": "+1-555-6000",
            "property_address": "600 Get St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Get the client
        response = await authenticated_client.get(f"/api/clients/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == client_id
        assert data["name"] == "Get Test Client"
        assert data["email"] == "get@example.com"
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_get_client_not_found(self, authenticated_client: AsyncClient):
        """Test getting a non-existent client returns 404."""
        response = await authenticated_client.get("/api/clients/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_client_invalid_id(self, authenticated_client: AsyncClient):
        """Test getting a client with invalid ID format."""
        response = await authenticated_client.get("/api/clients/not-a-number")
        
        assert response.status_code == 422  # Validation error for int type


class TestUpdateClient:
    """Test PATCH /api/clients/{client_id} - Update client endpoint."""

    @pytest.mark.asyncio
    async def test_update_client_partial(self, authenticated_client: AsyncClient):
        """Test updating a client with partial data."""
        # Create a client first
        client_data = {
            "name": "Original Name",
            "email": "original@example.com",
            "phone": "+1-555-7000",
            "property_address": "700 Original St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Update only name
        update_data = {"name": "Updated Name"}
        response = await authenticated_client.patch(f"/api/clients/{client_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "original@example.com"  # Unchanged

    @pytest.mark.asyncio
    async def test_update_client_stage(self, authenticated_client: AsyncClient):
        """Test updating a client's stage."""
        # Create a client first
        client_data = {
            "name": "Stage Client",
            "email": "stage@example.com",
            "phone": "+1-555-7001",
            "property_address": "701 Stage St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Update stage
        update_data = {"stage": "negotiating"}
        response = await authenticated_client.patch(f"/api/clients/{client_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == "negotiating"

    @pytest.mark.asyncio
    async def test_update_client_multiple_fields(self, authenticated_client: AsyncClient):
        """Test updating multiple fields at once."""
        # Create a client first
        client_data = {
            "name": "Multi Update",
            "email": "multi@example.com",
            "phone": "+1-555-7002",
            "property_address": "702 Multi St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Update multiple fields
        update_data = {
            "phone": "+1-555-9999",
            "stage": "under_contract",
            "notes": "Updated notes"
        }
        response = await authenticated_client.patch(f"/api/clients/{client_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+1-555-9999"
        assert data["stage"] == "under_contract"
        assert data["notes"] == "Updated notes"
        assert data["name"] == "Multi Update"  # Unchanged

    @pytest.mark.asyncio
    async def test_update_client_custom_fields(self, authenticated_client: AsyncClient):
        """Test updating client custom_fields."""
        # Create a client first
        client_data = {
            "name": "Custom Update",
            "email": "customupdate@example.com",
            "phone": "+1-555-7003",
            "property_address": "703 Custom St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead",
            "custom_fields": {"old": "value"}
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Update custom_fields
        update_data = {"custom_fields": {"new": "value", "updated": True}}
        response = await authenticated_client.patch(f"/api/clients/{client_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["custom_fields"] == {"new": "value", "updated": True}

    @pytest.mark.asyncio
    async def test_update_client_not_found(self, authenticated_client: AsyncClient):
        """Test updating a non-existent client returns 404."""
        update_data = {"name": "Won't Work"}
        response = await authenticated_client.patch("/api/clients/99999", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_client_invalid_stage(self, authenticated_client: AsyncClient):
        """Test updating with invalid stage value."""
        # Create a client first
        client_data = {
            "name": "Invalid Update",
            "email": "invalid.update@example.com",
            "phone": "+1-555-7004",
            "property_address": "704 Invalid St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Try to update with invalid stage
        update_data = {"stage": "invalid_stage"}
        response = await authenticated_client.patch(f"/api/clients/{client_id}", json=update_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestDeleteClient:
    """Test DELETE /api/clients/{client_id} - Delete client endpoint."""

    @pytest.mark.asyncio
    async def test_delete_client_success(self, authenticated_client: AsyncClient, db_session):
        """Test soft deleting a client."""
        # Create a client first
        client_data = {
            "name": "Delete Client",
            "email": "delete@example.com",
            "phone": "+1-555-8000",
            "property_address": "800 Delete St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Delete the client
        response = await authenticated_client.delete(f"/api/clients/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify client is soft deleted (not in list)
        list_response = await authenticated_client.get("/api/clients/")
        list_data = list_response.json()
        assert client_id not in [item["id"] for item in list_data]
        
        # Verify client still exists in database with is_deleted=True
        result = await db_session.execute(
            select(Client).where(Client.id == client_id)
        )
        client = result.scalar_one_or_none()
        assert client is not None
        assert client.is_deleted is True

    @pytest.mark.asyncio
    async def test_delete_client_not_found(self, authenticated_client: AsyncClient):
        """Test deleting a non-existent client returns 404."""
        response = await authenticated_client.delete("/api/clients/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_client_then_get_returns_404(self, authenticated_client: AsyncClient):
        """Test that getting a deleted client returns 404."""
        # Create and delete a client
        client_data = {
            "name": "Deleted Get",
            "email": "deleted.get@example.com",
            "phone": "+1-555-8001",
            "property_address": "801 Deleted St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Delete the client
        await authenticated_client.delete(f"/api/clients/{client_id}")
        
        # Try to get the deleted client
        response = await authenticated_client.get(f"/api/clients/{client_id}")
        assert response.status_code == 404


class TestGetClientTasks:
    """Test GET /api/clients/{client_id}/tasks - Get client tasks endpoint."""

    @pytest.mark.asyncio
    async def test_get_client_tasks_empty(self, authenticated_client: AsyncClient):
        """Test getting tasks for a client - tasks are automatically created."""
        # Create a client first
        client_data = {
            "name": "No Tasks Client",
            "email": "notasks@example.com",
            "phone": "+1-555-9000",
            "property_address": "900 No Tasks St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Get tasks - should have 5 automatically created tasks
        response = await authenticated_client.get(f"/api/clients/{client_id}/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Tasks are automatically created when a client is created
        assert len(data) == 5

    @pytest.mark.asyncio
    async def test_get_client_tasks_with_tasks(self, authenticated_client: AsyncClient, db_session):
        """Test getting tasks for a client that has tasks."""
        # Create a client first
        client_data = {
            "name": "Tasks Client",
            "email": "tasks@example.com",
            "phone": "+1-555-9001",
            "property_address": "901 Tasks St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        client_json = create_response.json()
        client_id = client_json["id"]
        agent_id = client_json["agent_id"]
        
        # Tasks are automatically created when client is created (5 tasks)
        # Add 2 more tasks manually to verify the endpoint returns all tasks
        # Use valid followup_type values that match the schema pattern
        task1 = Task(
            agent_id=agent_id,
            client_id=client_id,
            followup_type="Custom",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            status="pending",
            priority="high"
        )
        task2 = Task(
            agent_id=agent_id,
            client_id=client_id,
            followup_type="Custom",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=7),
            status="pending",
            priority="medium"
        )
        db_session.add_all([task1, task2])
        await db_session.commit()
        
        # Get tasks - should have 5 automatic + 2 manual = 7 total
        response = await authenticated_client.get(f"/api/clients/{client_id}/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 7  # 5 automatic tasks + 2 manual tasks
        assert all("id" in item for item in data)
        assert all("followup_type" in item for item in data)
        assert all("status" in item for item in data)
        assert all("priority" in item for item in data)
        
        # Verify task types
        followup_types = [item["followup_type"] for item in data]
        assert "Day 1" in followup_types
        assert "Week 1" in followup_types

    @pytest.mark.asyncio
    async def test_get_client_tasks_not_found(self, authenticated_client: AsyncClient):
        """Test getting tasks for non-existent client."""
        response = await authenticated_client.get("/api/clients/99999/tasks")
        
        # Note: This endpoint doesn't explicitly check if client exists
        # It will return an empty list if client doesn't exist
        # This behavior may vary based on implementation
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestClientAPIIntegration:
    """Integration tests combining multiple operations."""

    @pytest.mark.asyncio
    async def test_client_full_lifecycle(self, authenticated_client: AsyncClient):
        """Test complete client lifecycle: create, read, update, delete."""
        # Create
        client_data = {
            "name": "Lifecycle Client",
            "email": "lifecycle@example.com",
            "phone": "+1-555-10000",
            "property_address": "10000 Lifecycle St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await authenticated_client.post("/api/clients/", json=client_data)
        assert create_response.status_code == 200
        client_id = create_response.json()["id"]
        
        # Read
        get_response = await authenticated_client.get(f"/api/clients/{client_id}")
        assert get_response.status_code == 200
        assert get_response.json()["stage"] == "lead"
        
        # Update - progress through stages
        update_response1 = await authenticated_client.patch(
            f"/api/clients/{client_id}",
            json={"stage": "negotiating"}
        )
        assert update_response1.status_code == 200
        assert update_response1.json()["stage"] == "negotiating"
        
        update_response2 = await authenticated_client.patch(
            f"/api/clients/{client_id}",
            json={"stage": "closed"}
        )
        assert update_response2.status_code == 200
        assert update_response2.json()["stage"] == "closed"
        
        # Delete
        delete_response = await authenticated_client.delete(f"/api/clients/{client_id}")
        assert delete_response.status_code == 200
        
        # Verify deleted
        get_response = await authenticated_client.get(f"/api/clients/{client_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_clients_excludes_deleted(self, authenticated_client: AsyncClient):
        """Test that listing clients excludes soft-deleted clients."""
        # Create multiple clients
        client_ids = []
        for i in range(5):
            client_data = {
                "name": f"List Delete {i}",
                "email": f"listdelete{i}@example.com",
                "phone": f"+1-555-{11000+i}",
                "property_address": f"{1100+i} List Delete St, City, ST 12345",
                "property_type": "residential",
                "stage": "lead"
            }
            create_response = await authenticated_client.post("/api/clients/", json=client_data)
            client_ids.append(create_response.json()["id"])
        
        # Delete some clients
        await authenticated_client.delete(f"/api/clients/{client_ids[1]}")
        await authenticated_client.delete(f"/api/clients/{client_ids[3]}")
        
        # List clients - should not include deleted ones
        list_response = await authenticated_client.get("/api/clients/")
        list_data = list_response.json()
        listed_ids = [item["id"] for item in list_data]
        
        assert client_ids[1] not in listed_ids
        assert client_ids[3] not in listed_ids
        assert client_ids[0] in listed_ids
        assert client_ids[2] in listed_ids
        assert client_ids[4] in listed_ids

