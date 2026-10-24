from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from . import config


class Base(DeclarativeBase):
    pass


def make_engine(url: str = config.DATABASE_URL):
    kwargs = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
    return create_engine(url, **kwargs)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def ensure_columns(eng=None) -> None:
    """Add nullable columns the models have but an older database lacks (no Alembic yet)."""
    from sqlalchemy import inspect, text

    eng = eng or engine
    insp = inspect(eng)
    for table in Base.metadata.sorted_tables:
        if not insp.has_table(table.name):
            continue
        have = {c["name"] for c in insp.get_columns(table.name)}
        for col in table.columns:
            if col.name not in have:
                if not col.nullable:
                    raise RuntimeError(f"{table.name}.{col.name} is missing and not nullable: migrate by hand")
                ddl = col.type.compile(dialect=eng.dialect)
                with eng.begin() as conn:
                    conn.execute(text(f'ALTER TABLE {table.name} ADD COLUMN {col.name} {ddl}'))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
