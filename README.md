# Team Assago — Hackathon 2026

## Participants
| Nome | Ruolo |
|------|-------|
| Luca Provvidenza | PM |
| Chiara Scarpino | Architect |
| Lucia Cilento | Dev |

## Scenario
**Scenario 1 — "The Monolith"** (Code Modernization)

**App: Brennero Logistics S.p.A.** — portale ordini interni legacy.

Modernizzazione senza big-bang rewrite: da Java/Servlet/H2 in-memory verso
Python + framework moderno + DB persistente, con nuove feature su ordini, clienti,
reportistica e integrità dati.

## What We Built

**Partenza — monolite Java (`monolith/`):**
- `PortalServlet.java` God Servlet con `?action=` dispatch
- H2 in-memory (dati volatili ad ogni riavvio)
- 6 JSP + JSTL 1.2, vanilla CSS, zero JavaScript
- Anomalie note: SQL injection, password in chiaro, dipendenze circolari, assenza transazioni

**Arrivo — Python:**
- App Python (Flask/FastAPI — vedi `decisions/ADR-001`) con route separate per dominio
- SQLite file persistente — nessun dato perso al riavvio
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
| E1 | Catalogo servizi e materiali | in progress | Lucia |
| E2 | Anagrafica clienti + ricerca + Gold/Silver/Bronze | in progress | Lucia |
| E3 | Dashboard Chart.js | in progress | Lucia |
| E4 | Migrazione Java → Python | in progress | Lucia + Chiara |
| E5 | H2 → SQLite + ottimizzazione schema | in progress | Chiara |
| 3 — The Map | ADR decomposizione monolite | pending | Chiara |

## Key Decisions
- User stories dettagliate con AC: `docs/user-stories.md`
- Decisioni architetturali: `decisions/` folder (ADR-001, ADR-002 in arrivo)
- Pending: D-1 (framework Python), D-2 (DB prod), D-3 (libreria grafici) — vedi CLAUDE.md

## How to Run It

### Legacy Java (esistente)
```bash
cd monolith
mvn spring-boot:run
# oppure
mvn package && java -jar target/*.jar
```
App su `http://localhost:8080` — login: admin/admin

### Python (target — in progress)
```bash
cp .env.example .env
pip install -r requirements.txt
flask run
# oppure
python app.py
```
App su `http://localhost:5000`

## Slides
Presentazione progetto: `slides/index.html` — apri nel browser (navigazione frecce tastiera).

## If We Had More Time
- E5 completo: check integrità automatici + job storicizzazione ordini
- Test suite pytest con copertura 80%+
- Docker Compose (app + DB)
- CI/CD GitHub Actions
- Challenge 3 (The Map): ADR decomposizione completa con seams ranking
- Challenge 7 (The Scorecard): eval harness per refactoring LLM-driven

## How We Used Claude Code
- **Luca (PM)**: generazione user stories con AC, session prompt, docs, commit messages, slides
- **Chiara (Architect)**: generazione monolite Java, analisi anomalie, scaffold ADR
- **Lucia (Dev)**: Python scaffold, migrazione route JSP → Jinja2, implementazione E2 + E3
