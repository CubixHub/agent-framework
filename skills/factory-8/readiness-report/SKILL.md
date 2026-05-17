---
name: readiness-report
description: Audit a project's AI-readiness — fast tests, lint, type-check, AGENTS.md, build commands documented, dependencies pinned, hooks wired. Emits a ranked punch-list of fixes that reduce token waste. Invoke at project start and after each phase.
---

# When to use

- Before starting work on an unfamiliar repo.
- Phase-exit gate ("are we ready to start P2?").
- After joining a new team — get the lay of the land.
- When token usage feels high without obvious cause.

# How to execute

## Step 1 — Probe the static surface
For each of these, record present/absent + 0-10 quality:

| Item | Check |
|---|---|
| `AGENTS.md` | Exists; has build/test/lint commands; references rules |
| `.agent-os/rules/` | Exists; ≥1 file per language used |
| Linter config | Detected + runs clean OR has documented failures |
| Type-checker | Detected (tsconfig, mypy, pyrightconfig, cargo.toml) |
| Test command | Documented in AGENTS.md AND runs in <30s |
| Format command | Detected and idempotent |
| Pre-commit hook | Exists; runs lint + typecheck + format-check |
| `.env.example` | Exists; `.env*` gitignored |
| Dependency pinning | Lockfile committed |
| CI | Runs the full verification stack |

## Step 2 — Probe the wiki + plan
- `wiki/PLAN.md` exists with vision + phase plan?
- `wiki/STATUS.md` is fresh (< 7 days)?
- `wiki/IDEAS.md` has ≥ 10 ideas?
- ADRs exist for cross-cutting decisions?

## Step 3 — Run a smoke command set
- `npm test` / `pytest` / `cargo test` — does it complete?
- Lint — clean?
- Type-check — clean?
- Time each. Score against thresholds (test <30s = good, <2min = ok, >2min = bad).

## Step 4 — Score & rank
Output a markdown report with:
- **Score**: out of 100, weighted by token-impact.
- **Top 5 fixable**: ranked by (token impact × effort to fix).
- **Estimated session-cost reduction**: rough %.

## Step 5 — File the report
- Save as `wiki/questions/readiness-<YYYY-MM-DD>.md`.
- Append summary to `wiki/log.md`.

# Output shape

```markdown
# Readiness report — YYYY-MM-DD

## Score: 67/100

## High-impact gaps (do these first)
1. No type-check (estimated +20% token cost from runtime errors) — wire `mypy --strict`.
2. Tests run in 3min (estimated +15% from skipped verification) — split into smoke + full.
3. No AGENTS.md (estimated +10% from re-exploration) — scaffold via Framework init.

## Medium-impact gaps
...

## Low-impact gaps
...
```

# Anti-patterns (refuse)
- Reporting a single overall percentage without ranking.
- Skipping the smoke-command runs — they expose flakiness.
- Recommending "use TypeScript" or other huge refactors as a readiness fix.
