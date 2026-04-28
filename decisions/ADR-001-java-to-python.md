# ADR-001: Migrate from Java/JSP Monolith to Python

**Date:** 2026-04-28  
**Status:** Accepted  
**Deciders:** Chiara Scarpino (Architect), Luca Provvidenza (PM)

---

## Context

The Brennero Logistics order portal is a Java 8 / JSP / embedded Tomcat monolith (`portal-ordini`). The codebase exhibits classic legacy symptoms: business logic scattered across `DatabaseManager`, undocumented state integers, plaintext passwords, dual inventory fields (`GIACENZA` / `QTA_MAGAZZINO`), and a trigger that calls a Java method directly from SQL. The hackathon scenario calls for a full modernization: extract services, clean the data model, and adopt a maintainable stack the team can sustain.

**Constraints:**
- Team has stronger Python fluency than Java (2 devs, limited JVM experience)
- Target deployment is containerised (Docker); no app-server license required
- SQLite chosen as embedded DB for portability (see ADR-002)
- Time-boxed hackathon: fast bootstrapping matters

---

## Decision

**Adopt Python 3.12 + FastAPI + SQLAlchemy 2.x (async) as the target stack.**

---

## Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **FastAPI** | Auto OpenAPI docs, Pydantic validation, async I/O, top Python perf, huge adoption | Newer (2018), smaller community vs Django | ✅ Selected |
| **Flask** | Minimal, battle-tested, large ecosystem | No built-in validation, no async, more boilerplate for REST APIs | ❌ Rejected |
| **Django + DRF** | Full batteries, mature ORM, admin panel free | Heavy, Django ORM != SQLAlchemy, overkill for a service-split target | ❌ Rejected |
| **Keep Java (Spring Boot)** | No language change, JVM ecosystem | Team friction, JVM overhead in containers, same paradigm as legacy | ❌ Rejected |

### ORM

**SQLAlchemy 2.x** with **Alembic** for migrations.

| Option | Decision |
|--------|----------|
| SQLAlchemy 2.x (async) | ✅ Selected — declarative models, best SQLite support, Alembic migrations, widely known |
| Tortoise ORM | ❌ — async-first but smaller community, less tooling |
| Peewee | ❌ — sync only, no migration tool bundled |
| Django ORM | ❌ — tied to Django |

---

## Rationale

1. **FastAPI** generates an OpenAPI spec at `/docs` with zero config — invaluable for the anti-corruption layer and for demoing to stakeholders.
2. **Pydantic v2** models enforce the data contracts we are adding (order status enum, priority field) that were previously free-text integers in the monolith.
3. **SQLAlchemy async** lets us reuse models across unit tests (sync) and production (async) without duplication.
4. **Alembic** solves the monolith's `schema.sql` with no migrations problem: every schema change is versioned and reversible.
5. Python container images are significantly smaller than JVM equivalents (`python:3.12-slim` ≈ 50 MB vs OpenJDK + WAR).

---

## Consequences

### Positive
- OpenAPI docs generated automatically → easier stakeholder review
- Pydantic models eliminate the undocumented integer state machine
- Alembic migrations replace the "one big schema.sql" anti-pattern
- Lighter containers, faster CI builds

### Negative / Risks
- JSP templating dropped — frontend must move to a separate SPA or Jinja2 templates (decision deferred)
- Python async can be subtle; team must avoid mixing sync DB calls in async routes
- SQLAlchemy 2.x async API is different from 1.x — docs must be checked

### Mitigation
- Add `asyncio` linting rule (`flake8-async`) to CI
- Pin SQLAlchemy `>=2.0,<3.0` in `requirements.txt`

---

## Stack Summary

```
Python          3.12
FastAPI         0.115.x
SQLAlchemy      2.0.x  (sync — see Update 2026-04-28)
Alembic         1.13.x
Pydantic        2.x
uvicorn         0.29.x  (ASGI server)
pytest          8.x    (planned post-MVP)
httpx           0.27.x (used in smoke tests)
```

---

## Update 2026-04-28 — Sync vs Async (D-7)

The original decision called for `SQLAlchemy 2.x async + aiosqlite`. During implementation we
opted for the **synchronous** SQLAlchemy API. Rationale:

- SQLite is a single-writer DB; async I/O does not unlock concurrency benefits the way it would
  for PostgreSQL/MySQL.
- `aiosqlite` adds a thread-pool layer with no measurable latency gain for hackathon-scale traffic.
- Sync code paths kept the FastAPI routes uniform and the smoke tests simpler.
- All scripts (Alembic, `seed.py`, ad-hoc utilities) remain plain sync SQLAlchemy.

The framework choice (FastAPI), the ORM (SQLAlchemy 2.x), and Alembic are unchanged. Switching
to async at a later stage is a localised refactor (`create_engine` → `create_async_engine`,
sessions/connections in routes become awaitable) with no schema or contract impact.
