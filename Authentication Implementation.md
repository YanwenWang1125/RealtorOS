# Google OAuth + Email/Password Authentication Implementation

## Overview
Implement multi-agent authentication system with Google OAuth (primary) and Email/Password (fallback) for RealtorOS. This allows multiple real estate agents to use the system with isolated data and personalized email signatures.

---

## PART 1: BACKEND IMPLEMENTATION

### Step 1.1: Install Required Dependencies

Add to `backend/requirements.txt`:
```txt
passlib[bcrypt]
python-jose[cryptography]
google-auth
google-auth-oauthlib
```

Run:
```bash
cd backend
pip install -r requirements.txt
```

---

### Step 1.2: Update Environment Variables

Add to `backend/.env`:
```env
# Google OAuth (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# JWT settings (already exist, but ensure they are set)
SECRET_KEY=your_secret_key_at_least_32_characters_long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

Update `backend/app/config.py` to include Google OAuth settings:
```python
# Add after SendGrid settings (around line 60)
# Google OAuth - Required for Google Sign-In
GOOGLE_CLIENT_ID: str = Field(description="Google OAuth Client ID")
GOOGLE_CLIENT_SECRET: str = Field(description="Google OAuth Client Secret")
```

---

### Step 1.3: Create Agent Model

Create new file: `backend/app/models/agent.py`

```python
"""
Agent model for realtor authentication and profiles.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    Index,
)
from app.db.postgresql import Base


def utcnow():
    """Return timezone-aware UTC datetime for column defaults."""
    return datetime.now(timezone.utc)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    google_sub = Column(String(255), nullable=True, unique=True, index=True)  # Google's user ID
    avatar_url = Column(String(500), nullable=True)
    auth_provider = Column(String(20), nullable=False, default='email')  # 'email' or 'google'

    # Profile information
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    title = Column(String(100), nullable=True)  # e.g., "Senior Real Estate Agent"
    company = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


# Composite indexes
Index("ix_agents_email_active", Agent.email, Agent.is_active)
Index("ix_agents_google_sub_active", Agent.google_sub, Agent.is_active)
```

Update `backend/app/models/__init__.py`:
```python
from app.models.agent import Agent  # noqa: F401
```

---

### Step 1.4: Update Existing Models to Add agent_id

**Update `backend/app/models/client.py`:**

Add after line 26:
```python
from sqlalchemy import ForeignKey

# Add this column after id
agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
```

Add composite index after line 43:
```python
Index("ix_clients_agent_stage", Client.agent_id, Client.stage)
```

**Update `backend/app/models/task.py`:**

Add similar agent_id column and import ForeignKey.

**Update `backend/app/models/email_log.py`:**

Add agent_id and additional fields:
```python
agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
from_name = Column(String(200), nullable=True)  # Store agent name at send time
from_email = Column(String(255), nullable=True)  # Store agent email at send time
```

---

### Step 1.5: Create Database Migration

```bash
cd backend
alembic revision --autogenerate -m "add_agent_model_and_foreign_keys"
```

**IMPORTANT**: Edit the generated migration file to add data migration for existing records:

```python
def upgrade():
    # Create agents table first
    op.create_table('agents', ...)

    # Create a default "System Agent" for existing data
    op.execute("""
        INSERT INTO agents (email, name, auth_provider, is_active, created_at, updated_at)
        VALUES ('system@realtoros.com', 'System Agent', 'email', true, NOW(), NOW())
    """)

    # Add agent_id columns (nullable first)
    op.add_column('clients', sa.Column('agent_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('agent_id', sa.Integer(), nullable=True))
    op.add_column('email_logs', sa.Column('agent_id', sa.Integer(), nullable=True))
    op.add_column('email_logs', sa.Column('from_name', sa.String(200), nullable=True))
    op.add_column('email_logs', sa.Column('from_email', sa.String(255), nullable=True))

    # Update existing records to use system agent
    op.execute("""
        UPDATE clients SET agent_id = (SELECT id FROM agents WHERE email = 'system@realtoros.com')
        WHERE agent_id IS NULL
    """)
    op.execute("""
        UPDATE tasks SET agent_id = (SELECT id FROM agents WHERE email = 'system@realtoros.com')
        WHERE agent_id IS NULL
    """)
    op.execute("""
        UPDATE email_logs SET agent_id = (SELECT id FROM agents WHERE email = 'system@realtoros.com')
        WHERE agent_id IS NULL
    """)

    # Make agent_id NOT NULL
    op.alter_column('clients', 'agent_id', nullable=False)
    op.alter_column('tasks', 'agent_id', nullable=False)
    op.alter_column('email_logs', 'agent_id', nullable=False)

    # Add foreign keys
    op.create_foreign_key('fk_clients_agent_id', 'clients', 'agents', ['agent_id'], ['id'])
    op.create_foreign_key('fk_tasks_agent_id', 'tasks', 'agents', ['agent_id'], ['id'])
    op.create_foreign_key('fk_email_logs_agent_id', 'email_logs', 'agents', ['agent_id'], ['id'])

    # Add indexes
    op.create_index('ix_clients_agent_id', 'clients', ['agent_id'])
    op.create_index('ix_tasks_agent_id', 'tasks', ['agent_id'])
    op.create_index('ix_email_logs_agent_id', 'email_logs', ['agent_id'])
```

Run migration:
```bash
alembic upgrade head
```

---

### Step 1.6: Create Agent Schemas

Create new file: `backend/app/schemas/agent_schema.py`

```python
"""
Agent Pydantic schemas for API validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class AgentCreate(BaseModel):
    """Schema for email/password registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=200)


class AgentLogin(BaseModel):
    """Schema for email/password login."""
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    """Schema for Google OAuth login."""
    credential: str  # Google ID token


class AgentUpdate(BaseModel):
    """Schema for updating agent profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None


