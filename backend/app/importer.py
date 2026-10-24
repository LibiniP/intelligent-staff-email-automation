"""Load staff from a CSV. Safe to re-run: rows are matched on employee_id and updated."""
import csv
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Staff

# CSV header (lowercased, spaces/dashes -> _) -> field. Add aliases as her columns turn up.
ALIASES = {
    "employee_id": ["employee_id", "emp_id", "empid", "staff_id", "id", "employee_code"],
    "name": ["name", "full_name", "employee_name", "staff_name"],
    "preferred_name": ["preferred_name", "nickname", "known_as"],
    "email": ["email", "e_mail", "email_id", "email_address", "official_email", "mail"],
    "department": ["department", "dept", "school", "school_department"],
    "designation": ["designation", "role", "position", "title"],
    "joining_date": ["joining_date", "date_of_joining", "doj", "join_date", "joined"],
    "birth_date": ["birth_date", "date_of_birth", "dob", "birthday"],
    "retirement_date": ["retirement_date", "date_of_retirement", "dor", "retire_date"],
    "opted_out": ["opted_out", "opt_out", "unsubscribe"],
}
REQUIRED = ["employee_id", "name", "email", "department", "designation", "joining_date"]
DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%d-%b-%Y", "%d %b %Y"]


def norm(h: str) -> str:
    return h.strip().lower().replace(" ", "_").replace("-", "_")


def parse_date(value: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"unreadable date '{value}'")


def parse_bool(value: str) -> bool:
    return (value or "").strip().lower() in {"1", "yes", "y", "true", "t"}


def map_headers(headers: list[str]) -> dict[str, str]:
    """field -> actual CSV header."""
    by_norm = {norm(h): h for h in headers}
    mapping = {}
    for field, names in ALIASES.items():
        for n in names:
            if n in by_norm:
                mapping[field] = by_norm[n]
                break
    return mapping


def import_csv(db: Session, path: str) -> dict:
    """Returns {created, updated, errors: [(line, reason)]}. Bad rows are skipped, not fatal."""
    result = {"created": 0, "updated": 0, "errors": []}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        mapping = map_headers(reader.fieldnames or [])
        missing = [r for r in REQUIRED if r not in mapping]
        if missing:
            raise ValueError(f"CSV is missing columns: {', '.join(missing)}. Found: {reader.fieldnames}")

        for line, row in enumerate(reader, start=2):
            try:
                get = lambda k: (row.get(mapping[k]) or "").strip() if k in mapping else ""
                values = dict(
                    name=get("name"), preferred_name=get("preferred_name") or None, email=get("email"),
                    department=get("department"), designation=get("designation"),
                    joining_date=parse_date(get("joining_date")), birth_date=parse_date(get("birth_date")),
                    retirement_date=parse_date(get("retirement_date")),
                )
                if "opted_out" in mapping:  # absent column must not clear an existing opt-out
                    values["opted_out"] = parse_bool(get("opted_out"))
                eid = get("employee_id")
                if not eid or not values["name"] or "@" not in values["email"] or not values["joining_date"]:
                    raise ValueError("missing employee_id, name, valid email or joining_date")
                staff = db.scalar(select(Staff).where(Staff.employee_id == eid))
                if staff:
                    for k, v in values.items():
                        setattr(staff, k, v)
                    result["updated"] += 1
                else:
                    db.add(Staff(employee_id=eid, **values))
                    result["created"] += 1
            except ValueError as e:
                result["errors"].append((line, str(e)))
    db.commit()
    return result
