# CLAUDE.md — Hackathon Project

## Project Context
Claude Code Hackathon 2026 — Assago.
Scenario 1 — "The Monolith" (Code Modernization).
Team of 3: Luca (PM), Chiara (Architect), Lucia (Dev).

## What We Are Building
Modernizzazione di un'applicazione web Java legacy (God Servlet + H2 in-memory + JSP)
verso Python + Flask + SQLite persistente, con nuove feature su clienti, ordini e reportistica.

## Stack

### Legacy (Java — da migrare)
- Language: Java (Servlet puro, no Spring)
- Frontend: JSP + JSTL 1.2, vanilla CSS, zero JavaScript
- Routing: `PortalServlet.java` — God Servlet unico con `?action=` dispatch
- Database: H2 in-memory (`jdbc:h2:mem:brennero`), schema da `schema.sql` + `data.sql`
- Known issues: credenziali hardcoded in `DatabaseManager.java`, dati volatili

### Target (Python)
- Language: Python 3.11
- Framework: Flask + Blueprint (un blueprint per dominio)
- Templates: Jinja2
- Database: SQLite file persistente
- Frontend: Jinja2 + Chart.js (CDN) per dashboard
- Config: `python-dotenv` — nessun secret nel codice

## Team Roles
| Nome | Ruolo | Responsabilità |
|------|-------|----------------|
| Luca | PM | CLAUDE.md, README, ADR structure, commit messages, demo coordination |
| Chiara | Architect | ADR-001 Python migration, ADR-002 DB migration, schema SQLite |
| Lucia | Dev | Flask scaffold, migrazione route, E2 clienti, E3 dashboard |

## Epics
| Epic | Titolo | Priorità |
|------|--------|----------|
| E1 | Gestione Ordini — catalogo esteso (prodotti + servizi) | P1 |
| E2 | Gestione Clienti — anagrafica estesa, ricerca, priorità 1/2/3 | P1 |
| E3 | Reportistica — dashboard moderna Chart.js | P2 |
| E4 | Modernizzazione — Java → Python, fix anomalie note | OBBLIGATORIA |
| E5 | Integrità Dati — H2 → SQLite persistente, storicizzazione ordini | P2 |

## Conventions
- Language: English for code and identifiers, Italian allowed in comments/docs
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`)
- No placeholder code shipped — mark as `# TODO` if not implemented
- No hardcoded secrets — use `.env` + `python-dotenv`
- ADRs go in `/decisions/` folder, filename: `ADR-NNN-short-title.md`
- Keep this file updated as conventions evolve

## Key Rules
- Commit often — commit history is judged
- Every architectural decision → ADR in `/decisions/`
- No hardcoded credentials anywhere
- Smoke test before every demo
