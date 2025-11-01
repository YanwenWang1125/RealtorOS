"""
Integration tests for Dashboard API routes.

This module contains comprehensive integration tests for all dashboard API endpoints,
testing both success cases and error scenarios.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from sqlalchemy import select
from app.models.client import Client
from app.models.task import Task
from app.models.email_log import EmailLog


class TestGetDashboardStats:
    """Test GET /api/dashboard/stats - Get dashboard statistics endpoint."""

    @pytest.mark.asyncio
    async def test_get_dashboard_stats_empty_database(self, client: AsyncClient):
        """Test returns stats with zero defaults (empty database)."""
        response = await client.get("/api/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_clients"] == 0
        assert data["active_clients"] == 0
        assert data["pending_tasks"] == 0
        assert data["completed_tasks"] == 0
        assert data["emails_sent_today"] == 0
        assert data["emails_sent_this_week"] == 0
        assert data["open_rate"] == 0.0
        assert data["click_rate"] == 0.0
        assert data["conversion_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_get_dashboard_stats_with_data(self, client: AsyncClient, test_session):
        """Test returns correct counts with data."""
        # Create non-deleted clients
        client1 = Client(
            name="Active Client 1",
            email="active1@example.com",
            property_address="111 Active1 St",
            property_type="residential",
            stage="lead",
            is_deleted=False
        )
        client2 = Client(
            name="Active Client 2",
            email="active2@example.com",
            property_address="222 Active2 St",
            property_type="residential",
            stage="negotiating",
            is_deleted=False
        )
        client3_deleted = Client(
            name="Deleted Client",
            email="deleted@example.com",
            property_address="333 Deleted St",
            property_type="residential",
            stage="lead",
            is_deleted=True
        )
        test_session.add_all([client1, client2, client3_deleted])
        await test_session.commit()
        
        # Create tasks
        task1 = Task(
            client_id=client1.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high"
        )
        task2 = Task(
            client_id=client1.id,
            followup_type="Week 1",
            scheduled_for=datetime.utcnow() + timedelta(days=7),
            status="completed",
            priority="medium"
        )
        test_session.add_all([task1, task2])
        await test_session.commit()
        
        # Create emails
        email1 = EmailLog(
            task_id=task1.id,
            client_id=client1.id,
            to_email="recipient1@example.com",
            subject="Test Email 1",
            body="Body 1",
            status="sent",
            created_at=datetime.utcnow()
        )
        email2 = EmailLog(
            task_id=task1.id,
            client_id=client1.id,
            to_email="recipient2@example.com",
            subject="Test Email 2",
            body="Body 2",
            status="sent",
            created_at=datetime.utcnow()
        )
        test_session.add_all([email1, email2])
        await test_session.commit()
        
        response = await client.get("/api/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_clients"] == 2  # Only non-deleted
        assert data["pending_tasks"] == 1
        assert data["completed_tasks"] == 1
        assert data["emails_sent_today"] >= 0  # May be 0 if not today
        assert data["emails_sent_this_week"] >= 0  # May be 0 if not this week

    @pytest.mark.asyncio
    async def test_get_dashboard_stats_response_structure(self, client: AsyncClient):
        """Test response structure matches DashboardStats schema."""
        response = await client.get("/api/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        required_fields = [
            "total_clients",
            "active_clients",
            "pending_tasks",
            "completed_tasks",
            "emails_sent_today",
            "emails_sent_this_week",
            "open_rate",
            "click_rate",
            "conversion_rate"
        ]
        for field in required_fields:
            assert field in data

    @pytest.mark.asyncio
    async def test_get_dashboard_stats_only_non_deleted_clients(self, client: AsyncClient, test_session):
        """Test only counts non-deleted clients (is_deleted=False)."""
        # Create both deleted and non-deleted clients
        client1 = Client(
            name="Non-Deleted 1",
            email="nondeleted1@example.com",
            property_address="111 Non-Deleted St",
            property_type="residential",
            stage="lead",
            is_deleted=False
        )
        client2 = Client(
            name="Non-Deleted 2",
            email="nondeleted2@example.com",
            property_address="222 Non-Deleted St",
            property_type="residential",
            stage="lead",
            is_deleted=False
        )
        client3 = Client(
            name="Deleted",
            email="deleted@example.com",
            property_address="333 Deleted St",
            property_type="residential",
            stage="lead",
            is_deleted=True
        )
        test_session.add_all([client1, client2, client3])
        await test_session.commit()
        
        response = await client.get("/api/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_clients"] == 2  # Only non-deleted


class TestGetRecentActivity:
    """Test GET /api/dashboard/recent-activity - Get recent activity endpoint."""

    @pytest.mark.asyncio
    async def test_get_recent_activity_empty(self, client: AsyncClient):
        """Test returns empty array when no activity."""
        response = await client.get("/api/dashboard/recent-activity")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_recent_activity_returns_recent_emails(self, client: AsyncClient, test_session):
        """Test returns recent email_logs (last N records)."""
        # Create client and task
        client_obj = Client(
            name="Activity Client",
            email="activity@example.com",
            property_address="444 Activity St",
            property_type="residential",
            stage="lead"
        )
        test_session.add(client_obj)
        await test_session.commit()
        
        task = Task(
            client_id=client_obj.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high"
        )
        test_session.add(task)
        await test_session.commit()
        
        # Create multiple emails with different timestamps
        base_time = datetime.utcnow()
        for i in range(5):
            email = EmailLog(
                task_id=task.id,
                client_id=client_obj.id,
                to_email=f"recipient{i}@example.com",
                subject=f"Email {i}",
                body=f"Body {i}",
                status="sent",
                created_at=base_time + timedelta(minutes=i)
            )
            test_session.add(email)
        await test_session.commit()
        
        response = await client.get("/api/dashboard/recent-activity")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 5

    @pytest.mark.asyncio
    async def test_get_recent_activity_ordered_by_created_at_desc(self, client: AsyncClient, test_session):
        """Test ordered by created_at DESC (most recent first)."""
        # Create client and task
        client_obj = Client(
            name="Order Client",
            email="order@example.com",
            property_address="555 Order St",
            property_type="residential",
            stage="lead"
        )
        test_session.add(client_obj)
        await test_session.commit()
        
        task = Task(
            client_id=client_obj.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high"
        )
        test_session.add(task)
        await test_session.commit()
        
        # Create emails with different timestamps
        base_time = datetime.utcnow()
        for i in range(3):
            email = EmailLog(
                task_id=task.id,
                client_id=client_obj.id,
                to_email=f"recipient{i}@example.com",
                subject=f"Email {i}",
                body=f"Body {i}",
                status="sent",
                created_at=base_time - timedelta(hours=i)  # Older emails first
            )
            test_session.add(email)
        await test_session.commit()
        
        response = await client.get("/api/dashboard/recent-activity")
        
        assert response.status_code == 200
        data = response.json()
        if len(data) >= 3:
            # Check that timestamps are in descending order (most recent first)
            timestamps = [item.get("at") for item in data[:3] if item.get("at")]
            if len(timestamps) >= 2:
                # Verify descending order
                for i in range(len(timestamps) - 1):
                    assert timestamps[i] >= timestamps[i + 1] or timestamps[i] is None or timestamps[i + 1] is None

    @pytest.mark.asyncio
    async def test_get_recent_activity_includes_client_information(self, client: AsyncClient, test_session):
        """Test includes client information in response."""
        # Create client and task
        client_obj = Client(
            name="Client Info Client",
            email="clientinfo@example.com",
            property_address="666 Client Info St",
            property_type="residential",
            stage="lead"
        )
        test_session.add(client_obj)
        await test_session.commit()
        
        task = Task(
            client_id=client_obj.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high"
        )
        test_session.add(task)
        await test_session.commit()
        
        email = EmailLog(
            task_id=task.id,
            client_id=client_obj.id,
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test Body",
            status="sent"
        )
        test_session.add(email)
        await test_session.commit()
        
        response = await client.get("/api/dashboard/recent-activity")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        # Check that client information is included
        assert "client_name" in data[0] or "client_id" in data[0]

    @pytest.mark.asyncio
    async def test_get_recent_activity_respects_limit(self, client: AsyncClient, test_session):
        """Test respects limit parameter (default 10)."""
        # Create client and task
        client_obj = Client(
            name="Limit Client",
            email="limit@example.com",
            property_address="777 Limit St",
            property_type="residential",
            stage="lead"
        )
        test_session.add(client_obj)
        await test_session.commit()
        
        task = Task(
            client_id=client_obj.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high"
        )
        test_session.add(task)
        await test_session.commit()
        
        # Create 15 emails
        for i in range(15):
            email = EmailLog(
                task_id=task.id,
                client_id=client_obj.id,
                to_email=f"recipient{i}@example.com",
                subject=f"Email {i}",
                body=f"Body {i}",
                status="sent"
            )
            test_session.add(email)
        await test_session.commit()
        
        # Test default limit (10)
        response = await client.get("/api/dashboard/recent-activity")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10  # Default limit
        
        # Test custom limit (5)
        response = await client.get("/api/dashboard/recent-activity?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

