"""
Database seeding script for RealtorOS.

This module provides functions to seed the database with demo data
for development and testing purposes.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select
from app.db import postgresql
from app.models.client import Client
from app.models.task import Task
from app.models.email_log import EmailLog
from app.models.agent import Agent
from app.constants.followup_schedules import FOLLOWUP_SCHEDULE


def utcnow():
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

async def seed_database():
    """Seed the database with demo data (PostgreSQL)."""
    await postgresql.init_db()
    
    if postgresql.SessionLocal is None:
        raise RuntimeError("Database not initialized. SessionLocal is None.")
    
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
            "custom_fields": {
                "budget": "$300k",
                "preferred_neighborhoods": ["Downtown", "Riverside"],
                "bedrooms": 3
            },
            "created_at": utcnow() - timedelta(days=5),
            "last_contacted": utcnow() - timedelta(days=2)
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.j@email.com",
            "phone": "+1-555-0456",
            "property_address": "456 Oak Ave, Anytown, ST 12345",
            "property_type": "commercial",
            "stage": "negotiating",
            "notes": "Looking for office space, needs parking for 20+ cars",
            "custom_fields": {
                "square_feet": "5000-7500",
                "parking_spaces": 20,
                "lease_type": "long_term"
            },
            "created_at": utcnow() - timedelta(days=10),
            "last_contacted": utcnow() - timedelta(hours=6)
        },
        {
            "name": "Mike Wilson",
            "email": "mike.wilson@email.com",
            "phone": "+1-555-0789",
            "property_address": "789 Pine Rd, Anytown, ST 12345",
            "property_type": "residential",
            "stage": "under_contract",
            "notes": "First-time buyer, very excited about the property",
            "custom_fields": {
                "first_time_buyer": True,
                "financing_preapproved": True,
                "timeline": "ASAP"
            },
            "created_at": utcnow() - timedelta(days=15),
            "last_contacted": utcnow() - timedelta(hours=2)
        },
        {
            "name": "Emily Chen",
            "email": "emily.chen@email.com",
            "phone": "+1-555-0321",
            "property_address": "321 Elm St, Springfield, ST 54321",
            "property_type": "residential",
            "stage": "lead",
            "notes": "Interested in suburban homes, has two kids",
            "custom_fields": {
                "children": 2,
                "school_district": "Springfield ISD",
                "preferred_style": "ranch"
            },
            "created_at": utcnow() - timedelta(days=3),
            "last_contacted": utcnow() - timedelta(days=1)
        },
        {
            "name": "Robert Martinez",
            "email": "robert.m@email.com",
            "phone": "+1-555-0654",
            "property_address": "654 Maple Dr, Lakeside, ST 67890",
            "property_type": "land",
            "stage": "negotiating",
            "notes": "Looking to purchase land for future development",
            "custom_fields": {
                "acres": "10-20",
                "zoning": "mixed_use",
                "development_plans": "commercial_residential"
            },
            "created_at": utcnow() - timedelta(days=20),
            "last_contacted": utcnow() - timedelta(hours=12)
        },
        {
            "name": "Lisa Anderson",
            "email": "lisa.a@email.com",
            "phone": "+1-555-0987",
            "property_address": "987 Cedar Ln, Hilltop, ST 11223",
            "property_type": "residential",
            "stage": "closed",
            "notes": "Successfully closed on property last month",
            "custom_fields": {
                "closing_date": "2024-01-15",
                "final_price": "$425k",
                "satisfaction_rating": 5
            },
            "created_at": utcnow() - timedelta(days=45),
            "last_contacted": utcnow() - timedelta(days=30)
        },
        {
            "name": "David Thompson",
            "email": "david.t@email.com",
            "phone": "+1-555-0147",
            "property_address": "147 Birch Way, Valley View, ST 44556",
            "property_type": "commercial",
            "stage": "lead",
            "notes": "Investor looking for multi-unit properties",
            "custom_fields": {
                "investment_type": "rental_income",
                "target_units": "4-8",
                "cash_buyer": True
            },
            "created_at": utcnow() - timedelta(days=7),
            "last_contacted": utcnow() - timedelta(days=3)
        },
        {
            "name": "Jennifer White",
            "email": "jennifer.w@email.com",
            "phone": "+1-555-0258",
            "property_address": "258 Spruce Ave, Mountain View, ST 77889",
            "property_type": "residential",
            "stage": "lost",
            "notes": "Client decided to work with another agent",
            "custom_fields": {
                "lost_reason": "competitor",
                "followup_date": "2024-03-01"
            },
            "created_at": utcnow() - timedelta(days=30),
            "last_contacted": utcnow() - timedelta(days=25)
        }
    ]
    
    async with postgresql.SessionLocal() as session:
        try:
            # Ensure system agent exists
            stmt = select(Agent).where(Agent.email == "system@realtoros.com")
            result = await session.execute(stmt)
            system_agent = result.scalar_one_or_none()
            
            if not system_agent:
                system_agent = Agent(
                    email="system@realtoros.com",
                    name="System Agent",
                    auth_provider="email",
                    is_active=True
                )
                session.add(system_agent)
                await session.commit()
                await session.refresh(system_agent)
                print("Created system agent...")
            else:
                print("System agent already exists...")
            
            # Get agent_id for clients (use system agent)
            agent_id = system_agent.id
            
            # Clear existing data (using proper SQLAlchemy syntax)
            await session.execute(delete(EmailLog))
            await session.execute(delete(Task))
            await session.execute(delete(Client))
            await session.commit()
            
            print("Cleared existing data...")

            # Insert clients
            client_ids = []
            for client_data in demo_clients:
                client = Client(**client_data, agent_id=agent_id)
                session.add(client)
                await session.flush()  # Flush to get the ID
                client_ids.append(client.id)
            
            await session.commit()
            print(f"Inserted {len(demo_clients)} clients...")

            # Create follow-up tasks for each client
            total_tasks = 0
            for client_id in client_ids:
                for followup_type, config in FOLLOWUP_SCHEDULE.items():
                    scheduled_date = utcnow() + timedelta(days=config["days"])

                    task = Task(
                        client_id=client_id,
                        agent_id=agent_id,
                        followup_type=followup_type,
                        scheduled_for=scheduled_date,
                        status="pending",
                        priority=config["priority"],
                        notes=f"Automated follow-up: {config['description']}"
                    )
                    session.add(task)
                    total_tasks += 1
            
            await session.commit()
            print(f"Created {total_tasks} follow-up tasks...")

            print(f"\n✅ Successfully seeded database:")
            print(f"   - {len(demo_clients)} clients")
            print(f"   - {total_tasks} follow-up tasks")
            print("Demo data created successfully!")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding database: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(seed_database())
