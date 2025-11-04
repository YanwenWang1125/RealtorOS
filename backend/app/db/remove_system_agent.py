"""
Remove the system agent from the database and reassign all references to the test agent.
"""

import asyncio
from sqlalchemy import select, update
from app.db import postgresql
from app.models.agent import Agent
from app.models.client import Client
from app.models.task import Task
from app.models.email_log import EmailLog


async def remove_system_agent():
    """Remove the system agent from the database and reassign references to test agent."""
    await postgresql.init_db()
    
    if postgresql.SessionLocal is None:
        raise RuntimeError("Database not initialized. SessionLocal is None.")
    
    async with postgresql.SessionLocal() as session:
        try:
            # Find system agent
            stmt = select(Agent).where(Agent.email == "system@realtoros.com")
            result = await session.execute(stmt)
            system_agent = result.scalar_one_or_none()
            
            if not system_agent:
                print("[INFO] System agent not found. Nothing to remove.")
                return
            
            # Find test agent
            test_email = "yanwenwang1125@gmail.com"
            test_stmt = select(Agent).where(Agent.email == test_email)
            test_result = await session.execute(test_stmt)
            test_agent = test_result.scalar_one_or_none()
            
            if not test_agent:
                print(f"[ERROR] Test agent ({test_email}) not found!")
                print("[INFO] Please run 'python -m app.db.ensure_agent' first to create the test agent.")
                return
            
            print(f"[INFO] Found system agent (ID: {system_agent.id})")
            print(f"[INFO] Found test agent (ID: {test_agent.id})")
            
            # Reassign all clients from system agent to test agent
            clients_stmt = select(Client).where(Client.agent_id == system_agent.id)
            clients_result = await session.execute(clients_stmt)
            clients = clients_result.scalars().all()
            
            if clients:
                await session.execute(
                    update(Client)
                    .where(Client.agent_id == system_agent.id)
                    .values(agent_id=test_agent.id)
                )
                print(f"[OK] Reassigned {len(clients)} client(s) to test agent")
            
            # Reassign all tasks from system agent to test agent
            tasks_stmt = select(Task).where(Task.agent_id == system_agent.id)
            tasks_result = await session.execute(tasks_stmt)
            tasks = tasks_result.scalars().all()
            
            if tasks:
                await session.execute(
                    update(Task)
                    .where(Task.agent_id == system_agent.id)
                    .values(agent_id=test_agent.id)
                )
                print(f"[OK] Reassigned {len(tasks)} task(s) to test agent")
            
            # Reassign all email logs from system agent to test agent
            emails_stmt = select(EmailLog).where(EmailLog.agent_id == system_agent.id)
            emails_result = await session.execute(emails_stmt)
            emails = emails_result.scalars().all()
            
            if emails:
                await session.execute(
                    update(EmailLog)
                    .where(EmailLog.agent_id == system_agent.id)
                    .values(agent_id=test_agent.id)
                )
                print(f"[OK] Reassigned {len(emails)} email log(s) to test agent")
            
            # Now delete the system agent
            await session.delete(system_agent)
            await session.commit()
            
            print(f"[OK] Removed system agent (ID: {system_agent.id}, Email: {system_agent.email})")
            
            # Show remaining agents
            remaining_stmt = select(Agent).where(Agent.is_active == True)
            remaining_result = await session.execute(remaining_stmt)
            remaining_agents = remaining_result.scalars().all()
            
            print(f"\nRemaining active agents: {len(remaining_agents)}")
            for agent in remaining_agents:
                print(f"  - ID: {agent.id}, Email: {agent.email}, Name: {agent.name}")
            
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Error removing system agent: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(remove_system_agent())

