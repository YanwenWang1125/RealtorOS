"""
Integration tests for Client API routes.

This module contains comprehensive integration tests for all client API endpoints,
testing both success cases and error scenarios.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from sqlalchemy import select
from app.models.client import Client
from app.models.task import Task


class TestCreateClient:
    """Test POST /api/clients/ - Create client endpoint."""

    @pytest.mark.asyncio
    async def test_create_client_success(self, client: AsyncClient):
        """Test creating a client with valid data."""
        client_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "555-0123",
            "property_address": "123 Main St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        response = await client.post("/api/clients/", json=client_data)
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["email"] == "jane@example.com"
        assert "id" in data
        assert "created_at" in data
        assert isinstance(data["id"], int)

    @pytest.mark.asyncio
    async def test_create_client_invalid_email(self, client: AsyncClient):
        """Test 422 error with invalid email format."""
        client_data = {
            "name": "John Doe",
            "email": "not-an-email",  # Invalid
            "phone": "555-0123",
            "property_address": "123 Main St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        response = await client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_client_missing_required_fields(self, client: AsyncClient):
        """Test 422 error with missing required fields (name, email)."""
        client_data = {
            "name": "Incomplete Client"
            # Missing: email, property_address, property_type, stage
        }
        response = await client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_client_invalid_stage(self, client: AsyncClient):
        """Test 422 error with invalid stage enum."""
        client_data = {
            "name": "Invalid Stage",
            "email": "invalid@example.com",
            "phone": "555-0123",
            "property_address": "123 Main St, City, ST 12345",
            "property_type": "residential",
            "stage": "invalid_stage"  # Invalid
        }
        response = await client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_client_invalid_property_type(self, client: AsyncClient):
        """Test 422 error with invalid property_type enum."""
        client_data = {
            "name": "Invalid Property",
            "email": "invalid2@example.com",
            "phone": "555-0123",
            "property_address": "123 Main St, City, ST 12345",
            "property_type": "invalid_type",  # Invalid
            "stage": "lead"
        }
        response = await client.post("/api/clients/", json=client_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestListClients:
    """Test GET /api/clients/ - List clients endpoint."""

    @pytest.mark.asyncio
    async def test_list_clients_default_pagination(self, client: AsyncClient):
        """Test list clients with default pagination (page=1, limit=10)."""
        response = await client.get("/api/clients/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_clients_empty(self, client: AsyncClient):
        """Test returns empty array when no clients."""
        response = await client.get("/api/clients/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_list_clients_with_data(self, client: AsyncClient):
        """Test returns array of clients when data exists."""
        # Create some clients
        for i in range(3):
            client_data = {
                "name": f"Client {i}",
                "email": f"client{i}@example.com",
                "phone": f"555-{1000+i}",
                "property_address": f"{i} Main St, City, ST 12345",
                "property_type": "residential",
                "stage": "lead"
            }
            await client.post("/api/clients/", json=client_data)
        
        response = await client.get("/api/clients/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    @pytest.mark.asyncio
    async def test_list_clients_pagination_page1(self, client: AsyncClient):
        """Test pagination: page=1&limit=5 returns first 5."""
        # Create 10 clients
        for i in range(10):
            client_data = {
                "name": f"Page Client {i}",
                "email": f"page{i}@example.com",
                "phone": f"555-{2000+i}",
                "property_address": f"{200+i} Main St, City, ST 12345",
                "property_type": "residential",
                "stage": "lead"
            }
            await client.post("/api/clients/", json=client_data)
        
        response = await client.get("/api/clients/?page=1&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    @pytest.mark.asyncio
    async def test_list_clients_pagination_page2(self, client: AsyncClient):
        """Test pagination: page=2&limit=5 returns next 5."""
        # Create 10 clients
        client_ids = []
        for i in range(10):
            client_data = {
                "name": f"Page2 Client {i}",
                "email": f"page2{i}@example.com",
                "phone": f"555-{3000+i}",
                "property_address": f"{300+i} Main St, City, ST 12345",
                "property_type": "residential",
                "stage": "lead"
            }
            resp = await client.post("/api/clients/", json=client_data)
            client_ids.append(resp.json()["id"])
        
        # Get page 1
        response1 = await client.get("/api/clients/?page=1&limit=5")
        data1 = response1.json()
        ids1 = {item["id"] for item in data1}
        
        # Get page 2
        response2 = await client.get("/api/clients/?page=2&limit=5")
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 5
        ids2 = {item["id"] for item in data2}
        
        # Verify no overlap
        assert ids1.isdisjoint(ids2)

    @pytest.mark.asyncio
    async def test_list_clients_filter_by_stage_lead(self, client: AsyncClient):
        """Test filter by stage: ?stage=lead returns only leads."""
        # Create clients in different stages
        stages = ["lead", "negotiating", "closed"]
        for stage in stages:
            for i in range(2):
                client_data = {
                    "name": f"{stage} Client {i}",
                    "email": f"{stage}{i}@example.com",
                    "phone": f"555-{4000+i}",
                    "property_address": f"{400+i} {stage} St, City, ST 12345",
                    "property_type": "residential",
                    "stage": stage
                }
                await client.post("/api/clients/", json=client_data)
        
        response = await client.get("/api/clients/?stage=lead")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(item["stage"] == "lead" for item in data)

    @pytest.mark.asyncio
    async def test_list_clients_filter_by_stage_closed(self, client: AsyncClient):
        """Test filter by stage: ?stage=closed returns only closed."""
        # Create a closed client
        client_data = {
            "name": "Closed Client",
            "email": "closed@example.com",
            "phone": "555-5000",
            "property_address": "500 Closed St, City, ST 12345",
            "property_type": "residential",
            "stage": "closed"
        }
        await client.post("/api/clients/", json=client_data)
        
        response = await client.get("/api/clients/?stage=closed")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(item["stage"] == "closed" for item in data)

    @pytest.mark.asyncio
    async def test_list_clients_combined_filters(self, client: AsyncClient):
        """Test combined: pagination + filtering."""
        # Create clients
        for i in range(5):
            client_data = {
                "name": f"Combined Client {i}",
                "email": f"combined{i}@example.com",
                "phone": f"555-{6000+i}",
                "property_address": f"{600+i} Combined St, City, ST 12345",
                "property_type": "residential",
                "stage": "lead" if i % 2 == 0 else "negotiating"
            }
            await client.post("/api/clients/", json=client_data)
        
        response = await client.get("/api/clients/?stage=lead&page=1&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert all(item["stage"] == "lead" for item in data)
        assert len(data) <= 2

    @pytest.mark.asyncio
    async def test_list_clients_limit_validation_min(self, client: AsyncClient):
        """Test limit validation: limit must be between 1 and 100."""
        response = await client.get("/api/clients/?limit=0")
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_clients_limit_validation_max(self, client: AsyncClient):
        """Test limit validation: limit must be between 1 and 100."""
        response = await client.get("/api/clients/?limit=101")
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_clients_page_validation(self, client: AsyncClient):
        """Test page validation: page must be >= 1."""
        response = await client.get("/api/clients/?page=0")
        
        assert response.status_code == 422


class TestGetClient:
    """Test GET /api/clients/{client_id} - Get single client endpoint."""

    @pytest.mark.asyncio
    async def test_get_client_success(self, client: AsyncClient):
        """Test get existing client returns 200 with client data."""
        # Create a client first
        client_data = {
            "name": "Get Test Client",
            "email": "get@example.com",
            "phone": "555-7000",
            "property_address": "700 Get St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Get the client
        response = await client.get(f"/api/clients/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == client_id
        assert data["name"] == "Get Test Client"
        assert data["email"] == "get@example.com"

    @pytest.mark.asyncio
    async def test_get_client_not_found(self, client: AsyncClient):
        """Test get non-existent client returns 404."""
        response = await client.get("/api/clients/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Client not found"


class TestUpdateClient:
    """Test PATCH /api/clients/{client_id} - Update client endpoint."""

    @pytest.mark.asyncio
    async def test_update_client_single_field(self, client: AsyncClient):
        """Test update single field (stage)."""
        # Create a client first
        client_data = {
            "name": "Update Test Client",
            "email": "update@example.com",
            "phone": "555-8000",
            "property_address": "800 Update St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Update stage
        update_data = {"stage": "negotiating"}
        response = await client.patch(f"/api/clients/{client_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == "negotiating"

    @pytest.mark.asyncio
    async def test_update_client_multiple_fields(self, client: AsyncClient):
        """Test update multiple fields (stage, notes, property_address)."""
        # Create a client first
        client_data = {
            "name": "Multi Update Client",
            "email": "multiupdate@example.com",
            "phone": "555-9000",
            "property_address": "900 Multi St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Update multiple fields
        update_data = {
            "stage": "under_contract",
            "notes": "Updated notes",
            "property_address": "New Address St, City, ST 54321"
        }
        response = await client.patch(f"/api/clients/{client_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == "under_contract"
        assert data["notes"] == "Updated notes"
        assert data["property_address"] == "New Address St, City, ST 54321"

    @pytest.mark.asyncio
    async def test_update_client_partial_update(self, client: AsyncClient):
        """Test partial update: other fields remain unchanged."""
        # Create a client first
        client_data = {
            "name": "Partial Update Client",
            "email": "partial@example.com",
            "phone": "555-10000",
            "property_address": "1000 Partial St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        original_name = create_response.json()["name"]
        
        # Update only stage
        update_data = {"stage": "negotiating"}
        response = await client.patch(f"/api/clients/{client_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == original_name  # Should remain unchanged
        assert data["stage"] == "negotiating"

    @pytest.mark.asyncio
    async def test_update_client_empty_body(self, client: AsyncClient):
        """Test update with empty body returns existing client."""
        # Create a client first
        client_data = {
            "name": "Empty Update Client",
            "email": "empty@example.com",
            "phone": "555-11000",
            "property_address": "1100 Empty St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        original_name = create_response.json()["name"]
        
        # Update with empty body
        update_data = {}
        response = await client.patch(f"/api/clients/{client_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == original_name

    @pytest.mark.asyncio
    async def test_update_client_not_found(self, client: AsyncClient):
        """Test update non-existent client returns 404."""
        update_data = {"stage": "closed"}
        response = await client.patch("/api/clients/99999", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Client not found"

    @pytest.mark.asyncio
    async def test_update_client_invalid_data(self, client: AsyncClient):
        """Test 422 error with invalid data (bad email)."""
        # Create a client first
        client_data = {
            "name": "Invalid Update Client",
            "email": "invalidupdate@example.com",
            "phone": "555-12000",
            "property_address": "1200 Invalid St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Try to update with invalid email
        update_data = {"email": "not-an-email"}
        response = await client.patch(f"/api/clients/{client_id}", json=update_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestDeleteClient:
    """Test DELETE /api/clients/{client_id} - Delete client endpoint."""

    @pytest.mark.asyncio
    async def test_delete_client_success(self, client: AsyncClient, test_session):
        """Test delete existing client returns {"success": true}."""
        # Create a client first
        client_data = {
            "name": "Delete Test Client",
            "email": "delete@example.com",
            "phone": "555-13000",
            "property_address": "1300 Delete St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Delete the client
        response = await client.delete(f"/api/clients/{client_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_delete_client_soft_delete(self, client: AsyncClient, test_session):
        """Test deleted client has is_deleted=True in database (soft delete)."""
        # Create a client first
        client_data = {
            "name": "Soft Delete Client",
            "email": "softdelete@example.com",
            "phone": "555-14000",
            "property_address": "1400 Soft St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Delete the client
        await client.delete(f"/api/clients/{client_id}")
        
        # Verify soft delete in database
        result = await test_session.execute(
            select(Client).where(Client.id == client_id)
        )
        deleted_client = result.scalar_one_or_none()
        assert deleted_client is not None
        assert deleted_client.is_deleted is True

    @pytest.mark.asyncio
    async def test_delete_client_not_in_list(self, client: AsyncClient):
        """Test deleted client doesn't appear in list endpoint."""
        # Create a client first
        client_data = {
            "name": "List Delete Client",
            "email": "listdelete@example.com",
            "phone": "555-15000",
            "property_address": "1500 List St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Delete the client
        await client.delete(f"/api/clients/{client_id}")
        
        # Verify not in list
        list_response = await client.get("/api/clients/")
        list_data = list_response.json()
        assert client_id not in [item["id"] for item in list_data]

    @pytest.mark.asyncio
    async def test_delete_client_not_found(self, client: AsyncClient):
        """Test delete non-existent client returns 404."""
        response = await client.delete("/api/clients/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Client not found"


class TestGetClientTasks:
    """Test GET /api/clients/{client_id}/tasks - Get client tasks endpoint."""

    @pytest.mark.asyncio
    async def test_get_client_tasks_empty(self, client: AsyncClient):
        """Test returns empty array when client has no tasks."""
        # Create a client first
        client_data = {
            "name": "No Tasks Client",
            "email": "notasks@example.com",
            "phone": "555-16000",
            "property_address": "1600 No Tasks St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Get tasks
        response = await client.get(f"/api/clients/{client_id}/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_client_tasks_with_tasks(self, client: AsyncClient, test_session):
        """Test returns array of tasks when client has tasks."""
        # Create a client first
        client_data = {
            "name": "Tasks Client",
            "email": "tasks@example.com",
            "phone": "555-17000",
            "property_address": "1700 Tasks St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create_response = await client.post("/api/clients/", json=client_data)
        client_id = create_response.json()["id"]
        
        # Create tasks directly in database
        task1 = Task(
            client_id=client_id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high"
        )
        task2 = Task(
            client_id=client_id,
            followup_type="Week 1",
            scheduled_for=datetime.utcnow() + timedelta(days=7),
            status="pending",
            priority="medium"
        )
        test_session.add_all([task1, task2])
        await test_session.commit()
        
        # Get tasks
        response = await client.get(f"/api/clients/{client_id}/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("id" in item for item in data)
        assert all("followup_type" in item for item in data)
        assert all("scheduled_for" in item for item in data)
        assert all("status" in item for item in data)
        assert all("priority" in item for item in data)
        assert all("notes" in item for item in data)

    @pytest.mark.asyncio
    async def test_get_client_tasks_only_for_client(self, client: AsyncClient, test_session):
        """Test only returns tasks for specified client."""
        # Create two clients
        client1_data = {
            "name": "Client 1",
            "email": "client1@example.com",
            "phone": "555-18000",
            "property_address": "1800 Client1 St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        client2_data = {
            "name": "Client 2",
            "email": "client2@example.com",
            "phone": "555-19000",
            "property_address": "1900 Client2 St, City, ST 12345",
            "property_type": "residential",
            "stage": "lead"
        }
        create1 = await client.post("/api/clients/", json=client1_data)
        create2 = await client.post("/api/clients/", json=client2_data)
        client1_id = create1.json()["id"]
        client2_id = create2.json()["id"]
        
        # Create tasks for both clients
        task1 = Task(
            client_id=client1_id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high"
        )
        task2 = Task(
            client_id=client2_id,
            followup_type="Week 1",
            scheduled_for=datetime.utcnow() + timedelta(days=7),
            status="pending",
            priority="medium"
        )
        test_session.add_all([task1, task2])
        await test_session.commit()
        
        # Get tasks for client1 only
        response = await client.get(f"/api/clients/{client1_id}/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["followup_type"] == "Day 1"
        # Note: get_client_tasks doesn't return client_id in response, but we verify
        # the correct tasks are returned by checking the followup_type
        followup_types = [item["followup_type"] for item in data]
        assert "Day 1" in followup_types
        assert "Week 1" not in followup_types  # Should not include client2's tasks

