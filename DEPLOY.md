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
  ```

### 4. Secrets & Configuration
- Store in **Azure Key Vault**:
  - `DATABASE_URL`
  - `OPENAI_API_KEY`
  - `AWS_SES_ACCESS_KEY_ID`
  - `AWS_SES_SECRET_ACCESS_KEY`
  - `SECRET_KEY` (JWT signing)
  - `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- Use **Managed Identity** for Container Apps to access Key Vault
- Inject secrets as environment variables at runtime

### 5. Container Deployment
- Deploy **Backend Container** to Azure Container Apps:
  - Single replica initially (APScheduler requires single instance)
  - Scale horizontally after implementing distributed locking (e.g., PostgreSQL advisory locks)
  - Configure health checks: `/health` endpoint
  - Set resource limits: 0.5 CPU, 1GB RAM (adjust based on load)

- Deploy **Frontend Container**:
  - Can scale horizontally (stateless)
  - Configure build-time env vars
  - Use Azure CDN for static assets (optional)

### 6. Database Migration
- Run Alembic migrations on deployment:
  ```bash
  kubectl exec -it <backend-pod> -- alembic upgrade head
  # OR via init container in deployment manifest
  ```

### 7. Monitoring & Logging
- Enable **Azure Monitor** and **Application Insights**
- Configure log aggregation from containers
- Set up alerts for:
  - High error rates
  - Database connection issues
  - Email delivery failures
  - APScheduler job failures

---

## 🔒 Security Best Practices

### 1. Network Security
- **Private Endpoints** for PostgreSQL and Key Vault
- **VNet Integration** for Container Apps
- **NSG Rules** to restrict traffic
- **Azure Front Door** with WAF for public-facing endpoints

### 2. Secrets Management
- **Never** commit secrets to git
- Use **Key Vault** for all sensitive data
- Rotate secrets regularly (90 days)
- Use **Managed Identity** instead of connection strings where possible

### 3. Database Security
- **SSL/TLS** required for PostgreSQL connections
- **Firewall rules** to allow only Azure services
- **Automated backups** with point-in-time restore
- **Read replicas** for high availability (optional)

### 4. Application Security
- Keep dependencies updated (use Dependabot)
- Scan containers for vulnerabilities (Azure Defender)
- Implement rate limiting
- Enable CORS only for trusted origins

---

## 📊 Deployment Options Comparison

### Option 1: Azure Container Apps (Recommended for MVP)
**Pros:**
- Fully managed serverless containers
- Built-in HTTPS, auto-scaling
- Easy integration with Key Vault
- Cost-effective for small scale

**Cons:**
- Less control than AKS
- Single replica limitation for APScheduler (until distributed locking)

**Best for:** Small to medium scale (< 10k clients)

### Option 2: Azure Kubernetes Service (AKS)
**Pros:**
- Full Kubernetes control
- Advanced scaling options
- Best for microservices architecture
- Can run APScheduler as separate job

**Cons:**
- Higher complexity
- Requires Kubernetes expertise
- Higher base cost

**Best for:** Large scale (> 10k clients), complex requirements

### Option 3: Azure App Service
**Pros:**
- Simple deployment
- Good for web apps
- Built-in CI/CD

**Cons:**
- Less container-native
- More expensive than Container Apps
- Limited scaling options

**Best for:** Traditional web apps, less container-focused

---

## 🚀 Quick Deployment Guide

### Prerequisites
1. Azure CLI installed and logged in
2. Azure subscription with appropriate permissions
3. Docker and docker-compose installed locally
4. GitHub repository set up

### Step-by-Step Deployment

#### 1. Prepare Azure Resources
```bash
# Set variables
export RESOURCE_GROUP="realtoros-rg"
export LOCATION="eastus"
export ACR_NAME="realtorosacrXXXX"  # Must be globally unique
export KEYVAULT_NAME="realtoros-kvXXXX"  # Must be globally unique

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME --sku Basic

# Create Key Vault
az keyvault create --name $KEYVAULT_NAME \
  --resource-group $RESOURCE_GROUP --location $LOCATION

# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name realtoros-db \
  --location $LOCATION \
  --admin-user postgres \
  --admin-password <secure-password> \
  --sku-name Standard_B1ms \
  --version 18 \
  --storage-size 32
```

