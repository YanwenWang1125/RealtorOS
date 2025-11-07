"""
Tests for Scheduler service (SQLAlchemy + AsyncSession).
"""

import pytest
from unittest.mock import patch, AsyncMock, Mock
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.services.scheduler_service import SchedulerService
from app.services.crm_service import CRMService
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.schemas.client_schema import ClientCreate
from app.models.task import Task
from app.models.client import Client
from app.models.email_log import EmailLog


class TestSchedulerService:
    """Test cases for scheduler service."""

    @pytest.mark.asyncio
    async def test_create_list_get_update_task(self, test_session, sample_agent):
        svc = SchedulerService(test_session)
        # Create client first
        from app.services.crm_service import CRMService
        from app.schemas.client_schema import ClientCreate
        crm = CRMService(test_session)
        client = await crm.create_client(ClientCreate(
            name="Test Client",
            email="test@example.com",
            phone="+1-555-0000",
            property_address="100 Test St",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        
        # create task
        tc = TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
            priority="high",
            notes="note",
        )
        created = await svc.create_task(tc, agent_id=sample_agent.id)
        assert isinstance(created.id, int)
        assert created.status == "pending"

        # list
        listed = await svc.list_tasks(agent_id=sample_agent.id, client_id=client.id)
        assert any(t.id == created.id for t in listed)

        # get
        got = await svc.get_task(created.id, agent_id=sample_agent.id)
        assert got is not None and got.id == created.id

        # update
        updated = await svc.update_task(created.id, TaskUpdate(status="completed"), agent_id=sample_agent.id)
        assert updated is not None and updated.status == "completed"

    @pytest.mark.asyncio
    async def test_get_due_and_reschedule(self, test_session, sample_agent):
        svc = SchedulerService(test_session)
        # Create client first
        from app.services.crm_service import CRMService
        from app.schemas.client_schema import ClientCreate
        crm = CRMService(test_session)
        client = await crm.create_client(ClientCreate(
            name="Test Client",
            email="test@example.com",
            phone="+1-555-0000",
            property_address="100 Test St",
            property_type="residential",
            stage="lead"
        ), agent_id=sample_agent.id)
        
        past = TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) - timedelta(hours=1),
            priority="medium",
        )
        created = await svc.create_task(past, agent_id=sample_agent.id)
        due = await svc.get_due_tasks()
        assert any(t.id == created.id for t in due)

        new_date = datetime.now(timezone.utc) + timedelta(days=2)
        res = await svc.reschedule_task(created.id, new_date, agent_id=sample_agent.id)
        assert res is not None and res.scheduled_for == new_date

    @pytest.mark.asyncio
    async def test_process_and_send_due_emails_no_due_tasks(self, test_session):
        """Test process_and_send_due_emails with no due tasks."""
        svc = SchedulerService(test_session)
        count = await svc.process_and_send_due_emails()
        assert count == 0

    @pytest.mark.asyncio
    @patch('app.services.scheduler_service.EmailService')
    @patch('app.services.scheduler_service.AIAgent')
    async def test_process_and_send_due_emails_single_success(self, mock_ai_class, mock_email_class, test_session):
        """Test successfully processing a single due task."""
        # Create client
        crm = CRMService(test_session)
        client = await crm.create_client(ClientCreate(
            name="Test Client",
            email="test@example.com",
            phone="+1-555-0100",
            property_address="100 Test St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ))
        
        # Create due task
        svc = SchedulerService(test_session)
        task = await svc.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) - timedelta(hours=1),  # Past time = due
            priority="high"
        ))
        
        # Mock AIAgent
        mock_ai = Mock()
        mock_ai.generate_email = AsyncMock(return_value={
            "subject": "Follow-up on your property inquiry",
            "body": "<html><body>Test email body</body></html>",
            "preview": "Test preview"
        })
        mock_ai_class.return_value = mock_ai
        
        # Mock EmailService
        mock_email_response = Mock()
        mock_email_response.id = 1
        mock_email = Mock()
        mock_email.send_email = AsyncMock(return_value=mock_email_response)
        mock_email_class.return_value = mock_email
        
        # Process due emails
        count = await svc.process_and_send_due_emails()
        
        assert count == 1
        
        # Verify task was updated
        updated_task = await svc.get_task(task.id)
        assert updated_task.status == "completed"
        assert updated_task.email_sent_id == 1
        assert updated_task.completed_at is not None
        
        # Verify AI agent was called
        mock_ai.generate_email.assert_called_once()
        call_args = mock_ai.generate_email.call_args
        assert call_args[0][0].id == client.id
        assert call_args[0][1].id == task.id
        
        # Verify email service was called
        mock_email.send_email.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.email_service.SendGridAPIClient')
    @patch('app.services.scheduler_service.AIAgent')
    async def test_process_and_send_due_emails_multiple_tasks(self, mock_ai_class, mock_sg_class, test_session):
        """Test processing multiple due tasks successfully."""
        # Mock SendGrid
        mock_response = Mock()
        mock_response.headers = {"X-Message-Id": "sg-123"}
        mock_sg_instance = Mock()
        mock_sg_instance.send = Mock(return_value=mock_response)
        mock_sg_class.return_value = mock_sg_instance
        
        with patch('app.services.email_service.settings') as mock_settings:
            mock_settings.SENDGRID_API_KEY = "test-key"
            mock_settings.SENDGRID_FROM_EMAIL = "from@example.com"
            mock_settings.SENDGRID_FROM_NAME = "Test From"
            
            # Create clients
            crm = CRMService(test_session)
            clients = []
            for i in range(3):
                client = await crm.create_client(ClientCreate(
                    name=f"Client {i}",
                    email=f"client{i}@example.com",
                    phone=f"+1-555-{1000+i}",
                    property_address=f"{100+i} Test St, City, ST 12345",
                    property_type="residential",
                    stage="lead"
                ))
                clients.append(client)
            
            # Create due tasks for each client
            svc = SchedulerService(test_session)
            tasks = []
            followup_types = ["Day 1", "Day 3", "Week 1"]
            for i, client in enumerate(clients):
                task = await svc.create_task(TaskCreate(
                    client_id=client.id,
                    followup_type=followup_types[i],
                    scheduled_for=datetime.now(timezone.utc) - timedelta(hours=i+1),
                    priority="high"
                ))
                tasks.append(task)
            
            # Mock AIAgent
            mock_ai = Mock()
            mock_ai.generate_email = AsyncMock(side_effect=[
                {"subject": f"Follow-up {i}", "body": f"<html><body>Body {i}</body></html>", "preview": f"Preview {i}"}
                for i in range(3)
            ])
            mock_ai_class.return_value = mock_ai
            
            # Process due emails (using real EmailService)
            count = await svc.process_and_send_due_emails()
            
            assert count == 3
            
            # Verify all tasks were completed
            for task in tasks:
                updated_task = await svc.get_task(task.id)
                assert updated_task.status == "completed"
                assert updated_task.email_sent_id is not None
            
            # Verify AI agent was called 3 times
            assert mock_ai.generate_email.call_count == 3

    @pytest.mark.asyncio
    @patch('app.services.scheduler_service.AIAgent')
    async def test_process_and_send_due_emails_missing_client(self, mock_ai_class, test_session):
        """Test handling task with missing client."""
        # Create task with non-existent client_id
        svc = SchedulerService(test_session)
        task = await svc.create_task(TaskCreate(
            client_id=99999,  # Non-existent client
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) - timedelta(hours=1),
            priority="high"
        ))
        
        # Process - should handle gracefully
        count = await svc.process_and_send_due_emails()
        
        assert count == 0
        
        # Task should still be pending (not completed)
        updated_task = await svc.get_task(task.id)
        assert updated_task.status == "pending"

    @pytest.mark.asyncio
    @patch('app.services.scheduler_service.AIAgent')
    async def test_process_and_send_due_emails_client_no_email(self, mock_ai_class, test_session):
        """Test handling client without email address."""
        # Create client with empty email string (simulating edge case where email might be empty)
        crm = CRMService(test_session)
        client = await crm.create_client(ClientCreate(
            name="No Email Client",
            email="noemail@example.com",
            phone="+1-555-0200",
            property_address="200 Test St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ))
        
        # Set email to empty string (simulating edge case - can't set to None due to constraint)
        from sqlalchemy import update as sql_update
        stmt = sql_update(Client).where(Client.id == client.id).values(email="")
        await test_session.execute(stmt)
        await test_session.commit()
        
        # Create due task
        svc = SchedulerService(test_session)
        task = await svc.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) - timedelta(hours=1),
            priority="high"
        ))
        
        # Process - should skip client without valid email
        count = await svc.process_and_send_due_emails()
        
        assert count == 0
        
        # Task should still be pending
        updated_task = await svc.get_task(task.id)
        assert updated_task.status == "pending"

    @pytest.mark.asyncio
    @patch('app.services.scheduler_service.EmailService')
    @patch('app.services.scheduler_service.AIAgent')
    async def test_process_and_send_due_emails_ai_generation_fails(self, mock_ai_class, mock_email_class, test_session):
        """Test handling AI email generation failure."""
        # Create client and task
        crm = CRMService(test_session)
        client = await crm.create_client(ClientCreate(
            name="AI Fail Client",
            email="aifail@example.com",
            phone="+1-555-0300",
            property_address="300 Test St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ))
        
        svc = SchedulerService(test_session)
        task = await svc.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) - timedelta(hours=1),
            priority="high"
        ))
        
        # Mock AIAgent to return invalid response
        mock_ai = Mock()
        mock_ai.generate_email = AsyncMock(return_value={})  # Missing subject/body
        mock_ai_class.return_value = mock_ai
        
        # Process - should skip task with failed generation
        count = await svc.process_and_send_due_emails()
        
        assert count == 0
        
        # Task should still be pending
        updated_task = await svc.get_task(task.id)
        assert updated_task.status == "pending"

    @pytest.mark.asyncio
    @patch('app.services.scheduler_service.EmailService')
    @patch('app.services.scheduler_service.AIAgent')
    async def test_process_and_send_due_emails_email_send_fails(self, mock_ai_class, mock_email_class, test_session):
        """Test handling email sending failure."""
        # Create client and task
        crm = CRMService(test_session)
        client = await crm.create_client(ClientCreate(
            name="Send Fail Client",
            email="sendfail@example.com",
            phone="+1-555-0400",
            property_address="400 Test St, City, ST 12345",
            property_type="residential",
            stage="lead"
        ))
        
        svc = SchedulerService(test_session)
        task = await svc.create_task(TaskCreate(
            client_id=client.id,
            followup_type="Day 1",
            scheduled_for=datetime.now(timezone.utc) - timedelta(hours=1),
            priority="high"
        ))
        
        # Mock AIAgent - succeeds
        mock_ai = Mock()
        mock_ai.generate_email = AsyncMock(return_value={
            "subject": "Test Subject",
            "body": "<html><body>Test body</body></html>",
            "preview": "Test preview"
        })
        mock_ai_class.return_value = mock_ai
        
        # Mock EmailService - fails
        mock_email = Mock()
        mock_email.send_email = AsyncMock(side_effect=Exception("SendGrid error"))
        mock_email_class.return_value = mock_email
        
        # Process - should handle exception gracefully
        count = await svc.process_and_send_due_emails()
        
        assert count == 0
        
        # Task should still be pending (not updated due to error)
        updated_task = await svc.get_task(task.id)
        assert updated_task.status == "pending"

    @pytest.mark.asyncio
    @patch('app.services.email_service.SendGridAPIClient')
    @patch('app.services.scheduler_service.AIAgent')
    async def test_process_and_send_due_emails_partial_success(self, mock_ai_class, mock_sg_class, test_session):
        """Test processing multiple tasks where some succeed and some fail."""
        # Mock SendGrid to fail on second call
        call_count = 0
        def send_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Second call fails
                raise Exception("SendGrid error")
            mock_response = Mock()
            mock_response.headers = {"X-Message-Id": f"sg-{call_count}"}
            return mock_response
        
        mock_sg_instance = Mock()
        mock_sg_instance.send = Mock(side_effect=send_side_effect)
        mock_sg_class.return_value = mock_sg_instance
        
        with patch('app.services.email_service.settings') as mock_settings:
            mock_settings.SENDGRID_API_KEY = "test-key"
            mock_settings.SENDGRID_FROM_EMAIL = "from@example.com"
            mock_settings.SENDGRID_FROM_NAME = "Test From"
            
            # Create clients
            crm = CRMService(test_session)
            clients = []
            for i in range(3):
                client = await crm.create_client(ClientCreate(
                    name=f"Partial Client {i}",
                    email=f"partial{i}@example.com",
                    phone=f"+1-555-{5000+i}",
                    property_address=f"{500+i} Test St, City, ST 12345",
                    property_type="residential",
                    stage="lead"
                ))
                clients.append(client)
            
            # Create due tasks
            svc = SchedulerService(test_session)
            tasks = []
            for i, client in enumerate(clients):
                task = await svc.create_task(TaskCreate(
                    client_id=client.id,
                    followup_type="Day 1",
                    scheduled_for=datetime.now(timezone.utc) - timedelta(hours=i+1),
                    priority="high"
                ))
                tasks.append(task)
            
            # Mock AIAgent - succeeds for all
            mock_ai = Mock()
            mock_ai.generate_email = AsyncMock(side_effect=[
                {"subject": f"Subject {i}", "body": f"<html><body>Body {i}</body></html>", "preview": f"Preview {i}"}
                for i in range(3)
            ])
            mock_ai_class.return_value = mock_ai
            
            # Process due emails (using real EmailService, which will fail on second SendGrid call)
            count = await svc.process_and_send_due_emails()
            
            # All 3 tasks should be processed (EmailService still returns response even on failure)
            # However, the second email will have status "failed" in the email log
            assert count == 3
            
            # All tasks are marked as completed (even though one email failed to send)
            task1 = await svc.get_task(tasks[0].id)
            assert task1.status == "completed"
            
            task2 = await svc.get_task(tasks[1].id)
            assert task2.status == "completed"  # Task completed, but email status will be "failed"
            
            task3 = await svc.get_task(tasks[2].id)
            assert task3.status == "completed"
            
            # Verify the second email has failed status
            from app.services.email_service import EmailService
            email_service = EmailService(test_session)
            emails = await email_service.list_emails(client_id=clients[1].id)
            # Find the email for task2
            task2_email = next((e for e in emails if e.task_id == tasks[1].id), None)
            assert task2_email is not None
            assert task2_email.status == "failed"  # Email sending failed

    @pytest.mark.asyncio
    @patch('app.services.email_service.SendGridAPIClient')
    @patch('app.services.scheduler_service.AIAgent')
    async def test_process_and_send_due_emails_verifies_email_log(self, mock_ai_class, mock_sg_class, test_session):
        """Test that email logs are created when processing due tasks."""
        # Mock SendGrid
        mock_response = Mock()
        mock_response.headers = {"X-Message-Id": "sg-test-123"}
        mock_sg_instance = Mock()
        mock_sg_instance.send = Mock(return_value=mock_response)
        mock_sg_class.return_value = mock_sg_instance
        
        with patch('app.services.email_service.settings') as mock_settings:
            mock_settings.SENDGRID_API_KEY = "test-key"
            mock_settings.SENDGRID_FROM_EMAIL = "from@example.com"
            mock_settings.SENDGRID_FROM_NAME = "Test From"
            
            # Create client and task
            crm = CRMService(test_session)
            client = await crm.create_client(ClientCreate(
                name="Email Log Client",
                email="emaillog@example.com",
                phone="+1-555-0600",
                property_address="600 Test St, City, ST 12345",
                property_type="residential",
                stage="lead"
            ))
            
            svc = SchedulerService(test_session)
            task = await svc.create_task(TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) - timedelta(hours=1),
                priority="high"
            ))
            
            # Mock AIAgent
            mock_ai = Mock()
            mock_ai.generate_email = AsyncMock(return_value={
                "subject": "Test Subject",
                "body": "<html><body>Test body</body></html>",
                "preview": "Test preview"
            })
            mock_ai_class.return_value = mock_ai
            
            # Process due emails (using real EmailService, not mocked)
            count = await svc.process_and_send_due_emails()
            
            assert count == 1
            
            # Verify email log was created
            email_stmt = select(EmailLog).where(EmailLog.client_id == client.id)
            result = await test_session.execute(email_stmt)
            email_logs = result.scalars().all()
            
            assert len(email_logs) == 1
            assert email_logs[0].task_id == task.id
            assert email_logs[0].to_email == client.email
            assert email_logs[0].subject == "Test Subject"

    @pytest.mark.asyncio
    @patch('app.services.email_service.SendGridAPIClient')
    @patch('app.services.scheduler_service.AIAgent')
    async def test_process_and_send_due_emails_only_processes_due_tasks(self, mock_ai_class, mock_sg_class, test_session):
        """Test that only due tasks are processed, not future tasks."""
        # Mock SendGrid
        mock_response = Mock()
        mock_response.headers = {"X-Message-Id": "sg-123"}
        mock_sg_instance = Mock()
        mock_sg_instance.send = Mock(return_value=mock_response)
        mock_sg_class.return_value = mock_sg_instance
        
        with patch('app.services.email_service.settings') as mock_settings:
            mock_settings.SENDGRID_API_KEY = "test-key"
            mock_settings.SENDGRID_FROM_EMAIL = "from@example.com"
            mock_settings.SENDGRID_FROM_NAME = "Test From"
            
            # Create client
            crm = CRMService(test_session)
            client = await crm.create_client(ClientCreate(
                name="Due Only Client",
                email="dueonly@example.com",
                phone="+1-555-0700",
                property_address="700 Test St, City, ST 12345",
                property_type="residential",
                stage="lead"
            ))
            
            svc = SchedulerService(test_session)
            
            # Create due task
            due_task = await svc.create_task(TaskCreate(
                client_id=client.id,
                followup_type="Day 1",
                scheduled_for=datetime.now(timezone.utc) - timedelta(hours=1),  # Due
                priority="high"
            ))
            
            # Create future task (not due)
            future_task = await svc.create_task(TaskCreate(
                client_id=client.id,
                followup_type="Day 3",
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=2),  # Future
                priority="medium"
            ))
            
            # Mock AIAgent
            mock_ai = Mock()
            mock_ai.generate_email = AsyncMock(return_value={
                "subject": "Test Subject",
                "body": "<html><body>Test body</body></html>",
                "preview": "Test preview"
            })
            mock_ai_class.return_value = mock_ai
            
            # Process due emails (using real EmailService)
            count = await svc.process_and_send_due_emails()
            
            assert count == 1
            
            # Verify only due task was processed
            due_task_updated = await svc.get_task(due_task.id)
            assert due_task_updated.status == "completed"
            
            future_task_updated = await svc.get_task(future_task.id)
            assert future_task_updated.status == "pending"  # Not processed
            
            # AI agent should only be called once (for due task)
            assert mock_ai.generate_email.call_count == 1
