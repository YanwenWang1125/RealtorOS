"""
Manual test script for AI Agent service.

This script tests the AI agent email generation functionality
without requiring a database connection.

Usage:
    # Run directly with Python (from backend directory):
    python tests/unit/services/test_ai_manual.py
    
    # Or with pytest:
    pytest tests/unit/services/test_ai_manual.py -v -s
"""

import sys
from pathlib import Path

# Add backend directory to path so we can import app modules
# File is at: backend/tests/unit/services/test_ai_manual.py
# Need to go up 3 levels to get to backend root
backend_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import asyncio
import pytest

from app.services.ai_agent import AIAgent
from app.models.client import Client
from app.models.task import Task


# Mock objects that mimic SQLAlchemy models for testing
class MockClient:
    """Mock Client object for testing without database."""
    def __init__(self, name, email, property_address, property_type, stage, notes=None, custom_fields=None):
        self.id = 1
        self.name = name
        self.email = email
        self.property_address = property_address
        self.property_type = property_type
        self.stage = stage
        self.notes = notes
        self.custom_fields = custom_fields


class MockTask:
    """Mock Task object for testing without database."""
    def __init__(self, followup_type, priority=None, notes=None):
        self.id = 1
        self.followup_type = followup_type
        self.priority = priority
        self.notes = notes
        self.scheduled_for = None
        self.status = "pending"


@pytest.mark.asyncio
async def test_basic_email_generation():
    """Test basic email generation."""
    print("=" * 80)
    print("TEST 1: Basic Email Generation (Day 1)")
    print("=" * 80)
    
    agent = AIAgent()
    
    client = MockClient(
        name="Jane Smith",
        email="jane@example.com",
        property_address="123 Oak Street",
        property_type="residential",
        stage="lead",
        notes="Interested in 3-bedroom house"
    )
    
    task = MockTask(
        followup_type="Day 1",
        priority="high"
    )
    
    try:
        result = await agent.generate_email(client, task)
        print("\n✅ Success!")
        print("\nSubject:", result["subject"])
        print("\nBody:")
        print(result["body"])
        print("\nPreview:", result["preview"])
        print()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


@pytest.mark.asyncio
async def test_day_3_followup():
    """Test Day 3 follow-up email."""
    print("=" * 80)
    print("TEST 2: Day 3 Follow-up")
    print("=" * 80)
    
    agent = AIAgent()
    
    client = MockClient(
        name="John Doe",
        email="john@example.com",
        property_address="456 Maple Avenue",
        property_type="commercial",
        stage="negotiating",
        notes="Looking for office space, needs parking",
        custom_fields={"budget": "$500k", "square_feet": "5000"}
    )
    
    task = MockTask(
        followup_type="Day 3",
        priority="medium",
        notes="Client had questions about parking availability"
    )
    
    try:
        result = await agent.generate_email(client, task)
        print("\n✅ Success!")
        print("\nSubject:", result["subject"])
        print("\nBody:")
        print(result["body"])
        print()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


@pytest.mark.asyncio
async def test_week_1_followup():
    """Test Week 1 follow-up email."""
    print("=" * 80)
    print("TEST 3: Week 1 Follow-up")
    print("=" * 80)
    
    agent = AIAgent()
    
    client = MockClient(
        name="Sarah Johnson",
        email="sarah@example.com",
        property_address="789 Pine Road",
        property_type="residential",
        stage="lead",
        notes="First-time buyer, very excited",
        custom_fields={"first_time_buyer": True, "timeline": "ASAP"}
    )
    
    task = MockTask(
        followup_type="Week 1",
        priority="medium"
    )
    
    try:
        result = await agent.generate_email(client, task)
        print("\n✅ Success!")
        print("\nSubject:", result["subject"])
        print("\nBody:")
        print(result["body"])
        print()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


@pytest.mark.asyncio
async def test_with_custom_instructions():
    """Test email generation with custom agent instructions."""
    print("=" * 80)
    print("TEST 4: Custom Agent Instructions")
    print("=" * 80)
    
    agent = AIAgent()
    
    client = MockClient(
        name="Mike Wilson",
        email="mike@example.com",
        property_address="321 Elm Street",
        property_type="residential",
        stage="under_contract",
        notes="Closing in 2 weeks"
    )
    
    task = MockTask(
        followup_type="Day 1",
        priority="high"
    )
    
    custom_instructions = "Please emphasize our expertise in closing deals quickly and mention our satisfaction guarantee."
    
    try:
        result = await agent.generate_email(client, task, agent_instructions=custom_instructions)
        print("\n✅ Success!")
        print("\nSubject:", result["subject"])
        print("\nBody:")
        print(result["body"])
        print()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


@pytest.mark.asyncio
async def test_email_preview():
    """Test email preview generation."""
    print("=" * 80)
    print("TEST 5: Email Preview Generation")
    print("=" * 80)
    
    agent = AIAgent()
    
    client = MockClient(
        name="Emily Chen",
        email="emily@example.com",
        property_address="654 Maple Drive",
        property_type="land",
        stage="lead",
        notes="Looking for land for future development"
    )
    
    task = MockTask(
        followup_type="Month 1",
        priority="low"
    )
    
    try:
        result = await agent.generate_email_preview(client, task)
        print("\n✅ Success!")
        print("\nSubject:", result["subject"])
        print("\nBody:")
        print(result["body"])
        print("\nPreview:", result["preview"])
        print()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def run_all_tests():
    """Run all test cases."""
    print("\n" + "=" * 80)
    print("AI AGENT MANUAL TEST SUITE")
    print("=" * 80)
    print("\nThis script tests the AI agent email generation functionality.")
    print("Make sure you have set OPENAI_API_KEY in your .env file.\n")
    
    try:
        await test_basic_email_generation()
        await asyncio.sleep(1)  # Small delay between tests
        
        await test_day_3_followup()
        await asyncio.sleep(1)
        
        await test_week_1_followup()
        await asyncio.sleep(1)
        
        await test_with_custom_instructions()
        await asyncio.sleep(1)
        
        await test_email_preview()
        
        print("=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if OpenAI API key is configured
    try:
        from app.config import settings
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "":
            print("⚠️  WARNING: OPENAI_API_KEY is not set in .env file")
            print("   Tests will fail. Please set your OpenAI API key first.\n")
    except Exception as e:
        print(f"⚠️  WARNING: Could not load settings: {e}")
        print("   Make sure .env file exists with OPENAI_API_KEY configured.\n")
    
    # Run the tests
    asyncio.run(run_all_tests())

