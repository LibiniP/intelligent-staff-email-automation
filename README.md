# Intelligent Staff Email Personalization & Automation System

An internal communication automation platform designed to identify staff occasions and institutional milestones, generate personalized email drafts using verified institutional information, route them through an approval workflow, schedule approved communications, and deliver them through Microsoft 365/Outlook.

## Project Workflow

Staff Data
→ Milestone Detection
→ Communication Rules
→ Context Selection
→ AI Personalization
→ Review & Approval
→ Scheduling
→ Outlook Delivery
→ Audit & Analytics

## Main Modules

- Microsoft 365 / Outlook Integration
- Staff Directory
- Milestone Detection
- Rules Engine
- Template Management
- AI-Assisted Email Generation
- Approval Workflow
- Scheduling
- Communication History
- Analytics
- Role-Based Access Control

## Tech Stack

### Frontend

### Backend
- Python

### Database

### AI

### Microsoft Integration

### DevOps
- Git
- GitHub

## Run locally

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest
.venv/bin/uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. With no Graph credentials, "sent" emails go to an in-memory mock outbox.
Load fake staff with `POST /api/dev/seed-demo` (role `admin`).

## Status

Built: milestone engine, rules, templates, fact-guarded drafting, approval, scheduling, audit, duplicate guard, opt-out, analytics, dashboard.
Not done yet: Entra ID login (dev header auth only), real staff sync from Graph/HR source, live Graph send test, Alembic migrations, background worker loop.

## Setup for a teammate (from GitHub, with Postgres)

```bash
git clone <repo-url> && cd intelligent-staff-email-automation
cp .env.example .env            # then fill in the keys; .env is never committed
docker compose up -d            # starts Postgres (or use your own and edit DATABASE_URL)
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

In `.env`, set `DATABASE_URL=postgresql+psycopg://staff:staff@localhost:5432/staff_email`.

### Load the staff data

Put the staff file in `data/` (that folder is gitignored, so real staff data stays off GitHub). Excel `.xlsx` works directly: every sheet with a `staff_id` column is read (README sheets are skipped). A plain CSV works too. Then:

```bash
.venv/bin/python -m app.cli init-db
.venv/bin/python -m app.cli import-csv ../data/staff_dataset.xlsx
```

Required columns: employee id (`staff_id`), name (or `first_name` + `last_name`), email, department, designation, joining date. Optional: title (Dr./Prof.), category, employment status, preferred name, birth date, retirement date, opt out (Y/N). Only `ACTIVE` and `ON_LEAVE` staff get emails; `RETIRED` and `RESIGNED` are kept but skipped. Common header names (DOJ, DOB, Dept, Emp ID...) are recognised; see `ALIASES` in `backend/app/importer.py`. Dates like `2001-06-01` and `01/06/2001` both work. Re-running updates existing people. Older databases get any new columns added automatically on startup. Bad rows are skipped and listed.

Then `.venv/bin/uvicorn app.main:app --reload`, or `python -m app.cli scan` / `dispatch`.

### API key slots (`.env`)

| Variable | For |
|---|---|
| `DATABASE_URL` | Postgres connection |
| `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`, `GRAPH_SENDER_MAILBOX` | Outlook sending. Empty = mock mode |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | AI wording polish. Empty = templates only |
| `AUTH_DEV`, `ENTRA_TENANT_ID`, `ENTRA_CLIENT_ID` | Login (Entra ID login not built yet) |

## Screenshots

Demo data only (fake staff).

**Drafts: review, edit, approve or reject**

![Drafts](docs/screenshots/1-drafts.png)

**Upcoming occasions**

![Upcoming](docs/screenshots/2-upcoming.png)

**Analytics**

![Analytics](docs/screenshots/3-analytics.png)

**Audit log**

![Audit](docs/screenshots/4-audit.png)
