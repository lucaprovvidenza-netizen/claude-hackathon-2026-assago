# Session Starter Prompt

Copy and paste this at the beginning of every Claude Code session.
Update the [PLACEHOLDERS] once the team has made decisions.

---

## PROMPT (copy from here)

```
You are helping us build a hackathon project for the Claude Code Hackathon 2026 (Assago).

## Our Project
- Repo: https://github.com/lucaprovvidenza-netizen/claude-hackathon-2026-assago
- Scenario: [SCENARIO NUMBER AND NAME — e.g. "Scenario 5: Agentic Solution"]
- Team: 3 people
- My role today: [YOUR ROLE — e.g. developer / architect / PM / tester]

## What We Are Building
[1-2 sentences describing the system — e.g. "An AI triage agent that classifies inbound IT helpdesk tickets, auto-resolves password resets, and routes the rest to the right queue."]

## Stack
- Language: [e.g. Python / TypeScript]
- Framework: [e.g. Claude Agent SDK / FastAPI / Next.js]
- DB: [e.g. PostgreSQL / SQLite]
- Infra: [e.g. Docker Compose]

## Conventions
- Commits: Conventional Commits format (feat:, fix:, chore:, docs:, test:)
- ADRs go in /decisions/ folder
- No hardcoded secrets — use environment variables
- English for code and identifiers, Italian allowed in comments
- Keep CLAUDE.md updated when conventions change

## Current Challenge I Am Working On
[NAME OF CHALLENGE — e.g. "Challenge 3: The Tools — building custom agent tools"]

## What Is Already Done
[BULLET LIST of completed challenges/components — e.g.:
- Challenge 1: Mandate document written
- Challenge 2: Architecture ADR drafted]

## What I Need From You Right Now
[SPECIFIC ASK — e.g. "Help me implement the classify_request tool with structured error responses"]
```

---

## How to Use

1. Copy the block above
2. Fill in all `[PLACEHOLDERS]`
3. Paste as first message in Claude Code (VS Code extension or CLI)
4. Update "What Is Already Done" each session as you make progress

## Keep This File Updated

When the team makes decisions (scenario, stack, completed challenges), update the placeholders here and commit. Everyone uses the same file → Claude gets the same context every session.
