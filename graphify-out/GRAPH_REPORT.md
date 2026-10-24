# Graph Report - intelligent-staff-email-automation  (2026-10-24)

## Corpus Check
- 18 files · ~16,157 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 2, .example 1, .csv 1)

## Summary
- 207 nodes · 559 edges · 11 communities (9 shown, 2 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 89 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `60a157d8`
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
- test_core.py

## God Nodes (most connected - your core abstractions)
1. `Draft` - 28 edges
2. `scan_and_draft()` - 28 edges
3. `Staff` - 24 edges
4. `User` - 19 edges
5. `occasions_for()` - 19 edges
6. `dispatch_due()` - 16 edges
7. `import_file()` - 15 edges
8. `Base` - 14 edges
9. `Rule` - 14 edges
10. `add_staff()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Load the staff data` --references--> `dispatch()`  [INFERRED]
  README.md → backend/app/main.py
- `Status and next work` --references--> `occasions_for()`  [INFERRED]
  CLAUDE.md → backend/app/milestones.py
- `Rules that must not break` --references--> `Draft`  [INFERRED]
  CLAUDE.md → backend/app/models.py
- `Rules that must not break` --references--> `build_context()`  [INFERRED]
  CLAUDE.md → backend/app/personalize.py
- `Conventions` --references--> `today()`  [INFERRED]
  CLAUDE.md → backend/app/services.py

## Import Cycles
- None detected.

## Communities (11 total, 2 thin omitted)

### Community 0 - "test_core.py"
Cohesion: 0.12
Nodes (9): Occasion, safe_date(), service_duration_text(), years_of_service(), build_context(), draft_email(), _llm_polish(), render() (+1 more)

### Community 1 - "main.py"
Cohesion: 0.12
Nodes (28): current_user(), require(), User, _act(), analytics(), approve(), audit_log(), cancel() (+20 more)

### Community 2 - "models.py"
Cohesion: 0.12
Nodes (12): main(), Base, ensure_columns(), get_db(), make_engine(), lifespan(), local_now(), Template (+4 more)

### Community 3 - "services.py"
Cohesion: 0.19
Nodes (24): Draft, Rule, approve(), audit(), cancel(), dispatch_due(), edit(), _get_pending() (+16 more)

### Community 4 - "graph.py"
Cohesion: 0.43
Nodes (3): is_live(), send_mail(), _token()

### Community 5 - "importer.py"
Cohesion: 0.17
Nodes (9): import_file(), map_headers(), norm(), parse_bool(), parse_date(), _read_csv(), _read_xlsx(), _text() (+1 more)

### Community 6 - "Intelligent Staff Email Personalization & Automation System"
Cohesion: 0.12
Nodes (16): AI, API key slots (`.env`), Backend, Database, DevOps, Frontend, Intelligent Staff Email Personalization & Automation System, Load the staff data (+8 more)

### Community 7 - "today"
Cohesion: 0.14
Nodes (11): AuditLog, guard(), today(), test_guard_blocks_invented_number(), Code map (`backend/app/`), Conventions, Keys (`.env`), Rules that must not break (+3 more)

### Community 10 - "test_core.py"
Cohesion: 0.23
Nodes (10): occasions_for(), person(), test_csv_import_aliases_dates_and_bad_rows(), test_leap_day_birthday_on_feb_28_in_normal_year(), test_no_anniversary_in_joining_year(), test_nothing_after_retirement_date_but_retirement_itself_is_found(), test_plain_anniversary_and_milestone(), test_reimport_without_optout_column_keeps_optout() (+2 more)

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dispatch()` connect `main.py` to `services.py`, `Intelligent Staff Email Personalization & Automation System`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `Draft` (e.g. with `analytics()` and `draft_out()`) actually correct?**
  _`Draft` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_core.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12169312169312169 - nodes in this community are weakly interconnected._
- **Why does `Load the staff data` connect `Intelligent Staff Email Personalization & Automation System` to `main.py`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `scan_and_draft()` (e.g. with `Rule` and `Staff`) actually correct?**
  _`scan_and_draft()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12050739957716702 - nodes in this community are weakly interconnected._
- **Are the 14 inferred relationships involving `Staff` (e.g. with `approve()` and `cancel()`) actually correct?**
  _`Staff` has 14 INFERRED edges - model-reasoned connections that need verification._