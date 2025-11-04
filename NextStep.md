 in the client property type
    land -> rental

Current stage:
    no under contract
    closed -> archieved
    no negotating|

holiday send followup toeveryone
google canlender supports
login ui
birthday celebration



# 🧩 RealtorOS To-Do List

> **Status:** 🚧 Not ready for MVP — pending critical backend, email automation, and frontend fixes.

---

## 🧱 1. Frontend Fixes & Build

- [ ] **Rebuild `frontend/src/lib` utility tree**
  - [ ] Create `utils/`, `constants/`, `formatters/`, `date/` helpers
  - [ ] Ensure `@/lib/...` aliases resolve correctly
  - [ ] Run `npm run lint && npm run build` until clean

- [ ] **UI & Theming**
  - [ ] Fix `Button.tsx` imports with shadcn/ui
  - [ ] Verify Tailwind + shadcn compatibility
  - [ ] Apply consistent white/brand theme colors

---

## 📧 2. Email System (SendGrid + Templates + Automation)

### 🔌 2.1 SendGrid Integration
- [ ] Wrap `SendGridAPIClient.send()` in `asyncio.to_thread`
- [ ] Remove duplicate `get_email` definitions
- [ ] Add retries, structured error handling, and logging
- [ ] Return clear status from `EmailService`

### 🧾 2.2 Email Templates
- [ ] Create `/templates/email/` directory
  - [ ] `welcome_client.html`
  - [ ] `followup_day3.html`
  - [ ] `birthday_greeting.html`
  - [ ] `property_anniversary.html`
- [ ] Support dynamic placeholders:
{client_name}}, {{agent_name}}, {{property_address}}, {{unsubscribe_link}}

需要新增邮件窗口；

- [ ] Optional: store templates in DB + build simple frontend editor

### 🎨 2.3 Formatting & Content
- [ ] Use unified HTML + inline CSS for all emails
- [ ] Add responsive design for mobile
- [ ] Include header/footer with RealtorOS branding
- [ ] Add open/click tracking pixel

### 🚪 2.4 Unsubscribe Flow
- [ ] Generate unique unsubscribe token per email
- [ ] Implement `/emails/unsubscribe` endpoint
- [ ] Mark unsubscribed clients in DB
- [ ] Update Celery logic to skip unsubscribed clients

### 🤖 2.5 Automation Tasks
- [ ] Implement `email_tasks.py`:
- [ ] Load tasks and client records
- [ ] Call `AIAgent.generate_email`
- [ ] Send via `EmailService.send_email`
- [ ] Retry or mark failed jobs
- [ ] Implement periodic scan (`periodic.py`)
- [ ] Daily check for due tasks
- [ ] Queue Celery worker jobs

---

## ⏰ 3. Scheduler & Task System

- [ ] **Unify SchedulerService interfaces**
- [ ] Ensure `agent_id` consistently required
- [ ] Fix Celery task calls and tests
- [ ] **Define automation task types**
- [ ] Day 1 / Day 3 / Week 1 / Month 1 / 6-Month follow-ups
- [ ] Birthday reminders
- [ ] Home purchase anniversaries
- [ ] Tax / utility / vacancy-tax reminders
- [ ] **Add failure handling**
- [ ] Log errors + retry
- [ ] Mark tasks as “manual check needed” after 3 fails

---

## 🔐 4. Authentication & Security

- [ ] Remove dev auth bypass in `get_current_agent`
- [ ] Require explicit token or seeded test accounts
- [ ] Add integration test: invalid token → 401
- [ ] Ensure sensitive keys only live in `.env`

---

## 🧮 5. Data Isolation & Dashboard Security

- [ ] Add `agent_id` filter to:
- [ ] `get_client_stats`
- [ ] `get_task_stats`
- [ ] `get_email_stats`
- [ ] Adjust APIs and frontend dashboard accordingly
- [ ] Add tests to confirm tenant isolation

---

## ⚙️ 6. Configuration & Deployment Hygiene

- [ ] **Clean repository**
- [ ] Remove committed `node_modules/`
- [ ] Prune unused deps (e.g. `passlib[bcrypt]`)
- [ ] **Add missing config files**
- [ ] `backend/.env.example`
- [ ] `frontend/.env.local.example`
- [ ] Optional: `docker-compose.override.yml`
- [ ] **CI/CD automation**
- [ ] Build → Test → Push container images
- [ ] Check environment variables
- [ ] Run lint/typecheck/unit tests automatically

---

## 🧪 7. Testing & Observability

- [ ] **End-to-end test coverage**
- [ ] Create client → Schedule → Run Celery → Send email
- [ ] Verify logs + DB states
- [ ] Cover success / failure / unsubscribe paths
- [ ] **Metrics & Monitoring**
- [ ] Structured logs (already partially done)
- [ ] Add metrics: task counts, error rates, latency
- [ ] Add `/healthz` health endpoint
- [ ] Optional: integrate Logtail / ELK for central logging

---

## 🚀 Priority Overview

| Priority | Area | Goal |
|-----------|------|------|
| 🟥 P0 | Email system (SendGrid + templates + unsubscribe) | Core functionality |
| 🟧 P1 | Scheduler + automation + e2e testing | Ensure task automation |
| 🟨 P2 | Auth + data isolation | Security & tenant safety |
| 🟩 P3 | Frontend fixes + build pass | UI functional |
| 🟦 P4 | Config cleanup + CI/CD | Delivery automation |
| ⚪ P5 | Monitoring & metrics | Stability enhancements |

---

> 📅 **Next milestone:** Achieve P0–P2 completion to enable first production-ready MVP build.