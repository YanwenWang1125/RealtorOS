# ⚠️ CRITICAL WARNING: Integration Tests Delete Database Data

## What Happened

The integration tests in `tests/integration/conftest.py` use the **REAL database** configured in your `.env` file and **DELETE ALL DATA** before and after each test.

**The `db_session` fixture automatically:**
- Deletes all EmailLogs
- Deletes all Tasks  
- Deletes all Clients
- Deletes all Agents (except system@realtoros.com)

This happens **BEFORE and AFTER** every integration test.

## How to Recover Your Data

### Option 1: Check PostgreSQL WAL (Write-Ahead Log)
If PostgreSQL is still running, you might be able to recover from transaction logs:
```bash
# Check if PostgreSQL has point-in-time recovery enabled
psql -U postgres -d realtoros -c "SHOW wal_level;"
```

### Option 2: Check Docker Volume Backups
If you're using Docker, check for volume snapshots:
```bash
docker volume inspect realtoros_postgres_data
```

### Option 3: Check for Database Backups
Look for any `.sql` backup files or automated backups.

## How to Prevent This in the Future

### Solution 1: Use a Separate Test Database (RECOMMENDED)

1. Create a test database:
```sql
CREATE DATABASE realtoros_test;
```

2. Set `TEST_DATABASE_URL` in your `.env`:
```env
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/realtoros_test
```

3. Update `tests/integration/conftest.py` to use test database:
```python
import os
from app.config import settings

# Use test database if available, otherwise warn
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    import warnings
    warnings.warn(
        "⚠️ WARNING: Integration tests are using PRODUCTION database! "
        "Set TEST_DATABASE_URL to use a separate test database.",
        UserWarning
    )
    TEST_DATABASE_URL = settings.DATABASE_URL
```

### Solution 2: Add Safety Check

Add a check to prevent running tests against production:
```python
@pytest_asyncio.fixture(scope="function")
async def db_session():
    # Safety check
    db_url = settings.DATABASE_URL.lower()
    if "production" in db_url or "prod" in db_url:
        pytest.skip("Skipping test - production database detected!")
    
    # ... rest of fixture
```

## Immediate Action Required

**DO NOT RUN INTEGRATION TESTS** until you've:
1. Set up a separate test database, OR
2. Added safety checks to prevent data deletion

The current test configuration is **DANGEROUS** and will delete your data every time tests run.

