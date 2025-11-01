"""
Integration tests for Emails API routes.

This module contains comprehensive integration tests for all email API endpoints,
testing both success cases and error scenarios with mocked external services.
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from datetime import datetime, timedelta
from sqlalchemy import select
from app.models.client import Client
from app.models.task import Task
from app.models.email_log import EmailLog


class TestListEmails:
    """Test GET /api/emails/ - List emails endpoint."""

    @pytest.mark.asyncio
    async def test_list_emails_default_pagination(self, client: AsyncClient):
        """Test list emails with default pagination."""
        response = await client.get("/api/emails/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_emails_empty(self, client: AsyncClient):
        """Test returns empty array when no emails."""
        response = await client.get("/api/emails/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_list_emails_filter_by_client_id(self, client: AsyncClient, test_session):
        """Test filter by client_id."""
        # Create clients and emails
        client1 = Client(
            name="Email Client 1",
            email="email1@example.com",
            property_address="111 Email1 St",
            property_type="residential",
            stage="lead"
        )
        client2 = Client(
            name="Email Client 2",
            email="email2@example.com",
            property_address="222 Email2 St",
            property_type="residential",
            stage="lead"
        )
        test_session.add_all([client1, client2])
        await test_session.commit()
        
        task1 = Task(
            client_id=client1.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high"
        )
        task2 = Task(
            client_id=client2.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high"
        )
        test_session.add_all([task1, task2])
        await test_session.commit()
        
        email1 = EmailLog(
            task_id=task1.id,
            client_id=client1.id,
            to_email="recipient1@example.com",
            subject="Test Email 1",
            body="Body 1",
            status="sent"
        )
        email2 = EmailLog(
            task_id=task2.id,
            client_id=client2.id,
            to_email="recipient2@example.com",
            subject="Test Email 2",
            body="Body 2",
            status="sent"
        )
        test_session.add_all([email1, email2])
        await test_session.commit()
        
        response = await client.get(f"/api/emails/?client_id={client1.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(item["client_id"] == client1.id for item in data)

    @pytest.mark.asyncio
    async def test_list_emails_filter_by_status(self, client: AsyncClient, test_session):
        """Test filter by status (sent, delivered, opened)."""
        # Create client and task
        client_obj = Client(
            name="Status Client",
            email="status@example.com",
            property_address="333 Status St",
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
        
        # Create emails with different statuses
        email1 = EmailLog(
            task_id=task.id,
            client_id=client_obj.id,
            to_email="sent@example.com",
            subject="Sent Email",
            body="Body",
            status="sent"
        )
        email2 = EmailLog(
            task_id=task.id,
            client_id=client_obj.id,
            to_email="delivered@example.com",
            subject="Delivered Email",
            body="Body",
            status="delivered"
        )
        email3 = EmailLog(
            task_id=task.id,
            client_id=client_obj.id,
            to_email="opened@example.com",
            subject="Opened Email",
            body="Body",
            status="opened"
        )
        test_session.add_all([email1, email2, email3])
        await test_session.commit()
        
        response = await client.get("/api/emails/?status=sent")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(item["status"] == "sent" for item in data)

    @pytest.mark.asyncio
    async def test_list_emails_pagination(self, client: AsyncClient, test_session):
        """Test pagination works."""
        # Create client and task
        client_obj = Client(
            name="Pagination Email Client",
            email="paginationemail@example.com",
            property_address="444 Pagination Email St",
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
        
        # Create multiple emails
        for i in range(10):
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
        
        response = await client.get("/api/emails/?page=1&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5


class TestGetEmail:
    """Test GET /api/emails/{email_id} - Get single email endpoint."""

    @pytest.mark.asyncio
    async def test_get_email_success(self, client: AsyncClient, test_session):
        """Test get existing email returns 200."""
        # Create client, task, and email
        client_obj = Client(
            name="Get Email Client",
            email="getemail@example.com",
            property_address="555 Get Email St",
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
        
        response = await client.get(f"/api/emails/{email.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == email.id
        assert data["subject"] == "Test Subject"
        assert data["to_email"] == "recipient@example.com"

    @pytest.mark.asyncio
    async def test_get_email_not_found(self, client: AsyncClient):
        """Test get non-existent email returns 404."""
        response = await client.get("/api/emails/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Email not found"


class TestPreviewEmail:
    """Test POST /api/emails/preview - Preview email endpoint."""

    @pytest.mark.asyncio
    @patch('app.services.ai_agent.AIAgent.generate_email_preview')
    async def test_preview_email_with_mocked_openai(self, mock_preview, client: AsyncClient, test_session):
        """Test preview email with mocked OpenAI."""
        # Create client and task
        client_obj = Client(
            name="Preview Client",
            email="preview@example.com",
            property_address="666 Preview St",
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
        
        # Mock AI agent response
        mock_preview.return_value = {
            "subject": "Mocked Subject",
            "body": "Mocked Body",
            "preview": "Mocked Preview"
        }
        
        # Make preview request
        preview_data = {
            "client_id": client_obj.id,
            "task_id": task.id
        }
        response = await client.post("/api/emails/preview", json=preview_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["subject"] == "Mocked Subject"
        assert data["body"] == "Mocked Body"
        mock_preview.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.ai_agent.AIAgent.generate_email_preview')
    async def test_preview_email_does_not_create_email_log(self, mock_preview, client: AsyncClient, test_session):
        """Test does NOT create email_log record."""
        # Create client and task
        client_obj = Client(
            name="Preview No Log Client",
            email="previewnolog@example.com",
            property_address="777 Preview No Log St",
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
        
        # Count emails before
        before_result = await test_session.execute(select(EmailLog))
        before_count = len(before_result.scalars().all())
        
        # Mock AI agent response
        mock_preview.return_value = {
            "subject": "Mocked Subject",
            "body": "Mocked Body"
        }
        
        # Make preview request
        preview_data = {
            "client_id": client_obj.id,
            "task_id": task.id
        }
        response = await client.post("/api/emails/preview", json=preview_data)
        
        assert response.status_code == 200
        
        # Count emails after
        after_result = await test_session.execute(select(EmailLog))
        after_count = len(after_result.scalars().all())
        
        # Should not have created any email log
        assert after_count == before_count

    @pytest.mark.asyncio
    async def test_preview_email_invalid_client_id(self, client: AsyncClient, test_session):
        """Test 422 error with invalid client_id."""
        # Create a task but not the client
        task = Task(
            client_id=99999,  # Non-existent client
            followup_type="Day 1",
            scheduled_for=datetime.utcnow() + timedelta(days=1),
            status="pending",
            priority="high"
        )
        test_session.add(task)
        await test_session.commit()
        
        preview_data = {
            "client_id": 99999,
            "task_id": task.id
        }
        response = await client.post("/api/emails/preview", json=preview_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestSendEmail:
    """Test POST /api/emails/send - Send email endpoint."""

    @pytest.mark.asyncio
    @patch('app.services.email_service.EmailService.send_email')
    async def test_send_email_with_mocked_sendgrid(self, mock_send, client: AsyncClient, test_session):
        """Test send email with mocked SendGrid."""
        # Create client and task
        client_obj = Client(
            name="Send Email Client",
            email="sendemail@example.com",
            property_address="888 Send Email St",
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
        
        # Mock SendGrid response
        from app.schemas.email_schema import EmailResponse
        mock_email_response = EmailResponse(
            id=1,
            task_id=task.id,
            client_id=client_obj.id,
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test Body",
            status="sent",
            created_at=datetime.utcnow()
        )
        mock_send.return_value = mock_email_response
        
        # Make send request
        send_data = {
            "client_id": client_obj.id,
            "task_id": task.id,
            "to_email": "recipient@example.com",
            "subject": "Test Subject",
            "body": "Test Body"
        }
        response = await client.post("/api/emails/send", json=send_data)
        
        # Note: Since we're mocking the service method, it won't actually call SendGrid
        # The actual implementation will create an email_log, but here we're testing the route
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_email_creates_email_log(self, client: AsyncClient, test_session):
        """Test creates email_log record with status='sent'."""
        # Create client and task
        client_obj = Client(
            name="Email Log Client",
            email="emaillog@example.com",
            property_address="999 Email Log St",
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
        
        # Mock SendGrid to avoid actual API call
        with patch('sendgrid.SendGridAPIClient.send') as mock_sendgrid:
            # Mock successful SendGrid response
            mock_response = type('MockResponse', (), {
                'headers': {'X-Message-Id': 'test-message-id'},
                'status_code': 202
            })()
            mock_sendgrid.return_value = mock_response
            
            # Make send request
            send_data = {
                "client_id": client_obj.id,
                "task_id": task.id,
                "to_email": "recipient@example.com",
                "subject": "Test Subject",
                "body": "Test Body"
            }
            response = await client.post("/api/emails/send", json=send_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify email_log was created
            result = await test_session.execute(
                select(EmailLog).where(EmailLog.id == data["id"])
            )
            email_log = result.scalar_one_or_none()
            assert email_log is not None
            assert email_log.status == "sent"

    @pytest.mark.asyncio
    async def test_send_email_invalid_email_address(self, client: AsyncClient, test_session):
        """Test 422 error with invalid email address."""
        # Create client and task
        client_obj = Client(
            name="Invalid Email Client",
            email="invalidemail@example.com",
            property_address="1000 Invalid Email St",
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
        
        # Try to send with invalid email
        send_data = {
            "client_id": client_obj.id,
            "task_id": task.id,
            "to_email": "not-an-email",  # Invalid
            "subject": "Test Subject",
            "body": "Test Body"
        }
        response = await client.post("/api/emails/send", json=send_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_send_email_handles_sendgrid_errors(self, client: AsyncClient, test_session):
        """Test handles SendGrid errors gracefully."""
        # Create client and task
        client_obj = Client(
            name="Error Client",
            email="error@example.com",
            property_address="1100 Error St",
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
        
        # Mock SendGrid to raise an error
        with patch('sendgrid.SendGridAPIClient.send') as mock_sendgrid:
            mock_sendgrid.side_effect = Exception("SendGrid API Error")
            
            send_data = {
                "client_id": client_obj.id,
                "task_id": task.id,
                "to_email": "recipient@example.com",
                "subject": "Test Subject",
                "body": "Test Body"
            }
            response = await client.post("/api/emails/send", json=send_data)
            
            # Should still return 200, but email_log should have status='failed'
            assert response.status_code == 200
            data = response.json()
            
            # Verify email_log was created with failed status
            result = await test_session.execute(
                select(EmailLog).where(EmailLog.id == data["id"])
            )
            email_log = result.scalar_one_or_none()
            assert email_log is not None
            assert email_log.status == "failed"

