from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import services
from .auth import User, require
from .db import Base, SessionLocal, engine, get_db
from .milestones import occasions_for
from .personalize import check_template
from .models import AuditLog, Draft, Rule, Staff, Template
from .seed import seed_defaults, seed_demo_staff

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_defaults(db)
    yield


app = FastAPI(title="Staff Email Automation", lifespan=lifespan)
FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "src" / "index.html"


def mask(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}"


def draft_out(d: Draft, staff: Staff) -> dict:
    return {
        "id": d.id, "staff": staff.preferred_name or staff.name, "department": staff.department,
        "to": mask(staff.email), "occasion": d.occasion, "occasion_date": d.occasion_date.isoformat(),
        "subject": d.subject, "body": d.body, "status": d.status, "generated_by": d.generated_by,
        "scheduled_for": d.scheduled_for.isoformat() if d.scheduled_for else None, "error": d.error,
    }


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(FRONTEND)


# ---- drafts / approval ----
@app.get("/api/drafts")
def list_drafts(status: str | None = None, db: Session = Depends(get_db),
                _: User = Depends(require("hr", "reviewer", "coordinator"))):
    q = select(Draft, Staff).join(Staff, Staff.id == Draft.staff_id).order_by(Draft.occasion_date)
    if status:
        q = q.where(Draft.status == status)
    return [draft_out(d, s) for d, s in db.execute(q)]


class EditBody(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1)


def _act(fn, *args):
    try:
        return fn(*args)
    except ValueError as e:
        raise HTTPException(409, str(e))


@app.post("/api/drafts/{draft_id}/approve")
def approve(draft_id: int, db: Session = Depends(get_db), u: User = Depends(require("hr", "reviewer"))):
    d = _act(services.approve, db, draft_id, u.name)
    return draft_out(d, db.get(Staff, d.staff_id))


@app.post("/api/drafts/{draft_id}/reject")
def reject(draft_id: int, db: Session = Depends(get_db), u: User = Depends(require("hr", "reviewer"))):
    d = _act(services.reject, db, draft_id, u.name)
    return draft_out(d, db.get(Staff, d.staff_id))


@app.post("/api/drafts/{draft_id}/edit")
def edit(draft_id: int, body: EditBody, db: Session = Depends(get_db), u: User = Depends(require("hr", "reviewer"))):
    d = _act(services.edit, db, draft_id, u.name, body.subject, body.body)
    return draft_out(d, db.get(Staff, d.staff_id))


@app.post("/api/drafts/{draft_id}/cancel")
def cancel(draft_id: int, db: Session = Depends(get_db), u: User = Depends(require("hr", "reviewer"))):
    d = _act(services.cancel, db, draft_id, u.name)
    return draft_out(d, db.get(Staff, d.staff_id))


# ---- jobs ----
@app.post("/api/jobs/scan")
def scan(db: Session = Depends(get_db), u: User = Depends(require("hr"))):
    return {"created": len(services.scan_and_draft(db, services.today(), u.name))}


@app.post("/api/jobs/dispatch")
def dispatch(db: Session = Depends(get_db), _: User = Depends(require("hr"))):
    return {"sent": services.dispatch_due(db)}


# ---- upcoming, rules, templates, audit, analytics ----
@app.get("/api/upcoming")
def upcoming(days: int = Query(30, ge=0, le=365), db: Session = Depends(get_db), _: User = Depends(require("hr", "reviewer", "coordinator"))):
    out = []
    for s in db.scalars(select(Staff).where(Staff.active)):
        for o in occasions_for(s, services.today(), days):
            out.append({"staff": s.preferred_name or s.name, "department": s.department,
                        "occasion": o.kind, "date": o.on.isoformat(), "years": o.years})
    return sorted(out, key=lambda x: x["date"])


@app.get("/api/rules")
def rules(db: Session = Depends(get_db), _: User = Depends(require("hr"))):
    return [{c.name: getattr(r, c.name) for c in Rule.__table__.columns} for r in db.scalars(select(Rule))]


class RuleBody(BaseModel):
    enabled: bool
    days_ahead: int = Field(ge=0, le=365)
    requires_approval: bool
    send_hour: int = Field(ge=0, le=23)


@app.put("/api/rules/{occasion}")
def update_rule(occasion: str, body: RuleBody, db: Session = Depends(get_db), u: User = Depends(require("hr"))):
    r = db.scalar(select(Rule).where(Rule.occasion == occasion))
    if not r:
        raise HTTPException(404, "no such rule")
    for k, v in body.model_dump().items():
        setattr(r, k, v)
    services.audit(db, None, u.name, "rule_updated", occasion)
    db.commit()
    return {"ok": True}


@app.get("/api/templates")
def templates(db: Session = Depends(get_db), _: User = Depends(require("hr"))):
    return [{c.name: getattr(t, c.name) for c in Template.__table__.columns} for t in db.scalars(select(Template))]


class TemplateBody(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1)


@app.put("/api/templates/{template_id}")
def update_template(template_id: int, body: TemplateBody, db: Session = Depends(get_db), u: User = Depends(require("hr"))):
    t = db.get(Template, template_id)
    if not t:
        raise HTTPException(404, "no such template")
    bad = check_template(body.subject, body.body)
    if bad:
        raise HTTPException(422, f"unknown placeholder(s): {', '.join(bad)}. Allowed: name, department, designation, years, duration")
    t.subject, t.body, t.version = body.subject, body.body, t.version + 1
    services.audit(db, None, u.name, "template_updated", f"{t.occasion} v{t.version}")
    db.commit()
    return {"ok": True, "version": t.version}


@app.get("/api/audit")
def audit_log(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db), _: User = Depends(require("hr"))):
    rows = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit))
    return [{"draft_id": a.draft_id, "actor": a.actor, "action": a.action, "detail": a.detail,
             "at": a.at.isoformat()} for a in rows]


@app.get("/api/analytics")
def analytics(db: Session = Depends(get_db), _: User = Depends(require("hr", "reviewer", "coordinator"))):
    by_status = dict(db.execute(select(Draft.status, func.count()).group_by(Draft.status)).all())
    by_occasion = dict(db.execute(select(Draft.occasion, func.count()).group_by(Draft.occasion)).all())
    return {"by_status": by_status, "by_occasion": by_occasion}


# ---- dev helper ----
@app.post("/api/dev/seed-demo")
def seed_demo(db: Session = Depends(get_db), _: User = Depends(require("admin"))):
    seed_demo_staff(db)
    return {"ok": True}
