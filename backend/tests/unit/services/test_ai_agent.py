"""
Unit tests for AI Agent service.

Tests email generation, prompt building, and response parsing with mocked OpenAI.
"""

import json
import sys
from pathlib import Path

# Add backend directory to Python path so we can import app
backend_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from app.services.ai_agent import AIAgent
from app.models.client import Client
from app.models.task import Task
from app.models.agent import Agent
from app.config import settings


# Helper functions
def create_test_client(**kwargs):
    """Helper to create test client with defaults."""
    defaults = {
        "id": 1,
        "name": "Test Client",
        "email": "test@example.com",
        "phone": None,
        "property_address": "123 Oak Street",
        "property_type": "residential",
        "stage": "lead",
        "notes": "Interested in 3-bedroom house",
        "custom_fields": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "last_contacted": None,
        "is_deleted": False
    }
    defaults.update(kwargs)
    return Client(**defaults)


def create_test_task(**kwargs):
    """Helper to create test task with defaults."""
    defaults = {
        "id": 1,
        "client_id": 1,
        "email_sent_id": None,
        "followup_type": "Day 1",
        "scheduled_for": datetime.now(timezone.utc),
        "status": "pending",
        "priority": "medium",
        "notes": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "completed_at": None
    }
    defaults.update(kwargs)
    return Task(**defaults)


