# Alembic Explained - Simple Guide for RealtorOS

## What is Alembic? 🤔

**Alembic is a database version control tool** - think of it like Git, but for your database structure (tables, columns, indexes, etc.).

Just like Git tracks changes to your code:
- **Git** → tracks code changes
- **Alembic** → tracks database schema changes

### Simple Analogy:
Imagine you're building a house:
- Your **Python models** (`app/models/*.py`) = the **blueprints**
- **Alembic migrations** = the **construction instructions** 
- Your **PostgreSQL database** = the **actual house**

When you change the blueprints (models), Alembic creates instructions (migrations) to update the house (database).

---

## What You Have Set Up ✅

### 1. **Configuration Files**

#### `alembic.ini` (Main Config)
- Tells Alembic where to find everything
- Points to your `alembic/` folder
- Gets database URL from environment variables

#### `alembic/env.py` (Migration Engine)
- Connects Alembic to your project
- Imports all your models (`Client`, `Task`, `EmailLog`)
- Converts async database URL to sync (because Alembic autogenerate needs sync)
- Tells Alembic: "Here are all the tables to track"

### 2. **Migration Files**

#### `alembic/versions/9632c8ae555a_init.py`
- Your **first migration** (initial database setup)
- Creates all 3 tables:
  - `clients` table
  - `tasks` table  
  - `email_logs` table
- Has been **applied** to your database ✅

### 3. **Database State**

Your PostgreSQL database currently has:
- ✅ All 3 tables created
- ✅ All indexes created
- ✅ All foreign keys set up
- ✅ Migration version recorded (at revision `9632c8ae555a`)

---

## How Alembic Works with Other Components 🔗

### Your Project Architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Your Python Code                      │
│                                                           │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │   Models     │───▶│  SQLAlchemy  │                  │
│  │ (client.py)  │    │  (postgresql) │                  │
│  │ (task.py)    │    │     Base     │                  │
│  │ (email_log)  │    │              │                  │
│  └──────────────┘    └──────┬───────┘                  │
│                              │                           │
└──────────────────────────────┼───────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │      Alembic         │
                    │  (env.py + .ini)     │
                    │                      │
                    │  • Reads models       │
                    │  • Generates changes │
                    │  • Applies migrations│
                    └──────────┬───────────┘
                               │
                    ┌──────────▼──────────┐
                    │   PostgreSQL DB      │
                    │  (localhost:5432)   │
                    │                      │
                    │  • clients table     │
                    │  • tasks table       │
                    │  • email_logs table  │
                    └──────────────────────┘
```

### Component Interactions:

#### 1. **Models → Alembic**
- Your models in `app/models/*.py` define what tables should exist
- Alembic reads these models via `env.py`
- When you change models, Alembic detects the differences

#### 2. **Alembic → Database**
- Alembic creates migration files (Python scripts)
- These migrations modify your PostgreSQL database
- Each migration is a version - you can go forward or backward

#### 3. **Your App → Database**
- FastAPI app uses SQLAlchemy to query the database
- SQLAlchemy uses the same models that Alembic tracks
- Everything stays in sync! 🎯

---

## Common Workflow 🚀

### Scenario: You want to add a new field to the Client model

**Step 1:** Edit `app/models/client.py`
```python
class Client(Base):
    # ... existing fields ...
    new_field = Column(String(100), nullable=True)  # ← Add this
```

**Step 2:** Generate migration
```bash
alembic revision --autogenerate -m "add new_field to clients"
```

**Step 3:** Review the generated migration file
- Check `alembic/versions/[new_file].py`
- Make sure it looks correct

**Step 4:** Apply the migration
```bash
alembic upgrade head
```

**Step 5:** Done! ✅
- Your database now has the new field
- Your models match your database
- Everyone's happy!

---

## Key Commands 📋

```bash
# Check current database version
alembic current

# See migration history
alembic history

# Generate new migration (after changing models)
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Undo last migration (rollback)
alembic downgrade -1

# Go to specific version
alembic upgrade [revision_id]
alembic downgrade [revision_id]
```

---

## What Makes Your Setup Special 🎯

### 1. **Sync Engine Conversion**
Your `env.py` automatically converts `postgresql+asyncpg://` to `postgresql+psycopg2://` because:
- Your app uses async (asyncpg) for speed
- Alembic autogenerate needs sync (psycopg2) to work properly
- This conversion happens automatically! ✨

### 2. **Model Auto-Discovery**
Your `env.py` imports all models:
```python
from app.models import client, task, email_log
```
This means Alembic automatically sees ALL your tables - no manual registration needed!

### 3. **Circular Dependency Handling**
You have a circular FK between `tasks` and `email_logs`:
- `Task.email_sent_id` → `EmailLog.id`
- `EmailLog.task_id` → `Task.id`

Your migration handles this by:
1. Creating `tasks` first (without FK to email_logs)
2. Creating `email_logs` (with FK to tasks)
3. Adding the FK from `tasks` to `email_logs` afterward

---

## Important Notes ⚠️

1. **Always backup before migrations in production!**
2. **Review autogenerated migrations** - Alembic is smart but not perfect
3. **Never edit applied migrations** - create new ones instead
4. **Test migrations** on a copy of production data first

---

## Summary 🎓

- **Alembic** = Database version control
- **Migrations** = Step-by-step instructions to change database
- **Current State** = Your database has 3 tables, all set up correctly
- **Next Steps** = When you change models, run autogenerate + upgrade

Your setup is ready to go! 🚀

