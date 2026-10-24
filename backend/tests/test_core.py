from datetime import date, datetime
from types import SimpleNamespace

import pytest
from sqlalchemy.orm import sessionmaker

from app import graph, services
from app.db import Base, make_engine
from app.milestones import occasions_for
from app.models import Draft, Staff
from app.personalize import guard
from app.seed import seed_defaults


def person(joining, birth=None, retire=None):
    return SimpleNamespace(joining_date=joining, birth_date=birth, retirement_date=retire)


@pytest.fixture
def db():
    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)
    s = sessionmaker(bind=engine, expire_on_commit=False)()
    seed_defaults(s)
    graph.MOCK_OUTBOX.clear()
    yield s
    s.close()
    engine.dispose()


def add_staff(db, **kw):
    base = dict(employee_id="E1", name="Test Person", email="t@example.test",
                department="Physics", designation="Lecturer", joining_date=date(2000, 1, 1))
    base.update(kw)
    s = Staff(**base)
    db.add(s)
    db.commit()
    return s


# ---- milestone logic ----
def test_silver_jubilee_at_25_years():
    occ = occasions_for(person(date(2001, 6, 1)), date(2026, 5, 30), 7)
    assert [(o.kind, o.years) for o in occ] == [("silver_jubilee", 25)]


def test_plain_anniversary_and_milestone():
    assert occasions_for(person(date(2020, 6, 1)), date(2026, 6, 1), 0)[0].kind == "joining_anniversary"
    assert occasions_for(person(date(2016, 6, 1)), date(2026, 6, 1), 0)[0].kind == "service_milestone"


def test_no_anniversary_in_joining_year():
    assert occasions_for(person(date(2026, 6, 1)), date(2026, 6, 1), 0) == []


def test_leap_day_birthday_on_feb_28_in_normal_year():
    occ = occasions_for(person(date(2010, 1, 1), birth=date(1980, 2, 29)), date(2027, 2, 27), 3)
    assert occ[0].kind == "birthday" and occ[0].on == date(2027, 2, 28)


def test_window_across_new_year():
    occ = occasions_for(person(date(2010, 6, 1), birth=date(1980, 1, 2)), date(2026, 12, 30), 5)
    assert occ[0].on == date(2027, 1, 2)


# ---- guard ----
def test_guard_blocks_invented_number():
    ctx = {"name": "Asha", "years": "25", "duration": "25 years"}
    assert guard("Dear Asha, 25 years!", ctx) == []
    assert guard("Dear Asha, 30 years!", ctx) != []
    assert guard("Dear Someone, 25 years", ctx) != []
    assert guard("Dear Asha, $department", ctx) != []


# ---- pipeline ----
def test_scan_creates_one_draft_and_no_duplicates(db):
    add_staff(db, joining_date=date(2001, 6, 1))
    today = date(2026, 5, 30)
    assert len(services.scan_and_draft(db, today)) == 1
    assert len(services.scan_and_draft(db, today)) == 0
    d = db.query(Draft).one()
    assert d.occasion == "silver_jubilee" and "25" in d.subject and d.status == "pending"


def test_opted_out_staff_get_nothing(db):
    add_staff(db, joining_date=date(2001, 6, 1), opted_out=True)
    assert services.scan_and_draft(db, date(2026, 5, 30)) == []


def test_birthday_auto_schedules_but_jubilee_needs_approval(db):
    add_staff(db, birth_date=date(1980, 6, 2), joining_date=date(2001, 6, 2))
    services.scan_and_draft(db, date(2026, 6, 1))
    status = {d.occasion: d.status for d in db.query(Draft)}
    assert status["birthday"] == "scheduled"
    assert status["silver_jubilee"] == "pending"


def test_full_flow_approve_then_send(db):
    add_staff(db, joining_date=date(2001, 6, 1))
    services.scan_and_draft(db, date(2026, 5, 30))
    d = db.query(Draft).one()
    services.dispatch_due(db, datetime(2026, 6, 1, 12))
    assert graph.MOCK_OUTBOX == []  # not approved, not sent
    services.approve(db, d.id, "reviewer1")
    assert services.dispatch_due(db, datetime(2026, 5, 31, 12)) == 0  # too early
    assert services.dispatch_due(db, datetime(2026, 6, 1, 9, 1)) == 1
    assert len(graph.MOCK_OUTBOX) == 1 and d.status == "sent"
    assert services.dispatch_due(db, datetime(2026, 6, 2)) == 0  # never twice
    actions = [a.action for a in db.query(services.AuditLog).filter_by(draft_id=d.id)]
    assert actions == ["generated", "approved", "scheduled", "sent"]


def test_reject_and_cancel(db):
    add_staff(db, joining_date=date(2001, 6, 1))
    services.scan_and_draft(db, date(2026, 5, 30))
    d = db.query(Draft).one()
    services.reject(db, d.id, "hr")
    with pytest.raises(ValueError):
        services.approve(db, d.id, "hr")


def test_failed_send_is_recorded(db, monkeypatch):
    add_staff(db, joining_date=date(2001, 6, 1))
    services.scan_and_draft(db, date(2026, 5, 30))
    d = db.query(Draft).one()
    services.approve(db, d.id, "hr")
    monkeypatch.setattr(graph, "send_mail", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    services.dispatch_due(db, datetime(2026, 6, 2))
    assert d.status == "failed" and "boom" in d.error


# ---- CSV import ----
def test_csv_import_aliases_dates_and_bad_rows(db, tmp_path):
    from app.importer import import_csv

    f = tmp_path / "s.csv"
    f.write_text(
        "Emp ID,Full Name,Official Email,Dept,Role,DOJ,DOB\n"
        "A1,Asha M,asha@example.test,Physics,Professor,01/06/2001,14-03-1975\n"
        "A2,No Email,,Physics,Professor,01/06/2001,\n"
        "A3,Bad Date,b@example.test,Physics,Professor,not-a-date,\n",
        encoding="utf-8-sig",
    )
    r = import_csv(db, str(f))
    assert (r["created"], len(r["errors"])) == (1, 2)
    s = db.query(Staff).one()
    assert s.joining_date == date(2001, 6, 1) and s.birth_date == date(1975, 3, 14)
    assert import_csv(db, str(f))["updated"] == 1  # re-run updates, no duplicate


def test_csv_missing_required_column(db, tmp_path):
    from app.importer import import_csv

    f = tmp_path / "s.csv"
    f.write_text("name,email\nA,a@b.c\n")
    with pytest.raises(ValueError, match="missing columns"):
        import_csv(db, str(f))


def test_reimport_without_optout_column_keeps_optout(db, tmp_path):
    from app.importer import import_csv

    add_staff(db, employee_id="A1", opted_out=True)
    f = tmp_path / "s.csv"
    f.write_text("employee_id,name,email,department,designation,joining_date\nA1,T,t@example.test,Physics,Lecturer,2000-01-01\n")
    import_csv(db, str(f))
    assert db.query(Staff).one().opted_out is True


def test_approve_without_rule_row_still_schedules(db):
    from app.models import Rule

    add_staff(db, joining_date=date(2001, 6, 1))
    services.scan_and_draft(db, date(2026, 5, 30))
    d = db.query(Draft).one()
    db.query(Rule).filter_by(occasion="silver_jubilee").delete()
    db.commit()
    services.approve(db, d.id, "hr")
    assert d.status == "scheduled" and d.scheduled_for.hour == 9
