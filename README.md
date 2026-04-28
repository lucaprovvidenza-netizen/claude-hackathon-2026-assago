# Team Assago — Hackathon 2026

## Participants
| Nome | Ruolo |
|------|-------|
| Luca Provvidenza | PM |
| Chiara | Architect |
| Lucia | Dev |

## Scenario
**Scenario 1 — "The Monolith"** (Code Modernization)

Modernizzazione di un'applicazione web Java legacy verso Python + Flask,
senza big-bang rewrite. Strangler fig approach: l'app Java esiste, la migriamo
pezzo per pezzo aggiungendo feature nuove direttamente in Python.

## What We Built

Partenza: monolite Java con God Servlet, H2 in-memory, JSP puro, zero JavaScript.

Arrivo:
- App Python Flask con Blueprint separation
- SQLite persistente (no più dati persi al riavvio)
- Dashboard moderna con Chart.js
- Gestione clienti con priorità (1/2/3) e ricerca
- Catalogo ordini esteso (prodotti + servizi)
- Credenziali via `.env` (no hardcoded secrets)

## Challenges Attempted
| # | Challenge | Status | Notes |
|---|-----------|--------|-------|
| E1 | Gestione Ordini — catalogo esteso | in progress | Lucia |
| E2 | Gestione Clienti — anagrafica + ricerca + priorità | in progress | Lucia |
| E3 | Reportistica — dashboard Chart.js | in progress | Lucia |
| E4 | Modernizzazione Java → Python | in progress | Lucia + Chiara |
| E5 | Integrità Dati — H2 → SQLite persistente | in progress | Chiara |

## Key Decisions
- **Python + Flask** scelto per semplicità di scaffolding rapido vs Django overhead
- **SQLite** invece di PostgreSQL — sufficiente per hackathon, zero setup infra
- **Chart.js CDN** — no build step, integrazione immediata in Jinja2
- **Blueprint pattern** — separa dominio ordini, clienti, report fin da subito
- Dettagli in `/decisions/ADR-001-python-migration.md` e `/decisions/ADR-002-db-migration.md`

## How to Run It

```bash
# Clone
git clone https://github.com/lucaprovvidenza-netizen/claude-hackathon-2026-assago
cd claude-hackathon-2026-assago

# Setup Python env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Config
cp .env.example .env

# Run
flask run
# oppure
python app.py
```

App disponibile su `http://localhost:5000`

## Slides

Presentazione del progetto: `slides/index.html` — apri nel browser.

## If We Had More Time
- E5 completo: check integrità automatici + job storicizzazione ordini
- Test suite con pytest
- Containerizzazione Docker
- CI/CD con GitHub Actions
- Migrazione completa di tutti e 6 i moduli JSP

## How We Used Claude Code
- PM (Luca): generazione prompt di sessione, aggiornamento docs, commit messages
- Architect (Chiara): scaffolding ADR, review schema DB, decomposizione God Servlet
- Dev (Lucia): Flask scaffold, migrazione route JSP → Jinja2, feature E2 + E3