class AgentResponse(BaseModel):
    """Schema for agent API responses."""
    id: int
    email: EmailStr
    name: str
    phone: Optional[str]
    title: Optional[str]
    company: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    auth_provider: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for authentication response."""
    access_token: str
    token_type: str = "bearer"
    agent: AgentResponse
```

---

### Step 1.7: Update Existing Schemas

**Update `backend/app/schemas/client_schema.py`:**

Add to `ClientResponse`:
```python
agent_id: int
```

**Update `backend/app/schemas/task_schema.py`:**

Add to `TaskResponse`:
```python
agent_id: int
```

**Update `backend/app/schemas/email_schema.py`:**

Add to `EmailResponse`:
```python
agent_id: int
from_name: Optional[str] = None
from_email: Optional[str] = None
```

---

### Step 1.8: Create Auth Utilities

Create new file: `backend/app/utils/auth.py`

```python
"""
Authentication utilities for password hashing and JWT tokens.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

---

### Step 1.9: Create Google OAuth Utility

Create new file: `backend/app/utils/google_oauth.py`

```python
"""
Google OAuth verification utilities.
"""

from google.auth.transport import requests
from google.oauth2 import id_token
from app.config import settings
from typing import Optional


def verify_google_token(token: str) -> Optional[dict]:
    """
    Verify Google ID token and return user info.

    Returns:
        dict with keys: sub (Google user ID), email, name, picture
        None if verification fails
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        # Verify the token was issued by Google
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return None

        return {
            'sub': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', idinfo['email'].split('@')[0]),
            'picture': idinfo.get('picture')
        }
    except ValueError:
        return None
```

---

### Step 1.10: Create Agent Service

Create new file: `backend/app/services/agent_service.py`

