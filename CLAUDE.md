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

### Target (Python — stack decided, see ADR-001 + ADR-002)
- Language: **Python 3.12**
- Framework: **FastAPI 0.115.x** + SQLAlchemy 2.x async (aiosqlite)
- Migrations: **Alembic 1.13.x**
- Validation: **Pydantic v2**
- DB: **SQLite 3** (WAL mode) — baseline schema in `decisions/schema-sqlite-v1.sql`
- Frontend: Jinja2 templates + Chart.js CDN (no build step)
- Config: `python-dotenv` — no secrets in code
- Test: pytest 8.x + httpx 0.27.x (async test client)
- Server: uvicorn 0.29.x

## Decisions Log
| ID | Decision | Status | Owner | Reference |
|----|----------|--------|-------|-----------|
| D-1 | Python framework | done — FastAPI | Chiara | ADR-001 |
| D-2 | Target database | done — SQLite 3 + WAL | Chiara | ADR-002 |
| D-3 | Chart library | pending — Chart.js assumed | Lucia | — |
| D-4 | Discount rule | done — per-line + order-level override | Chiara | schema-sqlite-v1.sql |
| D-5 | Archival threshold | pending — 2 years assumed | PM | — |
| D-6 | Data migration strategy | done — H2 CSV export → Python → SQLite | Chiara | ADR-002 |

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
| E1 | Order Management — extended catalog (5 product types) | TODO | Lucia |
| E2 | Customer Management — extended fields, search, Gold/Silver/Bronze | TODO | Lucia |
| E3 | Reporting — KPI dashboard + Chart.js | TODO | Lucia |
| E4 | Modernization — FastAPI scaffold + route migration | TODO | Lucia |
| E5 | Data Integrity — H2→SQLite migration script, order archival | TODO | Chiara |

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
