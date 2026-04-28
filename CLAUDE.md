# CLAUDE.md — Hackathon Project

## Project Context
Claude Code Hackathon 2026 — Assago.
Scenario 1 — "The Monolith" (Code Modernization).
App: **Brennero Logistics S.p.A.** — portale ordini interni.
Team of 3.

## What We Are Building
Modernizzazione del portale ordini Brennero Logistics: da Java/Servlet/H2 in-memory
verso Python + framework moderno + DB persistente, con feature nuove su clienti,
ordini, reportistica e integrità dati.

## Stack

### Legacy (Java — `monolith/`)
- Language: Java (Servlet puro, no Spring Boot runtime — embedded Tomcat via pom.xml)
- Frontend: 6 JSP + JSTL 1.2, vanilla CSS, zero JavaScript
- Routing: `PortalServlet.java` — God Servlet con `?action=` dispatch
- DB: H2 in-memory (`jdbc:h2:mem:brennero`), schema da `schema.sql` + `data.sql`
- Known anomalies: SQL injection, password in chiaro, God class, dipendenze circolari, assenza transazioni, credenziali hardcoded in `DatabaseManager.java`

### Target (Python — decisione pendente D-1, D-2)
- Language: Python 3.11
- Framework: Flask / FastAPI / Django — **decidere in D-1**
- Templates: Jinja2 (o equivalente)
- DB: SQLite persistente (dev) — **decidere D-2 per prod**
- Frontend: Jinja2 + Chart.js CDN (no build step)
- Config: `python-dotenv` — nessun secret nel codice

## Team Roles
| Name | Role | Responsabilità |
|------|------|----------------|
| Luca Provvidenza | PM | User stories, ADR structure, CLAUDE.md, commit messages, demo |
| Chiara Scarpino | Architect | Monolith analysis, ADR-001 Python migration, ADR-002 DB, schema |
| Lucia Cilento | Dev | Flask scaffold, migrazione route, feature E2 clienti, E3 dashboard |

## Epics & User Stories
Dettaglio completo con acceptance criteria: `docs/user-stories.md`

| Epic | Titolo | Priorità |
|------|--------|----------|
| E1 | Gestione Ordini — catalogo esteso (TRASPORTO/DOGANA/MAGAZZINO/ASSICURAZIONE/CONSULENZA) | MUST |
| E2 | Gestione Clienti — anagrafica estesa, ricerca, classificazione Gold/Silver/Bronze | MUST |
| E3 | Reportistica — dashboard KPI + Chart.js (bar, line, donut) | MUST/SHOULD |
| E4 | Modernizzazione — Java → Python, fix SQL injection, password hash, God class | MUST |
| E5 | Integrità Dati — H2 → SQLite, fix schema, storicizzazione ordini > 2 anni | MUST/SHOULD |

## Pending Decisions
| ID | Decisione | Owner | Impatto |
|----|-----------|-------|---------|
| D-1 | Framework Python: Flask vs FastAPI vs Django | Chiara + Lucia | E4 |
| D-2 | DB target: SQLite vs PostgreSQL | Chiara | E5 |
| D-3 | Libreria grafici: Chart.js vs Plotly vs D3.js | Lucia | E3 |
| D-4 | Regola sconto cliente: per riga vs per ordine | PM | E1 |
| D-5 | Soglia storicizzazione: 2 anni vs 3 anni | PM | E5 |
| D-6 | Strategia migrazione dati Java → Python | Chiara | E4, E5 |

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
- No hardcoded credentials anywhere
- Smoke test before every demo
- User stories + AC in `docs/user-stories.md` — non modificare senza allineare il team
