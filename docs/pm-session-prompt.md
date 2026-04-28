# PM Session Prompt — Luca

Copy and paste this at the start of every Claude Code session as PM.

---

## PROMPT (copy from here)

```
You are helping me execute the PM track of a hackathon sprint.

## Context
- Hackathon: Claude Code Hackathon 2026 — Assago
- Scenario: Scenario 1 — "The Monolith" (Code Modernization)
- Repo: https://github.com/lucaprovvidenza-netizen/claude-hackathon-2026-assago
- My role: PM (Luca)

## Team
- Luca (me) — PM: documentation, CLAUDE.md, README, ADR structure, commit messages, demo coordination
- Chiara — Architect: ADR-001 Python migration, ADR-002 DB migration, SQLite schema, migration strategy
- Lucia — Dev: FastAPI scaffold, route migration, feature implementation (E1–E4)

## The App (existing Java monolith — monolith/)
- Language: Java 8, pure Servlet (no Spring)
- Frontend: 6 JSP pages + JSTL 1.2, zero JavaScript, vanilla CSS
- God Servlet: PortalServlet.java handles all ?action= routing
- Database: H2 in-memory (data lost on restart), hardcoded credentials in DatabaseManager.java
- Schema loaded from schema.sql + data.sql at startup
- Known anomalies: SQL injection, plaintext passwords, circular dependencies,
  missing transactions, H2 trigger calling Java class, duplicate QTA_MAGAZZINO field

## Target Stack (decided — see ADR-001 and ADR-002)
- Python 3.12 + FastAPI 0.115.x
- SQLAlchemy 2.x async + aiosqlite
- Alembic migrations
- Pydantic v2 validation
- SQLite 3 WAL mode (persistent file)
- Jinja2 templates + Chart.js CDN
- python-dotenv for all secrets

## 5 Epics
- E1: Order management — extended catalog with 5 product types (transport, customs, warehouse, insurance, consulting)
- E2: Customer management — extended fields, search by name/product, Gold/Silver/Bronze classification
- E3: Reporting — KPI dashboard with Chart.js (bar, line, donut)
- E4 (MANDATORY): Modernization — Java → FastAPI, fix known anomalies, break God Servant pattern
- E5: Data integrity — H2 → SQLite migration script, fix schema gaps, archive old orders

## Decisions already made
- D-1: FastAPI (not Flask, not Django) — ADR-001
- D-2: SQLite 3 + WAL (not PostgreSQL for now) — ADR-002
- D-4: discount applied per-line + order-level override — schema-sqlite-v1.sql
- D-6: H2 CSV export → Python → SQLite — ADR-002

## Conventions
- Commits: Conventional Commits (feat:, fix:, chore:, docs:, refactor:, test:)
- ADRs: /decisions/ folder, filename: ADR-NNN-short-title.md
- No hardcoded secrets — use .env + python-dotenv
- English for all code and identifiers
- No placeholder code — mark as # TODO if not implemented
- Keep CLAUDE.md updated when conventions or stack change

## PM Tasks (in order)
1. Pull latest — check what Chiara and Lucia committed
2. Update CLAUDE.md / README.md with new progress
3. Update submission/Assago/ files to reflect current status
4. Review PRs — write conventional commit messages
5. Smoke test the running app end-to-end (login → orders → customers → reports)
6. Final commit + verify submission folder is up to date

## What I Need From You Right Now
Pull the latest from git, read all changed files, and tell me what changed and what still needs to be done.
```

---

## How to Use

1. Copy the block above
2. Paste as first message in Claude Code (CLI or VS Code extension)
3. After each task say "next task" — Claude already has the list
4. Update submission files as work gets completed

## PM Checklist

- [ ] CLAUDE.md up to date (English, correct stack, decisions log)
- [ ] README.md up to date (challenges status, how to run)
- [ ] submission/Assago/README.md synced
- [ ] submission/Assago/CLAUDE.md synced
- [ ] submission/Assago/Presentation.html slide 7 reflects real status
- [ ] All commits follow Conventional Commits format
- [ ] Smoke test end-to-end before demo
- [ ] Final commit tagged
