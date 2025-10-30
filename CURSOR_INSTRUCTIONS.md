# RealtorOS - Cursor Build Instructions

## Phase 1: Project Structure (Use this first)

Generate the complete project folder structure based on REALTOROS_ARCHITECTURE.md 
section 1. Include:
- All backend Python package structure
- All frontend Next.js app structure
- All config files (.gitignore, .dockerignore, tsconfig.json, etc)
- Placeholder files with docstrings only

## Phase 2: Configuration Files

Create these files (exact specifications below):
- .env.example (use backend/.env section from ARCHITECTURE.md)
- docker-compose.yml (from ARCHITECTURE.md section 6)
- Dockerfile for both backend and frontend

## Phase 3: Models & Schemas

Create based on backend_models.py template:
- app/models/__init__.py (export all)
- MongoDB document models
- Pydantic validators
- Request/response schemas

## Phase 4: Services (Scaffolds Only)

Create service files with function signatures only:
- app/services/crm_service.py
- app/services/scheduler_service.py
- app/services/ai_agent.py
- app/services/email_service.py
- app/db/mongodb.py

Ensure each has:
- Type hints
- Docstrings
- Comments about what it should do
- NO implementation code

## Phase 5: API Routes (Scaffolds Only)

Create route files:
- app/api/routes/clients.py
- app/api/routes/tasks.py
- app/api/routes/emails.py
- app/api/routes/dashboard.py

Each should have:
- All endpoints defined with @router decorators
- Request/response models
- Docstrings
- Empty implementations (return placeholder)

## Phase 6: Frontend Scaffolds

Create component files (no styling):
- src/components/*.tsx
- src/hooks/*.ts
- src/lib/api.ts
- src/types/*.ts

Only TypeScript interfaces and component shells.

## Phase 7: Database Migrations

Create MongoDB index setup:
- app/db/indices.py
- app/db/seed.py (demo data structure)

## Current Phase: [START WITH PHASE 1]
```

---

## 🎯 Optimal Cursor Workflow

Instead of giving it code files, give it **this exact prompt** to Cursor:
```
I'm building RealtorOS - an AI-powered CRM for real estate agents.

Architecture Overview:
- Backend: FastAPI + MongoDB + Celery + Redis
- Frontend: Next.js 14 + TypeScript + Tailwind CSS
- Services: CRM, Scheduler, AI Agent, Email, Celery Workers
- APIs: 11 endpoints for clients, tasks, emails, dashboard

I have the complete architecture documented. I need you to build the 
project structure first (not implementation code, just scaffolding).

Step 1: Create the complete folder structure for both backend and frontend
Step 2: Create all config files (docker-compose.yml, .env.example, etc)
Step 3: Create placeholder/scaffold files with docstrings
Step 4: Create TypeScript type definitions and interfaces
Step 5: Create API route definitions (no logic)
Step 6: Create React component shells (no styling)

Here is the complete architecture documentation:
[PASTE: REALTOROS_ARCHITECTURE.md]

Start with Step 1 and create the folder structure. I'll guide you through each step.