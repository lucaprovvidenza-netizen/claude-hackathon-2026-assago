# CLAUDE.md — Brennero Logistics Modernization

## Project Context
Claude Code Hackathon 2026 — Assago.
Scenario 1 — "The Monolith" (Code Modernization).
App: **Brennero Logistics S.p.A.** — internal order portal, Java 8, built in 2015.
Team of 3.

## What We Are Building
Modernizing the Brennero Logistics order portal from Java 8 / Servlet / H2 in-memory
toward Python 3.12 + FastAPI + SQLite persistent, adding new features across
orders, customers, reporting, and data integrity.

## Stack

### Legacy (Java — `monolith/`)
- Language: Java 8 (pure Servlet, embedded Tomcat via pom.xml)
- Frontend: 6 JSP pages + JSTL 1.2, vanilla CSS, zero JavaScript
- Routing: `PortalServlet.java` — God Servlet, all actions via `?action=` dispatch
- DB: H2 in-memory (`jdbc:h2:mem:brennero`), schema from `schema.sql` + `data.sql`
- Known anomalies: SQL injection, plaintext passwords, God class, circular dependencies,
  missing transactions, hardcoded credentials, H2 trigger calling Java class directly,
  duplicate field `QTA_MAGAZZINO` / `GIACENZA`, `STATO` as undocumented integer,
  duplicate client "Trasporti Alpini" (IDs 1 and 7), phantom product TRN001 (ID 8)

### Target (Python — implemented in `fastapi-app/`)
- Language: **Python 3.12**
- Framework: **FastAPI 0.115.x** + SQLAlchemy 2.x sync (sufficient for SQLite single-writer; async planned post-MVP — see ADR-001 update note)
- Migrations: **Alembic 1.13.x** — baseline `0001_initial_schema_v2.py` covers schema v2
- Validation: form `Form(...)` + manual checks (Pydantic v2 available, used selectively)
- DB: **SQLite 3** (WAL mode) — schema v2 active (see `decisions/schema-sqlite-v2.sql`)
- Frontend: Jinja2 templates + Chart.js (self-hosted in `static/js/chart.min.js`)
- Config: `python-dotenv` — no secrets in code
- Server: uvicorn 0.29.x
- Security: bcrypt passwords, CSRF tokens on every POST, security headers middleware (X-Frame-Options DENY, CSP, X-Content-Type-Options nosniff, Referrer-Policy), 30-min session timeout

## Decisions Log
| ID | Decision | Status | Owner | Reference |
|----|----------|--------|-------|-----------|
| D-1 | Python framework | done — FastAPI | Chiara | ADR-001 |
| D-2 | Target database | done — SQLite 3 + WAL | Chiara | ADR-002 |
| D-3 | Chart library | done — Chart.js (self-hosted) | Lucia | reports.html |
| D-4 | Discount rule | done — applied per-line in `save_order` | Chiara | main.py |
| D-5 | Archival threshold | done — 2 years (730 days, override via `ARCHIVE_THRESHOLD_DAYS`) | PM | main.py |
| D-6 | Data migration strategy | done — H2 CSV export → Python → SQLite | Chiara | ADR-002 |
| D-7 | Sync vs async SQLAlchemy | done — sync for hackathon scope | Chiara | ADR-001 update note |

## Team Roles
| Name | Role | Responsibilities |
|------|------|-----------------|
| Luca Provvidenza | PM | User stories, docs, ADR structure, commit messages, demo coordination |
| Chiara Scarpino | Architect | Legacy monolith, ADR-001, ADR-002, SQLite schema, migration strategy |
| Lucia Cilento | Dev | FastAPI scaffold, route migration, E2 customers, E3 dashboard |

## Epics
Full user stories with acceptance criteria: `docs/user-stories.md`

| Epic | Title | Status | Owner |
|------|-------|--------|-------|
| E1 | Order Management — extended catalog (5 product types), workflow stati | done | Lucia |
| E2 | Customer Management — extended fields, global search, Gold/Silver/Bronze edit | done | Lucia |
| E3 | Reporting — KPI dashboard + bar/line/donut Chart.js | done | Lucia |
| E4 | Modernization — FastAPI scaffold + route migration + security (CSRF/headers/timeout) | done | Lucia |
| E5 | Data Integrity — Alembic baseline, integrity-check, order archival + restore | done | Chiara |

## Schema
- v1 baseline: `decisions/schema-sqlite-v1.sql`
- v2 (use this): `decisions/schema-sqlite-v2.sql` — adds `classificazione`, `tipologia`, commercial fields, archive tables
- v1→v2 migration SQL included as comments at bottom of schema-sqlite-v2.sql
- `utenti` bootstrap uses placeholder bcrypt hashes — replace with real seed script before demo

## Conventions
- Language: English for code and identifiers
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`)
- No placeholder code — mark as `# TODO` if not implemented
- No hardcoded secrets — use `.env` + `python-dotenv`
- ADRs in `/decisions/` folder, filename: `ADR-NNN-short-title.md`
- PR reviews required — no direct push to main for feature work
- Tests must pass before merging
- Keep this file updated as conventions evolve

## Key Rules
- Commit often — commit history is judged
- Every architectural decision → ADR in `/decisions/`
- Schema changes → new Alembic migration file, never edit `schema-sqlite-v1.sql` directly
- No hardcoded credentials anywhere
- Smoke test before every demo
