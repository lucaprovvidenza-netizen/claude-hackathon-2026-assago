# PM Session Prompt — Luca

Copia e incolla questo all'inizio di ogni sessione Claude Code come PM.

---

## PROMPT (copia da qui)

```
You are helping me execute the PM track of a hackathon sprint.

## Context
- Hackathon: Claude Code Hackathon 2026 — Assago
- Scenario: Scenario 1 — "The Monolith" (Code Modernization)
- Repo: https://github.com/lucaprovvidenza-netizen/claude-hackathon-2026-assago
- Time available: 53 minutes total
- My role: PM (Luca)

## Team
- Luca (me) — PM: documentation, CLAUDE.md, README, ADRs structure, commit messages, demo coordination
- Chiara — Architect: ADR-001 Python migration, ADR-002 DB migration, schema design
- Lucia — Dev: Flask scaffold, route migration, feature implementation

## The App (existing Java monolith)
- Language: Java, Servlet pure (no Spring)
- Frontend: 6 JSP pages + JSTL 1.2, zero JavaScript, vanilla CSS
- God Servlet: PortalServlet.java handles all ?action= routing
- Database: H2 in-memory (data lost on restart), credentials hardcoded in DatabaseManager.java
- Schema loaded from schema.sql + data.sql at startup

## What We Are Modernizing Toward
Python + Flask + SQLite (persistent file), Jinja2 templates, Chart.js for dashboard,
env vars for all secrets, Flask Blueprint split (no more God Servlet pattern).

## 5 Epics
- E1 (P1): Order management — extended catalog with product/service types
- E2 (P1): Customer management — extended fields, search by name/product, priority 1/2/3
- E3 (P2): Reporting — modern dashboard with Chart.js charts
- E4 (MANDATORY): Modernization — Java → Python, fix known anomalies, break God Servlet
- E5 (P2): Data integrity — H2 → SQLite persistent, fix hardcoded credentials, archive old orders

## Conventions (enforce these on all commits)
- Commits: Conventional Commits format (feat:, fix:, chore:, docs:, refactor:, test:)
- ADRs: go in /decisions/ folder, filename format: ADR-NNN-short-title.md
- No hardcoded secrets — use .env + python-dotenv
- English for code and identifiers, Italian allowed in comments
- No placeholder code shipped — mark as # TODO if not implemented
- Keep CLAUDE.md updated when conventions or stack change

## My PM Tasks This Session (in order)
1. Update CLAUDE.md with: stack (Python+Flask+SQLite), team roles, scenario name, conventions
2. Update README.md with: team members+roles, scenario, what we built, how to run
3. Create /decisions/ folder with ADR template file
4. Write commit for all docs changes
5. During 20–50 min: review PRs from Chiara and Lucia, write conventional commit messages
6. At 50–53 min: smoke test the running app end-to-end (login → orders → customers → reports)

## What I Need From You Right Now
Help me execute task 1: rewrite CLAUDE.md completely with all the information above.
After each task I'll tell you what's next.
```

---

## Come usare

1. Copia il blocco sopra
2. Incolla come primo messaggio in Claude Code (CLI o VS Code extension)
3. Dopo ogni task completato, di' a Claude "next task" — conosce già la lista
4. Aggiorna "What Is Already Done" man mano che avanzi

## Task checklist PM

- [ ] CLAUDE.md aggiornato
- [ ] README.md compilato
- [ ] /decisions/ folder creato con template ADR
- [ ] Commit docs (chore: update project docs with stack, team, scenario)
- [ ] Review PR Chiara (ADR-001, ADR-002)
- [ ] Review PR Lucia (Flask scaffold, features)
- [ ] Smoke test end-to-end
- [ ] Commit finale + tag release
