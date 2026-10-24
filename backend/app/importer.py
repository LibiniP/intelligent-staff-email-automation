"""Load staff from a CSV or Excel file. Safe to re-run: rows are matched on employee_id and updated.

Excel: every sheet that has an employee id column is read (e.g. FACULTY / NON_TEACHING / ADMIN);
other sheets (README etc.) are skipped.
"""
import csv
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Staff

# header (lowercased, spaces/dashes -> _) -> field. Add aliases as new columns turn up.
ALIASES = {
    "employee_id": ["employee_id", "staff_id", "emp_id", "empid", "id", "employee_code"],
    "name": ["name", "full_name", "employee_name", "staff_name"],
    "first_name": ["first_name", "firstname", "given_name"],
    "last_name": ["last_name", "lastname", "surname", "family_name"],
    "title": ["title", "salutation", "prefix"],
    "preferred_name": ["preferred_name", "nickname", "known_as"],
    "category": ["category", "staff_category", "staff_type", "type"],
    "email": ["email", "e_mail", "email_id", "email_address", "official_email", "mail"],
    "department": ["department", "dept", "school", "school_department"],
    "designation": ["designation", "role", "position"],
    "joining_date": ["joining_date", "date_of_joining", "doj", "join_date", "joined"],
    "birth_date": ["birth_date", "date_of_birth", "dob", "birthday"],
    "retirement_date": ["retirement_date", "date_of_retirement", "dor", "retire_date"],
    "employment_status": ["employment_status", "status", "staff_status"],
    "opted_out": ["opted_out", "opt_out", "unsubscribe"],
}
REQUIRED = ["employee_id", "email", "department", "designation", "joining_date"]
DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%d-%b-%Y", "%d %b %Y"]
# Statuses that still get emails. RETIRED / RESIGNED / anything else do not.
ACTIVE_STATUSES = {"ACTIVE", "ON_LEAVE"}


def norm(h) -> str:
    return str(h or "").strip().lower().replace(" ", "_").replace("-", "_")


def _text(value) -> str:
    if isinstance(value, float) and value.is_integer():
        value = int(value)  # Excel stores 10051 as 10051.0
    return str(value if value is not None else "").strip()


def parse_date(value) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    value = str(value or "").strip()
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"unreadable date '{value}'")


def parse_bool(value) -> bool:
    return str(value or "").strip().lower() in {"1", "yes", "y", "true", "t"}


def map_headers(headers: list) -> dict[str, str]:
    """field -> actual header text."""
    by_norm = {norm(h): h for h in headers if h is not None}
    mapping = {}
    for field, names in ALIASES.items():
        for n in names:
            if n in by_norm:
                mapping[field] = by_norm[n]
                break
    return mapping


def _read_csv(path: str):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        yield "csv", reader.fieldnames or [], ((i, row) for i, row in enumerate(reader, start=2))


def _read_xlsx(path: str):
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for ws in wb:
        rows = ws.iter_rows(values_only=True)
        headers = list(next(rows, ()))
        yield ws.title, headers, ((i, dict(zip(headers, r))) for i, r in enumerate(rows, start=2))


def import_file(db: Session, path: str) -> dict:
    """Returns {created, updated, errors: [(where, reason)]}. Bad rows are skipped, not fatal."""
    result = {"created": 0, "updated": 0, "errors": []}
    sources = _read_xlsx(path) if Path(path).suffix.lower() in {".xlsx", ".xlsm"} else _read_csv(path)
    is_excel = Path(path).suffix.lower() in {".xlsx", ".xlsm"}
    read_any = False

    for sheet, headers, rows in sources:
        mapping = map_headers(headers)
        if is_excel and "employee_id" not in mapping:
            continue  # README or notes sheet
        has_name = "name" in mapping or ("first_name" in mapping and "last_name" in mapping)
        missing = [r for r in REQUIRED if r not in mapping] + ([] if has_name else ["name (or first_name + last_name)"])
        if missing:
            db.rollback()  # nothing from earlier sheets is kept when a later sheet is unusable
            raise ValueError(f"'{sheet}' is missing columns: {', '.join(missing)}. Found: {headers}")
        read_any = True

        for line, row in rows:
            where = f"{sheet} row {line}"
            try:
                get = lambda k: _text(row.get(mapping[k])) if k in mapping else ""
                name = get("name") or f"{get('first_name')} {get('last_name')}".strip()
                values = dict(
                    name=name, preferred_name=get("preferred_name") or None, title=get("title") or None,
                    category=get("category") or None, email=get("email"),
                    department=get("department"), designation=get("designation"),
                    joining_date=parse_date(row.get(mapping["joining_date"])),
                    birth_date=parse_date(row.get(mapping["birth_date"])) if "birth_date" in mapping else None,
                    retirement_date=parse_date(row.get(mapping["retirement_date"])) if "retirement_date" in mapping else None,
                )
                if "employment_status" in mapping:
                    status = get("employment_status").upper()
                    values["employment_status"] = status or None
                    values["active"] = status in ACTIVE_STATUSES
                if "opted_out" in mapping:  # absent column must not clear an existing opt-out
                    values["opted_out"] = parse_bool(row.get(mapping["opted_out"]))
                eid = get("employee_id")
                if not eid or not name or "@" not in values["email"] or not values["joining_date"]:
                    raise ValueError("missing employee_id, name, valid email or joining_date")
                staff = db.scalar(select(Staff).where(Staff.employee_id == eid))
                if staff:
                    for k, v in values.items():
                        setattr(staff, k, v)
                    result["updated"] += 1
                else:
                    db.add(Staff(employee_id=eid, **values))
                    db.flush()
                    result["created"] += 1
            except ValueError as e:
                result["errors"].append((where, str(e)))
    if not read_any:
        db.rollback()
        raise ValueError("no sheet or file with an employee id column was found")
    db.commit()
    return result


import_csv = import_file  # old name
