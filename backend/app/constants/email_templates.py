"""
Email template constants for RealtorOS.

This module defines email prompt templates and formatting
for the RealtorOS email generation system.
"""

# Base email prompt template
EMAIL_PROMPT_TEMPLATE = """
You are a friendly, professional real estate agent following up with a client.

Client Profile:
- Name: {client_name}
- Email: {client_email}
- Property: {property_address}
- Property Type: {property_type}
- Stage: {client_stage}
- Last Note: {client_notes}
- Last Contacted: {last_contacted}

Follow-up Type: {followup_type}
Current Date: {current_date}
Days Since Last Contact: {days_since_contact}

Agent Instructions: {agent_instructions}

Generate a personalized, concise email (under 200 words) that:
1. References their property or interest specifically
2. Provides value or next steps
3. Encourages a response
4. Maintains a professional yet friendly tone
5. Is appropriate for the follow-up type and timing

Format your response as JSON:
{{
    "subject": "Your email subject here",
    "body": "Your email body here"
}}
"""

# Follow-up type specific templates
FOLLOWUP_TEMPLATES = {
    "Day 1": {
        "tone": "enthusiastic",
        "focus": "immediate interest and next steps",
        "call_to_action": "schedule a showing or call"
    },
    "Day 3": {
        "tone": "helpful",
        "focus": "additional information or market updates",
        "call_to_action": "answer questions or provide more details"
    },
    "Week 1": {
        "tone": "professional",
        "focus": "market updates or new listings",
        "call_to_action": "schedule a meeting or property tour"
    },
    "Week 2": {
        "tone": "nurturing",
        "focus": "market insights or property value updates",
        "call_to_action": "maintain relationship and interest"
    },
    "Month 1": {
        "tone": "checking in",
        "focus": "market trends or new opportunities",
        "call_to_action": "re-engage or update preferences"
    }
}

# Email signature template
EMAIL_SIGNATURE = """
Best regards,
{agent_name}
{agent_title}
{company_name}
Phone: {agent_phone}
Email: {agent_email}
"""

# Subject line templates
SUBJECT_TEMPLATES = {
    "Day 1": [
        "Quick follow-up on your {property_type} interest",
        "Next steps for {property_address}",
        "Let's schedule your property viewing"
    ],
    "Day 3": [
        "Additional info about {property_address}",
        "Market update for your area",
        "Questions about your property search?"
    ],
    "Week 1": [
        "Weekly market update for you",
        "New listings that might interest you",
        "How's your property search going?"
    ],
    "Week 2": [
        "Checking in on your property search",
        "Market insights for your area",
        "Any updates on your preferences?"
    ],
    "Month 1": [
        "Monthly market update",
        "Checking in on your real estate needs",
        "New opportunities in your area"
    ]
}
