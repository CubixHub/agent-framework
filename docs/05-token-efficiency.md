# Token Efficiency Strategies (Tri-Platform)

> Applies to: Claude Code, Codex, Pi. Rewrites Factory.ai's Token Efficiency guide. The unit of cost is **tokens per task**, not tokens per request — a cheaper model that needs three turns can cost more than a frontier model that nails it in one.

## Where tokens go

```
┌──────────────────────────────────────────────────────────┐
│ Tokens per task                                          │
├──────────────────────────────────────────────────────────┤
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  Context (system + AGENTS + memory) │
│  ▓▓▓▓▓▓▓▓▓▓          Tool-call I/O (file reads, runs)   │
│  ▓▓▓                 Output (the agent's reply)         │
└──────────────────────────────────────────────────────────┘
```

The bulk of cost is context and tool-call I/O. Output is usually the smallest slice — optimizing output verbosity first is a misdiagnosis.

## Project setup for efficiency

The single biggest lever: a project the agent can navigate cheaply.

- **Fast, reliable tests.** A 30-second `pnpm test` costs 30 seconds of agent wait per iteration. A 5-minute one costs sessions.
- **Fast lint + format + typecheck.** Same. The post-edit hook must finish in under 5s.
- **Clear directory structure.** If the agent has to grep to find the entry point, you pay the grep cost. Document it in `AGENTS.md` slot table.
- **Skills indexed in AGENTS.md.** The agent doesn't have to discover the skill index; it's pointed at it.

## Agent Readiness checklist

The readiness check (introduced in [Setup checklist](./01-setup-checklist.md) L5) gates whether the harness is in a state where token cost is bounded. Before any non-trivial session:

- [ ] Entry docs present (`AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `PI.md`)
- [ ] `.agent-os/rules/` populated; relevant rules match the files you'll edit
- [ ] Skills indexed and discoverable (`skills/skill-discovery/` installed)
- [ ] Hooks wired (post-edit, memory-capture)
- [ ] Wiki has `SCHEMA.md`, `index.md`, `PLAN.md`, `STATUS.md`
- [ ] Tests run green from a fresh clone in under 60s
- [ ] Default model declared per CLI (see L1)

Run `skills/readiness-check/` to verify. CI runs it on every commit to `.agent-os/`.

## Model selection strategy (cost multipliers, 2026-05)

Multipliers are relative to the cheapest tier per vendor. Treat absolute prices as ranges that move; check the vendor page for current numbers.

| Tier | Anthropic | OpenAI | Pi (defaults to vendor key) | Cost multiplier vs. cheapest |
|------|-----------|--------|------------------------------|------------------------------|
| Mini | Haiku 4.5 | gpt-5-nano / o4-mini | configured in SYSTEM.md | 1x (baseline) |
| Standard | Sonnet 4.5 | gpt-5-codex | Sonnet 4.5 | 5–10x |
| Frontier | Opus 4.7 | gpt-5 | Opus 4.7 | 25–50x |

Heuristic: use **Frontier** only for irreversible decisions (architecture, naming, security). Use **Standard** for editing and refactoring. Use **Mini** for triage and routing.

## Reasoning-effort impact

For OpenAI o-family and Claude Opus, reasoning effort is tunable:

- **Low**: ≤ 1k reasoning tokens. Fine for editing.
- **Medium**: ~4–8k. Default for planning.
- **High**: 16k+. Reserve for architecture and unblocking.

Set per-call. Don't leave it on High globally; you'll burn budget on routine work.

## Workflow patterns

### Spec mode equivalents per CLI

Two-pass workflow: plan → critique → code. Cheaper than one-pass + rework.

- **Claude Code**: `claude --mode plan` then continue.
- **Codex**: `codex --plan` then continue.
- **Pi**: invoke `skills/spec-mode/` explicitly. Pi has no built-in plan flag.

### IDE plugin

When using a CLI as an IDE plugin (e.g., VS Code), prefer the IDE's "selection" or "context-from-cursor" feature over re-pasting code into chat. Selection context is cached and deduplicated across turns; pasted code is not.

### Specific over general

A turn that says "rename `oldHandler` to `newHandler` across `src/api/`" is cheaper than "clean up the API module". The first scopes the search; the second forces exploration.

### Batch similar work

If you have five similar edits, ask for all five at once. The agent reads the project structure once and applies the pattern. Five separate turns each re-load context.

## Common waste patterns

| Pattern | Why it wastes | Fix |
|---------|---------------|-----|
| Re-pasting the same code each turn | Context grows linearly with turns | Use IDE selection or pointer (`see src/foo.ts:42`) |
| Asking for explanation + code together | Doubles output | Ask for one. Re-ask for the other if needed. |
| Long role-framing prompts | Burns context every turn | Move role to `AGENTS.md`. Reference it. |
| Frontier model for triage | 25–50x more expensive than necessary | Default to Mini; route up only when needed |
| No tests → agent guesses | Each guess costs a turn | Add a test that pins the behavior first |
| Re-deriving knowledge instead of querying wiki | Repeats research | Use the wiki; that's why it exists |

## Format constraints

Tell the agent the format you want. Short formats cost less.

- "Diff only, no prose."
- "JSON, no fenced block."
- "≤ 5 bullets."

The agent honors these and stops earlier.

## Monitoring per CLI

| CLI | Cost command | What it shows |
|-----|--------------|---------------|
| Claude Code | `/cost` (in-session) | Cumulative tokens + estimated USD for this session |
| Codex | `codex usage` | Same, plus per-model breakdown |
| Pi | `pi -p "/cost"` or `pi --mode json` + read the cost event stream | Tokens per request; cumulative session |

Wire these into the orchestration daemon's cost-tracking ADR. See [Orchestration](./07-orchestration.md).

## Token-budget guidelines per task type

| Task type | Reasonable budget (Standard tier) |
|-----------|-------------------------------------|
| Triage / classify a ticket | 1–5k tokens |
| Generate a single file (~200 lines) | 10–30k |
| Refactor across ≤ 5 files | 30–80k |
| Plan a feature (spec mode) | 50–100k |
| Deep research (multi-agent) | 200k–1M (Opus, 1M context) |

If a task consistently exceeds its budget, the diagnosis is upstream: the project structure is not navigable, or the skill is missing, or the prompt is general where it should be specific.
