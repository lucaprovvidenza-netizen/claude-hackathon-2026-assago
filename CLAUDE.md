# CLAUDE.md — Hackathon Project

## Project Context
Claude Code Hackathon 2026 — Assago.
Scenario 1 — "The Monolith" (Code Modernization).
App: **Brennero Logistics S.p.A.** — portale ordini interni.
Team of 3.

## What We Are Building
Modernizzazione del portale ordini Brennero Logistics: da Java 8/Servlet/H2 in-memory
verso Python 3.12 + FastAPI + SQLite persistente, con feature nuove su clienti,
ordini, reportistica e integrità dati.

## Stack

### Legacy (Java — `monolith/`)
- Language: Java 8 (Servlet puro, embedded Tomcat via pom.xml)
- Frontend: 6 JSP + JSTL 1.2, vanilla CSS, zero JavaScript
- Routing: `PortalServlet.java` — God Servlet con `?action=` dispatch
- DB: H2 in-memory (`jdbc:h2:mem:brennero`), schema da `schema.sql` + `data.sql`
- Known anomalies: SQL injection, password plaintext, God class, dipendenze circolari,
  assenza transazioni, credenziali hardcoded, trigger H2 che chiama classe Java,
  campo `QTA_MAGAZZINO` duplicato di `GIACENZA`, `STATO` come int senza documenti,
  clienti duplicati (Trasporti Alpini ID 1 e 7), prodotto fantasma TRN001 (ID 8)

### Target (Python — stack DECISO, vedi ADR-001 + ADR-002)
- Language: **Python 3.12**
- Framework: **FastAPI 0.115.x** + SQLAlchemy 2.x async (aiosqlite)
- Migrations: **Alembic 1.13.x**
- Validation: **Pydantic v2**
- DB: **SQLite 3** (WAL mode) — schema baseline in `decisions/schema-sqlite-v1.sql`
- Frontend: Jinja2 templates + Chart.js CDN (no build step) — decision deferred
- Config: `python-dotenv` — nessun secret nel codice
- Test: pytest 8.x + httpx 0.27.x (async test client)
- Server: uvicorn 0.29.x

## Decisions Log
| ID | Decisione | Stato | Owner | Riferimento |
|----|-----------|-------|-------|-------------|
| D-1 | Framework Python | ✅ FastAPI | Chiara | ADR-001 |
| D-2 | DB target | ✅ SQLite 3 + WAL | Chiara | ADR-002 |
| D-3 | Libreria grafici | ⏳ Chart.js (ipotesi) | Lucia | — |
| D-4 | Regola sconto | ✅ per-riga + sconto ordine override | Chiara | schema-sqlite-v1.sql |
| D-5 | Soglia storicizzazione | ⏳ 2 anni (da confermare) | PM | — |
| D-6 | Strategia migrazione dati | ✅ H2 CSV → Python → SQLite | Chiara | ADR-002 |

## Team Roles
| Name | Role | Responsabilità |
|------|------|----------------|
| Luca Provvidenza | PM | User stories, docs, ADR structure, commit messages, demo |
| Chiara Scarpino | Architect | Monolith, ADR-001, ADR-002, schema SQLite, migration strategy |
| Lucia Cilento | Dev | FastAPI scaffold, route migration, E2 clienti, E3 dashboard |

## Epics & User Stories
Dettaglio completo con acceptance criteria: `docs/user-stories.md`

| Epic | Titolo | Stato | Owner |
|------|--------|-------|-------|
| E1 | Gestione Ordini — catalogo esteso (5 tipologie) | ⏳ TODO | Lucia |
| E2 | Gestione Clienti — anagrafica, ricerca, Gold/Silver/Bronze | ⏳ TODO | Lucia |
| E3 | Reportistica — dashboard KPI + Chart.js | ⏳ TODO | Lucia |
| E4 | Modernizzazione — FastAPI scaffold + migrazione route | ⏳ TODO | Lucia |
| E5 | Integrità Dati — migration script H2→SQLite, storicizzazione | ⏳ TODO | Chiara |

## Known Schema Gaps (da risolvere prima di code)
- `CLIENTI` manca campo `classificazione` (Gold=1/Silver=2/Bronze=3) — E2 richiede
- `PRODOTTI` manca campo `tipologia` (TRASPORTO/DOGANA/MAGAZZINO/ASSICURAZIONE/CONSULENZA) — E1 richiede
- `CLIENTI` manca campi: `settore_merceologico`, `referente_commerciale`, `telefono_referente` — E2 richiede
- `UTENTI` placeholder bcrypt hash — sostituire con seed script reale

## Conventions
- Language: English for code and identifiers, Italian allowed in comments/docs
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`)
- No placeholder code shipped — mark as `# TODO` if not implemented
- No hardcoded secrets — use `.env` + `python-dotenv`
- ADRs go in `/decisions/` folder, filename: `ADR-NNN-short-title.md`
- PR reviews required — no direct push to main for feature work
- Tests must pass before merging
- Keep this file updated as conventions evolve

## Key Rules
- Commit often — commit history is judged
- Every architectural decision → ADR in `/decisions/`
- Schema changes → nuovo file Alembic migration, non modificare schema-sqlite-v1.sql
- No hardcoded credentials anywhere
- Smoke test before every demo
