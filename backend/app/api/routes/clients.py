"""
Client management API routes.

This module provides CRUD endpoints for managing real estate clients
in the RealtorOS CRM system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse
from app.services.crm_service import CRMService
from app.api.dependencies import get_crm_service
from app.tasks.scheduler_tasks import create_followup_tasks_task

router = APIRouter()

@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    crm_service: CRMService = Depends(get_crm_service)
):
    """Create a new client."""
    created = await crm_service.create_client(client_data)
    create_followup_tasks_task.delay(created.id)
    return created

@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    stage: Optional[str] = None,
    crm_service: CRMService = Depends(get_crm_service)
):
    """List clients with pagination and filtering."""
    return await crm_service.list_clients(page=page, limit=limit, stage=stage)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    crm_service: CRMService = Depends(get_crm_service)
):
    """Get a specific client by ID."""
    client = await crm_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    crm_service: CRMService = Depends(get_crm_service)
):
    """Update a client's information."""
    updated = await crm_service.update_client(client_id, client_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    return updated

@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    crm_service: CRMService = Depends(get_crm_service)
):
    """Soft delete a client."""
    ok = await crm_service.delete_client(client_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"success": True}

@router.get("/{client_id}/tasks")
async def get_client_tasks(
    client_id: int,
    crm_service: CRMService = Depends(get_crm_service)
):
    """Get all tasks for a specific client."""
    return await crm_service.get_client_tasks(client_id)
