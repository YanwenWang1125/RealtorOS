"""
Quick utility to check agent status in the database.
"""

import asyncio
from sqlalchemy import select
from app.db import postgresql
from app.models.agent import Agent


async def check_agents():
    """Check all agents in the database."""
    await postgresql.init_db()
    
    if postgresql.SessionLocal is None:
        raise RuntimeError("Database not initialized. SessionLocal is None.")
    
    async with postgresql.SessionLocal() as session:
        try:
            # Get all agents
            stmt = select(Agent)
            result = await session.execute(stmt)
            agents = result.scalars().all()
            
            if not agents:
                print("[WARNING] No agents found in database!")
                return
            
            print(f"Found {len(agents)} agent(s):")
            for agent in agents:
                status = "ACTIVE" if agent.is_active else "INACTIVE"
                print(f"  - ID: {agent.id}, Email: {agent.email}, Name: {agent.name}, Status: {status}")
            
            # Check active agents specifically
            active_stmt = select(Agent).where(Agent.is_active == True)
            active_result = await session.execute(active_stmt)
            active_agents = active_result.scalars().all()
            
            print(f"\nActive agents: {len(active_agents)}")
            if len(active_agents) == 0:
                print("[ERROR] No active agents found! This will cause API errors.")
                print("Solution: Run 'python -m app.db.ensure_agent' to create/fix the system agent.")
            
        except Exception as e:
            print(f"[ERROR] Error checking agents: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(check_agents())

