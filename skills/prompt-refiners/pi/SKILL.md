---
name: pi-prompt-refiner
description: Rewrite a prompt to follow the Pi pattern — AGENTS.md + SYSTEM.md split, capability-package on-demand skill loading, print mode vs JSON mode choice
---

# When to use

Target is Pi (pi.dev) coding CLI. Apply when:
- You're configuring a Pi-based project for the first time.
- Pi is "missing context" or over-asking for clarification.
- You need to make Pi reliable in CI (parseable output, no chatter).

# How to execute

1. Decide what is **stable** (goes in `AGENTS.md` — project-level, every run sees it) vs **role-specific** (goes in `SYSTEM.md` — overlay for this run).
2. Move on-demand expertise into **capability packages** (Pi's skill extension model). Don't dump everything into one giant prompt — Pi loads packages lazily based on the task.
3. Pick invocation mode: `pi -p` (print, no chrome, scriptable) vs `pi --mode json` (structured output, parseable). Default `--mode json` for any automation.
4. Compose: `AGENTS.md` (project) + `SYSTEM.md` (role) + `pi run "<task>"`. The task is the variable; the rest is fixed.
5. Re-check: nothing in `AGENTS.md` should change between runs. If it does, hoist to `SYSTEM.md` or pass as `--var`.

# The Pi pattern (canonical structure)

## AGENTS.md (stable, per-project)

```markdown
# {{Project}} — Agent Guide

## Project
- Repo: <path>
- Stack: <languages, frameworks>
- Conventions: conventional commits; never push without ask; lint must pass before commit

## Where things live
- Wiki: `wiki/`
- Rules: `.pi/rules/*.md`
- Skills: `.pi/skills/**/SKILL.md`
- Hooks: `.pi/hooks/`

## Commands (slot table)
- build: <cmd>
- test: <cmd>
- lint: <cmd>
- format: <cmd>

## Hard rules
- Never bypass hooks
- Never commit `.env*`
- Always run lint before commit
```

## SYSTEM.md (role overlay, per-task-family)

```markdown
# Role: Backend Implementer

You implement small focused changes. You:
- Read AGENTS.md before any change
- Add tests before code (TDD)
- Run lint + tests after each change
- Update the wiki when learning a non-obvious fact
- Refuse to make changes >100 lines without surfacing a plan first
```

## Capability packages (`.pi/skills/<name>/SKILL.md`)

```markdown
---
name: <name>
description: <one line — used for relevance scoring>
---

# When to use
<trigger conditions>

# How to execute
<steps>

# Reference
<links>
```

Pi loads capability packages on-demand by matching the user request against the `description` field. Make descriptions specific.

## Invocation

```bash
pi run "implement <feature>"               # default; print + structured
pi -p "explain this stacktrace"            # print mode; no chrome
pi --mode json run "extract..."            # JSON output; parse downstream
pi --mode json -p "lint the wiki"          # combine
```

# Worked transformation

## Before (single mega-prompt)

```
You are an engineer for project Foo. The repo is at /home/x/foo. Use conventional commits. Never push without asking. The stack is Rust + Postgres + React. To build: cargo build. To test: cargo test. To lint: cargo clippy. Implement a feature that does X with constraints Y and Z. Write tests. Run them. Make a commit.
```

## After (Pi pattern)

`AGENTS.md`:
```markdown
# Foo — Agent Guide

## Project
- Repo: /home/x/foo
- Stack: Rust + Postgres + React
- Conventions: conventional commits; never push without ask

## Commands
- build: cargo build
- test: cargo test
- lint: cargo clippy --all-targets -- -D warnings

## Hard rules
- Never push without explicit ask
- Run `cargo test` + `cargo clippy` before any commit
```

`.pi/skills/backend-feature/SKILL.md`:
```markdown
---
name: backend-feature
description: Implement a new backend feature in Foo's Rust crates with TDD and conventional commits
---

# When to use
User asks: "implement X", "add feature X", "support X in backend"

# How to execute
1. Read AGENTS.md
2. Write the failing test first
3. Implement until test passes
4. Run lint
5. Commit with conventional-commit prefix
```

Run:
```bash
pi run "implement X with constraints Y and Z"
```

# Mode choice

| Goal | Mode |
|---|---|
| Interactive use | default (no `-p`, no `--mode`) |
| Scripted, plain output | `pi -p` |
| Pipe into another tool | `pi --mode json` |
| CI: structured + scriptable | `pi --mode json -p` |

# Anti-patterns

- Repeating AGENTS.md content in every task prompt. The whole point of AGENTS.md is to NOT repeat.
- Capability-package description = "various tasks". Skills won't load when needed; specificity matters.
- Default JSON mode for human-facing interactive use. Noise.
- Mixing role and project context in one file. Hard to override per run.

# Reference

- Pi docs at https://pi.dev/
- Sibling: `claude/SKILL.md`, `codex/SKILL.md` for cross-platform pattern comparison
- AGENTS.md pattern is shared across Pi, Claude Code (CLAUDE.md), Factory Droid (.factory/)
