# Team Assago — Hackathon 2026

## Participants
| Nome | Ruolo |
|------|-------|
| Luca Provvidenza | PM |
| Chiara Scarpino | Architect |
| Lucia Cilento | Dev |

## Scenario
**Scenario 1 — "The Monolith"** (Code Modernization)

**App: Brennero Logistics S.p.A.** — portale ordini interni legacy (Java 8, 2015).

Modernizzazione senza big-bang rewrite: da Java/Servlet/H2 in-memory verso
Python 3.12 + FastAPI + SQLite persistente, con nuove feature su ordini, clienti,
reportistica e integrità dati.

## What We Built

**Partenza — monolite Java (`monolith/`):**
- `PortalServlet.java` God Servlet con `?action=` dispatch
- H2 in-memory — dati volatili ad ogni riavvio
- 6 JSP + JSTL 1.2, vanilla CSS, zero JavaScript
- Anomalie note: SQL injection, password plaintext, dipendenze circolari,
  assenza transazioni, trigger H2 che chiama classe Java, campo duplicato `QTA_MAGAZZINO`

**Target — Python:**
- FastAPI + SQLAlchemy 2.x async + Alembic migrations
- SQLite 3 WAL mode — dati persistenti
- Classificazione clienti Gold/Silver/Bronze con badge visivo
- Ricerca globale per nome cliente e prodotto
- Catalogo esteso: TRASPORTO, DOGANA, MAGAZZINO, ASSICURAZIONE, CONSULENZA
- Dashboard KPI con Chart.js (bar, line, donut)
- Credenziali via `.env` — zero hardcoded secrets
- Fix anomalie sicurezza: query parametrizzate, bcrypt, CSRF, security headers

## Challenges Attempted
| # | Challenge | Status | Owner |
|---|-----------|--------|-------|
| 1 — The Stories | User stories + AC per 5 epics | done | Luca |
| 2 — The Patient | Legacy monolith Java generato | done | Chiara |
| ADR-001 | Java → Python (FastAPI deciso) | done | Chiara |
| ADR-002 | H2 → SQLite (strategia migrazione) | done | Chiara |
| Schema v1 | Schema SQLite modernizzato | done | Chiara |
| E1 | Catalogo 5 tipologie prodotto | TODO | Lucia |
| E2 | Anagrafica + ricerca + Gold/Silver/Bronze | TODO | Lucia |
| E3 | Dashboard Chart.js | TODO | Lucia |
| E4 | FastAPI scaffold + migrazione route | TODO | Lucia |
| E5 | Migration script H2 to SQLite + storicizzazione | TODO | Chiara |
| 3 — The Map | ADR decomposizione monolite | TODO | Chiara |

## Key Decisions
| Decisione | Scelta | ADR |
|-----------|--------|-----|
| Framework Python | FastAPI 0.115.x | ADR-001 |
| ORM | SQLAlchemy 2.x async | ADR-001 |
| Migrations | Alembic 1.13.x | ADR-001 |
| Database | SQLite 3 + WAL | ADR-002 |
| Migrazione dati | H2 CSV export to SQLite via Python | ADR-002 |

## How to Run It

### Legacy Java (esistente)
```bash
cd monolith
mvn spring-boot:run
```
App su `http://localhost:8080` — login: `admin` / `admin`

### Python target (in progress)
```bash
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```
App su `http://localhost:8000` — docs su `http://localhost:8000/docs`

## Repo Structure
```
monolith/           Java legacy app (Brennero Logistics)
decisions/          ADRs + schema SQLite
  ADR-001-java-to-python.md
  ADR-002-h2-to-sqlite.md
  schema-sqlite-v1.sql
docs/
  user-stories.md   5 epics + acceptance criteria completi
  pm-session-prompt.md
slides/
  index.html        Presentazione progetto (apri nel browser)
```

## Slides
Presentazione progetto: `slides/index.html` — apri nel browser (navigazione frecce tastiera).

## If We Had More Time
- E5: check integrita automatici + job storicizzazione
- pytest suite con copertura 80%+
- Docker Compose (FastAPI + SQLite volume)
- CI/CD GitHub Actions
- Challenge 3 The Map: ADR decomposizione con seams ranking
- Challenge 7 The Scorecard: eval harness LLM-driven refactoring
- Upgrade path PostgreSQL (gia documentato in ADR-002)

## How We Used Claude Code
- **Luca (PM)**: user stories con AC, session prompt, docs, commit messages, slides
- **Chiara (Architect)**: generazione monolite Java, ADR-001, ADR-002, schema SQLite
- **Lucia (Dev)**: FastAPI scaffold, migrazione route, E2 + E3 implementation
