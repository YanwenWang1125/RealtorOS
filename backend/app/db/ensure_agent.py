"""
Quick utility to ensure default agents exist in the database.
Run this if you get "No active agents found" error.
"""

import asyncio
from sqlalchemy import select
from app.db import postgresql
from app.models.agent import Agent


async def ensure_default_agents():
    """Ensure test agent exists in the database (for development bypass)."""
    await postgresql.init_db()
    
    if postgresql.SessionLocal is None:
        raise RuntimeError("Database not initialized. SessionLocal is None.")
    
    async with postgresql.SessionLocal() as session:
        try:
            # Ensure test agent exists (used for development bypass)
            test_email = "yanwenwang1125@gmail.com"
            stmt = select(Agent).where(Agent.email == test_email)
            result = await session.execute(stmt)
            test_agent = result.scalar_one_or_none()
            
            if test_agent:
                print(f"[OK] Test agent already exists (ID: {test_agent.id}, Email: {test_agent.email})")
                return test_agent
            else:
                print(f"Creating test agent ({test_email})...")
                test_agent = Agent(
                    email=test_email,
                    name="Test Agent",
                    phone="+1-555-0000",
                    title="Senior Real Estate Agent",
                    company="Test Realty",
                    bio="Test agent for development and testing purposes",
                    auth_provider="email",
                    is_active=True
                )
                session.add(test_agent)
                await session.commit()
                await session.refresh(test_agent)
                print(f"[OK] Created test agent (ID: {test_agent.id}, Email: {test_agent.email})")
                return test_agent
            
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Error ensuring agents: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(ensure_default_agents())

