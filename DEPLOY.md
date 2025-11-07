# 🏗️ RealtorOS Architecture & Deployment Guide

## Overview

**RealtorOS** is an AI-powered CRM platform for real estate agents, integrating automated follow-ups, task scheduling, and intelligent email generation.  
This document provides a unified overview of the system architecture, Azure deployment mapping, and configuration best practices.

---

## 🧩 Application Architecture

### 1. FastAPI Backend
- **Purpose:** Core API server exposing CRM, task, email, and dashboard routes.
- **Lifecycle:**  
  - Initializes async PostgreSQL connection at startup.  
  - Launches an **APScheduler** background job for automated task/email generation.  
  - Runs HTTP services (via `uvicorn app.main:app`) and scheduled tasks **within the same process**.
- **Deployment Fit:** Designed for containerized environments with horizontal scalability.

### 2. Configuration System
- Backend relies on `.env` / environment variables for:
  - `DATABASE_URL`, `OPENAI_API_KEY`, `AWS_SES_*`, `JWT_SECRET`, `GOOGLE_CLIENT_ID`, `CORS_ORIGINS`, etc.
- In production:
  - All secrets must be injected from **Azure Key Vault**.
  - Validation must ensure key length, boolean flags, and proper formats.

### 3. Data & Task Processing
- **Async SQLAlchemy engine** provides PostgreSQL access through `init_db()` and `get_session()`.
- **APScheduler** executes scheduled jobs every minute via `SchedulerService`:
  - Generates AI-driven emails (OpenAI).
  - Sends via AWS SES.
  - Logs activity and updates task statuses, forming an **automated CRM follow-up loop**.

### 4. External Integrations
- **OpenAI API:** Chat Completions for intelligent email generation.
- **AWS SES:** Email delivery and tracking via `boto3`.
  - In Azure, ensure SES credentials are securely injected and outbound access is allowed.

### 5. Next.js Frontend
- **Architecture:** App Router + hybrid SSR/CSR.
- **Context Providers:** Theme, React Query, and Google OAuth.
- **Deployment:** Configure `NEXT_PUBLIC_API_URL` and other public variables at build time.

### 6. Containerization & Local Development
- `docker-compose.yml` defines **three services**:
  - `postgres` — database
  - `backend` — FastAPI + APScheduler
  - `frontend` — Next.js UI
- Mirrors Azure service separation and provides isolated local development environments.

---

## ☁️ Azure Service Mapping

| Component | Code Reference | Recommended Azure Resource | Key Notes |
|------------|----------------|-----------------------------|------------|
| **PostgreSQL** | `DATABASE_URL` in `.env` | Azure Database for PostgreSQL Flexible Server | Private subnet + automatic backup |
| **FastAPI + APScheduler** | `app/main.py` lifecycle + APScheduler | Azure Container Apps (small scale) or AKS (large scale) | Single replica required to avoid duplicate scheduling |
| **Task Processing** | APScheduler jobs | Same container or Azure Functions (Timer trigger) | Use KEDA/Functions if scaling horizontally |
| **OpenAI Integration** | Async client with env vars | Azure OpenAI Service (optional) | Store API key in Key Vault |
| **Email Sending (SES)** | `email_service.py` | Continue using AWS SES or migrate to Azure Communication Services Email | Inject SES credentials securely |
| **Frontend** | `frontend/Dockerfile` | Static: Azure Static Web Apps<br>SSR: Container Apps / App Service | Set `NEXT_PUBLIC_API_URL` at build time |
| **Secrets** | `.env` variables | Azure Key Vault + Managed Identity | Centralized secrets management |
| **Images** | Dockerfiles | Azure Container Registry (ACR) | CI/CD push from GitHub Actions |

---

## 🚀 Deployment Pipeline

### 1. Network & Security
- Create **VNet + subnets**.
- Enable VNet integration for Container Apps.
- Use **Private Endpoints** for PostgreSQL and Key Vault.
- Route external access via **Azure Front Door** or **Application Gateway**.

### 2. Data Layer Initialization
- Deploy **PostgreSQL Flexible Server**.
- Configure private access/firewall.
- Create `realtoros` database and app credentials.

### 3. Image Build & Registry
- Build backend and frontend via GitHub Actions:
  ```yaml
  - name: Build and push backend
    run: docker build -t $ACR_NAME.azurecr.io/realtoros-api:latest backend/
  - name: Build and push frontend
    run: docker build -t $ACR_NAME.azurecr.io/realtoros-frontend:latest frontend/
