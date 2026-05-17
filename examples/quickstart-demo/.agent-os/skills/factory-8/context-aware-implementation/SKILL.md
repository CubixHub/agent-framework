---
name: context-aware-implementation
description: Implement features using the project's memory + rules + wiki BEFORE writing code. Prevents the #1 failure mode of agent coding — re-deriving decisions that already exist in the project history.
---

# When to use

- ANY non-trivial implementation in a project with a `wiki/` or `.agent-os/`.
- Before adopting a library or pattern.
- When you're tempted to "just do it the standard way" — the project may have
  a non-standard decision documented somewhere.

# How to execute

## Step 1 — Read the four context surfaces

In this order:

1. **`.agent-os/memories.md`** (project memory) — recent non-obvious decisions.
2. **`.agent-os/rules/`** (matched to file extension) — coding conventions.
3. **`wiki/index.md`** — what knowledge exists in the wiki.
4. **`wiki/plan/adr/`** + per-package ADRs — what decisions have been made.

Then optional but valuable:

5. **`wiki/concepts/`** — patterns the project has adopted.
6. **`wiki/questions/`** — Q&A that touched the area you're working on.
7. **`wiki/sources/`** — upstream knowledge the project ingested.

## Step 2 — Map context to decisions

For each thing you'd otherwise have decided yourself, check: did the project
already decide this?

| Decision | Where to check |
|---|---|
| Test framework | `.agent-os/rules/testing.md` |
| State management library | `.agent-os/memories.md`, ADRs |
| API style | `.agent-os/rules/api.md`, ADRs |
| Naming convention | `.agent-os/rules/<lang>.md` |
| Error handling pattern | `.agent-os/rules/<lang>.md` + memories |

## Step 3 — Surface unresolved decisions

If a decision is required but the project hasn't documented it:
- Surface to the user. Don't silently invent a project convention.
- If they decide, write the answer to memories AND/OR an ADR before coding.

## Step 4 — Implement with the context in mind

When you write code:
- Quote the relevant rule / ADR in a comment IF it's non-obvious.
- Match the existing style in nearby files.
- Don't introduce a new pattern without an ADR.

## Step 5 — File new context

If you LEARNED something during the task:
- New pattern → wiki concept page.
- Non-obvious decision → memory entry or ADR.
- Resolved a Q → wiki question page.

# Output shape

A brief preamble before coding:

```
Context check:
- Memory says: <relevant snippet>.
- Rules say: <relevant snippet>.
- ADR-NNN: <decision>.
- Wiki concept [[<slug>]]: <relevant fact>.

Implementing accordingly.
```

# Anti-patterns (refuse)
- Skipping the four reads "because I know what to do".
- Inventing a project convention without an ADR.
- Letting newly-learned context vanish into chat history.
