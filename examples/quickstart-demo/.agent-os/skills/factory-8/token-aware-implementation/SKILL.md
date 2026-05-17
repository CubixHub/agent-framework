---
name: token-aware-implementation
description: Implement with token budget in mind. Choose the right model tier per task. Skip exploration cycles via good context loading. Use spec mode for >2-file changes. Halves session cost without quality loss.
---

# When to use

- Cost-sensitive sessions (budget-constrained projects, demos).
- Long-running orchestration daemons (token spend compounds).
- ANY task — the techniques are no-loss when applied correctly.

# How to execute

## Step 1 — Match model to task

| Task shape | Model tier |
|---|---|
| Quick edit, formatting, single-fact lookup | Haiku / GPT-mini / Pi-default |
| Standard implementation against accepted ADR | Sonnet / GPT-codex / Pi-fast |
| Complex debugging, multi-attempt | Opus / GPT-5 / Pi-best |
| Architecture decision, cross-package review | Opus / GPT-5 / Pi-best (with extended thinking on) |

For orchestration daemon, the role file's `model_preference` declares the right
tier. Don't override unless task-specific.

## Step 2 — Load context up front, don't explore

Cost: each exploration round-trip is ~5-15k tokens.

Up-front (cheap):
- AGENTS.md
- relevant `.agent-os/rules/<lang>.md`
- the files you'll edit (Read directly, not via Grep first)

Skip:
- "Let me first understand the codebase" sweeps without a specific question.

## Step 3 — Use spec mode for >2-file changes

A 2-file change in spec mode: 2 turns. Without: typically 4-6 turns from
discovery + false starts. See [../spec-mode/SKILL.md](../spec-mode/SKILL.md).

## Step 4 — Apply format constraints to reduce output

Ask for what you need:
- "Return just the diff, no explanation."
- "List files only."
- "JSON with fields X, Y, Z."

The agent generates fewer tokens; you get the same useful information.

## Step 5 — Batch similar work

Three "add logging to <service>" turns ≈ 3x context rebuild = 3x cost.
One "add logging to <list of services> using <pattern>" turn ≈ 1x.

## Step 6 — Monitor

- Claude Code: `/cost` shows session spend.
- Codex: `codex --show-cost`.
- Pi: `pi stats`.

Check after every significant session. If a session cost > 5x your estimate,
audit which step was expensive.

# Token waste table

| Pattern | Cost | Fix |
|---|---|---|
| Multiple Grep cycles before reading | High | Read directly when you know the file |
| Re-reading the same file across turns | High | Use the context summary (see [../../context-compression/](../../context-compression/SKILL.md)) |
| Verbose explanations in implementation tasks | Medium | Constrain output format |
| Opus for trivial edits | High | Drop to Sonnet/Haiku for the trivial parts |
| No AGENTS.md / project context | Compounds | Scaffold one — even minimal AGENTS.md saves a lot |

# Anti-patterns (refuse)
- Picking Opus for every task — quality plateau hit before cost.
- Reading 10 files to "build context" without a specific question.
- Skipping format constraints because "the user will skim".
- Not tracking cost.
