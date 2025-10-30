"""
CRM service for client management (SQLAlchemy + AsyncSession).
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.client import Client
from app.models.task import Task
from app.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse


class CRMService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_client(self, client_data: ClientCreate) -> ClientResponse:
        client = Client(
            name=client_data.name,
            email=client_data.email,
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

    async def get_client(self, client_id: int) -> Optional[ClientResponse]:
        stmt = select(Client).where(Client.id == client_id)
        result = await self.session.execute(stmt)
        client = result.scalar_one_or_none()
        if client is None:
            return None
        return ClientResponse.model_validate(client.__dict__, from_attributes=True)

    async def list_clients(self, page: int = 1, limit: int = 10, stage: Optional[str] = None) -> List[ClientResponse]:
        offset = (page - 1) * limit
        stmt = select(Client).where(Client.is_deleted == False)  # noqa: E712
        if stage:
            stmt = stmt.where(Client.stage == stage)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        clients = result.scalars().all()
        return [ClientResponse.model_validate(c.__dict__, from_attributes=True) for c in clients]

    async def update_client(self, client_id: int, client_data: ClientUpdate) -> Optional[ClientResponse]:
        update_data = client_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_client(client_id)
        stmt = (
            update(Client)
            .where(Client.id == client_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_client(client_id)

    async def delete_client(self, client_id: int) -> bool:
        stmt = (
            update(Client)
            .where(Client.id == client_id)
            .values(is_deleted=True)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_client_tasks(self, client_id: int) -> List[Dict[str, Any]]:
        stmt = select(Task).where(Task.client_id == client_id)
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
