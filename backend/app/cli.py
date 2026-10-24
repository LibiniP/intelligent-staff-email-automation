"""python -m app.cli <init-db | import-csv FILE | scan | dispatch>"""
import sys

from . import services
from .db import Base, SessionLocal, engine
from .importer import import_csv
from .seed import seed_defaults


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in {"init-db", "import-csv", "scan", "dispatch"}:
        print(__doc__)
        return 1
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_defaults(db)
        cmd = argv[0]
        if cmd == "init-db":
            print("tables ready, default templates and rules loaded")
        elif cmd == "import-csv":
            if len(argv) < 2:
                print("usage: import-csv FILE")
                return 1
            r = import_csv(db, argv[1])
            print(f"created {r['created']}, updated {r['updated']}, skipped {len(r['errors'])}")
            for line, why in r["errors"]:
                print(f"  line {line}: {why}")
        elif cmd == "scan":
            print(f"{len(services.scan_and_draft(db, services.today(), 'cli'))} new draft(s)")
        elif cmd == "dispatch":
            print(f"{services.dispatch_due(db)} sent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
