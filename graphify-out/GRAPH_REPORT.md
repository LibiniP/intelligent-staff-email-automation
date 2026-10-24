# Graph Report - intelligent-staff-email-automation  (2026-10-24)

## Corpus Check
- 18 files · ~15,186 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 2, .example 1, .csv 1)

## Summary
- 197 nodes · 528 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 82 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8a869c7b`
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
1. `Draft` - 26 edges
2. `scan_and_draft()` - 26 edges
3. `Staff` - 21 edges
4. `User` - 19 edges
5. `occasions_for()` - 17 edges
6. `dispatch_due()` - 16 edges
7. `Base` - 14 edges
8. `Rule` - 14 edges
9. `import_csv()` - 13 edges
10. `audit()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Load the staff data` --references--> `dispatch()`  [INFERRED]
  README.md → backend/app/main.py
- `Rules that must not break` --references--> `Draft`  [INFERRED]
  CLAUDE.md → backend/app/models.py
- `Code map (`backend/app/`)` --references--> `guard()`  [INFERRED]
  CLAUDE.md → backend/app/personalize.py
- `Code map (`backend/app/`)` --references--> `today()`  [INFERRED]
  CLAUDE.md → backend/app/services.py
- `Conventions` --references--> `today()`  [INFERRED]
  CLAUDE.md → backend/app/services.py

## Import Cycles
- None detected.

## Communities (10 total, 2 thin omitted)

### Community 0 - "test_core.py"
Cohesion: 0.09
Nodes (19): Occasion, occasions_for(), safe_date(), service_duration_text(), years_of_service(), build_context(), draft_email(), guard() (+11 more)

### Community 1 - "main.py"
Cohesion: 0.13
Nodes (28): current_user(), require(), User, _act(), analytics(), approve(), audit_log(), cancel() (+20 more)

### Community 2 - "models.py"
Cohesion: 0.16
Nodes (9): main(), Base, get_db(), make_engine(), lifespan(), Template, seed_defaults(), db() (+1 more)

### Community 3 - "services.py"
Cohesion: 0.17
Nodes (25): AuditLog, Draft, Rule, approve(), audit(), cancel(), dispatch_due(), edit() (+17 more)

### Community 4 - "graph.py"
Cohesion: 0.24
Nodes (3): is_live(), send_mail(), _token()

### Community 5 - "importer.py"
Cohesion: 0.19
Nodes (7): import_csv(), map_headers(), norm(), parse_bool(), parse_date(), test_csv_import_aliases_dates_and_bad_rows(), test_csv_missing_required_column()

### Community 6 - "Intelligent Staff Email Personalization & Automation System"
Cohesion: 0.12
Nodes (16): AI, API key slots (`.env`), Backend, Database, DevOps, Frontend, Intelligent Staff Email Personalization & Automation System, Load the staff data (+8 more)

### Community 7 - "today"
Cohesion: 0.17
Nodes (7): local_now(), today(), Conventions, Keys (`.env`), Run, Start here, Status and next work

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dispatch()` connect `main.py` to `services.py`, `Intelligent Staff Email Personalization & Automation System`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Draft` (e.g. with `analytics()` and `draft_out()`) actually correct?**
  _`Draft` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_core.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09206349206349207 - nodes in this community are weakly interconnected._
- **Why does `Load the staff data` connect `Intelligent Staff Email Personalization & Automation System` to `main.py`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `scan_and_draft()` (e.g. with `Rule` and `Staff`) actually correct?**
  _`scan_and_draft()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12513842746400886 - nodes in this community are weakly interconnected._
- **Are the 11 inferred relationships involving `Staff` (e.g. with `approve()` and `cancel()`) actually correct?**
  _`Staff` has 11 INFERRED edges - model-reasoned connections that need verification._