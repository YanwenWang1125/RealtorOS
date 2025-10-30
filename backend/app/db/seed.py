"""
Database seeding script for RealtorOS.

This module provides functions to seed the database with demo data
for development and testing purposes.
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgresql import init_db, get_session
from app.models.client import Client
from app.models.task import Task
from app.constants.followup_schedules import FOLLOWUP_SCHEDULE

async def seed_database():
    """Seed the database with demo data (PostgreSQL)."""
    await init_db()
    # Create demo clients
    demo_clients = [
        {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone": "+1-555-0123",
            "property_address": "123 Main St, Anytown, ST 12345",
            "property_type": "residential",
            "stage": "lead",
            "notes": "Interested in 3-bedroom home, budget around $300k",
            "created_at": datetime.utcnow() - timedelta(days=5),
            "last_contacted": datetime.utcnow() - timedelta(days=2)
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.j@email.com",
            "phone": "+1-555-0456",
            "property_address": "456 Oak Ave, Anytown, ST 12345",
            "property_type": "commercial",
            "stage": "negotiating",
            "notes": "Looking for office space, needs parking for 20+ cars",
            "created_at": datetime.utcnow() - timedelta(days=10),
            "last_contacted": datetime.utcnow() - timedelta(hours=6)
        },
        {
            "name": "Mike Wilson",
            "email": "mike.wilson@email.com",
            "phone": "+1-555-0789",
            "property_address": "789 Pine Rd, Anytown, ST 12345",
            "property_type": "residential",
            "stage": "under_contract",
            "notes": "First-time buyer, very excited about the property",
            "created_at": datetime.utcnow() - timedelta(days=15),
            "last_contacted": datetime.utcnow() - timedelta(hours=2)
        }
    ]
    
    async for session in get_session():
        # Clear existing data
        await session.execute("DELETE FROM email_logs")
        await session.execute("DELETE FROM tasks")
        await session.execute("DELETE FROM clients")
        await session.commit()

        # Insert clients
        client_ids = []
        for client_data in demo_clients:
            client = Client(**client_data)
            session.add(client)
            await session.flush()
            client_ids.append(client.id)
        await session.commit()

        # Create follow-up tasks for each client
        for client_id in client_ids:
            for followup_type, config in FOLLOWUP_SCHEDULE.items():
                scheduled_date = datetime.utcnow() + timedelta(days=config["days"])

                task = Task(
                    client_id=client_id,
                    followup_type=followup_type,
                    scheduled_for=scheduled_date,
                    status="pending",
                    priority=config["priority"],
                )
                session.add(task)
        await session.commit()

        print(f"Seeded database with {len(demo_clients)} clients and their follow-up tasks")
        print("Demo data created successfully!")

if __name__ == "__main__":
    asyncio.run(seed_database())
