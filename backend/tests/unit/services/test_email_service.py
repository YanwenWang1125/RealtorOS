"""
Tests for email service.

This module contains unit tests for the email service
in the RealtorOS system.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from app.services.email_service import EmailService
from app.services.scheduler_service import SchedulerService
from app.services.crm_service import CRMService
from app.schemas.email_schema import EmailSendRequest
from app.schemas.client_schema import ClientCreate
from app.schemas.task_schema import TaskCreate
from app.models.agent import Agent

class TestEmailService:
    """Test cases for email service."""
    
    @pytest.mark.asyncio
    async def test_log_email(self, test_session):
        """Test logging an email before sending."""
        # Create agent first
        agent = Agent(name="Test Agent", email="agent@example.com", auth_provider="email")
        test_session.add(agent)
        await test_session.commit()
        await test_session.refresh(agent)
        
        # Create client and task
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
        ), agent_id=agent.id)
        
        task = await scheduler.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc),
            priority="high"
        ), agent_id=agent.id)
        
        # Log email
        email_log = await email_service.log_email(
            task_id=task.id,
            client_id=client.id,
            agent_id=agent.id,
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test body content",
            from_name=agent.name,
            from_email=agent.email
        )
        
        assert email_log.id is not None
        assert email_log.status == "queued"
        assert email_log.to_email == "recipient@example.com"
        assert email_log.subject == "Test Subject"
    
    @pytest.mark.asyncio
    async def test_get_email(self, test_session):
        """Test getting an email by ID."""
        # Create agent first
        agent = Agent(name="Test Agent", email="agent@example.com", auth_provider="email")
        test_session.add(agent)
        await test_session.commit()
        await test_session.refresh(agent)
        
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
        ), agent_id=agent.id)
        
        task = await scheduler.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc),
            priority="high"
        ), agent_id=agent.id)
        
        email_log = await email_service.log_email(
            task_id=task.id,
            client_id=client.id,
            agent_id=agent.id,
            to_email="get@example.com",
            subject="Get Test",
            body="Get body",
            from_name=agent.name,
            from_email=agent.email
        )
        
        fetched = await email_service.get_email(email_log.id, agent.id)
        assert fetched is not None
        assert fetched.id == email_log.id
        assert fetched.to_email == "get@example.com"
    
    @pytest.mark.asyncio
    async def test_list_emails(self, test_session):
        """Test listing emails with pagination and filtering."""
        # Create agent first
        agent = Agent(name="Test Agent", email="agent@example.com", auth_provider="email")
        test_session.add(agent)
        await test_session.commit()
        await test_session.refresh(agent)
        
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
        ), agent_id=agent.id)
        
        # Create multiple emails
        for i in range(5):
            task = await scheduler.create_task(TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc),
                priority="high"
            ), agent_id=agent.id)
            await email_service.log_email(
                task_id=task.id,
                client_id=client.id,
                agent_id=agent.id,
                to_email=f"list{i}@example.com",
                subject=f"List {i}",
                body=f"Body {i}",
                from_name=agent.name,
                from_email=agent.email
            )
        
        # List all emails
        emails = await email_service.list_emails(agent_id=agent.id)
        assert len(emails) >= 5
        
        # Filter by client
        client_emails = await email_service.list_emails(agent_id=agent.id, client_id=client.id)
        assert len(client_emails) >= 5
        assert all(e.client_id == client.id for e in client_emails)
    
    @pytest.mark.asyncio
    async def test_update_email_status(self, test_session):
        """Test updating email status."""
        # Create agent first
        agent = Agent(name="Test Agent", email="agent@example.com", auth_provider="email")
        test_session.add(agent)
        await test_session.commit()
        await test_session.refresh(agent)
        
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
        ), agent_id=agent.id)
        
        task = await scheduler.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc),
            priority="high"
        ), agent_id=agent.id)
        
        email_log = await email_service.log_email(
            task_id=task.id,
            client_id=client.id,
            agent_id=agent.id,
            to_email="update@example.com",
            subject="Update Test",
            body="Body",
            from_name=agent.name,
            from_email=agent.email
        )
        
        # Update status
        result = await email_service.update_email_status(email_log.id, "sent", ses_message_id="msg-123")
        assert result is True
        
        # Verify update
        updated = await email_service.get_email(email_log.id, agent.id)
        assert updated.status == "sent"
        assert updated.ses_message_id == "msg-123"
    
    @pytest.mark.asyncio
    @patch('app.services.email_service.boto3.client')
    async def test_ses_integration(self, mock_boto3_client, test_session):
        """Test Amazon SES API integration."""
        # Mock SES client response
        mock_ses_instance = Mock()
        mock_ses_instance.send_email = Mock(return_value={'MessageId': 'ses-123456'})
        mock_boto3_client.return_value = mock_ses_instance
        
        # Mock settings
        with patch('app.services.email_service.settings') as mock_settings:
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.SES_FROM_EMAIL = "test@example.com"
            mock_settings.SES_FROM_NAME = "Test Sender"
            
            crm = CRMService(test_session)
            scheduler = SchedulerService(test_session)
            email_service = EmailService(test_session)
            
            # Create agent first
            agent = Agent(name="Test Agent", email="agent@example.com", auth_provider="email")
            test_session.add(agent)
            await test_session.commit()
            await test_session.refresh(agent)
            
            client = await crm.create_client(ClientCreate(
                name="SES Client",
                email="ses@example.com",
                phone="+1-555-0004",
                property_address="104 Email St, City, ST 12345",
                property_type="residential",
                stage="lead"
            ), agent_id=agent.id)
            
            task = await scheduler.create_task(TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc),
                priority="high"
            ), agent_id=agent.id)
            
            email_data = EmailSendRequest(
                client_id=client.id,
                task_id=task.id,
                to_email="ses@example.com",
                subject="SES Test",
                body="<html>Test body</html>"
            )
            
            # Send email (mocked) - use the agent created above
            result = await email_service.send_email(email_data, agent)
            assert result.id is not None
            mock_ses_instance.send_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_email(self, test_session):
        """Test sending an email via Amazon SES (with mocked SES)."""
        with patch('app.services.email_service.boto3.client') as mock_boto3_client:
            mock_ses_instance = Mock()
            mock_ses_instance.send_email = Mock(return_value={'MessageId': 'sent-123'})
            mock_boto3_client.return_value = mock_ses_instance
            
            with patch('app.services.email_service.settings') as mock_settings:
                mock_settings.AWS_REGION = "us-east-1"
                mock_settings.SES_FROM_EMAIL = "from@example.com"
                mock_settings.SES_FROM_NAME = "Test From"
                
                crm = CRMService(test_session)
                scheduler = SchedulerService(test_session)
                email_service = EmailService(test_session)
                
                # Create agent first
                agent = Agent(name="Test Agent", email="agent@example.com", auth_provider="email")
                test_session.add(agent)
                await test_session.commit()
                await test_session.refresh(agent)
                
                client = await crm.create_client(ClientCreate(
                    name="Send Client",
                    email="send@example.com",
                    phone="+1-555-0005",
                    property_address="105 Email St, City, ST 12345",
                    property_type="residential",
                    stage="lead"
                ), agent_id=agent.id)
                
                task = await scheduler.create_task(TaskCreate(
                    client_id=client.id,
                    followup_type="Day 1",
                    scheduled_for=datetime.now(timezone.utc),
                    priority="high"
                ), agent_id=agent.id)
                
                email_data = EmailSendRequest(
                    client_id=client.id,
                    task_id=task.id,
                    to_email="recipient@example.com",
                    subject="Test Email",
                    body="<html><body>Test content</body></html>"
                )
                
                result = await email_service.send_email(email_data, agent)
                assert result.id is not None
                assert result.to_email == "recipient@example.com"
    
    @pytest.mark.asyncio
    async def test_process_webhook_event(self, test_session):
        """Test processing SES SNS webhook events."""
        # Create agent first
        agent = Agent(name="Test Agent", email="agent@example.com", auth_provider="email")
        test_session.add(agent)
        await test_session.commit()
        await test_session.refresh(agent)
        
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
        ), agent_id=agent.id)
        
        task = await scheduler.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc),
            priority="high"
        ), agent_id=agent.id)
        
        email_log = await email_service.log_email(
            task_id=task.id,
            client_id=client.id,
            agent_id=agent.id,
            to_email="webhook@example.com",
            subject="Webhook Test",
            body="Body",
            from_name=agent.name,
            from_email=agent.email
        )
        
        # Set message ID first
        await email_service.update_email_status(email_log.id, "sent", ses_message_id="ses-webhook-123")
        
        # Process webhook event (SES SNS format)
        event_data = {
            "mail": {"messageId": "ses-webhook-123"},
            "eventType": "open"
        }
        result = await email_service.process_webhook_event(event_data)
        assert result is True
        
        # Verify status updated
        updated = await email_service.get_email(email_log.id, agent.id)
        assert updated.status == "open"
        
        # Test invalid webhook
        invalid_event = {"eventType": "bounced"}  # Missing message_id
        result = await email_service.process_webhook_event(invalid_event)
        assert result is False