```python
"""
Agent service for authentication and profile management.
"""

from typing import Optional
from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.agent import Agent
from app.schemas.agent_schema import (
    AgentCreate, AgentUpdate, AgentResponse, TokenResponse
)
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.google_oauth import verify_google_token
from app.config import settings


class AgentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_email(self, agent_data: AgentCreate) -> TokenResponse:
        """Register a new agent with email/password."""
        # Check if email already exists
        stmt = select(Agent).where(Agent.email == agent_data.email)
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Create new agent
        agent = Agent(
            email=agent_data.email,
            password_hash=hash_password(agent_data.password),
            name=agent_data.name,
            phone=agent_data.phone,
            title=agent_data.title,
            company=agent_data.company,
            auth_provider='email'
        )
        self.session.add(agent)
        await self.session.commit()
        await self.session.refresh(agent)

        # Generate token
        access_token = create_access_token(
            data={"sub": str(agent.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        agent_response = AgentResponse.model_validate(agent)
        return TokenResponse(access_token=access_token, agent=agent_response)

    async def login_email(self, email: str, password: str) -> TokenResponse:
        """Login with email/password."""
        stmt = select(Agent).where(
            Agent.email == email,
            Agent.is_active == True,
            Agent.auth_provider == 'email'
        )
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent or not agent.password_hash or not verify_password(password, agent.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        access_token = create_access_token(
            data={"sub": str(agent.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        agent_response = AgentResponse.model_validate(agent)
        return TokenResponse(access_token=access_token, agent=agent_response)

    async def login_google(self, google_token: str) -> TokenResponse:
        """Login or register with Google OAuth."""
        # Verify Google token
        google_info = verify_google_token(google_token)
        if not google_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )

        # Try to find existing agent by google_sub or email
        stmt = select(Agent).where(
            (Agent.google_sub == google_info['sub']) | (Agent.email == google_info['email'])
        )
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()

        if agent:
            # Update Google info if needed
            if not agent.google_sub:
                agent.google_sub = google_info['sub']
                agent.auth_provider = 'google'
            if not agent.avatar_url and google_info.get('picture'):
                agent.avatar_url = google_info['picture']
            await self.session.commit()
            await self.session.refresh(agent)
        else:
            # Create new agent
            agent = Agent(
                email=google_info['email'],
                google_sub=google_info['sub'],
                name=google_info['name'],
                avatar_url=google_info.get('picture'),
                auth_provider='google',
                is_active=True
            )
            self.session.add(agent)
            await self.session.commit()
            await self.session.refresh(agent)

        # Generate token
        access_token = create_access_token(
            data={"sub": str(agent.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        agent_response = AgentResponse.model_validate(agent)
        return TokenResponse(access_token=access_token, agent=agent_response)

    async def get_profile(self, agent_id: int) -> Optional[AgentResponse]:
        """Get agent profile by ID."""
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            return None

        return AgentResponse.model_validate(agent)

    async def update_profile(self, agent_id: int, agent_data: AgentUpdate) -> Optional[AgentResponse]:
        """Update agent profile."""
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            return None

        # Update fields
        update_data = agent_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(agent, key, value)

        await self.session.commit()
        await self.session.refresh(agent)

        return AgentResponse.model_validate(agent)
```

---

### Step 1.11: Update Dependencies to Add Auth Middleware

Update `backend/app/api/dependencies.py`:

```python
# Add these imports at the top
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.agent import Agent
from app.utils.auth import decode_access_token

# Add after existing dependencies
security = HTTPBearer()

async def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> Agent:
    """Get the current authenticated agent from JWT token."""
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    agent_id = payload.get("sub")
    if agent_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from sqlalchemy import select
    stmt = select(Agent).where(Agent.id == int(agent_id), Agent.is_active == True)
    result = await session.execute(stmt)
    agent = result.scalar_one_or_none()

    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return agent

# Add service for agent
async def get_agent_service(session: AsyncSession = Depends(get_session)):
    """Get agent service instance."""
    from app.services.agent_service import AgentService
    return AgentService(session)
```

---

### Step 1.12: Create Agent Routes

Create new file: `backend/app/api/routes/agents.py`

```python
"""
Agent authentication and profile management API routes.
"""

from fastapi import APIRouter, Depends
from app.schemas.agent_schema import (
    AgentCreate, AgentUpdate, AgentResponse, AgentLogin,
    GoogleLoginRequest, TokenResponse
)
from app.services.agent_service import AgentService
from app.api.dependencies import get_agent_service, get_current_agent
from app.models.agent import Agent

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register_agent(
    agent_data: AgentCreate,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Register a new agent with email/password."""
    return await agent_service.register_email(agent_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: AgentLogin,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Login with email/password."""
    return await agent_service.login_email(credentials.email, credentials.password)


@router.post("/google", response_model=TokenResponse)
async def google_login(
    request: GoogleLoginRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Login or register with Google OAuth."""
    return await agent_service.login_google(request.credential)


@router.get("/me", response_model=AgentResponse)
async def get_my_profile(agent: Agent = Depends(get_current_agent)):
    """Get current authenticated agent's profile."""
    return AgentResponse.model_validate(agent)


@router.patch("/me", response_model=AgentResponse)
async def update_my_profile(
    agent_data: AgentUpdate,
    agent: Agent = Depends(get_current_agent),
    agent_service: AgentService = Depends(get_agent_service)
):
    """Update current agent's profile."""
    updated = await agent_service.update_profile(agent.id, agent_data)
    if not updated:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Agent not found")
    return updated
```

Update `backend/app/main.py` to include the router:

```python
# Add import
from app.api.routes import agents

# Add after other routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
```

---

### Step 1.13: Protect Existing Routes with Authentication

**Update `backend/app/api/routes/clients.py`:**

Add to all route functions:
```python
from app.api.dependencies import get_current_agent
from app.models.agent import Agent

# Example for create_client:
async def create_client(
    client_data: ClientCreate,
    agent: Agent = Depends(get_current_agent),  # Add this
    crm_service: CRMService = Depends(get_crm_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    # Auto-set agent_id
    client_data_dict = client_data.model_dump()
    client_data_dict['agent_id'] = agent.id
    # Pass to service...
```

**Update `backend/app/services/crm_service.py`:**

Modify methods to accept and use `agent_id`:

```python
async def create_client(self, client_data: ClientCreate, agent_id: int):
    # Create client with agent_id

async def get_clients(self, agent_id: int, page: int = 1, limit: int = 10, ...):
    # Filter by agent_id
    stmt = select(Client).where(Client.agent_id == agent_id, ...)
```

Apply similar changes to:
- `backend/app/api/routes/tasks.py`
- `backend/app/api/routes/emails.py`
- `backend/app/api/routes/dashboard.py`
- Corresponding services

---

### Step 1.14: Update Email Generation with Agent Info

**Update `backend/app/services/ai_agent.py`:**

Modify `generate_email` method:

```python
async def generate_email(
    self,
    client_id: int,
    task_id: int,
    agent: Agent,  # Add agent parameter
    agent_instructions: Optional[str] = None
) -> dict:
    # In _build_prompt, add agent info:
    prompt += f"""

=== AGENT INFORMATION ===
Agent Name: {agent.name}
Agent Title: {agent.title or 'Real Estate Agent'}
Agent Company: {agent.company or ''}
Agent Phone: {agent.phone or ''}
Agent Email: {agent.email}

IMPORTANT: Sign the email with the agent's name and details. Use a professional signature like:

Best regards,
{agent.name}
{agent.title or 'Real Estate Agent'}
{agent.company or ''}
Phone: {agent.phone or ''}
Email: {agent.email}

DO NOT use placeholders like [Your Name] or [Your Company]. Use the actual agent information provided above.
"""
```

**Update `backend/app/services/email_service.py`:**

```python
async def send_email(
    self,
    agent: Agent,  # Add agent parameter
    client_id: int,
    ...
):
    # Use agent's email as sender
    message.from_email = (agent.email, agent.name)

    # Log with agent info
    await self.log_email(
        client_id=client_id,
        agent_id=agent.id,
        from_name=agent.name,
        from_email=agent.email,
        ...
    )
```

---

## PART 2: FRONTEND IMPLEMENTATION

### Step 2.1: Install Google OAuth Library

```bash
cd frontend
npm install @react-oauth/google
```

---

### Step 2.2: Add Environment Variables

Create/update `frontend/.env.local`:

```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here
```

---

### Step 2.3: Create Agent Types

Create new file: `frontend/src/lib/types/agent.types.ts`

```typescript
export interface Agent {
  id: number;
  email: string;
  name: string;
  phone?: string;
  title?: string;
  company?: string;
  bio?: string;
  avatar_url?: string;
  auth_provider: 'email' | 'google';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentCreate {
  email: string;
  password: string;
  name: string;
  phone?: string;
  title?: string;
  company?: string;
}

export interface AgentLogin {
  email: string;
  password: string;
}

export interface GoogleLoginRequest {
  credential: string;
}

export interface AgentUpdate {
  name?: string;
  phone?: string;
  title?: string;
  company?: string;
  bio?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  agent: Agent;
}
```

---

### Step 2.4: Update Existing Types

**Update `frontend/src/lib/types/client.types.ts`:**
```typescript
export interface Client {
  // ... existing fields
  agent_id: number;
}
```

**Update `frontend/src/lib/types/task.types.ts`:**
```typescript
export interface Task {
  // ... existing fields
  agent_id: number;
}
```

**Update `frontend/src/lib/types/email.types.ts`:**
```typescript
export interface Email {
  // ... existing fields
  agent_id: number;
  from_name?: string;
  from_email?: string;
}
```

---

### Step 2.5: Update Auth Store

Update `frontend/src/store/useAuthStore.ts`:

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Agent, TokenResponse } from '@/lib/types/agent.types';

