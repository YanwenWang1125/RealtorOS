# Database Deployment Fix Summary

## Problem
The Azure Container App was failing with a DNS resolution error:
```
socket.gaierror: [Errno -2] Name or service not known
```

This occurred because the PostgreSQL database was not deployed in Azure. The deployment workflow was referencing `DATABASE_URL` from GitHub secrets, but the database infrastructure was never created.

## Solution
Added automatic database provisioning to the GitHub Actions workflow.

## Changes Made

### 1. Updated `.github/workflows/azure-deploy.yml`

#### Added Environment Variables
- `DB_SERVER_NAME`: `realtoros-db`
- `DB_NAME`: `realtoros`
- `DB_ADMIN_USER`: `adminuser`

#### Added New Job: `provision-database`
This job runs before backend deployment and:
1. Checks if PostgreSQL Flexible Server exists
2. Creates the server if it doesn't exist (using `DB_PASSWORD` secret)
3. Checks if the database exists
4. Creates the `realtoros` database if it doesn't exist
5. Verifies database hostname resolution

#### Updated `deploy-backend` Job
- Now depends on `provision-database` job
- Constructs `DATABASE_URL` automatically if not provided in secrets
- Uses `DB_PASSWORD` to build connection string when `DATABASE_URL` is not set

### 2. Updated `.github/GITHUB_SECRETS.md`

Added documentation for:
- New `DB_PASSWORD` secret requirement
- Clarified that `DATABASE_URL` is now optional (auto-constructed if not provided)
- Updated minimum configuration requirements

## Required GitHub Secrets

### New Secret Required
- **`DB_PASSWORD`**: PostgreSQL database administrator password (minimum 8 characters)

### Updated Secret
- **`DATABASE_URL`**: Now optional - if not provided, will be auto-constructed from `DB_PASSWORD`

## How It Works

1. **First Deployment**:
   - Workflow checks if PostgreSQL server exists
   - If not, creates PostgreSQL Flexible Server with:
     - Name: `realtoros-db`
     - Admin user: `adminuser`
     - Password: from `DB_PASSWORD` secret
     - Database: `realtoros`
   - Constructs `DATABASE_URL` automatically
   - Deploys backend with the connection string

2. **Subsequent Deployments**:
   - Workflow detects existing database server
   - Skips creation steps
   - Uses existing database
   - Can use either `DATABASE_URL` secret or auto-constructed URL

## Database Configuration

The PostgreSQL server is created with:
- **SKU**: `Standard_B1ms` (Basic tier, 1 vCore, 2GB RAM)
- **Version**: PostgreSQL 16
- **Storage**: 32GB
- **Public Access**: `0.0.0.0-255.255.255.255` (allows all IPs)
  - ⚠️ **Security Note**: For production, consider using private endpoints or restricting IP ranges

## Next Steps

1. **Add `DB_PASSWORD` secret to GitHub**:
   - Go to repository Settings → Secrets and variables → Actions
   - Add new secret: `DB_PASSWORD` with a secure password (min 8 chars)

2. **Optional: Add `AZURE_LOCATION` secret** (if you want to override auto-detection):
   - The workflow automatically detects the region from your existing resource group (`realtoros-rg`)
   - If resource group exists in `canadacentral`, it will use that region
   - If you want to override, set `AZURE_LOCATION` secret (e.g., `canadacentral`, `eastus2`, `westus2`)
   - If the specified region is restricted, the workflow will automatically try fallback regions

3. **Optional: Add `DATABASE_URL` secret** (if you want to use a custom connection string):
   - Format: `postgresql+asyncpg://adminuser:<password>@realtoros-db.postgres.database.azure.com:5432/realtoros`

4. **Trigger deployment**:
   - Push to `main` branch, or
   - Manually trigger workflow from GitHub Actions UI

5. **Verify database creation**:
   - Check workflow logs for "PostgreSQL server already exists" or "Creating PostgreSQL Flexible Server..."
   - Verify database connectivity in the "Verify database connectivity" step

## Troubleshooting

### If database creation fails:
- Check that `DB_PASSWORD` secret is set (minimum 8 characters)
- Verify Azure service principal has permissions to create PostgreSQL resources
- Check Azure resource group exists: `realtoros-rg`
- **Region restrictions**: If you see "location is restricted" error:
  - The workflow will automatically try fallback regions (eastus2, westus2, centralus, westus3, eastus)
  - You can set `AZURE_LOCATION` secret to specify a preferred region
  - Check Azure service availability in your subscription

### If connection still fails:
- Verify database server hostname: `realtoros-db.postgres.database.azure.com`
- Check firewall rules allow Azure Container Apps to connect
- Verify `DB_PASSWORD` matches the password used during server creation

### If DNS resolution fails:
- Wait a few minutes for DNS propagation after server creation
- Verify the server was created successfully in Azure Portal
- Check that the server name is correct: `realtoros-db`

## Security Recommendations

For production environments:
1. **Use Private Endpoints**: Configure PostgreSQL with private endpoints instead of public access
2. **Restrict Firewall**: Limit IP ranges instead of allowing all IPs (0.0.0.0-255.255.255.255)
3. **Use Key Vault**: Store `DB_PASSWORD` in Azure Key Vault and reference it via managed identity
4. **Network Isolation**: Deploy Container Apps and PostgreSQL in the same VNet

## Related Files
- `.github/workflows/azure-deploy.yml` - Main deployment workflow
- `.github/GITHUB_SECRETS.md` - Secrets documentation
- `deploy/scripts/deploy-azure.sh` - Manual deployment script (also creates database)

