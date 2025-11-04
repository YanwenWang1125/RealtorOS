# RealtorOS - Next Steps & Implementation Guide

## 📋 Table of Contents

- [Current Status](#-current-status)
- [Issues Fixed](#-issues-fixed-in-this-session)
- [Next Implementation: Agent Model](#-next-implementation-agent-model---full-multi-agent-support)
- [Next Steps Required](#-next-steps-required)
- [Testing Checklists](#-testing-checklist)
- [Troubleshooting](#-troubleshooting)
- [Documentation](#-additional-documentation)

---

## ✅ Current Status

**All code issues have been fixed!** The system is fully functional except for webhook configuration which requires a public URL.

**Remaining Blocker:** SendGrid webhooks require a publicly accessible URL. Use ngrok for local development or deploy to production.

---

## 🔧 Issues Fixed in This Session

This document summarizes all the issues encountered and resolved during the current development session.

### 1. **"Send Email" Button Not Working**
**Problem:** Clicking "Send Email" in the task actions menu did nothing.

**Solution:** 
- Integrated `EmailPreviewModal` component into `TaskActionsMenu`
- Added client data fetching when email modal opens
- Connected the menu item click handler to open the email preview modal

**Files Changed:**
- `frontend/src/components/tasks/TaskActionsMenu.tsx`

**Status:** ✅ Fixed

---

### 2. **TipTap Editor SSR Error**
**Problem:** Runtime error: "SSR has been detected, please set `immediatelyRender` explicitly to `false`"

**Solution:** 
- Added `immediatelyRender: false` to `useEditor` configuration in `EmailComposer`

**Files Changed:**
- `frontend/src/components/emails/EmailComposer.tsx`

**Status:** ✅ Fixed

---

### 3. **Missing TipTap Dependencies**
**Problem:** Module not found errors for `@tiptap/react` and `@tiptap/starter-kit`

**Solution:** 
- Installed required packages: `@tiptap/react` and `@tiptap/starter-kit`

**Commands Run:**
```bash
cd frontend
npm install @tiptap/react @tiptap/starter-kit
```

**Status:** ✅ Fixed

---

### 4. **Import Path Errors in Tasks Detail Page**
**Problem:** Module not found errors for EmailPreview, TaskForm, Modal, and hook imports

**Solution:** 
- Updated all import paths to use correct locations:
  - `@/components/EmailPreview` → `@/components/emails/EmailPreview`
  - `@/components/TaskForm` → `@/components/tasks/TaskForm`
  - `@/components/Modal` → `@/components/ui/Modal`
  - `@/hooks/*` → `@/lib/hooks/queries/*`
- Updated hook usage to match React Query API (`data`, `isLoading`, `isError`)

**Files Changed:**
- `frontend/src/app/(dashboard)/tasks/[id]/page.tsx`

**Status:** ✅ Fixed

---

### 5. **Tasks Not Generated Automatically When Creating Clients**
**Problem:** When creating a new client, no follow-up tasks were being created automatically.

**Solution:** 
- Changed task creation from asynchronous Celery task to synchronous execution
- Now tasks are created immediately when a client is created, without requiring Celery workers

**Files Changed:**
- `backend/app/api/routes/clients.py`

**Before:**
```python
create_followup_tasks_task.delay(created.id)  # Requires Celery
```

**After:**
```python
tasks = await scheduler_service.create_followup_tasks(created.id)  # Synchronous
```

**Status:** ✅ Fixed

---

### 6. **Tasks Not Marked as Completed When Email Sent**
**Problem:** After sending an email from a task, the task status remained "pending" instead of "completed".

**Solution:** 
- Updated `/api/emails/send` endpoint to automatically mark task as completed after successful email send
- Sets `status="completed"`, `email_sent_id`, and `completed_at` timestamp

**Files Changed:**
- `backend/app/api/routes/emails.py`

**Status:** ✅ Fixed

---

### 7. **Engagement Timeline Showing No Data**
**Problem:** Engagement Timeline component displayed empty placeholders (no sent_at, opened_at, clicked_at timestamps).

**Solution:** 
- Fixed `update_email_status` method to set timestamps based on status:
  - `sent` → sets `sent_at`
  - `opened` → sets `opened_at`
  - `clicked` → sets `clicked_at`
- Added refresh to email_log after status update to return latest data

**Files Changed:**
- `backend/app/services/email_service.py`

**Status:** ✅ Fixed

---

### 8. **SendGrid Webhooks Not Being Received**
**Problem:** SendGrid webhook events (open, click, delivered) not being received, so `opened_at` and `clicked_at` remain NULL in database.

**Root Cause:** 
- SendGrid cannot reach `localhost:8000` - webhooks require a publicly accessible URL

**Solutions Implemented:**
- Made webhook signature verification optional in development mode
- Made `SENDGRID_WEBHOOK_VERIFICATION_KEY` optional (not required)
- Added test endpoint: `/webhook/sendgrid/test`
- Created setup guide: `WEBHOOK_SETUP.md`

**Files Changed:**
- `backend/app/api/routes/emails.py`
- `backend/app/config.py`
- `WEBHOOK_SETUP.md` (new file)

**Status:** ⚠️ **Requires Action** (see Next Steps)

---

## 🚀 Next Implementation: Agent Model - Full Multi-Agent Support

This section outlines the complete implementation plan for adding multi-agent support to RealtorOS, enabling multiple real estate agents to use the system with full data isolation.

### Phase 1: Backend - Database & Models (2-3 hours)

**Objectives:**
- Create Agent model with authentication fields
- Add agent relationships to existing models
- Extend EmailLog for agent-specific sender information

**Tasks:**
1. Create Agent model with fields:
   - `email` (unique, indexed)
   - `password_hash` (for authentication)
   - `name`, `phone`, `title`, `company`, `bio`
   - Standard timestamps (`created_at`, `updated_at`)

2. Add `agent_id` foreign key to:
   - `Client` model
   - `Task` model
   - `EmailLog` model

3. Add to `EmailLog` model:
   - `from_name` (agent's name as sender)
   - `from_email` (agent's email as sender)

4. Create Alembic migration:
   ```bash
   alembic revision --autogenerate -m "add_agent_model_and_relationships"
   alembic upgrade head
   ```

5. Add auth dependencies to `requirements.txt`:
   - `passlib[bcrypt]` - password hashing
   - `python-jose[cryptography]` - JWT token generation

**Files to Create/Modify:**
- `backend/app/models/agent.py` (new)
- `backend/app/models/client.py` (modify)
- `backend/app/models/task.py` (modify)
- `backend/app/models/email_log.py` (modify)
- `backend/requirements.txt` (add dependencies)

---

### Phase 2: Backend - Authentication System (2-3 hours)

**Objectives:**
- Implement secure password hashing
- Create JWT token generation and validation
- Build agent registration and login endpoints

**Tasks:**
1. Create auth utilities (`backend/app/utils/auth.py`):
   - `hash_password(password: str) -> str` - using bcrypt
   - `verify_password(plain: str, hashed: str) -> bool`
   - `create_access_token(data: dict, expires_delta: timedelta) -> str`
   - `decode_access_token(token: str) -> dict`

2. Create agent schemas (`backend/app/schemas/agent_schema.py`):
   - `AgentCreate` - registration schema
   - `AgentLogin` - login schema
   - `AgentUpdate` - profile update schema
   - `AgentResponse` - response schema (excludes password_hash)
   - `TokenResponse` - JWT token response

3. Create `AgentService` (`backend/app/services/agent_service.py`):
   - `register(agent_data: AgentCreate) -> Agent`
   - `login(email: str, password: str) -> Agent`
   - `get_by_id(agent_id: int) -> Agent`
   - `update_profile(agent_id: int, update_data: AgentUpdate) -> Agent`

4. Create agent API routes (`backend/app/api/routes/agents.py`):
   - `POST /api/agents/register` - create new agent account
   - `POST /api/agents/login` - authenticate and get JWT token
   - `GET /api/agents/me` - get current agent profile
   - `PUT /api/agents/me` - update current agent profile

5. Create auth dependency (`backend/app/api/dependencies.py`):
   - `get_current_agent(token: str = Depends(...)) -> Agent`
   - Validates JWT token and returns current agent
   - Raises `HTTPException(401)` if invalid

6. Update `config.py` with JWT settings:
   ```python
   SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
   ALGORITHM = "HS256"
   TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
   ```

**Files to Create/Modify:**
- `backend/app/utils/auth.py` (new)
- `backend/app/schemas/agent_schema.py` (new)
- `backend/app/services/agent_service.py` (new)
- `backend/app/api/routes/agents.py` (new)
- `backend/app/api/dependencies.py` (modify)
- `backend/app/config.py` (modify)
- `backend/app/main.py` (add agent routes)

---

### Phase 3: Backend - Protect Existing Routes (1-2 hours)

**Objectives:**
- Add authentication to all existing routes
- Ensure data isolation between agents
- Auto-assign agent_id on record creation

**Tasks:**
1. Update all route handlers to require authentication:
   - Add `agent: Agent = Depends(get_current_agent)` to all endpoints
   - Clients routes: `/api/clients/*`
   - Tasks routes: `/api/tasks/*`
   - Emails routes: `/api/emails/*`
   - Dashboard routes: `/api/dashboard/*`

2. Filter all database queries by `agent_id`:
   - Client queries: `.filter(Client.agent_id == agent.id)`
   - Task queries: `.filter(Task.agent_id == agent.id)`
   - EmailLog queries: `.filter(EmailLog.agent_id == agent.id)`

3. Auto-set `agent_id` when creating records:
   - `ClientService.create()` → set `agent_id=agent.id`
   - `TaskService.create()` → set `agent_id=agent.id`
   - `EmailService.send_email()` → set `agent_id=agent.id`

**Files to Modify:**
- `backend/app/api/routes/clients.py`
- `backend/app/api/routes/tasks.py`
- `backend/app/api/routes/emails.py`
- `backend/app/api/routes/dashboard.py`
- `backend/app/services/crm_service.py`
- `backend/app/services/email_service.py`

---

### Phase 4: Backend - Email Integration (1 hour)

**Objectives:**
- Include agent information in AI-generated emails
- Use agent's email as sender
- Store agent details in email logs

**Tasks:**
1. Update `AIAgent.generate_email()`:
   - Accept `agent: Agent` parameter
   - Include agent details in prompt:
     - Agent name, title, company, phone, email
     - Agent bio (if available)
   - Add agent signature to generated email body

2. Update `EmailService.send_email()`:
   - Use `agent.email` as sender email
   - Use `agent.name` as sender name (or `agent.title + " " + agent.name`)
   - Store `agent_id`, `from_name`, `from_email` in `EmailLog`

3. Update email templates to support agent signatures

**Files to Modify:**
- `backend/app/services/ai_agent.py`
- `backend/app/services/email_service.py`
- `backend/app/constants/email_templates.py`

---

### Phase 5: Frontend - Types & Auth Store (1 hour)

**Objectives:**
- Create TypeScript types for agent data
- Implement token storage with persistence
- Add authentication headers to API requests

**Tasks:**
1. Create `frontend/src/lib/types/agent.types.ts`:
   ```typescript
   interface Agent {
     id: number;
     email: string;
     name: string;
     phone?: string;
     title?: string;
     company?: string;
     bio?: string;
     created_at: string;
     updated_at: string;
   }
   
   interface AgentCreate {
     email: string;
     password: string;
     name: string;
     phone?: string;
     title?: string;
     company?: string;
     bio?: string;
   }
   
   interface AgentUpdate {
     name?: string;
     phone?: string;
     title?: string;
     company?: string;
     bio?: string;
   }
   
   interface TokenResponse {
     access_token: string;
     token_type: string;
   }
   ```

2. Update existing types to include `agent_id`:
   - `Client` interface
   - `Task` interface
   - `Email` interface

3. Update `useAuthStore` (`frontend/src/store/useAuthStore.ts`):
   - Add `token: string | null`
   - Add `agent: Agent | null`
   - Add persistence (localStorage)
   - Add `setAuth(token: string, agent: Agent)`
   - Add `logout()`
   - Add `isAuthenticated` computed

4. Update API client (`frontend/src/lib/api/client.ts`):
   - Add JWT token to request headers: `Authorization: Bearer ${token}`
   - Add 401 interceptor to:
     - Clear auth store on 401
     - Redirect to `/login`

**Files to Create/Modify:**
- `frontend/src/lib/types/agent.types.ts` (new)
- `frontend/src/lib/types/index.ts` (modify - export agent types)
- `frontend/src/lib/types/*` (modify - add agent_id to existing types)
- `frontend/src/store/useAuthStore.ts` (modify)
- `frontend/src/lib/api/client.ts` (modify)

---

### Phase 6: Frontend - Agent API & Hooks (1 hour)

**Objectives:**
- Create API endpoints for agent operations
- Build React Query hooks for authentication

**Tasks:**
1. Create `frontend/src/lib/api/endpoints/agents.ts`:
   ```typescript
   export const agentsApi = {
     register: (data: AgentCreate) => 
       api.post<TokenResponse>('/agents/register', data),
     login: (email: string, password: string) => 
       api.post<TokenResponse>('/agents/login', { email, password }),
     getProfile: () => 
       api.get<Agent>('/agents/me'),
     updateProfile: (data: AgentUpdate) => 
       api.put<Agent>('/agents/me', data),
   };
   ```

2. Create auth hooks (`frontend/src/lib/hooks/mutations/auth.ts`):
   - `useRegister()` - mutation hook for registration
   - `useLogin()` - mutation hook for login
   - `useUpdateProfile()` - mutation hook for profile update
   - `useGetProfile()` - query hook for fetching profile

3. Integrate with auth store:
   - On successful login/register, store token and agent data
   - Redirect to dashboard after successful auth

**Files to Create/Modify:**
- `frontend/src/lib/api/endpoints/agents.ts` (new)
- `frontend/src/lib/hooks/mutations/auth.ts` (new)
- `frontend/src/lib/hooks/queries/auth.ts` (new)

---

### Phase 7: Frontend - Auth Pages (2 hours)

**Objectives:**
- Create login and registration pages
- Build profile management interface
- Add logout functionality

**Tasks:**
1. Create login page (`frontend/src/app/(auth)/login/page.tsx`):
   - Email/password form
   - Error handling and validation
   - Redirect to dashboard on success
   - Link to register page

2. Create register page (`frontend/src/app/(auth)/register/page.tsx`):
   - Full profile form:
     - Email, password, confirm password
     - Name (required)
     - Phone, title, company (optional)
     - Bio (optional, textarea)
   - Validation for all fields
   - Redirect to dashboard on success

3. Create profile page (`frontend/src/app/(dashboard)/profile/page.tsx`):
   - Display current agent profile
   - Edit form for updating profile
   - Change password section (optional)

4. Add logout button to sidebar:
   - Update `Sidebar.tsx` to show logout option
   - Clear auth store and redirect to login

**Files to Create/Modify:**
- `frontend/src/app/(auth)/login/page.tsx` (modify/enhance)
- `frontend/src/app/(auth)/register/page.tsx` (create or modify)
- `frontend/src/app/(dashboard)/profile/page.tsx` (new)
- `frontend/src/components/layout/Sidebar.tsx` (modify)

---

### Phase 8: Frontend - Route Protection (1 hour)

**Objectives:**
- Protect dashboard routes from unauthenticated access
- Redirect to login when token is missing or invalid

**Tasks:**
1. Create `AuthGuard` component (`frontend/src/components/auth/AuthGuard.tsx`):
   ```typescript
   export function AuthGuard({ children }: { children: React.ReactNode }) {
     const { isAuthenticated, token } = useAuthStore();
     const router = useRouter();
     
     useEffect(() => {
       if (!isAuthenticated || !token) {
         router.push('/login');
       }
     }, [isAuthenticated, token, router]);
     
     if (!isAuthenticated) return <LoadingSpinner />;
     return <>{children}</>;
   }
   ```

2. Wrap dashboard layout with AuthGuard:
   - Update `frontend/src/app/(dashboard)/layout.tsx`
   - Wrap children with `<AuthGuard>`

3. Add loading state during authentication check

**Files to Create/Modify:**
- `frontend/src/components/auth/AuthGuard.tsx` (new)
- `frontend/src/app/(dashboard)/layout.tsx` (modify)

---

### Phase 9: Testing & Seed Data (1 hour)

**Objectives:**
- Create demo agent for testing
- Verify complete authentication flow
- Test data isolation between agents

**Tasks:**
1. Update seed script (`backend/app/db/seed.py`):
   - Create demo agent with known credentials:
     - Email: `demo@realtoros.com`
     - Password: `demo123`
     - Full profile: name, title, company, etc.
   - Create sample clients/tasks/emails for demo agent

2. Test complete flow:
   - Register new agent → verify JWT token received
   - Login with credentials → verify token stored
   - Create client → verify `agent_id` is set
   - Send email → verify agent signature in email
   - Verify `from_name` and `from_email` in EmailLog
   - Logout → verify redirect to login
   - Login as different agent → verify data isolation

3. Test data isolation:
   - Create agent A, create clients
   - Create agent B, verify cannot see agent A's clients
   - Create clients for agent B, verify agent A cannot see them

**Files to Modify:**
- `backend/app/db/seed.py`

---

## 🚀 Next Steps Required

### Priority 1: Set Up SendGrid Webhooks (Critical)

**To receive email engagement data (opens, clicks), you MUST expose your backend to the internet.**

#### Option A: Using ngrok (Recommended for Development)

1. **Install ngrok:**
   ```bash
   # Windows (with Chocolatey)
   choco install ngrok
   
   # Or download from: https://ngrok.com/download
   ```

2. **Start your backend:**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **In a new terminal, start ngrok:**
   ```bash
   ngrok http 8000
   ```

4. **Copy the public URL** (e.g., `https://abc123.ngrok.io`)

5. **Configure SendGrid:**
   - Go to: SendGrid Dashboard → Settings → Mail Settings → Event Webhook
   - Set HTTP POST URL: `https://your-ngrok-url.ngrok.io/webhook/sendgrid`
   - Enable events: **Delivered**, **Opened**, **Clicked**, **Bounced**, **Dropped**
   - Copy the verification key and add to `.env`:
     ```env
     SENDGRID_WEBHOOK_VERIFICATION_KEY=-----BEGIN PUBLIC KEY-----
     ... (paste key here)
     -----END PUBLIC KEY-----
     ```

6. **Test the webhook:**
   ```bash
   curl https://your-ngrok-url.ngrok.io/webhook/sendgrid/test
   ```

**Note:** Free ngrok URLs change on restart. For stable URLs, consider:
- Paid ngrok account (static domain)
- Deploy to production (Heroku, AWS, DigitalOcean, etc.)

#### Option B: Deploy to Production

Deploy your backend to a cloud service and set the webhook URL to your production domain:
```
https://your-production-domain.com/webhook/sendgrid
```

---

### Priority 2: Verify Everything Works

After setting up webhooks, test the complete flow:

1. **Create a new client** → Verify 5 tasks are automatically created
2. **Send an email from a task** → Verify:
   - Email is sent successfully
   - Task is marked as "completed"
   - `sent_at` timestamp is set in database
3. **Open the email** → Verify:
   - Webhook is received (check backend logs)
   - `opened_at` timestamp is updated in database
   - Engagement Timeline shows "Opened" timestamp
4. **Click a link in the email** → Verify:
   - Webhook is received
   - `clicked_at` timestamp is updated
   - Engagement Timeline shows "Clicked" timestamp

---

### Priority 3: Environment Configuration

Ensure your `.env` file has all required variables:

```env
# Backend .env file
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/realtoros
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# JWT Authentication (add for agent implementation)
SECRET_KEY=your-secret-key-change-in-production
TOKEN_EXPIRE_MINUTES=1440

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# SendGrid
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=agent@yourdomain.com
SENDGRID_FROM_NAME=Your Real Estate Team
SENDGRID_WEBHOOK_VERIFICATION_KEY=  # Optional in dev, required in production

# Logging
LOG_LEVEL=INFO
```

---

## 📝 Testing Checklist

### Current Features
- [ ] Create a new client → Tasks automatically created
- [ ] Click "Send Email" from task menu → Email preview modal opens
- [ ] Send an email → Task marked as completed
- [ ] Check database → `sent_at` timestamp populated
- [ ] Set up ngrok/public URL
- [ ] Configure SendGrid webhook
- [ ] Open sent email → `opened_at` timestamp populated
- [ ] Click link in email → `clicked_at` timestamp populated
- [ ] Engagement Timeline shows all timestamps

### Agent Model Implementation (Phase 9)
- [ ] Register new agent → JWT token received
- [ ] Login with credentials → Token stored in auth store
- [ ] Create client → `agent_id` automatically set
- [ ] Send email → Agent signature appears in email
- [ ] EmailLog → `from_name` and `from_email` populated
- [ ] Logout → Redirects to login page
- [ ] Login as different agent → Cannot see other agent's data
- [ ] Data isolation verified between agents

---

## 🔍 Troubleshooting

### Webhooks Still Not Working?

1. **Check if webhook endpoint is accessible:**
   ```bash
   curl https://your-public-url/webhook/sendgrid/test
   ```
   Should return: `{"status": "ok", ...}`

2. **Check backend logs** for webhook events:
   - Look for: "Successfully processed webhook event"
   - Or errors: "Webhook signature verification failed"

3. **Check SendGrid Activity Feed:**
   - Go to SendGrid Dashboard → Activity
   - Look for webhook delivery status
   - Check for any error messages

4. **Verify environment variables:**
   - `ENVIRONMENT=development` allows bypassing signature verification
   - `SENDGRID_WEBHOOK_VERIFICATION_KEY` should be set if using signature verification

### Tasks Not Created Automatically?

- Check backend logs for errors when creating clients
- Verify database connection is working
- Check that `SchedulerService.create_followup_tasks` is being called

### Engagement Timeline Still Empty?

- Verify `sent_at` is being set when email is sent (check database)
- Check that webhook events are being received
- Verify `process_webhook_event` is updating `opened_at` and `clicked_at`

### Authentication Issues?

- Verify `SECRET_KEY` is set in environment variables
- Check JWT token expiration time
- Verify token is being sent in request headers
- Check backend logs for authentication errors

---

## 📚 Additional Documentation

- **Webhook Setup:** See `WEBHOOK_SETUP.md` for detailed webhook configuration guide
- **Architecture:** See `REALTOROS_ARCHITECTURE.md` for system architecture
- **Features:** See `FEATURES.md` for complete feature list
- **Modules:** 
  - `MODULE_1_CLIENTS.md` - Clients module documentation
  - `MODULE_2_TASKS.md` - Tasks module documentation
  - `MODULE_3_EMAILS.md` - Emails module documentation
  - `MODULE_4_DASHBOARD.md` - Dashboard module documentation

---

## 🎯 Summary

**Current Status:** All code issues have been fixed! The system is fully functional.

**Remaining Blockers:**
1. **SendGrid webhooks require a public URL** - Use ngrok for local development or deploy to production
2. **Configure webhook URL in SendGrid dashboard** - Point it to your public URL
3. **Test the complete flow** - Verify opens and clicks are tracked

**Next Major Implementation:**
- **Agent Model Implementation** - Full multi-agent support with authentication and data isolation (see detailed plan above)

Once webhooks are configured and the agent model is implemented, the system will have complete multi-agent support with full engagement tracking!

---

**Last Updated:** Current Session  
**Status:** All code fixes complete, awaiting webhook configuration and agent model implementation
