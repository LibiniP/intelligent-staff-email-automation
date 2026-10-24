"""Pure milestone detection. No DB, no clock: caller passes `today`."""
from dataclasses import dataclass
from datetime import date, timedelta

from . import config


@dataclass(frozen=True)
class Occasion:
    kind: str  # birthday, joining_anniversary, service_milestone, silver_jubilee, retirement
    on: date   # the day it falls
    year: int  # calendar year of `on`, used for duplicate key
    years: int | None = None  # age-free: years of service where relevant


def safe_date(year: int, month: int, day: int) -> date:
    """Feb 29 falls on Feb 28 in non-leap years."""
    try:
        return date(year, month, day)
    except ValueError:
        return date(year, 2, 28)


def years_of_service(joining: date, on: date) -> int:
    return on.year - joining.year


def service_duration_text(joining: date, on: date) -> str:
    years = years_of_service(joining, on)
    return f"{years} year" + ("" if years == 1 else "s")


def occasions_for(staff, today: date, days_ahead: int) -> list[Occasion]:
    """Occasions for one staff member falling in [today, today + days_ahead]."""
    end = today + timedelta(days=days_ahead)
    found: list[Occasion] = []

    def in_window(d: date) -> bool:
        return today <= d <= end

    # a window can span New Year, so test this year and next
    for year in {today.year, end.year}:
        if staff.birth_date:
            d = safe_date(year, staff.birth_date.month, staff.birth_date.day)
            if in_window(d):
                found.append(Occasion("birthday", d, year))

        j = staff.joining_date
        d = safe_date(year, j.month, j.day)
        n = years_of_service(j, d)
        if in_window(d) and n >= 1:
            if n == config.SILVER_JUBILEE_YEARS:
                found.append(Occasion("silver_jubilee", d, year, n))
            elif n in config.MILESTONE_YEARS:
                found.append(Occasion("service_milestone", d, year, n))
            else:
                found.append(Occasion("joining_anniversary", d, year, n))

    r = staff.retirement_date
    if r:
        # after the retirement date nobody gets birthday/anniversary mail, even if the status is stale
        found = [o for o in found if o.on <= r]
        if in_window(r):
            found.append(Occasion("retirement", r, r.year, years_of_service(staff.joining_date, r)))

    return sorted(found, key=lambda o: (o.on, o.kind))
