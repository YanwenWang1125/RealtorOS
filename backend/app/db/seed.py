"""
Database seeding script for RealtorOS.

This module provides functions to seed the database with demo data
for development and testing purposes.
"""

import asyncio
from datetime import datetime, timedelta
from app.db.mongodb import connect_to_mongo, get_database
from app.models.client import Client
from app.models.task import Task
from app.models.email_log import EmailLog
from app.constants.followup_schedules import FOLLOWUP_SCHEDULE

async def seed_database():
    """Seed the database with demo data."""
    await connect_to_mongo()
    db = get_database()
    
    # Clear existing data
    await db.clients.delete_many({})
    await db.tasks.delete_many({})
    await db.email_logs.delete_many({})
    
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
    
    # Insert clients
    client_ids = []
    for client_data in demo_clients:
        client = Client(**client_data)
        result = await db.clients.insert_one(client.dict(by_alias=True))
        client_ids.append(str(result.inserted_id))
    
    # Create follow-up tasks for each client
    for client_id in client_ids:
        for followup_type, config in FOLLOWUP_SCHEDULE.items():
            scheduled_date = datetime.utcnow() + timedelta(days=config["days"])
            
            task_data = {
                "client_id": client_id,
                "followup_type": followup_type,
                "scheduled_for": scheduled_date,
                "status": "pending",
                "priority": config["priority"],
                "created_at": datetime.utcnow()
            }
            
            task = Task(**task_data)
            await db.tasks.insert_one(task.dict(by_alias=True))
    
    print(f"Seeded database with {len(demo_clients)} clients and their follow-up tasks")
    print("Demo data created successfully!")

if __name__ == "__main__":
    asyncio.run(seed_database())
