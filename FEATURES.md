# RealtorOS - Complete Feature Documentation

**An AI-Powered CRM System for Real Estate Agents**

This document provides a comprehensive overview of all features available in RealtorOS from a realtor's perspective. RealtorOS helps real estate agents manage clients, automate follow-ups, and track engagement using AI-powered email generation.

---

## Table of Contents

1. [Client Management](#1-client-management)
2. [Task & Follow-Up Automation](#2-task--follow-up-automation)
3. [AI-Powered Email Generation](#3-ai-powered-email-generation)
4. [Email Management & Tracking](#4-email-management--tracking)
5. [Dashboard & Analytics](#5-dashboard--analytics)
6. [API Capabilities](#6-api-capabilities)
7. [Automation & Background Tasks](#7-automation--background-tasks)
8. [Database & Data Model](#8-database--data-model)

---

## 1. Client Management

### ✅ Fully Implemented

**Complete CRUD Operations**
- **Create Clients**: Add new real estate clients with comprehensive information
- **List Clients**: Browse all clients with pagination (default 10 per page, up to 100)
- **View Client Details**: Get complete information for any specific client
- **Update Clients**: Modify any client information at any time
- **Delete Clients**: Soft delete functionality - clients are marked as deleted but data is preserved

**Client Data Fields Tracked**
- **Basic Information**:
  - Name (required, 1-100 characters)
  - Email address (required, unique, validated format)
  - Phone number (optional, up to 20 characters)
  
- **Property Information**:
  - Property Address (required, 1-200 characters)
  - Property Type (required): `residential`, `commercial`, `land`, or `other`
  
- **Pipeline Management**:
  - Stage (required): `lead`, `negotiating`, `under_contract`, `closed`, or `lost`
  
- **Additional Data**:
  - Notes (optional, up to 1000 characters) - Free-form notes about the client
  - Custom Fields (JSON) - Flexible key-value pairs for custom data tracking
  - Last Contacted timestamp - Automatically tracked
  - Created At / Updated At timestamps - Automatic audit trail

**Client Organization & Filtering**
- **Filter by Stage**: List clients by pipeline stage (lead, negotiating, under_contract, closed, lost)
- **Search by Email**: Fast email-based lookup (indexed)
- **Pagination**: Efficient browsing with configurable page size (1-100 items per page)
- **Client-Task Relationship**: View all tasks associated with a specific client

**Soft Delete & Data Preservation**
- Clients are never permanently deleted
- `is_deleted` flag preserves all historical data
- Deleted clients are automatically excluded from normal listings
- Full audit trail maintained with created_at and updated_at timestamps

**Client-Task Integration**
- Automatically create follow-up tasks when a new client is added
- View all tasks for any client via dedicated endpoint
- Tasks linked to clients via foreign key relationship

---

## 2. Task & Follow-Up Automation

### ✅ Fully Implemented

**Automated Task Creation**
- **Automatic Follow-Up Schedule**: When you create a new client, the system automatically creates a series of follow-up tasks:
  - **Day 1** (High Priority): First follow-up after initial contact (1 day after client creation)
  - **Day 3** (Medium Priority): Second follow-up to maintain engagement (3 days after)
  - **Week 1** (Medium Priority): Weekly check-in (7 days after)
  - **Week 2** (Low Priority): Bi-weekly follow-up (14 days after)
  - **Month 1** (Low Priority): Monthly follow-up for long-term nurturing (30 days after)

**Task Management Capabilities**
- **View All Tasks**: List all tasks with pagination
- **Filter Tasks**: 
  - By status: `pending`, `completed`, `skipped`, `cancelled`
  - By client: View all tasks for a specific client
- **View Task Details**: Get complete information for any task
- **Update Tasks**: Modify task status, reschedule, update priority, or add notes
- **Manual Task Creation**: Create custom tasks outside the automated schedule
- **Task Rescheduling**: Move tasks to different dates/times
- **Mark Tasks Complete**: Update status and add completion notes

**Follow-Up Types & Timing**
- **Predefined Types**: Day 1, Day 3, Week 1, Week 2, Month 1, Custom
- **Priority Levels**: `high`, `medium`, `low` - assigned automatically based on follow-up type
- **Scheduled Dates**: Automatically calculated based on client creation date + schedule offset
- **Custom Follow-Ups**: Create tasks with custom follow-up types for unique scenarios

**Task Status Workflow**
- **Pending**: Default status for new tasks - waiting to be processed
- **Completed**: Task finished (automatically set when email is sent)
- **Skipped**: Task skipped intentionally
- **Cancelled**: Task cancelled and won't be processed

**Task Details Tracked**
- Client ID (foreign key relationship)
- Follow-up type (Day 1, Day 3, Week 1, Week 2, Month 1, Custom)
- Scheduled date/time (timezone-aware UTC)
- Status (pending, completed, skipped, cancelled)
- Priority (high, medium, low)
- Notes (optional, up to 500 characters)
- Email sent ID (links to EmailLog when email is sent)
- Created/Updated/Completed timestamps

**Automated Email Processing**
- Tasks scheduled for past dates are automatically processed
- System generates AI-powered emails and sends them via SendGrid
- Task status automatically updated to "completed" after successful email send
- Email sent ID recorded for full traceability

---

## 3. AI-Powered Email Generation

### ✅ Fully Implemented

**OpenAI Integration**
- Uses OpenAI's Chat API (configurable model, e.g., GPT-3.5-turbo or GPT-4)
- Configurable max tokens for response length control
- Async processing for fast generation

**Personalization Features**
- **Client-Specific Content**:
  - Uses client name throughout the email
  - References property address and property type
  - Incorporates client notes and custom fields
  - Adapts to current pipeline stage
  
- **Follow-Up Context Awareness**:
  - Different email templates based on follow-up type (Day 1, Day 3, Week 1, etc.)
  - Understands the relationship stage (initial contact vs. ongoing nurturing)
  - Adapts tone and goals based on timing

- **Dynamic Prompt Engineering**:
  - Day 1: Warm introduction, confirm interest, offer next steps
  - Day 3: Check-in, answer questions, maintain momentum
  - Week 1: Market insights, schedule showings, share listings
  - Week 2: Follow up on interactions, address concerns
  - Month 1: Long-term relationship building, market updates

**Email Preview Before Sending**
- Preview endpoint allows reviewing AI-generated emails before sending
- Shows subject line and full email body
- Can preview with custom agent instructions
- Preview doesn't create an email log entry

**Custom Instructions Capability**
- Realtors can provide custom instructions for email generation
- Instructions up to 500 characters
- Instructions guide AI behavior for specific scenarios
- Example: "Emphasize the backyard space" or "Be more casual"

**Fallback Templates**
- If OpenAI API fails or times out, system uses fallback email templates
- Fallback includes basic subject line and body
- Ensures email delivery even during API issues
- Logs errors for debugging

**Email Quality Features**
- **Professional Tone**: Friendly, professional, helpful (not pushy)
- **Appropriate Length**: 3-5 short paragraphs (concise)
- **Clear Call-to-Action**: Each email includes specific next steps
- **Property Reference**: Naturally references client's property when relevant
- **Natural Language**: Uses client's name naturally throughout

**Response Parsing**
- Handles JSON responses from OpenAI
- Falls back to text parsing if JSON fails
- Validates subject and body presence
- Generates email preview snippets (first 150-200 characters)

---

## 4. Email Management & Tracking

### ✅ Fully Implemented

**Email Sending via SendGrid**
- Integrated with SendGrid API for reliable email delivery
- Configurable sender email and name
- HTML email body support
- Automatic message ID tracking for webhook correlation

**Email Logging & Tracking**
- **Complete Audit Trail**: Every email is logged with:
  - Task ID and Client ID (full relationship tracking)
  - Recipient email and subject
  - Email body (HTML content)
  - Status tracking (queued → sent → delivered → opened → clicked)
  - SendGrid message ID for correlation
  - Created/sent/opened/clicked timestamps
  - Error messages if sending fails

**Email Status Tracking**
- **Status Values**:
  - `queued`: Email created, waiting to send
  - `sent`: Successfully sent via SendGrid
  - `delivered`: SendGrid confirmed delivery
  - `opened`: Recipient opened email (first open tracked)
  - `clicked`: Recipient clicked link (first click tracked)
  - `bounced`: Email bounced (invalid address)
  - `failed`: Send failed (network error, API error, etc.)
  - `dropped`: SendGrid dropped email (spam, invalid, etc.)
  - `spamreport`: Recipient marked as spam
  - `deferred`: Temporarily rejected, will retry

**Real-Time Engagement Tracking**
- **Webhook Integration**: Secure SendGrid webhook endpoint (`/webhook/sendgrid`)
- **ECDSA Signature Verification**: All webhook requests verified for security
- **Timestamp Validation**: Rejects requests older than 10 minutes (replay attack protection)
- **Automatic Status Updates**: 
  - `opened_at` timestamp set on first open event
  - `clicked_at` timestamp set on first click event
  - Status updated to latest event type
- **Event History**: All webhook events stored in `webhook_events` JSON array

**Email History & Audit Trail**
- **List All Emails**: Browse email history with pagination
- **Filter by Client**: View all emails for a specific client
- **Filter by Status**: List emails by delivery/engagement status
- **View Email Details**: Get complete email information including:
  - Full email body
  - Engagement timestamps (sent, opened, clicked)
  - SendGrid message ID
  - Error messages if any
  - Complete webhook event history

**Email Metadata Tracking**
- **IP Address**: Track IP address from open/click events
- **User Agent**: Browser/client information from engagement events
- **URL Tracking**: Track which links were clicked (for click events)
- **Event IDs**: SendGrid event IDs for correlation
- **Full Event Data**: Complete webhook payload stored for analysis

**Email Service Features**
- **Retry Logic**: Failed sends can be retried (retry_count tracked)
- **Error Handling**: Detailed error messages logged
- **Idempotency**: Webhook events can be safely reprocessed
- **Multiple Events**: Handles multiple events for same email (all stored)

---

## 5. Dashboard & Analytics

### ✅ Fully Implemented

**KPIs and Statistics**
- **Client Metrics**:
  - Total clients (all non-deleted clients)
  - Active clients (clients in lead, negotiating, or under_contract stages)
  
- **Task Metrics**:
  - Pending tasks (tasks waiting to be processed)
  - Completed tasks (successfully finished tasks)
  
- **Email Activity**:
  - Emails sent today (count of emails with status="sent" created today)
  - Emails sent this week (count of emails created this week)
  
- **Engagement Metrics**:
  - **Open Rate**: Percentage of sent emails that were opened
  - **Click Rate**: Percentage of sent emails that had clicks
  - **Conversion Rate**: Percentage of leads that became closed deals

**Client Pipeline Metrics**
- **Stage Distribution**: Count of clients in each pipeline stage:
  - Lead
  - Negotiating
  - Under Contract
  - Closed
  - Lost
  
- **Active vs. Total**: Distinction between total clients and active pipeline clients

**Task Completion Tracking**
- Total pending tasks
- Total completed tasks
- Task status breakdown (pending, completed, skipped, cancelled)

**Email Engagement Metrics**
- **Open Rate Calculation**: (Opened emails / Total sent emails) × 100
- **Click Rate Calculation**: (Clicked emails / Total sent emails) × 100
- **Time-based Filtering**: Today's and this week's email counts
- **Real-time Updates**: Metrics update as webhooks are received

**Recent Activity Feed**
- **Activity Types**: Email sent events
- **Activity Information**:
  - Activity type (e.g., "email")
  - Email subject
  - Recipient email address
  - Email status
  - Client name and ID
  - Timestamp (ISO format)
- **Sorting**: Most recent activities first
- **Limit**: Configurable limit (default 10 items)

**Dashboard Service Capabilities**
- Client statistics by stage
- Task statistics by status
- Email statistics by status
- Time-aware queries (today, this week)
- Efficient database aggregations

### ⚠️ Partially Implemented

**Recent Activity Feed**
- Currently only shows email activities
- Could be extended to include:
  - Client creation events
  - Task completion events
  - Client stage changes
  - Custom activity types

---

## 6. API Capabilities

### ✅ Fully Implemented

**REST API Architecture**
- FastAPI framework with automatic OpenAPI documentation
- Swagger UI available at `/docs`
- ReDoc documentation at `/redoc`
- Type-safe request/response validation using Pydantic
- Async/await for high performance

**Client Management Endpoints**
```
POST   /api/clients              Create a new client
GET    /api/clients              List clients (with pagination & filtering)
GET    /api/clients/{id}         Get specific client details
PATCH  /api/clients/{id}         Update client information
DELETE /api/clients/{id}         Soft delete a client
GET    /api/clients/{id}/tasks   Get all tasks for a client
```

**Task Management Endpoints**
```
GET    /api/tasks                List tasks (with pagination & filtering)
GET    /api/tasks/{id}           Get specific task details
POST   /api/tasks                Manually create a new task
PATCH  /api/tasks/{id}           Update task (status, schedule, notes, priority)
```

**Email Management Endpoints**
```
GET    /api/emails               List email history (with pagination & filtering)
GET    /api/emails/{id}         Get specific email details
POST   /api/emails/preview      Preview AI-generated email (no send)
POST   /api/emails/send         Generate and send email
```

**Dashboard Endpoints**
```
GET    /api/dashboard/stats           Get dashboard KPIs and statistics
GET    /api/dashboard/recent-activity Get recent activity feed
```

**Webhook Endpoints**
```
POST   /webhook/sendgrid        SendGrid webhook endpoint (public, signature verified)
```

**System Endpoints**
```
GET    /                          API root with version info
GET    /health                    Health check endpoint
```

**Query Parameters & Filtering**
- **Pagination**: `page` (default: 1), `limit` (default: 10, max: 100)
- **Client Filtering**: `stage` (lead, negotiating, under_contract, closed, lost)
- **Task Filtering**: `status` (pending, completed, skipped, cancelled), `client_id`
- **Email Filtering**: `client_id`, `status` (queued, sent, delivered, opened, clicked, etc.)

**Response Formats**
- JSON responses with consistent structure
- Pydantic schema validation ensures type safety
- Error responses follow standard HTTP status codes
- Detailed error messages for debugging

**Integration Capabilities**
- CORS enabled for cross-origin requests
- Configurable allowed origins
- RESTful design principles
- Stateless API design
- Easy integration with frontend applications or third-party tools

---

## 7. Automation & Background Tasks

### ✅ Fully Implemented

**Celery Background Processing**
- Celery workers process tasks asynchronously
- Redis as message broker and result backend
- Non-blocking email sending and task processing
- Automatic retry logic for failed tasks

**Automated Follow-Up Task Creation**
- **Trigger**: When a new client is created
- **Task**: `create_followup_tasks_task`
- **Behavior**: Automatically creates 5 follow-up tasks (Day 1, Day 3, Week 1, Week 2, Month 1)
- **Execution**: Runs asynchronously via Celery

**Periodic Task Processing**
- **Task**: `process_due_tasks`
- **Schedule**: Runs every minute via Celery Beat
- **Behavior**:
  - Finds all tasks where `scheduled_for <= now` and `status = "pending"`
  - For each due task:
    - Fetches client information
    - Generates AI-powered email using OpenAI
    - Sends email via SendGrid
    - Updates task status to "completed"
    - Records email_sent_id and completed_at timestamp
  - Continues processing even if individual tasks fail
  - Logs all activities for monitoring

**Background Email Processing**
- Email sending happens asynchronously
- Non-blocking API responses
- Retry logic for failed sends (max 3 retries)
- Error handling and logging

**System Health Monitoring**
- **Task**: `health_check_task`
- **Schedule**: Runs every 5 minutes
- **Purpose**: Monitor database connectivity and system health

**Cleanup Tasks**
- **Task**: `cleanup_old_tasks`
- **Schedule**: Runs daily
- **Purpose**: Maintain database performance (currently stubbed)

### ⚠️ Partially Implemented

**Cleanup Tasks**
- Task exists but cleanup logic is not yet implemented
- Could clean up old completed tasks, deleted clients, etc.

### ❌ Not Implemented

**Scheduled Reports**
- No automated email reports to realtors
- No weekly/monthly summary emails

**Automated Client Stage Progression**
- No automatic stage updates based on activity
- Manual stage updates required

---

## 8. Database & Data Model

### ✅ Fully Implemented

**PostgreSQL Database**
- Production-grade relational database
- ACID compliance for data integrity
- Foreign key relationships for data consistency
- Indexes for fast queries
- Timezone-aware timestamps (UTC)

**Client Model (clients table)**
```sql
- id (Primary Key)
- name (Required, 100 chars)
- email (Required, Unique, Indexed)
- phone (Optional, 20 chars)
- property_address (Required, 200 chars)
- property_type (Required: residential/commercial/land/other)
- stage (Required: lead/negotiating/under_contract/closed/lost, Indexed)
- notes (Optional, Text)
- custom_fields (JSON, Optional)
- created_at (Timestamp, UTC)
- updated_at (Timestamp, UTC)
- last_contacted (Timestamp, UTC, Optional)
- is_deleted (Boolean, Default: false, Indexed)
```

**Task Model (tasks table)**
```sql
- id (Primary Key)
- client_id (Foreign Key → clients.id, Indexed)
- email_sent_id (Foreign Key → email_logs.id, Optional)
- followup_type (Required: Day 1/Day 3/Week 1/Week 2/Month 1/Custom)
- scheduled_for (Timestamp, UTC, Indexed)
- status (Required: pending/completed/skipped/cancelled, Indexed)
- priority (Optional: high/medium/low)
- notes (Optional, Text)
- created_at (Timestamp, UTC)
- updated_at (Timestamp, UTC)
- completed_at (Timestamp, UTC, Optional)
```

**EmailLog Model (email_logs table)**
```sql
- id (Primary Key)
- task_id (Foreign Key → tasks.id, Required)
- client_id (Foreign Key → clients.id, Required, Indexed)
- to_email (Required, 255 chars)
- subject (Required, 200 chars)
- body (Text, Required)
- status (Required: queued/sent/delivered/opened/clicked/bounced/failed/dropped/etc., Indexed)
- sendgrid_message_id (Optional, 255 chars, Indexed)
- created_at (Timestamp, UTC, Indexed)
- sent_at (Timestamp, UTC, Optional)
- opened_at (Timestamp, UTC, Optional)
- clicked_at (Timestamp, UTC, Optional)
- error_message (Text, Optional)
- retry_count (Integer, Default: 0)
- webhook_events (JSON Array, Optional) - Stores all webhook events
```

**Database Relationships**
- **Clients → Tasks**: One-to-many (one client has many tasks)
- **Tasks → EmailLogs**: One-to-one (one task can have one email sent)
- **Clients → EmailLogs**: One-to-many (one client can have many emails)

**Data Integrity Features**
- Foreign key constraints ensure referential integrity
- Unique constraints on email addresses
- Indexes on frequently queried fields
- Soft delete pattern (is_deleted flag) preserves data
- Automatic timestamp updates (created_at, updated_at)

**Database Indexes**
- Client email lookup (fast client search)
- Client stage filtering (pipeline queries)
- Task client filtering (client task lists)
- Task scheduled date (due task queries)
- Task status filtering (pending task queries)
- Email status filtering (email history queries)
- Composite indexes for common query patterns

**Migration Management**
- Alembic for database migrations
- Version-controlled schema changes
- Rollback capabilities

---

## Feature Status Summary

### ✅ Fully Implemented (Production Ready)
- Client CRUD operations with soft delete
- Automated follow-up task creation
- Task management and scheduling
- AI-powered email generation with OpenAI
- Email sending via SendGrid
- Email engagement tracking via webhooks
- Dashboard statistics and KPIs
- Complete REST API
- Background task processing
- Database models and relationships

### ⚠️ Partially Implemented (Needs Enhancement)
- Recent activity feed (currently only emails)
- Cleanup tasks (task exists but logic stubbed)
- Custom instructions (supported but could have UI improvements)

### ❌ Not Implemented (Future Features)
- User authentication and authorization
- Multi-user/team support
- Scheduled reports (weekly/monthly summaries)
- Automated client stage progression
- SMS follow-ups
- Calendar integration
- Mobile application
- Bulk operations
- Data export (CSV, PDF)
- Email template library
- Advanced analytics (charts, trends)
- Client activity timeline view
- Document management

---

## Getting Started

### For Realtors

1. **Add a Client**: Create a new client with their property information
2. **Automated Follow-Ups**: The system automatically creates follow-up tasks
3. **Monitor Dashboard**: View your KPIs and recent activity
4. **Preview Emails**: Use the preview endpoint to see AI-generated emails
5. **Send Emails**: Emails are automatically sent when tasks are due
6. **Track Engagement**: View open rates and click rates in the dashboard

### For Developers

See the main [README.md](README.md) for setup instructions, API documentation, and technical details.

---

## Security Features

- **Webhook Signature Verification**: ECDSA signature verification for SendGrid webhooks
- **Timestamp Validation**: Replay attack protection (10-minute window)
- **Input Validation**: Pydantic schemas validate all API inputs
- **SQL Injection Protection**: SQLAlchemy ORM prevents injection attacks
- **Soft Delete**: Data preservation and audit trails

---

## Performance Features

- **Async Processing**: FastAPI async/await for high concurrency
- **Background Tasks**: Celery workers handle heavy processing
- **Database Indexes**: Optimized queries for fast responses
- **Pagination**: Efficient data retrieval for large datasets
- **Connection Pooling**: Optimized database connections

---

**Last Updated**: Based on codebase analysis as of current implementation

**Version**: See API version in `/` endpoint or `app.config.Settings.API_VERSION`

---

*Built with ❤️ for real estate professionals*

