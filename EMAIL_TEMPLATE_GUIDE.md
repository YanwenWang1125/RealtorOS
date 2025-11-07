# Email Template Customization Guide

## Overview

RealtorOS uses AI-powered email generation. Emails are created dynamically by OpenAI based on prompts built in `backend/app/services/ai_agent.py`. The `email_templates.py` file exists but is currently not integrated.

## How to Modify Email Templates

### Method 1: Modify the AI Prompt (Current System)

The main file to edit is: `backend/app/services/ai_agent.py`

#### Change Email Tone/Style

Edit the `_build_prompt()` method around **lines 48-52**:

```python
# Current (lines 48-52)
prompt_parts = [
    "You are a professional real estate agent assistant.",
    "Your task is to write personalized, professional follow-up emails.",
    "Tone: Friendly, professional, helpful (not pushy).",
    "Goal: Build relationship, provide value, move deal forward.",
    "",
]

# Example: More formal tone
prompt_parts = [
    "You are a professional real estate agent assistant.",
    "Your task is to write personalized, professional follow-up emails.",
    "Tone: Formal, courteous, and business-focused.",
    "Goal: Build relationship, provide value, move deal forward.",
    "",
]

# Example: More casual tone
prompt_parts = [
    "You are a friendly real estate agent assistant.",
    "Your task is to write warm, personalized follow-up emails.",
    "Tone: Casual, friendly, and approachable (like talking to a friend).",
    "Goal: Build relationship, provide value, move deal forward.",
    "",
]
```

#### Modify Follow-up Type Instructions

Edit the `followup_context` dictionary around **lines 98-139**:

```python
# Example: Add a new follow-up type
followup_context = {
    "Day 1": (
        "Initial contact after client expressed interest.",
        "Goals:\n"
        "- Introduce yourself warmly\n"
        "- Confirm their interest\n"
        "- Offer to answer questions\n"
        "- Suggest next steps (phone call or showing)"
    ),
    # Add new type
    "Day 7": (
        "Week follow-up to re-engage.",
        "Goals:\n"
        "- Re-engage with market updates\n"
        "- Share new property listings\n"
        "- Schedule property tour"
    ),
    # ... rest of types
}
```

#### Change Email Structure/Format

Edit the instructions around **lines 165-181**:

```python
# Current instructions
prompt_parts.extend([
    "- Write a friendly, professional email",
    "- Keep it concise (3-5 short paragraphs)",
    "- Use the client's name naturally",
    "- Reference the specific property when relevant",
    "- Include a clear call-to-action",
    "- End with a professional closing",
    "",
])

# Example: Longer, more detailed emails
prompt_parts.extend([
    "- Write a detailed, professional email",
    "- Use 5-7 paragraphs with more context",
    "- Use the client's name naturally",
    "- Reference the specific property when relevant",
    "- Include market data and insights",
    "- Include multiple call-to-action options",
    "- End with a professional closing",
    "",
])
```

### Method 2: Integrate the Templates File (Optional)

If you want to use the existing `email_templates.py` file, you can modify `ai_agent.py` to import and use it:

1. **Import the templates** at the top of `ai_agent.py`:

```python
from app.constants.email_templates import EMAIL_PROMPT_TEMPLATE, FOLLOWUP_TEMPLATES, SUBJECT_TEMPLATES
```

2. **Use the template in `_build_prompt()`**:

```python
def _build_prompt(self, client: Client, task: Task, agent: Agent, agent_instructions: Optional[str] = None) -> str:
    # Use the template from email_templates.py
    template = EMAIL_PROMPT_TEMPLATE.format(
        client_name=client.name,
        client_email=client.email,
        property_address=client.property_address or "Not specified",
        property_type=client.property_type,
        client_stage=client.stage,
        client_notes=client.notes or "None",
        last_contacted="N/A",  # You'd need to track this
        followup_type=task.followup_type,
        current_date=datetime.now().strftime("%Y-%m-%d"),
        days_since_contact=0,  # You'd need to calculate this
        agent_instructions=agent_instructions or "None"
    )
    return template
```

### Method 3: Add Static Templates (Advanced)

If you want completely static templates (no AI generation), you can create a new method:

```python
def _get_static_template(self, client: Client, task: Task, agent: Agent) -> Dict[str, str]:
    """Return a static email template based on follow-up type."""
    templates = {
        "Day 1": {
            "subject": f"Quick follow-up on {client.property_address or 'your inquiry'}",
            "body": f"""Hi {client.name},

Thank you for your interest in {client.property_address or 'real estate'}.

I wanted to reach out and see if you have any questions. I'm here to help!

Would you like to schedule a call or property showing?

Best regards,
{agent.name}
{agent.title or 'Real Estate Agent'}
{agent.company or ''}
Phone: {agent.phone or ''}
Email: {agent.email}"""
        },
        # Add more templates...
    }
    
    followup_type = task.followup_type
    if followup_type in templates:
        return templates[followup_type]
    else:
        return templates["Day 1"]  # Default
```

## Common Customizations

### 1. Change Email Length

**Location**: `ai_agent.py`, line 167

```python
# Short emails
"- Keep it concise (2-3 short paragraphs)",

# Medium emails (current)
"- Keep it concise (3-5 short paragraphs)",

# Long emails
"- Write a detailed email (5-7 paragraphs)",
```

### 2. Add HTML Formatting

**Location**: `ai_agent.py`, line 177

```python
# Current
'  "body": "Full email body with paragraphs separated by \\n\\n"',

# With HTML
'  "body": "Full email body in HTML format with <p> tags for paragraphs"',
```

### 3. Customize Signature Format

**Location**: `ai_agent.py`, lines 82-91

```python
# Current format
prompt_parts.append("Best regards,")
prompt_parts.append(f"{agent.name}")
# ...

# Alternative format
prompt_parts.append("Warm regards,")
prompt_parts.append(f"{agent.name}")
prompt_parts.append(f"{agent.title or 'Real Estate Agent'}")
if agent.company:
    prompt_parts.append(f"at {agent.company}")
# ...
```

### 4. Add More Context to Prompts

**Location**: `ai_agent.py`, after line 72

```python
# Add market data
if hasattr(client, 'market_data'):
    prompt_parts.append(f"Market Data: {client.market_data}")

# Add previous email history
if hasattr(client, 'email_history'):
    prompt_parts.append(f"Previous Emails: {client.email_history}")
```

## Testing Your Changes

1. **Restart the backend server** after making changes
2. **Generate a test email** through the UI or API
3. **Check the generated email** to see if it matches your expectations
4. **Iterate** by adjusting the prompt until you get the desired output

## Files to Edit

- **Primary**: `backend/app/services/ai_agent.py` - Main AI email generation
- **Templates**: `backend/app/constants/email_templates.py` - Template constants (currently unused)
- **Fallback**: `backend/app/services/ai_agent.py`, `_get_fallback_email()` method (lines 523-569) - Used when AI fails

## Notes

- Changes to `ai_agent.py` take effect immediately after server restart
- The AI will interpret your prompts, so be specific about what you want
- Test with different follow-up types to ensure all scenarios work
- The `agent_instructions` parameter allows per-email customization via the UI

