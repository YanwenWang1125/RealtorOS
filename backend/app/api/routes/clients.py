"""
Client management API routes.

This module provides CRUD endpoints for managing real estate clients
in the RealtorOS CRM system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse
from app.services.crm_service import CRMService
from app.services.scheduler_service import SchedulerService
from app.api.dependencies import get_crm_service, get_scheduler_service, get_current_agent
from app.models.agent import Agent
from sqlalchemy.exc import IntegrityError
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    agent: Agent = Depends(get_current_agent),
    crm_service: CRMService = Depends(get_crm_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Create a new client and automatically create follow-up tasks."""
    try:
        created = await crm_service.create_client(client_data, agent.id)
        
        # Create follow-up tasks synchronously
        try:
            tasks = await scheduler_service.create_followup_tasks(created.id, agent.id)
            logger.info(f"Created {len(tasks)} follow-up tasks for client {created.id}")
        except Exception as e:
            # Log error but don't fail client creation if task creation fails
            logger.error(f"Failed to create follow-up tasks for client {created.id}: {str(e)}", exc_info=True)
        
        return created
    except IntegrityError as e:
        # Handle duplicate email (unique constraint) gracefully
        raise HTTPException(status_code=409, detail="A client with this email already exists.") from e

@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    stage: Optional[str] = None,
    agent: Agent = Depends(get_current_agent),
    crm_service: CRMService = Depends(get_crm_service)
):
    """List clients with pagination and filtering."""
    return await crm_service.list_clients(agent.id, page=page, limit=limit, stage=stage)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    agent: Agent = Depends(get_current_agent),
    crm_service: CRMService = Depends(get_crm_service)
):
    """Get a specific client by ID."""
    client = await crm_service.get_client(client_id, agent.id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    agent: Agent = Depends(get_current_agent),
    crm_service: CRMService = Depends(get_crm_service)
):
    """Update a client's information."""
    updated = await crm_service.update_client(client_id, client_data, agent.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated

@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    agent: Agent = Depends(get_current_agent),
    crm_service: CRMService = Depends(get_crm_service)
):
    """Soft delete a client."""
    ok = await crm_service.delete_client(client_id, agent.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"success": True}

@router.get("/{client_id}/tasks")
async def get_client_tasks(
    client_id: int,
    agent: Agent = Depends(get_current_agent),
    crm_service: CRMService = Depends(get_crm_service)
):
    """Get all tasks for a specific client."""
    return await crm_service.get_client_tasks(client_id, agent.id)
