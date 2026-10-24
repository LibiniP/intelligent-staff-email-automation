# Graph Report - intelligent-staff-email-automation  (2026-10-24)

## Corpus Check
- 18 files · ~5,809 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .example 1, .csv 1)

## Summary
- 184 nodes · 488 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 71 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ceb9eb37`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_core.py
- main.py
- models.py
- services.py
- graph.py
- importer.py
- Intelligent Staff Email Personalization & Automation System
- today

## God Nodes (most connected - your core abstractions)
1. `Draft` - 23 edges
2. `scan_and_draft()` - 22 edges
3. `Staff` - 21 edges
4. `User` - 19 edges
5. `occasions_for()` - 17 edges
6. `dispatch_due()` - 15 edges
7. `Base` - 14 edges
8. `Rule` - 14 edges
9. `import_csv()` - 13 edges
10. `audit()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Load the staff data` --references--> `dispatch()`  [INFERRED]
  README.md → backend/app/main.py
- `Rules that must not break` --references--> `Draft`  [INFERRED]
  CLAUDE.md → backend/app/models.py
- `Code map (`backend/app/`)` --references--> `AuditLog`  [INFERRED]
  CLAUDE.md → backend/app/models.py
- `Code map (`backend/app/`)` --references--> `guard()`  [INFERRED]
  CLAUDE.md → backend/app/personalize.py
- `Conventions` --references--> `today()`  [INFERRED]
  CLAUDE.md → backend/app/services.py

## Import Cycles
- None detected.

## Communities (10 total, 2 thin omitted)

### Community 0 - "test_core.py"
Cohesion: 0.10
Nodes (18): Occasion, occasions_for(), safe_date(), service_duration_text(), years_of_service(), build_context(), draft_email(), guard() (+10 more)

### Community 1 - "main.py"
Cohesion: 0.17
Nodes (25): User, _act(), analytics(), approve(), audit_log(), cancel(), dashboard(), dispatch() (+17 more)

### Community 2 - "models.py"
Cohesion: 0.16
Nodes (10): main(), Base, get_db(), make_engine(), lifespan(), AuditLog, Template, utcnow() (+2 more)

### Community 3 - "services.py"
Cohesion: 0.22
Nodes (20): Draft, Rule, approve(), audit(), cancel(), dispatch_due(), edit(), _get_pending() (+12 more)

### Community 4 - "graph.py"
Cohesion: 0.14
Nodes (5): current_user(), require(), is_live(), send_mail(), _token()

### Community 5 - "importer.py"
Cohesion: 0.17
Nodes (8): import_csv(), map_headers(), norm(), parse_bool(), parse_date(), test_csv_import_aliases_dates_and_bad_rows(), test_csv_missing_required_column(), test_reimport_without_optout_column_keeps_optout()

### Community 6 - "Intelligent Staff Email Personalization & Automation System"
Cohesion: 0.12
Nodes (15): AI, API key slots (`.env`), Backend, Database, DevOps, Frontend, Intelligent Staff Email Personalization & Automation System, Load the staff data (+7 more)

### Community 7 - "today"
Cohesion: 0.22
Nodes (7): today(), Code map (`backend/app/`), Conventions, Keys (`.env`), Run, Start here, Status and next work

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dispatch()` connect `main.py` to `services.py`, `Intelligent Staff Email Personalization & Automation System`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Draft` (e.g. with `analytics()` and `draft_out()`) actually correct?**
  _`Draft` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_core.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1036036036036036 - nodes in this community are weakly interconnected._
- **Why does `Load the staff data` connect `Intelligent Staff Email Personalization & Automation System` to `main.py`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `scan_and_draft()` (e.g. with `Rule` and `Staff`) actually correct?**
  _`scan_and_draft()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `graph.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13970588235294118 - nodes in this community are weakly interconnected._
- **Are the 11 inferred relationships involving `Staff` (e.g. with `approve()` and `cancel()`) actually correct?**
  _`Staff` has 11 INFERRED edges - model-reasoned connections that need verification._