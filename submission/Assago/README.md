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
| ADR-001: Java → Python (FastAPI + SQLAlchemy selected, rationale documented) | done | Chiara |
| ADR-002: H2 → SQLite (migration strategy, data quality issues, cutover plan) | done | Chiara |
| SQLite schema v1: modernized baseline with E2 fields, enums, FK, WAL | done | Chiara |

## Challenges In Progress
| Challenge | Status | Owner |
|-----------|--------|-------|
| E4 — FastAPI app scaffold + route migration from Java | in progress | Lucia |
| E2 — Customer Gold/Silver/Bronze + extended fields + search | in progress | Lucia |
| E1 — Extended order catalog (5 product types) | in progress | Lucia |
| E3 — KPI dashboard with Chart.js | in progress | Lucia |
| E5 — H2→SQLite migration script + order archival | in progress | Chiara |
| 3 — The Map: decomposition ADR with seam risk ranking | pending | Chiara |

## Key Decisions
| Decision | Choice | ADR |
|----------|--------|-----|
| Python framework | FastAPI 0.115.x | ADR-001 |
| ORM | SQLAlchemy 2.x async | ADR-001 |
| Migrations | Alembic 1.13.x | ADR-001 |
| Database | SQLite 3 + WAL mode | ADR-002 |
| Data migration | H2 CSV export → Python → SQLite | ADR-002 |
| Discount rule | per-line + order-level override | schema-sqlite-v1.sql |

## How to Run It

### Legacy Java (working)
```bash
cd monolith
mvn spring-boot:run
```
Open `http://localhost:8080` — login: `admin` / `admin`

### Python target (in progress — not yet runnable)
```bash
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```
Open `http://localhost:8000` — API docs at `http://localhost:8000/docs`

## Repository Structure
```
monolith/                     Java legacy app — Brennero Logistics
decisions/
  ADR-001-java-to-python.md   FastAPI selection rationale
  ADR-002-h2-to-sqlite.md     SQLite selection + full migration strategy
  schema-sqlite-v1.sql        Modernized SQLite schema (baseline)
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
