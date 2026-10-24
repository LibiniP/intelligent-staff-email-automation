from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from . import config
from .db import Base


def local_now() -> datetime:
    """Naive local time in config.TIMEZONE. All stored timestamps use this, so they line up."""
    return datetime.now(ZoneInfo(config.TIMEZONE)).replace(tzinfo=None)


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    preferred_name: Mapped[str | None] = mapped_column(String(120), default=None)
    title: Mapped[str | None] = mapped_column(String(20), default=None)  # Dr., Prof., Mr., Ms.
    category: Mapped[str | None] = mapped_column(String(30), default=None)  # FACULTY, NON_TEACHING, ADMIN
    employment_status: Mapped[str | None] = mapped_column(String(20), default=None)
    email: Mapped[str] = mapped_column(String(200))
    department: Mapped[str] = mapped_column(String(120))
    designation: Mapped[str] = mapped_column(String(120))
    joining_date: Mapped[date] = mapped_column(Date)
    birth_date: Mapped[date | None] = mapped_column(Date, default=None)
    retirement_date: Mapped[date | None] = mapped_column(Date, default=None)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    opted_out: Mapped[bool] = mapped_column(Boolean, default=False)


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    occasion: Mapped[str] = mapped_column(String(40))
    tone: Mapped[str] = mapped_column(String(20), default="warm")
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    occasion: Mapped[str] = mapped_column(String(40), unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    days_ahead: Mapped[int] = mapped_column(Integer, default=7)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    send_hour: Mapped[int] = mapped_column(Integer, default=9)
    cc: Mapped[str | None] = mapped_column(String(400), default=None)


class Draft(Base):
    __tablename__ = "drafts"
    __table_args__ = (UniqueConstraint("staff_id", "occasion", "occasion_year", name="uq_one_per_occasion"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.id"))
    occasion: Mapped[str] = mapped_column(String(40))
    occasion_year: Mapped[int] = mapped_column(Integer)
    occasion_date: Mapped[date] = mapped_column(Date)
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    # pending, approved, rejected, scheduled, sent, failed, cancelled
    status: Mapped[str] = mapped_column(String(20), default="pending")
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    generated_by: Mapped[str] = mapped_column(String(20), default="template")
    error: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=local_now)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int | None] = mapped_column(ForeignKey("drafts.id"), default=None)
    actor: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(40))
    detail: Mapped[str | None] = mapped_column(Text, default=None)
    at: Mapped[datetime] = mapped_column(DateTime, default=local_now)
