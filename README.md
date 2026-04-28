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
  missing transactions, H2 trigger calling a Java class, duplicate field `QTA_MAGAZZINO`

**Target — Python:**
- FastAPI + SQLAlchemy 2.x async + Alembic migrations
- SQLite 3 WAL mode — persistent data
- Customer classification Gold / Silver / Bronze with color badge
- Global search by customer name and product
- Extended catalog: TRANSPORT, CUSTOMS, WAREHOUSE, INSURANCE, CONSULTING
- KPI dashboard with Chart.js (bar, line, donut)
- Credentials via `.env` — zero hardcoded secrets
- Security fixes: parameterized queries, bcrypt, CSRF protection, security headers

## Challenges Attempted
| Challenge | Status | Owner |
|-----------|--------|-------|
| 1 — The Stories: user stories + AC for 5 epics | done | Luca |
| 2 — The Patient: Java legacy monolith generated | done | Chiara |
| ADR-001: Java → Python (FastAPI decided) | done | Chiara |
| ADR-002: H2 → SQLite (migration strategy defined) | done | Chiara |
| SQLite schema v1 (baseline with E2 fields) | done | Chiara |
| E4 — FastAPI scaffold + route migration | in progress | Lucia |
| E2 — Customer management + Gold/Silver/Bronze + search | in progress | Lucia |
| E1 — Extended order catalog (5 product types) | in progress | Lucia |
| E3 — Chart.js dashboard | in progress | Lucia |
| E5 — H2→SQLite migration script + order archival | in progress | Chiara |
| 3 — The Map: decomposition ADR with seam ranking | pending | Chiara |

## Key Decisions
| Decision | Choice | ADR |
|----------|--------|-----|
| Python framework | FastAPI 0.115.x | ADR-001 |
| ORM | SQLAlchemy 2.x async | ADR-001 |
| Migrations | Alembic 1.13.x | ADR-001 |
| Database | SQLite 3 + WAL mode | ADR-002 |
| Data migration | H2 CSV export → Python → SQLite | ADR-002 |

## How to Run It

### Legacy Java
```bash
cd monolith
mvn spring-boot:run
```
Open `http://localhost:8080` — login: `admin` / `admin`

### Python target
```bash
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```
Open `http://localhost:8000` — API docs at `http://localhost:8000/docs`

## Repository Structure
```
monolith/                     Java legacy app (Brennero Logistics)
decisions/
  ADR-001-java-to-python.md   FastAPI decision rationale
  ADR-002-h2-to-sqlite.md     SQLite decision + migration strategy
  schema-sqlite-v1.sql        Modernized SQLite baseline schema
docs/
  user-stories.md             5 epics with full acceptance criteria
  pm-session-prompt.md        Claude Code session template for PM
slides/
  index.html                  Project presentation (open in browser)
submission/Assago/
  README.md                   Submission readme
  CLAUDE.md                   Project conventions and context
  Presentation.html           Submission slides
```

## Presentation
Project presentation: `slides/index.html` — open in browser, navigate with arrow keys.

## If We Had More Time
- E5 complete: automated integrity checks + order archival job
- pytest suite with 80%+ coverage
- Docker Compose (FastAPI + SQLite volume mount)
- CI/CD via GitHub Actions
- Challenge 3 — The Map: full decomposition ADR with seam risk ranking
- Challenge 7 — The Scorecard: eval harness for LLM-driven refactoring
- PostgreSQL upgrade path (already documented in ADR-002)

## How We Used Claude Code
- **Luca (PM)**: user stories with acceptance criteria, session prompts, docs, commit messages, presentation slides
- **Chiara (Architect)**: Java monolith generation, ADR-001, ADR-002, SQLite schema, migration strategy
- **Lucia (Dev)**: FastAPI scaffold, JSP → Jinja2 route migration, E2 + E3 implementation
