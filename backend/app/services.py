"""Pipeline: scan -> draft -> approve -> schedule -> send. Every step is audited."""
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import config, graph
from .milestones import occasions_for
from .models import AuditLog, Draft, Rule, Staff, Template
from .personalize import draft_email


def local_now() -> datetime:
    return datetime.now(ZoneInfo(config.TIMEZONE)).replace(tzinfo=None)


def today() -> date:
    return local_now().date()


def audit(db: Session, draft_id: int | None, actor: str, action: str, detail: str | None = None) -> None:
    db.add(AuditLog(draft_id=draft_id, actor=actor, action=action, detail=detail))


def scan_and_draft(db: Session, today: date, actor: str = "system") -> list[Draft]:
    """Create drafts for upcoming occasions. Safe to run daily: duplicates are skipped."""
    rules = {r.occasion: r for r in db.scalars(select(Rule)) if r.enabled}
    templates = {t.occasion: t for t in db.scalars(select(Template).where(Template.active)) }
    created: list[Draft] = []

    for staff in db.scalars(select(Staff).where(Staff.active, ~Staff.opted_out)):
        horizon = max((r.days_ahead for r in rules.values()), default=0)
        for occ in occasions_for(staff, today, horizon):
            rule = rules.get(occ.kind)
            tmpl = templates.get(occ.kind)
            if not rule or not tmpl or (occ.on - today).days > rule.days_ahead:
                continue
            exists = db.scalar(
                select(Draft.id).where(
                    Draft.staff_id == staff.id, Draft.occasion == occ.kind, Draft.occasion_year == occ.year
                )
            )
            if exists:
                continue
            subject, body, by = draft_email(tmpl, staff, occ)
            draft = Draft(
                staff_id=staff.id, occasion=occ.kind, occasion_year=occ.year, occasion_date=occ.on,
                subject=subject, body=body, generated_by=by,
            )
            db.add(draft)
            try:
                db.flush()
            except IntegrityError:
                db.rollback()
                continue
            audit(db, draft.id, actor, "generated", f"by={by}")
            created.append(draft)
            if not (rule.requires_approval or occ.kind in config.ALWAYS_REVIEW):
                schedule(db, draft, rule, actor="system:auto")
    db.commit()
    return created


def schedule(db: Session, draft: Draft, rule: Rule, actor: str) -> None:
    draft.status = "scheduled"
    draft.scheduled_for = datetime.combine(draft.occasion_date, time(rule.send_hour))
    audit(db, draft.id, actor, "scheduled", draft.scheduled_for.isoformat())


def approve(db: Session, draft_id: int, actor: str) -> Draft:
    draft = _get_pending(db, draft_id)
    rule = db.scalar(select(Rule).where(Rule.occasion == draft.occasion))
    audit(db, draft.id, actor, "approved")
    schedule(db, draft, rule or Rule(occasion=draft.occasion, send_hour=9), actor)
    db.commit()
    return draft


def reject(db: Session, draft_id: int, actor: str, reason: str = "") -> Draft:
    draft = _get_pending(db, draft_id)
    draft.status = "rejected"
    audit(db, draft.id, actor, "rejected", reason)
    db.commit()
    return draft


def edit(db: Session, draft_id: int, actor: str, subject: str, body: str) -> Draft:
    draft = _get_pending(db, draft_id)
    draft.subject, draft.body = subject, body
    audit(db, draft.id, actor, "edited")
    db.commit()
    return draft


def cancel(db: Session, draft_id: int, actor: str) -> Draft:
    draft = db.get(Draft, draft_id)
    if not draft or draft.status not in ("pending", "approved", "scheduled"):
        raise ValueError("draft cannot be cancelled")
    draft.status = "cancelled"
    audit(db, draft.id, actor, "cancelled")
    db.commit()
    return draft


def _get_pending(db: Session, draft_id: int) -> Draft:
    draft = db.get(Draft, draft_id)
    if not draft or draft.status != "pending":
        raise ValueError("draft not pending")
    return draft


def dispatch_due(db: Session, now: datetime | None = None) -> int:
    """Send every scheduled draft whose time has come. Returns how many were sent."""
    now = now or local_now()
    sent = 0
    due = db.scalars(select(Draft).where(Draft.status == "scheduled", Draft.scheduled_for <= now)).all()
    for draft in due:
        staff = db.get(Staff, draft.staff_id)
        rule = db.scalar(select(Rule).where(Rule.occasion == draft.occasion))
        cc = [c.strip() for c in rule.cc.split(",")] if rule and rule.cc else None
        if staff.opted_out or not staff.active:
            draft.status = "cancelled"
            audit(db, draft.id, "system", "cancelled", "recipient opted out or inactive")
            continue
        try:
            graph.send_mail(staff.email, draft.subject, draft.body, cc)
            draft.status, draft.sent_at = "sent", now
            audit(db, draft.id, "system", "sent")
            sent += 1
        except Exception as exc:
            draft.status, draft.error = "failed", str(exc)[:500]
            audit(db, draft.id, "system", "failed", str(exc)[:200])
    db.commit()
    return sent
