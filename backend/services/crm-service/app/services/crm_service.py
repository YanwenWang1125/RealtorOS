"""
CRM service for client management (SQLAlchemy + AsyncSession).
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.client import Client
from shared.models.task import Task
from shared.models.email_log import EmailLog
from shared.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse


class CRMService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_client(self, client_data: ClientCreate, agent_id: int) -> ClientResponse:
        # Normalize email to avoid case-related duplicates
        normalized_email = client_data.email.strip().lower()
        client = Client(
            agent_id=agent_id,
            name=client_data.name,
            email=normalized_email,
            phone=client_data.phone,
            property_address=client_data.property_address,
            property_type=client_data.property_type,
            stage=client_data.stage,
            notes=client_data.notes,
            custom_fields=client_data.custom_fields,
        )
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return ClientResponse.model_validate(client.__dict__, from_attributes=True)

    async def get_client(self, client_id: int, agent_id: int) -> Optional[ClientResponse]:
        stmt = select(Client).where(
            Client.id == client_id,
            Client.agent_id == agent_id,
            Client.is_deleted == False  # noqa: E712
        )
        result = await self.session.execute(stmt)
        client = result.scalar_one_or_none()
        if client is None:
            return None
        return ClientResponse.model_validate(client.__dict__, from_attributes=True)

    async def list_clients(self, agent_id: int, page: int = 1, limit: int = 10, stage: Optional[str] = None) -> List[ClientResponse]:
        offset = (page - 1) * limit
        stmt = select(Client).where(
            Client.agent_id == agent_id,
            Client.is_deleted == False  # noqa: E712
        )
        if stage:
            stmt = stmt.where(Client.stage == stage)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        clients = result.scalars().all()
        return [ClientResponse.model_validate(c.__dict__, from_attributes=True) for c in clients]

    async def update_client(self, client_id: int, client_data: ClientUpdate, agent_id: int) -> Optional[ClientResponse]:
        # First check if client exists and is not deleted
        existing_client = await self.get_client(client_id, agent_id)
        if existing_client is None:
            return None
        
        update_data = client_data.model_dump(exclude_unset=True)
        if not update_data:
            return existing_client
        stmt = (
            update(Client)
            .where(
                Client.id == client_id,
                Client.agent_id == agent_id,
                Client.is_deleted == False  # noqa: E712
            )
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_client(client_id, agent_id)

    async def delete_client(self, client_id: int, agent_id: int) -> bool:
        # First check if client exists and is not already deleted
        client = await self.get_client(client_id, agent_id)
        if client is None:
            return False
        
        # Delete related records in the correct order to handle foreign key constraints
        # 1. First, clear the circular reference: set Task.email_sent_id to NULL for tasks of this client
        #    This breaks the circular dependency between Task and EmailLog
        await self.session.execute(
            update(Task)
            .where(
                Task.client_id == client_id,
                Task.agent_id == agent_id,
                Task.email_sent_id.isnot(None)
            )
            .values(email_sent_id=None)
        )
        
        # 2. Delete EmailLogs associated with this client
        await self.session.execute(
            delete(EmailLog).where(
                EmailLog.client_id == client_id,
                EmailLog.agent_id == agent_id
            )
        )
        
        # 3. Delete Tasks associated with this client
        await self.session.execute(
            delete(Task).where(
                Task.client_id == client_id,
                Task.agent_id == agent_id
            )
        )
        
        # 4. Finally, soft delete the client
        stmt = (
            update(Client)
            .where(
                Client.id == client_id,
                Client.agent_id == agent_id,
                Client.is_deleted == False  # noqa: E712
            )
            .values(is_deleted=True)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_client_tasks(self, client_id: int, agent_id: int) -> List[Dict[str, Any]]:
        stmt = select(Task).where(
            Task.client_id == client_id,
            Task.agent_id == agent_id
        )
        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        return [
            {
                "id": t.id,
                "followup_type": t.followup_type,
                "scheduled_for": t.scheduled_for,
                "status": t.status,
                "priority": t.priority,
                "notes": t.notes,
            }
            for t in tasks
        ]

