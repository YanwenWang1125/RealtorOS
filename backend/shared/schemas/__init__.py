"""
Shared Pydantic schemas for all microservices.
"""

from .agent_schema import (
    AgentCreate,
    AgentLogin,
    GoogleLoginRequest,
    AgentUpdate,
    AgentResponse,
    TokenResponse,
)
from .client_schema import (
    ClientBase,
    ClientCreate,
    ClientUpdate,
    ClientResponse,
)
from .task_schema import (
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)
from .email_schema import (
    EmailPreviewRequest,
    EmailSendRequest,
    EmailResponse,
)
from .dashboard_schema import (
    DashboardStats,
    ActivityItem,
)
from .webhook_schema import (
    SendGridWebhookEvent,
)

__all__ = [
    # Agent schemas
    "AgentCreate",
    "AgentLogin",
    "GoogleLoginRequest",
    "AgentUpdate",
    "AgentResponse",
    "TokenResponse",
    # Client schemas
    "ClientBase",
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    # Task schemas
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    # Email schemas
    "EmailPreviewRequest",
    "EmailSendRequest",
    "EmailResponse",
    # Dashboard schemas
    "DashboardStats",
    "ActivityItem",
    # Webhook schemas
    "SendGridWebhookEvent",
]