def create_test_agent(**kwargs):
    """Helper to create test agent with defaults."""
    defaults = {
        "id": 1,
        "name": "Test Agent",
        "email": "agent@example.com",
        "title": "Real Estate Agent",
        "company": "Test Realty",
        "phone": "+1-555-0000",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    defaults.update(kwargs)
    return Agent(**defaults)


def create_mock_openai_response(subject, body):
    """Helper to create mock OpenAI response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "subject": subject,
        "body": body
    })
    return mock_response


# Tests for generate_email
@pytest.mark.asyncio
async def test_generate_email():
    """Test email generation with mocked OpenAI."""
    
    # Setup: Create mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "subject": "Following up on 123 Oak Street",
        "body": "Hi Jane,\n\nI wanted to follow up regarding the property at 123 Oak Street.\n\nBest regards"
    })
    
    # Mock the OpenAI client
    with patch('app.services.ai_agent.AsyncOpenAI') as mock_openai_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_class.return_value = mock_client
        
        # Create agent and test data
        ai_agent = AIAgent()
        agent = create_test_agent()
        client = create_test_client(
            name="Jane Smith",
            email="jane@example.com",
            property_address="123 Oak Street",
            property_type="residential",
            stage="lead",
            notes="Interested in 3-bedroom house"
        )
        task = create_test_task(
            followup_type="Day 1",
            priority="high"
        )
        
        # Execute
        result = await ai_agent.generate_email(client, task, agent)
        
        # Assert
        assert "subject" in result
        assert "body" in result
        assert "preview" in result
        assert result["subject"] == "Following up on 123 Oak Street"
        assert "Jane" in result["body"] or "follow up" in result["body"].lower()
        assert len(result["preview"]) > 0
        
        # Verify API was called
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        
        # Verify correct parameters
        assert call_args.kwargs["model"] == settings.OPENAI_MODEL
        assert call_args.kwargs["max_tokens"] == settings.OPENAI_MAX_TOKENS
        assert "temperature" in call_args.kwargs
        assert call_args.kwargs["temperature"] == 0.7
        assert "response_format" in call_args.kwargs
        assert call_args.kwargs["response_format"]["type"] == "json_object"


@pytest.mark.asyncio
async def test_generate_email_with_instructions():
    """Test email generation with custom agent instructions."""
    
    mock_response = create_mock_openai_response(
        "Following up on your inquiry",
        "Hi Jane,\n\nBased on your specific requirements, I wanted to reach out..."
    )
    
    with patch('app.services.ai_agent.AsyncOpenAI') as mock_openai_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_class.return_value = mock_client
        
        ai_agent = AIAgent()
        agent = create_test_agent()
        client = create_test_client(name="Jane Smith", email="jane@example.com")
        task = create_test_task()
        
        custom_instructions = "Be extra friendly and mention the neighborhood schools"
        result = await ai_agent.generate_email(client, task, agent, agent_instructions=custom_instructions)
        
        # Verify result
        assert "subject" in result
        assert "body" in result
        
        # Verify instructions were included in prompt
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        user_message = next(m for m in messages if m["role"] == "user")
        prompt = user_message["content"]
        
        assert "extra friendly" in prompt.lower() or "friendly" in prompt.lower()
        assert "neighborhood schools" in prompt.lower() or "schools" in prompt.lower()


@pytest.mark.asyncio
async def test_generate_email_api_failure():
    """Test graceful handling when OpenAI API fails."""
    
    with patch('app.services.ai_agent.AsyncOpenAI') as mock_openai_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        mock_openai_class.return_value = mock_client
        
        ai_agent = AIAgent()
        agent = create_test_agent()
        client = create_test_client(name="Jane", email="jane@test.com", stage="lead")
        task = create_test_task(followup_type="Day 1", priority="high")
        
        # Should not crash, should return fallback
        result = await ai_agent.generate_email(client, task, agent)
        
        assert "subject" in result
        assert "body" in result
        assert "preview" in result
        assert len(result["subject"]) > 0
        assert len(result["body"]) > 0
        # Fallback should still personalize with client name
        assert "Jane" in result["body"]


@pytest.mark.asyncio
async def test_generate_email_rate_limit_error():
    """Test handling of OpenAI rate limit errors."""
    
    with patch('app.services.ai_agent.AsyncOpenAI') as mock_openai_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("Rate limit exceeded. Status code: 429")
        )
        mock_openai_class.return_value = mock_client
        
        ai_agent = AIAgent()
        agent = create_test_agent()
        client = create_test_client(name="John Doe", email="john@test.com")
        task = create_test_task()
        
        result = await ai_agent.generate_email(client, task, agent)
        
        # Should return fallback email
        assert "subject" in result
        assert "body" in result
        assert "John" in result["body"]


# Tests for generate_email_preview
@pytest.mark.asyncio
async def test_generate_email_preview():
    """Test email preview generation."""
    
    mock_response = create_mock_openai_response(
        "Preview Subject",
        "Preview body content with multiple sentences. This is a longer email body for testing purposes."
    )
    
    with patch('app.services.ai_agent.AsyncOpenAI') as mock_openai_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai_class.return_value = mock_client
        
        ai_agent = AIAgent()
        agent = create_test_agent()
        client = create_test_client(name="Jane", email="jane@test.com", stage="lead")
        task = create_test_task(followup_type="Day 3", priority="medium")
        
        result = await ai_agent.generate_email_preview(client, task, agent)
        
        assert "subject" in result
        assert "body" in result
        assert "preview" in result
        assert result["subject"] == "Preview Subject"
        assert result["body"] == "Preview body content with multiple sentences. This is a longer email body for testing purposes."
        
        # Verify API was called with reduced max_tokens for preview
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["max_tokens"] <= 300


@pytest.mark.asyncio
async def test_generate_email_preview_api_failure():
    """Test preview generation with API failure."""
    
    with patch('app.services.ai_agent.AsyncOpenAI') as mock_openai_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("Network error")
        )
        mock_openai_class.return_value = mock_client
        
        ai_agent = AIAgent()
        agent = create_test_agent()
        client = create_test_client(name="Bob", email="bob@test.com")
        task = create_test_task()
        
        result = await ai_agent.generate_email_preview(client, task, agent)
        
        # Should return fallback
        assert "subject" in result
        assert "body" in result
        assert "preview" in result
        assert "Bob" in result["body"]


# Tests for _build_prompt
def test_build_prompt():
    """Test prompt building with all client and task data."""
    
    ai_agent = AIAgent()
    agent = create_test_agent()
    
    client = create_test_client(
        name="Jane Smith",
        email="jane@example.com",
        property_address="123 Oak Street",
        property_type="residential",
        stage="lead",
        notes="Interested in family-friendly neighborhood"
    )
    
    task = create_test_task(
        followup_type="Day 1",
        priority="high"
    )
    
    prompt = ai_agent._build_prompt(client, task, agent, agent_instructions="Be extra friendly")
    
    # Assert prompt structure
    assert isinstance(prompt, str)
    assert len(prompt) > 100  # Substantial prompt
    
    # Assert client data included
    assert "Jane Smith" in prompt or "Jane" in prompt
    assert "123 Oak Street" in prompt or "Oak Street" in prompt
    assert "residential" in prompt.lower()
    assert "lead" in prompt.lower()
    assert "family-friendly" in prompt or "neighborhood" in prompt
    
    # Assert task data included
    assert "Day 1" in prompt
    assert "high" in prompt.lower() or "priority" in prompt.lower()
    
    # Assert instructions included
    assert "extra friendly" in prompt.lower() or "Be extra friendly" in prompt


def test_build_prompt_with_minimal_data():
    """Test prompt building with minimal client data."""
    
    ai_agent = AIAgent()
    agent = create_test_agent()
    
    client = create_test_client(
        name="John Doe",
        email="john@test.com",
        stage="negotiating",
        property_address="",  # Empty address
        notes=None  # No notes
    )
    
    task = create_test_task(followup_type="Week 1", priority="low")
    
    prompt = ai_agent._build_prompt(client, task, agent)
    
    assert isinstance(prompt, str)
    assert len(prompt) > 50
    assert "John" in prompt
    assert "Week 1" in prompt or "week" in prompt.lower()
    assert "None" not in prompt  # No Python None in string
    assert "null" not in prompt.lower()  # No null values
    # Should handle missing address gracefully
    assert "Not specified" in prompt or "property" in prompt.lower()


def test_build_prompt_includes_instructions():
    """Test that custom instructions are included in prompt."""
    
    ai_agent = AIAgent()
    agent = create_test_agent()
    
    client = create_test_client(name="Alice", email="alice@test.com")
    task = create_test_task()
    
    custom_instructions = "Focus on the investment potential and ROI"
    prompt = ai_agent._build_prompt(client, task, agent, agent_instructions=custom_instructions)
    
    assert "investment potential" in prompt.lower() or "ROI" in prompt.lower() or "investment" in prompt.lower()
    assert custom_instructions in prompt or "investment potential" in prompt.lower()


def test_build_prompt_with_custom_fields():
    """Test prompt building includes custom fields when available."""
    
    ai_agent = AIAgent()
    agent = create_test_agent()
    
    client = create_test_client(
        name="Bob",
        email="bob@test.com",
        custom_fields={"budget": "500k", "preferred_location": "Downtown"}
    )
    task = create_test_task()
    
    prompt = ai_agent._build_prompt(client, task, agent)
    
    assert "budget" in prompt.lower() or "500k" in prompt
    assert "preferred_location" in prompt.lower() or "downtown" in prompt.lower()


def test_build_prompt_with_task_notes():
    """Test prompt building includes task notes."""
    
    ai_agent = AIAgent()
    agent = create_test_agent()
    
    client = create_test_client(name="Charlie", email="charlie@test.com")
    task = create_test_task(notes="Client requested virtual tour")
    
    prompt = ai_agent._build_prompt(client, task, agent)
    
    assert "virtual tour" in prompt.lower() or "Client requested virtual tour" in prompt


# Tests for _parse_openai_response
def test_parse_openai_response_json():
    """Test parsing OpenAI response with JSON format."""
    
    agent = AIAgent()
    
    # Create mock response with JSON
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "subject": "Test Subject Line",
        "body": "This is the email body with multiple sentences. It contains important information."
    })
    
    result = agent._parse_openai_response(mock_response)
    
    assert result["subject"] == "Test Subject Line"
    assert result["body"] == "This is the email body with multiple sentences. It contains important information."
    assert "preview" in result
    assert len(result["preview"]) > 0
    assert len(result["preview"]) <= len(result["body"])


def test_parse_openai_response_json_with_markdown():
    """Test parsing JSON response wrapped in markdown code blocks."""
    
    agent = AIAgent()
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    # OpenAI sometimes returns JSON wrapped in markdown
    mock_response.choices[0].message.content = """```json
{
  "subject": "Markdown Subject",
  "body": "Email body here"
}
```"""
    
    result = agent._parse_openai_response(mock_response)
    
    assert result["subject"] == "Markdown Subject"
    assert result["body"] == "Email body here"


def test_parse_openai_response_plain_text():
    """Test parsing OpenAI response with plain text format."""
    
    agent = AIAgent()
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """Subject: Follow-up Email

Hi Jane,

I wanted to reach out regarding the property at 123 Oak Street.

Best regards"""
    
    result = agent._parse_openai_response(mock_response)
    
    assert "subject" in result
    assert "body" in result
    assert len(result["subject"]) > 0
    assert len(result["body"]) > 0
    assert "Follow-up" in result["subject"] or "Email" in result["subject"]
    assert "Jane" in result["body"] or "property" in result["body"].lower()


def test_parse_openai_response_plain_text_no_subject_prefix():
    """Test parsing plain text without explicit Subject: prefix."""
    
    agent = AIAgent()
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """Following up on your inquiry

Hi there,

This is the email body."""
    
    result = agent._parse_openai_response(mock_response)
    
    assert "subject" in result
    assert "body" in result
    assert "Following" in result["subject"] or "inquiry" in result["subject"]


def test_parse_openai_response_error():
    """Test parsing handles errors gracefully."""
    
    agent = AIAgent()
    
    # Empty response
    mock_response = MagicMock()
    mock_response.choices = []
    
    result = agent._parse_openai_response(mock_response)
    
    # Should return fallback, not crash
    assert "subject" in result
    assert "body" in result
    assert "preview" in result
    assert len(result["subject"]) > 0
    assert len(result["body"]) > 0


def test_parse_openai_response_missing_content():
    """Test parsing handles missing content field."""
    
    agent = AIAgent()
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = None
    
    result = agent._parse_openai_response(mock_response)
    
    # Should return fallback
    assert "subject" in result
    assert "body" in result


def test_parse_openai_response_invalid_json():
    """Test parsing handles invalid JSON gracefully."""
    
    agent = AIAgent()
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is not valid JSON { invalid }"
    
    result = agent._parse_openai_response(mock_response)
    
    # Should fallback to text parsing
    assert "subject" in result
    assert "body" in result


def test_parse_openai_response_preview_truncation():
    """Test preview is truncated for long emails."""
    
    agent = AIAgent()
    
    long_body = "A" * 300  # 300 character body
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "subject": "Test",
        "body": long_body
    })
    
    result = agent._parse_openai_response(mock_response)
    
    assert len(result["preview"]) < len(long_body)
    assert result["preview"].endswith("...")
    assert len(result["preview"]) <= 200 + 3  # Max 200 chars + "..."


def test_parse_openai_response_preview_short():
    """Test preview for short emails is not truncated."""
    
    agent = AIAgent()
    
    short_body = "Short email body."
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "subject": "Test",
        "body": short_body
    })
    
    result = agent._parse_openai_response(mock_response)
    
    assert result["preview"] == short_body
    assert not result["preview"].endswith("...")


def test_parse_openai_response_missing_fields():
    """Test parsing handles JSON with missing subject or body."""
    
    agent = AIAgent()
    
    # JSON missing subject
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "body": "Email body only"
    })
    
    result = agent._parse_openai_response(mock_response)
    
    # Should fallback to text parsing or use default subject
    assert "subject" in result
    assert "body" in result
    assert len(result["subject"]) > 0


# Integration test
@pytest.mark.asyncio
@patch('app.services.ai_agent.AsyncOpenAI')
async def test_openai_integration(mock_openai_class):
    """Test full integration with OpenAI API (mocked)."""
    
    # Setup realistic mock response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "subject": "Great to Connect About 123 Oak Street",
        "body": """Hi Jane,

I hope this email finds you well! I wanted to reach out following your interest in the residential property at 123 Oak Street.

Based on your note about looking for a family-friendly neighborhood, I think this property would be a great fit. The area has excellent schools and parks nearby.

Would you be available for a showing this week? I'd love to answer any questions you might have.

Looking forward to hearing from you!

Best regards,
Your Real Estate Agent"""
    })
    
    # Mock OpenAI client
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    mock_openai_class.return_value = mock_client
    
    # Create test data
    ai_agent = AIAgent()
    agent = create_test_agent()
    client = create_test_client(
        name="Jane Smith",
        email="jane@example.com",
        property_address="123 Oak Street",
        property_type="residential",
        stage="lead",
        notes="Looking for family-friendly neighborhood"
    )
    task = create_test_task(
        followup_type="Day 1",
        priority="high"
    )
    
    # Execute full flow
    result = await ai_agent.generate_email(client, task, agent, agent_instructions="Keep it warm and friendly")
    
    # Verify result structure
    assert result["subject"] == "Great to Connect About 123 Oak Street"
    assert "Jane" in result["body"]
    assert "123 Oak Street" in result["body"]
    assert "family-friendly" in result["body"]
    assert len(result["preview"]) > 0
    # Long email should be truncated
    if len(result["body"]) > 200:
        assert result["preview"].endswith("...")
    
    # Verify API call
    mock_client.chat.completions.create.assert_called_once()
    
    # Verify prompt construction
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    messages = call_kwargs["messages"]
    user_message = next(m for m in messages if m["role"] == "user")
    prompt = user_message["content"]
    
    assert "Jane Smith" in prompt
    assert "123 Oak Street" in prompt
    assert "Day 1" in prompt
    assert "warm and friendly" in prompt.lower()
    
    # Verify system message
    system_message = next(m for m in messages if m["role"] == "system")
    assert "real estate agent" in system_message["content"].lower()


@pytest.mark.asyncio
async def test_generate_email_with_none_client():
    """Test handling of invalid input (None client)."""
    
    ai_agent = AIAgent()
    agent = create_test_agent()
    task = create_test_task()
    
    # Implementation doesn't handle None client - it will raise AttributeError
    # This test documents the current behavior
    with pytest.raises(AttributeError):
        await ai_agent.generate_email(None, task, agent)


@pytest.mark.asyncio
async def test_generate_email_with_none_task():
    """Test handling of invalid input (None task)."""
    
    ai_agent = AIAgent()
    agent = create_test_agent()
    client = create_test_client()
    
    # Implementation doesn't handle None task - it will raise AttributeError
    # This test documents the current behavior
    with pytest.raises(AttributeError):
        await ai_agent.generate_email(client, None, agent)


def test_build_prompt_all_followup_types():
    """Test prompt building for different follow-up types."""
    
    ai_agent = AIAgent()
    agent = create_test_agent()
    client = create_test_client()
    
    followup_types = ["Day 1", "Day 3", "Week 1", "Week 2", "Month 1", "Custom Type"]
    
    for followup_type in followup_types:
        task = create_test_task(followup_type=followup_type)
        prompt = ai_agent._build_prompt(client, task, agent)
        
        assert followup_type in prompt
        assert isinstance(prompt, str)
        assert len(prompt) > 50
