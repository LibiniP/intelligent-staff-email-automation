"""Default templates, rules and FAKE staff for development. Never real data."""
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Rule, Staff, Template

TEMPLATES = {
    "birthday": (
        "Happy Birthday, $name!",
        "Dear $name,\n\nWishing you a very happy birthday! Thank you for everything you "
        "bring to the $department community as $designation.\n\nWarm regards,\nAmrita Administration",
    ),
    "joining_anniversary": (
        "Celebrating your journey with Amrita, $name",
        "Dear $name,\n\nToday marks $duration since you joined us in $department. Thank you for "
        "your continued contribution as $designation.\n\nWarm regards,\nAmrita Administration",
    ),
    "service_milestone": (
        "Congratulations on $years years of service, $name",
        "Dear $name,\n\nCongratulations on completing $years years of service with Amrita. Your "
        "work as $designation in $department is deeply valued.\n\nWith appreciation,\nAmrita Administration",
    ),
    "silver_jubilee": (
        "Silver Jubilee: $years years with Amrita, $name",
        "Dear $name,\n\nOn behalf of the institution, we congratulate you on your Silver Jubilee: "
        "$years years of dedicated service. Your role as $designation in $department has been "
        "a cornerstone of our community.\n\nWith sincere gratitude,\nAmrita Administration",
    ),
    "retirement": (
        "With gratitude, $name",
        "Dear $name,\n\nAs you retire after $years years of service, we thank you for your "
        "contributions as $designation in $department. We wish you the very best ahead.\n\n"
        "With respect and gratitude,\nAmrita Administration",
    ),
}

RULES = {
    "birthday": dict(days_ahead=3, requires_approval=False, send_hour=8),
    "joining_anniversary": dict(days_ahead=5, requires_approval=True, send_hour=9),
    "service_milestone": dict(days_ahead=7, requires_approval=True, send_hour=9),
    "silver_jubilee": dict(days_ahead=14, requires_approval=True, send_hour=9),
    "retirement": dict(days_ahead=14, requires_approval=True, send_hour=9),
}

DEMO_STAFF = [
    ("E001", "Asha Menon", None, "asha.menon@example.test", "Computer Science", "Professor", date(2001, 6, 1), date(1975, 3, 14)),
    ("E002", "Ravi Nair", "Ravi", "ravi.nair@example.test", "Administration", "Office Manager", date(2016, 7, 10), date(1988, 11, 2)),
    ("E003", "Meera Pillai", None, "meera.pillai@example.test", "Physics", "Associate Professor", date(2015, 1, 20), date(1980, 2, 29)),
]


def seed_defaults(db: Session) -> None:
    if not db.scalar(select(Template.id)):
        for occ, (subj, body) in TEMPLATES.items():
            db.add(Template(occasion=occ, subject=subj, body=body))
    if not db.scalar(select(Rule.id)):
        for occ, kw in RULES.items():
            db.add(Rule(occasion=occ, **kw))
    db.commit()


def seed_demo_staff(db: Session) -> None:
    if db.scalar(select(Staff.id)):
        return
    for eid, name, pref, email, dept, desig, join, dob in DEMO_STAFF:
        db.add(Staff(employee_id=eid, name=name, preferred_name=pref, email=email,
                     department=dept, designation=desig, joining_date=join, birth_date=dob))
    db.commit()
