"""
Client management API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import logging
from shared.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse
from shared.models.agent import Agent
from shared.auth.jwt_auth import get_current_agent
from shared.db.postgresql import get_session
from ...services.crm_service import CRMService

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_crm_service(session: AsyncSession = Depends(get_session)) -> CRMService:
    """Get CRM service instance."""
    return CRMService(session)


@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    agent: Agent = Depends(get_current_agent),
    crm_service: CRMService = Depends(get_crm_service)
):
    """Create a new client."""
    try:
        created = await crm_service.create_client(client_data, agent.id)
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

