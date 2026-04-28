# ADR-002: Migrate from H2 (embedded) to SQLite

**Date:** 2026-04-28  
**Status:** Accepted  
**Deciders:** Chiara Scarpino (Architect), Luca Provvidenza (PM)

---

## Context

The legacy monolith uses **H2** as its embedded database (JDBC, in-memory/file mode). H2 was chosen in the original 2015 codebase for zero-install local development. As part of the Java→Python migration (ADR-001), the persistence layer must also change.

**Observed issues with the current H2 setup:**
- Schema lives in a single `schema.sql` — no migration history, no rollback
- H2's `AUTO_INCREMENT` and trigger syntax are H2-specific (not standard SQL)
- The trigger `TRG_CALCOLA_TOTALE` calls a Java class directly (`CALL "com.brennero.portal.DatabaseManager.ricalcolaTotale"`) — impossible to port to any other DB
- Business logic embedded in the DB via Java triggers is a maintenance hazard
- H2 console disabled in prod; there is no operational tooling

---

## Decision

**Adopt SQLite 3 as the embedded database for the modernised Python service.**  
Schema migrations managed by **Alembic** (SQLAlchemy's migration tool).  
Business logic currently in triggers moves to the Python service layer.

---

## Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **SQLite** | Zero install, single file, universal tooling (`sqlite3` CLI, DBeaver, DB Browser), WAL mode for concurrency, native Python support | Single-writer limit (mitigated by WAL), not suited for multi-node horizontal scale | ✅ Selected |
| **PostgreSQL** | Full SQL, horizontal scale, JSONB, full-text search | Requires a server, adds infra complexity, overkill for single-service hackathon target | ❌ Rejected for now (clear upgrade path exists) |
| **Keep H2** | No change | Java-only JDBC driver, incompatible with Python/SQLAlchemy, H2 SQL dialect != standard | ❌ Rejected |
| **DuckDB** | Analytical queries, Parquet support | OLAP-oriented, not suited for transactional OLTP workload | ❌ Rejected |

---

## Migration Strategy

### Phase 1 — Schema (this sprint)
1. Author baseline `schema-sqlite-v1.sql` (see `decisions/schema-sqlite-v1.sql`)
2. Create Alembic environment inside the new Python service: `alembic init alembic`
3. Set `sqlalchemy.url = sqlite+aiosqlite:///./data/brennero.db` in `alembic.ini`
4. Generate initial migration from the SQLAlchemy models: `alembic revision --autogenerate -m "initial"`

### Phase 2 — Data migration (before go-live)
A one-shot migration script `tools/migrate_h2_to_sqlite.py` will:

```
H2 file DB  →  JDBC export (CSV per table)  →  Python pandas/csv  →  SQLite via SQLAlchemy
```

**Data cleaning steps required during migration:**

| Issue | H2 source | SQLite target fix |
|-------|-----------|-------------------|
| `STATO` INT (0–8, undocumented) | `ORDINI.STATO` | Map to TEXT enum; unknown values → `bozza` with `NOTE_INTERNE` preserved |
| `QTA_MAGAZZINO` duplicate | `PRODOTTI` | Drop column; take `MAX(GIACENZA, QTA_MAGAZZINO)` as authoritative value |
| Duplicate client `Trasporti Alpini` (IDs 1 & 7) | `CLIENTI` | Merge: keep ID 1, remap FK on `ORDINI.ID_CLIENTE = 7` → 1 |
| Plaintext passwords | `UTENTI.PASSWORD` | Force password reset for all users post-migration; generate bcrypt hashes |
| Phantom product `TRN001` (ID 8) | `PRODOTTI` | Keep record (has order rows), set `attivo = 0`, `codice = 'TRN-001-LEGACY'` |
| Trigger business logic | `TRG_CALCOLA_TOTALE` | Move to `OrderService.recalculate_total()` in Python; trigger dropped |

### Phase 3 — Cut-over
- Run migration in dry-run mode (`--dry-run`) against a copy of prod H2 file
- Validate row counts and FK integrity: `PRAGMA foreign_key_check;`
- Feature-flag the new Python service behind the anti-corruption layer
- Keep H2 monolith read-only for 1 sprint as fallback

---

## Consequences

### Positive
- SQLite file is trivially backed up (`cp brennero.db brennero.db.bak`)
- `sqlite3` CLI available on every developer machine — no JDBC driver needed
- WAL mode (`PRAGMA journal_mode = WAL`) allows concurrent reads while a write is in progress
- Alembic gives a full migration history — the "one big schema.sql" anti-pattern is gone
- Business logic leaves the DB and becomes testable Python code

### Negative / Risks
- SQLite does not enforce `ALTER TABLE ADD CONSTRAINT` after creation — constraints must be in `CREATE TABLE`
- Single writer: high write concurrency scenarios (bulk order import) need a task queue in front
- `aiosqlite` adds a thread-pool layer; latency slightly higher than sync SQLite

### Mitigation
- Document SQLite constraint limitation in `CLAUDE.md` / dev wiki
- Add `asyncio.Lock` at service layer for bulk import endpoint
- Benchmark write throughput in CI with `locust` before go-live; escalate to PostgreSQL if p99 > 200 ms under expected load

---

## Upgrade Path to PostgreSQL

If the service outgrows SQLite (multi-node, >10k orders/day), the migration is:
1. Change `sqlalchemy.url` to `postgresql+asyncpg://...`
2. Run `alembic upgrade head` against the new PG instance
3. Use `pgloader` to migrate SQLite → PostgreSQL in one command

No application code changes required — SQLAlchemy abstracts the dialect.