interface AuthState {
  token: string | null;
  agent: Agent | null;
  isAuthenticated: boolean;

  setAuth: (data: TokenResponse) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      agent: null,
      isAuthenticated: false,

      setAuth: (data: TokenResponse) => {
        set({
          token: data.access_token,
          agent: data.agent,
          isAuthenticated: true,
        });
      },

      logout: () => {
        set({
          token: null,
          agent: null,
          isAuthenticated: false,
        });
      },
    }),
    {
      name: 'realtor-auth-storage',
    }
  )
);
```

---

### Step 2.6: Update API Client with Auth

Update `frontend/src/lib/api/client.ts`:

Replace the comment section (lines 12-24) with:

```typescript
// Request interceptor for auth tokens
apiClient.interceptors.request.use(
  (config) => {
    // Get token from auth store
    const { token } = require('@/store/useAuthStore').useAuthStore.getState();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
```

Update response interceptor (around line 46):

```typescript
if (status === 401) {
  // Token expired or invalid - logout
  const { logout } = require('@/store/useAuthStore').useAuthStore.getState();
  logout();

  // Redirect to login
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}
```

---

### Step 2.7: Create Agent API Endpoints

Create new file: `frontend/src/lib/api/endpoints/agents.ts`

```typescript
import { apiClient } from '../client';
import {
  AgentCreate,
  AgentUpdate,
  AgentLogin,
  GoogleLoginRequest,
  TokenResponse,
  Agent,
} from '@/lib/types/agent.types';

export const agentsApi = {
  register: async (data: AgentCreate): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/agents/register', data);
    return response.data;
  },

  loginEmail: async (credentials: AgentLogin): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/agents/login', credentials);
    return response.data;
  },

  loginGoogle: async (googleToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/agents/google', {
      credential: googleToken,
    });
    return response.data;
  },

  getProfile: async (): Promise<Agent> => {
    const response = await apiClient.get<Agent>('/api/agents/me');
    return response.data;
  },

  updateProfile: async (data: AgentUpdate): Promise<Agent> => {
    const response = await apiClient.patch<Agent>('/api/agents/me', data);
    return response.data;
  },
};
```

---

### Step 2.8: Create Auth Hooks

Create new file: `frontend/src/lib/hooks/mutations/useAuth.ts`

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { agentsApi } from '@/lib/api/endpoints/agents';
import { useAuthStore } from '@/store/useAuthStore';
import { useRouter } from 'next/navigation';
import { useToast } from '@/lib/hooks/ui/useToast';
import { AgentCreate, AgentLogin, AgentUpdate } from '@/lib/types/agent.types';

export const useRegister = () => {
  const setAuth = useAuthStore((state) => state.setAuth);
  const router = useRouter();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: AgentCreate) => agentsApi.register(data),
    onSuccess: (data) => {
      setAuth(data);
      toast({
        title: 'Registration successful',
        description: 'Welcome to RealtorOS!',
      });
      router.push('/');
    },
    onError: (error: any) => {
      toast({
        title: 'Registration failed',
        description: error.response?.data?.detail || 'Something went wrong',
        variant: 'destructive',
      });
    },
  });
};

export const useLoginEmail = () => {
  const setAuth = useAuthStore((state) => state.setAuth);
  const router = useRouter();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (credentials: AgentLogin) => agentsApi.loginEmail(credentials),
    onSuccess: (data) => {
      setAuth(data);
      toast({
        title: 'Login successful',
        description: `Welcome back, ${data.agent.name}!`,
      });
      router.push('/');
    },
    onError: (error: any) => {
      toast({
        title: 'Login failed',
        description: error.response?.data?.detail || 'Invalid credentials',
        variant: 'destructive',
      });
    },
  });
};

export const useLoginGoogle = () => {
  const setAuth = useAuthStore((state) => state.setAuth);
  const router = useRouter();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (googleToken: string) => agentsApi.loginGoogle(googleToken),
    onSuccess: (data) => {
      setAuth(data);
      toast({
        title: 'Login successful',
        description: `Welcome, ${data.agent.name}!`,
      });
      router.push('/');
    },
    onError: (error: any) => {
      toast({
        title: 'Login failed',
        description: error.response?.data?.detail || 'Google authentication failed',
        variant: 'destructive',
      });
    },
  });
};

export const useUpdateProfile = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: AgentUpdate) => agentsApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent', 'me'] });
      toast({
        title: 'Profile updated',
        description: 'Your profile has been updated successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Update failed',
        description: error.response?.data?.detail || 'Something went wrong',
        variant: 'destructive',
      });
    },
  });
};
```

