# CLAUDE.md — Hackathon Project

## Project Context
Claude Code Hackathon 2026 — Assago.
Scenario 1: Code Modernization — "The Monolith".
Team of 3: 1 PM, 2 Dev.

## Conventions
- Language: English for code, Italian allowed in comments/docs
- Commits: Conventional Commits format (`feat:`, `fix:`, `chore:`, `docs:`, `test:`)
- No placeholder code shipped — if not implemented, mark as `# TODO`
- No hardcoded secrets — use env vars
- ADRs go in `/decisions/` folder
- Keep this file updated as conventions evolve

## Stack
- Legacy: Enterprise Java 2010 (Servlet/JSP, Maven, in-memory H2)
- Modernization target: TBD (strangler fig / service extraction)
- Infra: Docker Compose (target)

## Team Roles
| Name | Role | Focus |
|---|---|---|
| Luca Provvidenza | PM | Stories, acceptance criteria, stakeholder alignment |
| Lucia Cilento | Dev | Service extraction, tests, anti-corruption layer, eval harness |
| TBD | Dev | Architecture, decomposition map |

## Key Rules
- Commit often — commit history is judged
- Every challenge output goes in its own folder or file
- Tests must pass before merging
- PR reviews required (no direct push to main for feature work)