#### 2. Store Secrets in Key Vault
```bash
# Database connection string
az keyvault secret set --vault-name $KEYVAULT_NAME \
  --name "DATABASE-URL" \
  --value "postgresql+asyncpg://postgres:<password>@realtoros-db.postgres.database.azure.com:5432/realtoros"

# API Keys
az keyvault secret set --vault-name $KEYVAULT_NAME \
  --name "OPENAI-API-KEY" --value "<your-openai-key>"

az keyvault secret set --vault-name $KEYVAULT_NAME \
  --name "AWS-SES-ACCESS-KEY-ID" --value "<your-aws-key>"

az keyvault secret set --vault-name $KEYVAULT_NAME \
  --name "AWS-SES-SECRET-ACCESS-KEY" --value "<your-aws-secret>"

az keyvault secret set --vault-name $KEYVAULT_NAME \
  --name "SECRET-KEY" --value "<generate-32-char-random-string>"
```

#### 3. Build and Push Docker Images
```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build and push backend
docker build -t $ACR_NAME.azurecr.io/realtoros-api:latest ./backend
docker push $ACR_NAME.azurecr.io/realtoros-api:latest

# Build and push frontend
docker build -t $ACR_NAME.azurecr.io/realtoros-frontend:latest ./frontend
docker push $ACR_NAME.azurecr.io/realtoros-frontend:latest
```

#### 4. Deploy to Azure Container Apps
```bash
# Create Container Apps environment (Consumption Plan - default)
az containerapp env create \
  --name realtoros-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Deploy backend (Consumption plan with scale-to-zero enabled)
# Note: min-replicas 0 enables cost savings when no traffic
# If APScheduler requires always-on, consider min-replicas 1
az containerapp create \
  --name realtoros-backend \
  --resource-group $RESOURCE_GROUP \
  --environment realtoros-env \
  --image $ACR_NAME.azurecr.io/realtoros-api:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 10 \
  --cpu 0.5 --memory 1.0Gi \
  --secrets database-url=keyvaultref:<keyvault-uri>,identityref:<identity-id> \
  --env-vars DATABASE_URL=secretref:database-url

# Deploy frontend (Consumption plan with scale-to-zero enabled)
az containerapp create \
  --name realtoros-frontend \
  --resource-group $RESOURCE_GROUP \
  --environment realtoros-env \
  --image $ACR_NAME.azurecr.io/realtoros-frontend:latest \
  --target-port 3000 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 10 \
  --cpu 0.25 --memory 0.5Gi \
  --env-vars NEXT_PUBLIC_API_URL=<backend-url>
```

#### 5. Run Database Migrations
```bash
# Get backend container name
az containerapp exec \
  --name realtoros-backend \
  --resource-group $RESOURCE_GROUP \
  --command "alembic upgrade head"
```

---

## 📁 Deployment Files Location

All deployment-related files are now organized in the `deploy/` directory:

```
deploy/
├── azure/
│   ├── bicep/              # Infrastructure as Code templates
│   ├── container-apps/     # Container Apps configurations
│   └── keyvault/          # Key Vault setup scripts
├── docker/
│   ├── docker-compose.prod.yml
│   └── docker-compose.staging.yml
├── scripts/
│   ├── deploy-azure.sh    # Automated Azure deployment
│   ├── setup-keyvault.sh  # Key Vault initialization
│   └── build-images.sh    # Docker image build script
└── github-actions/
    └── azure-deploy.yml   # GitHub Actions CI/CD workflow
```

---

## 🔄 CI/CD with GitHub Actions

See `deploy/github-actions/azure-deploy.yml` for automated deployment pipeline.

**Workflow:**
1. Push to `main` branch triggers deployment
2. Run tests
3. Build Docker images
4. Push to Azure Container Registry
5. Deploy to Azure Container Apps
6. Run database migrations
7. Health check verification

---

## 🧪 Testing Deployment

### Health Checks
```bash
# Backend health
curl https://<backend-url>/health

# Database connectivity
curl https://<backend-url>/api/health/db

# Frontend
curl https://<frontend-url>
```

### Smoke Tests
1. Create a test client via API
2. Verify task creation
3. Send test email
4. Check dashboard metrics

---

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure PostgreSQL Flexible Server](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/)
- [Azure Key Vault Best Practices](https://learn.microsoft.com/en-us/azure/key-vault/general/best-practices)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)

---

## ⚠️ Important Notes

1. **APScheduler Single Instance**: Current implementation requires single replica. For horizontal scaling, implement distributed locking using PostgreSQL advisory locks or Redis.

2. **Email Service**: Using AWS SES requires AWS credentials. Consider migrating to Azure Communication Services for full Azure integration.

3. **Costs**: Monitor Azure costs using Cost Management. Container Apps pricing is based on vCPU-seconds and memory GB-seconds.

4. **Backups**: PostgreSQL Flexible Server has automated backups. Test restore procedures regularly.

5. **Monitoring**: Set up Application Insights for comprehensive monitoring and alerting.

---

**Last Updated:** 2025-11-06
**Architecture Version:** APScheduler (post-Celery migration)