---

### Step 2.9: Wrap App with Google OAuth Provider

Update `frontend/src/app/layout.tsx`:

```typescript
import { GoogleOAuthProvider } from '@react-oauth/google';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || '';

  return (
    <html lang="en">
      <body>
        <GoogleOAuthProvider clientId={googleClientId}>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </GoogleOAuthProvider>
      </body>
    </html>
  );
}
```

---

### Step 2.10: Create Login Page

Create new file: `frontend/src/app/(auth)/login/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useLoginEmail, useLoginGoogle } from '@/lib/hooks/mutations/useAuth';
import { GoogleLogin } from '@react-oauth/google';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { mutate: loginEmail, isPending: isEmailPending } = useLoginEmail();
  const { mutate: loginGoogle } = useLoginGoogle();

  const handleEmailLogin = (e: React.FormEvent) => {
    e.preventDefault();
    loginEmail({ email, password });
  };

  const handleGoogleSuccess = (credentialResponse: any) => {
    if (credentialResponse.credential) {
      loginGoogle(credentialResponse.credential);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">Login to RealtorOS</CardTitle>
          <CardDescription>Sign in with Google or your email</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Google Sign-In */}
          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => {
                console.error('Google Login Failed');
              }}
              useOneTap
            />
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-muted-foreground">Or continue with</span>
            </div>
          </div>

          {/* Email/Password Form */}
          <form onSubmit={handleEmailLogin} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={isEmailPending}>
              {isEmailPending ? 'Logging in...' : 'Login with Email'}
            </Button>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            Don't have an account?{' '}
            <Link href="/register" className="text-primary hover:underline font-medium">
              Register
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

### Step 2.11: Create Register Page

Create new file: `frontend/src/app/(auth)/register/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useRegister, useLoginGoogle } from '@/lib/hooks/mutations/useAuth';
import { GoogleLogin } from '@react-oauth/google';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import Link from 'next/link';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    phone: '',
    title: '',
    company: '',
  });

  const { mutate: register, isPending } = useRegister();
  const { mutate: loginGoogle } = useLoginGoogle();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    register(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleGoogleSuccess = (credentialResponse: any) => {
    if (credentialResponse.credential) {
      loginGoogle(credentialResponse.credential);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">Register for RealtorOS</CardTitle>
          <CardDescription>Create your account with Google or email</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Google Sign-Up */}
          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => {
                console.error('Google Sign-Up Failed');
              }}
              text="signup_with"
            />
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-muted-foreground">Or register with email</span>
            </div>
          </div>

          {/* Registration Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="name" className="text-sm font-medium">
                Full Name <span className="text-red-500">*</span>
              </label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="John Doe"
                required
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email <span className="text-red-500">*</span>
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
                required
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Password <span className="text-red-500">*</span>
              </label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Min 8 characters"
                minLength={8}
                required
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="phone" className="text-sm font-medium">
                Phone
              </label>
              <Input
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="title" className="text-sm font-medium">
                Title
              </label>
              <Input
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Senior Real Estate Agent"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="company" className="text-sm font-medium">
                Company
              </label>
              <Input
                id="company"
                name="company"
                value={formData.company}
                onChange={handleChange}
                placeholder="Your Realty Company"
              />
            </div>

            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending ? 'Creating account...' : 'Register'}
            </Button>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link href="/login" className="text-primary hover:underline font-medium">
              Login
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

### Step 2.12: Create Auth Guard Component

Create new file: `frontend/src/components/auth/AuthGuard.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    } else {
      setIsLoading(false);
    }
  }, [isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return <>{children}</>;
}
```

---

### Step 2.13: Protect Dashboard Routes

Update `frontend/src/app/(dashboard)/layout.tsx`:

```typescript
import { AuthGuard } from '@/components/auth/AuthGuard';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      {/* Your existing layout code */}
      {children}
    </AuthGuard>
  );
}
```

---

### Step 2.14: Create Profile Page

Create new file: `frontend/src/app/(dashboard)/profile/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useAuthStore } from '@/store/useAuthStore';
import { useUpdateProfile } from '@/lib/hooks/mutations/useAuth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import Image from 'next/image';

