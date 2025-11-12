"""
Task and follow-up management API routes.

This module provides endpoints for managing follow-up tasks and scheduling
in the RealtorOS CRM system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from app.services.scheduler_service import SchedulerService
from app.api.dependencies import get_scheduler_service, get_current_agent
from app.models.agent import Agent
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    agent: Agent = Depends(get_current_agent),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """List tasks with pagination and filtering."""
    return await scheduler_service.list_tasks(agent.id, page=page, limit=limit, status=status, client_id=client_id)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    agent: Agent = Depends(get_current_agent),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Get a specific task by ID."""
    task = await scheduler_service.get_task(task_id, agent.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    agent: Agent = Depends(get_current_agent),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Update a task (mark complete, reschedule, etc.)."""
    updated = await scheduler_service.update_task(task_id, task_data, agent.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    agent: Agent = Depends(get_current_agent),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Manually create a new task."""
    return await scheduler_service.create_task(task_data, agent.id)

class BulkDeleteRequest(BaseModel):
    ids: List[int]

@router.delete("/bulk")
async def bulk_delete_tasks(
    request: BulkDeleteRequest = Body(...),
    agent: Agent = Depends(get_current_agent),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Bulk delete multiple tasks and their associated email logs."""
    if not request.ids:
        raise HTTPException(status_code=400, detail="No task IDs provided")
    
    deleted_count = 0
    failed_ids = []
    
    for task_id in request.ids:
        try:
            deleted = await scheduler_service.delete_task(task_id, agent.id)
            if deleted:
                deleted_count += 1
            else:
                failed_ids.append(task_id)
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            failed_ids.append(task_id)
    
    return {
        "success": True,
        "deleted_count": deleted_count,
        "failed_ids": failed_ids,
        "total_requested": len(request.ids)
    }

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    agent: Agent = Depends(get_current_agent),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Delete a task and all associated email logs."""
    deleted = await scheduler_service.delete_task(task_id, agent.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}

@router.get("/diagnostics/due-tasks", response_model=dict)
async def get_due_tasks_diagnostics(
    agent: Agent = Depends(get_current_agent),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Get diagnostic information about due tasks."""
    from datetime import datetime, timezone
    from sqlalchemy import select, func
    from app.models.task import Task
    
    now = datetime.now(timezone.utc)
    
    # Get all tasks for this agent
    all_tasks_stmt = select(Task).where(Task.agent_id == agent.id)
    all_tasks_result = await scheduler_service.session.execute(all_tasks_stmt)
    all_tasks = all_tasks_result.scalars().all()
    
    # Get due tasks
    due_tasks_stmt = select(Task).where(
        Task.agent_id == agent.id,
        Task.scheduled_for <= now,
        Task.status == "pending"
    )
    due_tasks_result = await scheduler_service.session.execute(due_tasks_stmt)
    due_tasks = due_tasks_result.scalars().all()
    
    # Get pending tasks (not necessarily due)
    pending_tasks_stmt = select(Task).where(
        Task.agent_id == agent.id,
        Task.status == "pending"
    )
    pending_tasks_result = await scheduler_service.session.execute(pending_tasks_stmt)
    pending_tasks = pending_tasks_result.scalars().all()
    
    return {
        "current_time_utc": now.isoformat(),
        "total_tasks": len(all_tasks),
        "pending_tasks": len(pending_tasks),
        "due_tasks": len(due_tasks),
        "due_tasks_details": [
            {
                "id": t.id,
                "client_id": t.client_id,
                "followup_type": t.followup_type,
                "scheduled_for": t.scheduled_for.isoformat() if t.scheduled_for else None,
                "status": t.status,
                "is_due": t.scheduled_for <= now if t.scheduled_for else False
            }
            for t in due_tasks[:10]  # Limit to first 10 for response size
        ],
        "scheduler_status": "Check /health/scheduler endpoint"
    }

@router.post("/process-due", response_model=dict)
async def process_due_tasks_manual(
    agent: Agent = Depends(get_current_agent),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Manually trigger processing of due tasks for the current agent."""
    from datetime import datetime, timezone
    from sqlalchemy import select
    from app.models.task import Task
    
    # Get all due tasks for this agent
    now = datetime.now(timezone.utc)
    stmt = select(Task).where(
        Task.agent_id == agent.id,
        Task.scheduled_for <= now,
        Task.status == "pending"
    )
    result = await scheduler_service.session.execute(stmt)
    due_tasks = result.scalars().all()
    
    if not due_tasks:
        return {
            "message": "No due tasks found",
            "count": 0,
            "current_time": now.isoformat(),
            "hint": "Check if tasks have scheduled_for <= current time and status='pending'"
        }
    
    # Process the tasks (this processes ALL due tasks, not just for this agent)
    # Note: process_and_send_due_emails doesn't filter by agent_id
    count = await scheduler_service.process_and_send_due_emails()
    
    return {
        "message": f"Processed {count} due task(s)",
        "count": count,
        "due_tasks_found": len(due_tasks),
        "current_time": now.isoformat()
    }