"""
Task and follow-up management API routes.

This module provides endpoints for managing follow-up tasks and scheduling
in the RealtorOS CRM system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from app.services.scheduler_service import SchedulerService
from app.api.dependencies import get_scheduler_service

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """List tasks with pagination and filtering."""
    return await scheduler_service.list_tasks(page=page, limit=limit, status=status, client_id=client_id)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Get a specific task by ID."""
    task = await scheduler_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Update a task (mark complete, reschedule, etc.)."""
    updated = await scheduler_service.update_task(task_id, task_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Manually create a new task."""
    return await scheduler_service.create_task(task_data)
