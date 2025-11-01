"""
Tests for email service.

This module contains unit tests for the email service
in the RealtorOS system.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from app.services.email_service import EmailService
from app.services.scheduler_service import SchedulerService
from app.services.crm_service import CRMService
from app.schemas.email_schema import EmailSendRequest
from app.schemas.client_schema import ClientCreate
from app.schemas.task_schema import TaskCreate

class TestEmailService:
    """Test cases for email service."""
    
    @pytest.mark.asyncio
    async def test_log_email(self, test_session):
        """Test logging an email before sending."""
        # Create client and task first
        crm = CRMService(test_session)
        scheduler = SchedulerService(test_session)
        email_service = EmailService(test_session)
        
        client = await crm.create_client(ClientCreate(
            name="Email Test Client",
            email="emailtest@example.com",
            phone="+1-555-0000",
            property_address="100 Email St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ))
        
        task = await scheduler.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow(),
            priority="high"
        ))
        
        # Log email
        email_log = await email_service.log_email(
            task_id=task.id,
            client_id=client.id,
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test body content"
        )
        
        assert email_log.id is not None
        assert email_log.status == "queued"
        assert email_log.to_email == "recipient@example.com"
        assert email_log.subject == "Test Subject"
    
    @pytest.mark.asyncio
    async def test_get_email(self, test_session):
        """Test getting an email by ID."""
        crm = CRMService(test_session)
        scheduler = SchedulerService(test_session)
        email_service = EmailService(test_session)
        
        client = await crm.create_client(ClientCreate(
            name="Get Email Client",
            email="getemail@example.com",
            phone="+1-555-0001",
            property_address="101 Email St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ))
        
        task = await scheduler.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow(),
            priority="high"
        ))
        
        email_log = await email_service.log_email(
            task_id=task.id,
            client_id=client.id,
            to_email="get@example.com",
            subject="Get Test",
            body="Get body"
        )
        
        fetched = await email_service.get_email(email_log.id)
        assert fetched is not None
        assert fetched.id == email_log.id
        assert fetched.to_email == "get@example.com"
    
    @pytest.mark.asyncio
    async def test_list_emails(self, test_session):
        """Test listing emails with pagination and filtering."""
        crm = CRMService(test_session)
        scheduler = SchedulerService(test_session)
        email_service = EmailService(test_session)
        
        client = await crm.create_client(ClientCreate(
            name="List Email Client",
            email="listemail@example.com",
            phone="+1-555-0002",
            property_address="102 Email St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ))
        
        # Create multiple emails
        for i in range(5):
            task = await scheduler.create_task(TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.utcnow(),
                priority="high"
            ))
            await email_service.log_email(
                task_id=task.id,
                client_id=client.id,
                to_email=f"list{i}@example.com",
                subject=f"List {i}",
                body=f"Body {i}"
            )
        
        # List all emails
        emails = await email_service.list_emails()
        assert len(emails) >= 5
        
        # Filter by client
        client_emails = await email_service.list_emails(client_id=client.id)
        assert len(client_emails) >= 5
        assert all(e.client_id == client.id for e in client_emails)
    
    @pytest.mark.asyncio
    async def test_update_email_status(self, test_session):
        """Test updating email status."""
        crm = CRMService(test_session)
        scheduler = SchedulerService(test_session)
        email_service = EmailService(test_session)
        
        client = await crm.create_client(ClientCreate(
            name="Update Email Client",
            email="updateemail@example.com",
            phone="+1-555-0003",
            property_address="103 Email St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ))
        
        task = await scheduler.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow(),
            priority="high"
        ))
        
        email_log = await email_service.log_email(
            task_id=task.id,
            client_id=client.id,
            to_email="update@example.com",
            subject="Update Test",
            body="Body"
        )
        
        # Update status
        result = await email_service.update_email_status(email_log.id, "sent", sendgrid_message_id="msg-123")
        assert result is True
        
        # Verify update
        updated = await email_service.get_email(email_log.id)
        assert updated.status == "sent"
        assert updated.sendgrid_message_id == "msg-123"
    
    @pytest.mark.asyncio
    @patch('app.services.email_service.SendGridAPIClient')
    async def test_sendgrid_integration(self, mock_sg_class, test_session):
        """Test SendGrid API integration."""
        # Mock SendGrid response
        mock_response = Mock()
        mock_response.headers = {"X-Message-Id": "sg-123456"}
        mock_sg_instance = Mock()
        mock_sg_instance.send = Mock(return_value=mock_response)
        mock_sg_class.return_value = mock_sg_instance
        
        # Mock settings
        with patch('app.services.email_service.settings') as mock_settings:
            mock_settings.SENDGRID_API_KEY = "test-key"
            mock_settings.SENDGRID_FROM_EMAIL = "test@example.com"
            mock_settings.SENDGRID_FROM_NAME = "Test Sender"
            
            crm = CRMService(test_session)
            scheduler = SchedulerService(test_session)
            email_service = EmailService(test_session)
            
            client = await crm.create_client(ClientCreate(
                name="SendGrid Client",
                email="sendgrid@example.com",
                phone="+1-555-0004",
                property_address="104 Email St, City, ST 12345",
                property_type="residential",
                stage="lead"
            ))
            
            task = await scheduler.create_task(TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.utcnow(),
                priority="high"
            ))
            
            email_data = EmailSendRequest(
                client_id=client.id,
                task_id=task.id,
                to_email="sendgrid@example.com",
                subject="SendGrid Test",
                body="<html>Test body</html>"
            )
            
            # Send email (mocked)
            result = await email_service.send_email(email_data)
            assert result.id is not None
            mock_sg_instance.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_email(self, test_session):
        """Test sending an email via SendGrid (with mocked SendGrid)."""
        with patch('app.services.email_service.SendGridAPIClient') as mock_sg_class:
            mock_response = Mock()
            mock_response.headers = {"X-Message-Id": "sent-123"}
            mock_sg_instance = Mock()
            mock_sg_instance.send = Mock(return_value=mock_response)
            mock_sg_class.return_value = mock_sg_instance
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.SENDGRID_API_KEY = "test-key"
                mock_settings.SENDGRID_FROM_EMAIL = "from@example.com"
                mock_settings.SENDGRID_FROM_NAME = "Test From"
                
                crm = CRMService(test_session)
                scheduler = SchedulerService(test_session)
                email_service = EmailService(test_session)
                
                client = await crm.create_client(ClientCreate(
                    name="Send Client",
                    email="send@example.com",
                    phone="+1-555-0005",
                    property_address="105 Email St, City, ST 12345",
                    property_type="residential",
                    stage="lead"
                ))
                
                task = await scheduler.create_task(TaskCreate(
                    client_id=client.id,
                    followup_type="Day 1",
                    scheduled_for=datetime.utcnow(),
                    priority="high"
                ))
                
                email_data = EmailSendRequest(
                    client_id=client.id,
                    task_id=task.id,
                    to_email="recipient@example.com",
                    subject="Test Email",
                    body="<html><body>Test content</body></html>"
                )
                
                result = await email_service.send_email(email_data)
                assert result.id is not None
                assert result.to_email == "recipient@example.com"
    
    @pytest.mark.asyncio
    async def test_process_webhook_event(self, test_session):
        """Test processing SendGrid webhook events."""
        crm = CRMService(test_session)
        scheduler = SchedulerService(test_session)
        email_service = EmailService(test_session)
        
        client = await crm.create_client(ClientCreate(
            name="Webhook Client",
            email="webhook@example.com",
            phone="+1-555-0006",
            property_address="106 Email St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ))
        
        task = await scheduler.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.utcnow(),
            priority="high"
        ))
        
        email_log = await email_service.log_email(
            task_id=task.id,
            client_id=client.id,
            to_email="webhook@example.com",
            subject="Webhook Test",
            body="Body"
        )
        
        # Set message ID first
        await email_service.update_email_status(email_log.id, "sent", sendgrid_message_id="sg-webhook-123")
        
        # Process webhook event
        event_data = {
            "sg_message_id": "sg-webhook-123",
            "event": "opened"
        }
        result = await email_service.process_webhook_event(event_data)
        assert result is True
        
        # Verify status updated
        updated = await email_service.get_email(email_log.id)
        assert updated.status == "opened"
        
        # Test invalid webhook
        invalid_event = {"event": "bounced"}  # Missing message_id
        result = await email_service.process_webhook_event(invalid_event)
        assert result is False
