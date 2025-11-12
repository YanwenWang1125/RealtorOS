"""
Scheduler service for task and follow-up management (SQLAlchemy).
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from app.models.client import Client
from app.models.email_log import EmailLog
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.email_schema import EmailSendRequest
from app.constants.followup_schedules import FOLLOWUP_SCHEDULE
from app.services.ai_agent import AIAgent
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.followup_schedule = FOLLOWUP_SCHEDULE

    def _as_aware_utc(self, dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        # Ensure timezone-aware UTC
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)

    def _to_response(self, task: Task) -> TaskResponse:
        return TaskResponse(
            id=task.id,
            agent_id=task.agent_id,
            client_id=task.client_id,
            followup_type=task.followup_type,
            scheduled_for=self._as_aware_utc(task.scheduled_for),
            status=task.status,
            priority=task.priority,
            notes=task.notes,
            created_at=self._as_aware_utc(task.created_at),
            updated_at=self._as_aware_utc(task.updated_at),
            completed_at=self._as_aware_utc(task.completed_at),
            email_sent_id=task.email_sent_id,
        )

    async def create_followup_tasks(self, client_id: int, agent_id: int) -> List[TaskResponse]:
        now = datetime.now(timezone.utc)
        created: List[Task] = []
        # FOLLOWUP_SCHEDULE is a dict keyed by label {label: {days, priority, ...}}
        for label, cfg in self.followup_schedule.items():
            scheduled_for = now + timedelta(days=cfg.get("days", 0))
            task = Task(
                agent_id=agent_id,
                client_id=client_id,
                followup_type=label,
                scheduled_for=scheduled_for,
                status="pending",
                priority=cfg.get("priority", "medium"),
            )
            self.session.add(task)
            created.append(task)
        await self.session.commit()
        for t in created:
            await self.session.refresh(t)
        return [self._to_response(t) for t in created]

    async def get_task(self, task_id: int, agent_id: int) -> Optional[TaskResponse]:
        stmt = select(Task).where(Task.id == task_id, Task.agent_id == agent_id)
        result = await self.session.execute(stmt)
        task = result.scalar_one_or_none()
        if task is None:
            return None
        return self._to_response(task)

    async def list_tasks(self, agent_id: int, page: int = 1, limit: int = 10, status: Optional[str] = None, client_id: Optional[int] = None) -> List[TaskResponse]:
        offset = (page - 1) * limit
        stmt = select(Task).where(Task.agent_id == agent_id)
        if status:
            stmt = stmt.where(Task.status == status)
        if client_id:
            stmt = stmt.where(Task.client_id == client_id)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        return [self._to_response(t) for t in tasks]

    async def update_task(self, task_id: int, task_data: TaskUpdate, agent_id: int) -> Optional[TaskResponse]:
        update_data = task_data.model_dump(exclude_unset=True)
        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.agent_id == agent_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_task(task_id, agent_id)

    async def delete_task(self, task_id: int, agent_id: int) -> bool:
        """
        Delete a task and all associated email logs.
        Returns True if task was found and deleted, False otherwise.
        """
        # First check if task exists and belongs to the agent
        task = await self.get_task(task_id, agent_id)
        if task is None:
            return False
        
        # Delete email logs associated with this task
        await self.session.execute(
            delete(EmailLog).where(
                EmailLog.task_id == task_id,
                EmailLog.agent_id == agent_id
            )
        )
        
        # Delete the task itself
        await self.session.execute(
            delete(Task).where(
                Task.id == task_id,
                Task.agent_id == agent_id
            )
        )
        
        await self.session.commit()
        return True

    async def create_task(self, task_data: TaskCreate, agent_id: int) -> TaskResponse:
        task = Task(
            agent_id=agent_id,
            client_id=task_data.client_id,
            followup_type=task_data.followup_type,
            scheduled_for=task_data.scheduled_for,
            status="pending",
            priority=task_data.priority,
            notes=task_data.notes,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return self._to_response(task)

    async def get_due_tasks(self) -> List[TaskResponse]:
        now = datetime.now(timezone.utc)
        stmt = select(Task).where(Task.scheduled_for <= now, Task.status == "pending")
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        return [self._to_response(t) for t in tasks]

    async def reschedule_task(self, task_id: int, new_date: datetime, agent_id: int) -> Optional[TaskResponse]:
        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.agent_id == agent_id)
            .values(scheduled_for=new_date)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_task(task_id, agent_id)

    async def process_and_send_due_emails(self) -> int:
        """
        Process all due tasks and send automated follow-up emails.
        
        Queries all tasks where scheduled_for <= now AND status = "pending",
        generates personalized emails using AIAgent, sends them via EmailService,
        and marks tasks as completed.
        
        Returns:
            int: Count of successfully processed tasks
        """
        now = datetime.now(timezone.utc)
        
        # Query all due tasks
        stmt = select(Task).where(
            Task.scheduled_for <= now,
            Task.status == "pending"
        )
        result = await self.session.execute(stmt)
        due_tasks = result.scalars().all()
        
        logger.info(f"Found {len(due_tasks)} due task(s) to process")
        
        if not due_tasks:
            return 0
        
        # Initialize services
        ai_agent = AIAgent()
        email_service = EmailService(self.session)
        
        success_count = 0
        
        # Process each task
        for task in due_tasks:
            try:
                # Double-check task status to ensure it's still pending
                # This prevents sending emails for tasks that were completed between query and processing
                await self.session.refresh(task)
                if task.status != "pending":
                    logger.info(f"Skipping task_id={task.id} - status is '{task.status}', not 'pending'")
                    continue
                
                logger.info(f"Processing task_id={task.id}, client_id={task.client_id}, followup_type={task.followup_type}")
                
                # Fetch the client
                client_stmt = select(Client).where(Client.id == task.client_id)
                client_result = await self.session.execute(client_stmt)
                client = client_result.scalar_one_or_none()
                
                if not client:
                    logger.error(f"Client not found for task_id={task.id}, client_id={task.client_id}")
                    continue
                
                if not client.email:
                    logger.error(f"Client {client.id} has no email address for task_id={task.id}")
                    continue
                
                # Get agent for this task
                from app.models.agent import Agent
                agent_stmt = select(Agent).where(Agent.id == task.agent_id)
                agent_result = await self.session.execute(agent_stmt)
                agent = agent_result.scalar_one_or_none()
                
                if not agent:
                    logger.error(f"Agent not found for task_id={task.id}, agent_id={task.agent_id}")
                    continue
                
                # Generate email using AIAgent
                logger.info(f"Generating email for task_id={task.id}, client_id={client.id}, agent_id={agent.id}")
                email_content = await ai_agent.generate_email(client, task, agent)
                
                if not email_content or "subject" not in email_content or "body" not in email_content:
                    logger.error(f"Failed to generate email content for task_id={task.id}, client_id={client.id}")
                    continue
                
                # Create email send request
                email_request = EmailSendRequest(
                    client_id=client.id,
                    task_id=task.id,
                    to_email=client.email,
                    subject=email_content["subject"],
                    body=email_content["body"]
                )
                
                # Send email via EmailService
                logger.info(f"Sending email for task_id={task.id}, client_id={client.id}, to={client.email}")
                email_response = await email_service.send_email(email_request, agent)
                
                # Check if email was actually sent successfully
                if email_response.status != "sent":
                    logger.warning(
                        f"Email not sent successfully for task_id={task.id}. "
                        f"Status: {email_response.status}, Error: {email_response.error_message}"
                    )
                    # Still mark as completed if email was logged (even if sending failed)
                    # This prevents the task from being retried indefinitely
                
                # Update task: status="completed", email_sent_id, completed_at
                stmt = (
                    update(Task)
                    .where(Task.id == task.id)
                    .values(
                        status="completed",
                        email_sent_id=email_response.id,
                        completed_at=now
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await self.session.execute(stmt)
                await self.session.commit()
                
                logger.info(
                    f"Successfully processed task_id={task.id}, client_id={client.id}, "
                    f"email_id={email_response.id}, email_status={email_response.status}"
                )
                success_count += 1
                
            except Exception as e:
                # Get task info before potential session expiration
                task_id = task.id
                client_id = task.client_id
                logger.error(
                    f"Error processing task_id={task_id}, client_id={client_id}: {str(e)}",
                    exc_info=True
                )
                # Rollback for this task only
                try:
                    await self.session.rollback()
                except Exception as rollback_error:
                    logger.error(f"Rollback error for task_id={task_id}: {str(rollback_error)}")
                # Continue processing remaining tasks
                continue
        
        logger.info(f"Processed {success_count} out of {len(due_tasks)} due task(s) successfully")
        return success_count