export default function ProfilePage() {
  const agent = useAuthStore((state) => state.agent);
  const { mutate: updateProfile, isPending } = useUpdateProfile();

  const [formData, setFormData] = useState({
    name: agent?.name || '',
    phone: agent?.phone || '',
    title: agent?.title || '',
    company: agent?.company || '',
    bio: agent?.bio || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile(formData);
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">My Profile</h1>

      <Card>
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-6 mb-6">
            {agent?.avatar_url && (
              <Image
                src={agent.avatar_url}
                alt={agent.name}
                width={80}
                height={80}
                className="rounded-full"
              />
            )}
            <div>
              <p className="text-sm text-muted-foreground">Signed in with {agent?.auth_provider}</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="name" className="text-sm font-medium">
                Full Name
              </label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email (cannot be changed)
              </label>
              <Input id="email" value={agent?.email || ''} disabled className="bg-gray-100" />
            </div>

            <div className="space-y-2">
              <label htmlFor="phone" className="text-sm font-medium">
                Phone
              </label>
              <Input
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="title" className="text-sm font-medium">
                Title
              </label>
              <Input
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Senior Real Estate Agent"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="company" className="text-sm font-medium">
                Company
              </label>
              <Input
                id="company"
                name="company"
                value={formData.company}
                onChange={handleChange}
                placeholder="Your Realty Company"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="bio" className="text-sm font-medium">
                Bio
              </label>
              <Textarea
                id="bio"
                name="bio"
                value={formData.bio}
                onChange={handleChange}
                rows={4}
                placeholder="Tell clients about yourself..."
              />
            </div>

            <Button type="submit" disabled={isPending}>
              {isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

### Step 2.15: Add Logout to Sidebar

Update your sidebar component to add logout button:

```typescript
import { useAuthStore } from '@/store/useAuthStore';
import { useRouter } from 'next/navigation';
import { LogOut, User } from 'lucide-react';

// In your sidebar component:
const router = useRouter();
const { agent, logout } = useAuthStore();

const handleLogout = () => {
  logout();
  router.push('/login');
};

// Add profile link and logout button:
<div className="flex flex-col gap-2">
  <Link href="/profile" className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded">
    <User className="h-5 w-5" />
    Profile
  </Link>

  <button
    onClick={handleLogout}
    className="flex items-center gap-2 p-2 hover:bg-red-50 text-red-600 rounded"
  >
    <LogOut className="h-5 w-5" />
    Logout
  </button>
</div>
```

---

## TESTING

### Backend Testing:

1. **Start backend server:**
```bash
cd backend
uvicorn app.main:app --reload
```

2. **Test endpoints with curl or Postman:**

```bash
# Register with email
curl -X POST http://localhost:8000/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test1234","name":"Test Agent"}'

# Login
curl -X POST http://localhost:8000/api/agents/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test1234"}'

# Get profile (use token from login)
curl -X GET http://localhost:8000/api/agents/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

3. **Test client creation with auth:**
```bash
curl -X POST http://localhost:8000/api/clients \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Client","email":"client@test.com",...}'
```

### Frontend Testing:

1. **Start frontend dev server:**
```bash
cd frontend
npm run dev
```

2. **Test flows:**
- Navigate to http://localhost:3000/login
- Try Google Sign-In (ensure Google OAuth is configured)
- Try email/password registration
- Check that you're redirected to dashboard
- Try accessing protected routes
- Update profile
- Send email from task (check signature has real agent info!)
- Logout and verify redirect to login

---

## Google OAuth Setup Guide

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure OAuth consent screen
6. Add authorized redirect URIs:
   - `http://localhost:3000` (development)
   - `https://yourdomain.com` (production)
7. Copy Client ID and Client Secret to `.env` files

---

## Summary

This implementation provides:

✅ **Dual Authentication**: Google OAuth (primary) + Email/Password (fallback)
✅ **Multi-Agent Support**: Each agent has isolated data
✅ **JWT Security**: Stateless, scalable authentication
✅ **Email Personalization**: Agent info in email signatures (fixes placeholder issue!)
✅ **Profile Management**: Full CRUD for agent profiles
✅ **Route Protection**: All dashboard routes require authentication
✅ **Data Isolation**: Agents only see their own clients/tasks/emails

**Estimated Implementation Time**: 10-15 hours

**Next Steps After Implementation**:
1. Configure Google OAuth credentials
2. Run migrations
3. Test auth flows
4. Send test email to verify signature
5. Deploy to production
