# Team Assago — Claude Code Hackathon 2026

## Participants
| Name | Role |
|------|------|
| Luca Provvidenza | PM |
| Chiara Scarpino | Architect |
| Lucia Cilento | Dev |

## Scenario
**Scenario 1 — "The Monolith"** (Code Modernization)

**App: Brennero Logistics S.p.A.** — internal order portal, Java 8, built in 2015.

Modernizing without a big-bang rewrite: from Java / Servlet / H2 in-memory
toward Python 3.12 + FastAPI + SQLite persistent, with new features across
orders, customers, reporting, and data integrity.

## What We Built

**Starting point — Java monolith (`monolith/`):**
- `PortalServlet.java` — God Servlet handling all routes via `?action=` dispatch
- H2 in-memory database — all data lost on every restart
- 6 JSP pages + JSTL 1.2, vanilla CSS, zero JavaScript
- Known anomalies: SQL injection, plaintext passwords, circular dependencies,
  missing transactions, H2 trigger calling a Java class, duplicate field `QTA_MAGAZZINO`,
  undocumented integer state machine, duplicate client records, phantom product

**Architecture decisions and foundations (Python target):**
- FastAPI 0.115.x + SQLAlchemy 2.x async + Alembic migrations (decided and documented)
- SQLite 3 WAL mode — persistent, single-file, zero infra (decided and documented)
- Modernized schema: enums replacing magic integers, FK constraints, WAL mode,
  duplicate fields removed, business logic moved out of DB triggers
- Detailed data migration strategy from H2 to SQLite, including known data quality issues
- Security fixes designed: parameterized queries, bcrypt, CSRF, HTTP security headers
- Extended data model: customer classification Gold/Silver/Bronze, 5 product types,
  order priority levels, logistics fields

## Challenges Completed
| Challenge | Status | Owner |
|-----------|--------|-------|
| 1 — The Stories: 5 epics, 17 user stories, full AC, stakeholder conflicts | done | Luca |
| 2 — The Patient: Java legacy monolith with real anomalies | done | Chiara |
| ADR-001: Java → Python (FastAPI + SQLAlchemy selected, sync update note) | done | Chiara |
| ADR-002: H2 → SQLite (migration strategy, data quality issues, cutover plan) | done | Chiara |
| SQLite schema v2: classificazione, tipologia, tabelle archivio | done | Chiara |
| Alembic baseline migration `0001_initial_schema_v2.py` | done | Chiara |
| **E1** — Extended catalog 5 tipologie + creazione ordini transazionale + workflow stati | done | Lucia |
| **E2** — Customer extended (PEC/SDI/settore/referente), edit Gold/Silver/Bronze, global search | done | Lucia |
| **E3** — KPI dashboard (4 cards + delta YoY) + bar/line/donut Chart.js | done | Lucia |
| **E4** — FastAPI scaffold + route migration + sicurezza (CSRF, CSP, X-Frame-Options, 30min session) | done | Lucia |
| **E5** — Integrity check (US-5.1) + archive +2anni con restore (US-5.3) | done | Chiara |

## Open
| Challenge | Status | Owner |
|-----------|--------|-------|
| 3 — The Map: decomposition ADR with seam risk ranking | pending | Chiara |
| pytest test suite (smoke harness used during dev) | pending | team |
| Docker Compose for zero-config run | pending | team |

## Key Decisions
| ID | Decision | Choice | Reference |
|----|----------|--------|-----------|
| D-1 | Python framework | FastAPI 0.115.x | ADR-001 |
| D-2 | Database | SQLite 3 + WAL mode | ADR-002 |
| D-3 | Chart library | Chart.js (self-hosted) | reports.html |
| D-4 | Discount rule | applied per-line in `save_order` | main.py |
| D-5 | Archive threshold | 2 years (730 days, env-overridable) | main.py |
| D-6 | Data migration | H2 CSV export → Python → SQLite | ADR-002 |
| D-7 | SQLAlchemy mode | sync (async planned post-MVP) | ADR-001 update note |

## How to Run It

### Legacy Java (still runnable — H2 in-memory)
```bash
cd monolith
mvn compile exec:java -Dexec.mainClass=com.brennero.portal.PortalLauncher
```
Open `http://localhost:8080` — login: `admin` / `admin123`

### Python target (working — `fastapi-app/`)
```bash
cd fastapi-app
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head    # schema (option A — recommended)
python seed.py          # demo data
uvicorn main:app --reload
```
Open `http://localhost:8000` — login: `admin` / `admin123`
API docs at `http://localhost:8000/docs`

## Repository Structure
```
monolith/                     Java legacy app — Brennero Logistics
fastapi-app/
  main.py                     FastAPI app: routes, security middleware, CSRF, archive
  seed.py                     Demo data bootstrap (idempotent, Alembic-aware)
  alembic/                    Schema migrations (baseline = schema v2)
  templates/                  Jinja2 templates
  static/                     CSS + Chart.js
decisions/
  ADR-001-java-to-python.md   FastAPI selection rationale + sync update note
  ADR-002-h2-to-sqlite.md     SQLite selection + migration strategy
  schema-sqlite-v1.sql        Baseline (kept for history)
  schema-sqlite-v2.sql        Active schema (classificazione, tipologia, archivio)
docs/
  user-stories.md             5 epics, 17 stories, acceptance criteria
  pm-session-prompt.md        Claude Code PM session template
slides/
  index.html                  Project presentation (open in browser)
submission/Assago/
  README.md                   This file
  CLAUDE.md                   Conventions and project context
  Presentation.html           Submission slides
```

## How We Used Claude Code
- **Luca (PM)**: user stories with acceptance criteria, stakeholder conflict mapping,
  session prompts, all project docs, commit messages, presentation slides
- **Chiara (Architect)**: Java monolith generation with realistic anomalies,
  ADR-001, ADR-002, SQLite schema design, data migration strategy
- **Lucia (Dev)**: FastAPI scaffold, route migration from JSP, E2 + E3 implementation

## If We Had More Time
- Complete Python app with all 5 epics running
- pytest suite with 80%+ coverage
- Docker Compose for zero-config local run
- CI/CD via GitHub Actions
- Challenge 3 — The Map: seam decomposition with risk ranking
- Challenge 7 — The Scorecard: eval harness for LLM-driven refactoring
- PostgreSQL upgrade (already designed in ADR-002)
