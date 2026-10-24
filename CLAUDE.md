# CLAUDE.md

Internal tool for Amrita: finds staff occasions (birthdays, joining anniversaries, service milestones, Silver Jubilee, retirement), drafts personalized emails from verified data, routes them through human approval, schedules them, and sends via Microsoft 365 / Outlook (Graph API). Full brief: the project PDF "Intelligent Staff Email Personalization & Automation System".

Pipeline: Staff data -> Milestone detection -> Rules -> Context -> Draft -> Approval -> Schedule -> Send -> Audit.

## Start here

- `graphify-out/GRAPH_REPORT.md` is a map of the code (modules, central functions, how they connect). Read it before exploring. `graphify query "<question>"` answers from the graph.
- Code lives in `backend/app/`. Dashboard is one file: `frontend/src/index.html`. Tests: `backend/tests/`.

## Run

```bash
cp .env.example .env            # fill in keys; .env is gitignored
docker compose up -d            # Postgres; set DATABASE_URL to the postgresql+psycopg line
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest      # must pass before any change is done
.venv/bin/python -m app.cli init-db
.venv/bin/python -m app.cli import-csv ../data/staff_dataset.xlsx
.venv/bin/uvicorn app.main:app --reload     # http://127.0.0.1:8000
```

CLI: `python -m app.cli init-db | import-csv FILE | scan | dispatch`.

## Code map (`backend/app/`)

| File | Role |
|---|---|
| `milestones.py` | Pure date logic: which occasions fall in a window. No DB, takes `today`. |
| `personalize.py` | Builds verified-facts context, renders templates, `guard()` blocks invented facts, optional Claude polish. |
| `services.py` | Pipeline: `scan_and_draft`, `approve`, `reject`, `edit`, `cancel`, `dispatch_due`. Every step writes `AuditLog`. |
| `models.py` | Staff, Template, Rule, Draft (unique per staff+occasion+year), AuditLog. |
| `importer.py` | CSV or Excel (all sheets with a staff id column) -> Staff upsert by `employee_id`. Header names matched via `ALIASES`. Only ACTIVE/ON_LEAVE staff are active. |
| `graph.py` | Microsoft Graph `sendMail`. Mock mode (`MOCK_OUTBOX`) unless all four `GRAPH_*` vars set. |
| `auth.py` | DEV ONLY header auth (`X-Role`). Entra ID login not built yet. |
| `main.py` | FastAPI routes under `/api`, serves the dashboard at `/`. |
| `config.py` | Env settings, milestone years, `ALWAYS_REVIEW` occasions. |
| `seed.py` | Default templates, rules, fake demo staff. |

## Rules that must not break

1. **Never invent facts.** Emails use only fields from the DB. Template placeholders are limited to `ALLOWED_FIELDS` in `personalize.py` (`$name $department $designation $years $duration`); a new one must be added there and filled in `build_context`. Unknown placeholders are rejected on template save and at draft time. `guard()` rejects AI output with unverified numbers or a missing name; keep it strict.
2. **Human approval** for `ALWAYS_REVIEW` occasions (retirement, promotion, silver_jubilee) regardless of rule settings.
3. **No duplicates.** The `Draft` unique constraint (staff, occasion, year) is the backstop. Do not remove it.
4. **Audit everything.** Each state change calls `services.audit`. Do not log full emails or other PII in audit detail; the API masks recipient addresses.
5. **Least privilege.** Graph needs only `Mail.Send` (restricted to the one sender mailbox) and read access to staff. Do not ask for more.
6. **Real staff data never goes in git.** `data/` is gitignored except `sample_staff.csv`. Use fake data in tests and examples. Never commit `.env`.
7. Opted-out or inactive staff get nothing, checked at scan and again at send.

## Conventions

- Python 3.11+, SQLAlchemy 2.0 style, type hints, short docstrings only where the why is not obvious.
- `milestones.py` stays pure (no DB, no `date.today()`): pass `today` in so it is testable.
- Add a test in `backend/tests/test_core.py` for every behaviour change. Tests use in-memory SQLite and the mock outbox, so no Postgres or keys are needed.
- Postgres is the target database; SQLite is for tests and quick local runs only.

## Status and next work

Done: milestone engine, rules, templates, guarded drafting, approval flow, scheduling, audit, duplicate guard, opt-out, analytics API, dashboard, CSV import.

Not done (in rough priority):
1. Entra ID (Azure AD) login to replace header auth in `auth.py`. Set `AUTH_DEV=0` afterwards.
2. `staff_dataset.xlsx` is MOCK data. Its `retirement_date` is a made-up rule (last day of the month of the 60th birthday). With real data, take retirement dates from HR; never compute them in code. After a person's retirement date, `milestones.occasions_for` drops birthdays and anniversaries.
3. Live Graph send test with IT-approved app registration and a test mailbox (never real staff first).
4. Background worker (scan + dispatch on a schedule) instead of manual buttons/CLI.
5. Alembic migrations (tables are created on startup now).
6. Promotion and institutional-event occasions; template/rule edit screens in the dashboard (API exists).

## Keys (`.env`)

`DATABASE_URL`, `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`, `GRAPH_SENDER_MAILBOX`, `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `AUTH_DEV`, `ENTRA_TENANT_ID`, `ENTRA_CLIENT_ID`. Empty Graph vars = mock send. Empty Anthropic key = template-only drafts.
