# Power User Setup Checklist (Tri-Platform)

> Applies to: Claude Code, Codex, Pi. Five levels — Essential → Optimized. Each level is a discrete commit. New users do L1 only; power users complete L5.

## L1 — Essential (install + identity)

The minimum to drive any of the three CLIs against the Framework.

### Install the CLIs

```bash
# Claude Code (Anthropic)
# Install per https://docs.anthropic.com/en/docs/claude-code/ (npm or curl installer)
claude --version

# Codex (OpenAI)
npm i -g @openai/codex
codex --version

# Pi (earendil-works, pi.dev)
curl -fsSL https://pi.dev/install.sh | sh
pi --version
```

### Author the entry-point docs

Every project root has:

| File | Owner | Purpose |
|------|-------|---------|
| `AGENTS.md` | canonical | Single entry doc every CLI reads first |
| `CLAUDE.md` | overlay | Claude-specific deltas; usually points to AGENTS.md |
| `CODEX.md` | overlay | Codex-specific deltas; usually points to AGENTS.md |
| `PI.md` | overlay | Pi-specific deltas; references `.pi/SYSTEM.md` |

The overlays are short (1 screen). They do not duplicate AGENTS.md — they restate "read AGENTS.md, here are the per-CLI quirks". Template skeletons live at `template/`.

### Pick a default model per CLI

Set the default in each CLI's config so you don't pay frontier prices for trivia.

- **Claude Code**: `~/.claude/settings.json` → `"model": "claude-sonnet-4-5"` (or `claude-haiku-4-5` for routine work)
- **Codex**: `~/.codex/config.toml` → `model = "gpt-5-codex"` (or `o4-mini` for routine work)
- **Pi**: `~/.pi/SYSTEM.md` declares model; or per-invocation `pi --model <id>`

See [Token efficiency](./05-token-efficiency.md) for the model-selection strategy table.

## L2 — Memory (project + personal)

Memory is structured, not free-form. Two files per CLI, plus shared:

- `~/.agent-os/memories.md` — personal, cross-project (your style, your defaults)
- `.agent-os/memories.md` — project, committed to repo (project decisions)
- Per-CLI overlay: `~/.claude/memories.md`, `~/.codex/memories.md`, `~/.pi/MEMORIES.md` — CLI-specific quirks only

AGENTS.md references all of these. Capture rules: see [Memory management](./02-memory-management.md).

## L3 — Rules (project conventions)

`.agent-os/rules/` with one file per category:

```
.agent-os/rules/
├── _base/general.md     Universal rules (commit style, push policy, secret handling)
├── frontend/<lang>.md   Per-stack frontend rules
├── backend/<lang>.md    Per-stack backend rules
└── testing/<framework>.md
```

Each rule file is one screen. Format: **Applies to / Rule / Example / Rationale**. See [Rules and conventions](./03-rules-conventions.md).

## L4 — Skills + automation

### Skill-discovery first

Before adding hooks, ensure the **skill-discovery** skill is installed. It is the cornerstone meta-skill — every agent invokes it before taking action, scans `skills/` for a match, and only proceeds without a skill if none applies. See [Skills discovery](./08-skills-discovery.md).

```
skills/
├── skill-discovery/SKILL.md      mandatory; the decision tree
├── llm-wiki/SKILL.md             wiki ingest/query/lint
├── context-compression/SKILL.md  anchored summary at the end of long sessions
├── post-edit-hook/SKILL.md       reference implementation for the post-edit dispatcher
└── prompt-refiners/<role>/       reusable system prompts
```

Per-CLI loading mechanism:

- **Claude Code**: skills live at `.claude/skills/<name>/SKILL.md` and `~/.claude/skills/<name>/SKILL.md`. Loaded automatically; invoked by the agent via the `Skill` tool.
- **Codex**: skills live as files referenced from `AGENTS.md`. Codex reads `AGENTS.md`; the file's "Available skills" section is the index. Invocation is via natural-language reference (the agent reads the body inline).
- **Pi**: skills install as capability packages on demand: `pi install @framework/<skill>`. Pi pulls the package into `~/.pi/capabilities/<skill>/` and exposes its tools over JSON-RPC.

### Hooks (after skill-discovery is wired)

```
.agent-os/hooks/
├── post-edit.sh        format + lint + rule check on every Write/Edit
├── pre-commit.sh       (optional) re-run on commit; cannot be bypassed
├── memory-capture.sh   trigger on prompt submit
└── wiki-lint.sh        wikilink scanner (informational, never blocks)
```

Wire into each CLI per [Rules and conventions](./03-rules-conventions.md) §Auto-enforcement.

## L5 — Token optimization

The last 10% — make the harness cheap to run, fast to converge.

### Model tier per task class

| Task class | Recommended tier | Why |
|------------|------------------|-----|
| Triage / classify / route | Haiku-tier / mini-tier | Sub-cent per call; latency matters |
| Edit / refactor / generate | Sonnet-tier / standard | Quality threshold without frontier cost |
| Plan / architect / decide | Opus-tier / frontier | Worth the multiplier when reversal is expensive |
| Verify / scrutinize | Sonnet-tier (different model than generator) | Anti-gaming — never grade with the same model that generated |

Full vendor-specific table: [Token efficiency](./05-token-efficiency.md).

### Spec-mode equivalents

Factory has "Spec Mode" — a flagged mode that asks clarifying questions before editing. Per-CLI equivalents:

- **Claude Code**: `--mode plan` (plan mode); the agent drafts a plan before applying any tool that mutates state.
- **Codex**: `codex --plan` (plan mode); same contract.
- **Pi**: no built-in plan mode. Use the `plan-mode` capability package or the universal `skills/spec-mode/SKILL.md` skill which the agent invokes explicitly.

### Readiness check

Run the readiness check before kicking off a real build session. It verifies:

- All four entry docs exist (`AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `PI.md`)
- `.agent-os/` is populated (memories, rules, hooks)
- `skill-discovery` is installed and indexed
- Hooks are wired (post-edit, memory-capture)
- Wiki has `SCHEMA.md`, `index.md`, `PLAN.md`, `STATUS.md`, `IDEAS.md`
- Build / test / lint / typecheck / format slot table in `AGENTS.md` is filled
- Default model is set per CLI

See `skills/readiness-check/SKILL.md` for the runnable check. CI runs it on every commit to `.agent-os/` paths.

## Done criterion

You've completed L1..L5 when the readiness-check skill returns PASS on a fresh clone for each of `claude`, `codex`, `pi`.
