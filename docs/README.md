# Power-User Docs

Tri-platform guides for running the Framework with three coding CLIs:

- **Claude Code** (Anthropic, `claude`)
- **Codex** (OpenAI, `codex` via `npm i -g @openai/codex`)
- **Pi** ([pi.dev](https://pi.dev/) — minimal terminal harness with print mode `pi -p`, JSON RPC mode `pi --mode json`, AGENTS.md + SYSTEM.md, on-demand capability-package skills)

These docs are rewrites of Factory.ai's power-user guides, retargeted for the three CLIs above and operationalized against the Framework's standard layout: `.agent-os/`, `.claude/`, `.codex/`, `.pi/`, `wiki/`, `AGENTS.md` + `CLAUDE.md` + `CODEX.md` + `PI.md`, `skills/`, `agents/`, `orchestration/`, `integrations/{linear,plane}/`.

## Reading order for new users

| # | Doc | Why read it |
|---|-----|-------------|
| 01 | [Setup checklist](./01-setup-checklist.md) | 5-level ramp from raw install to optimized power user |
| 02 | [Memory management](./02-memory-management.md) | Three-layer memory model + capture triggers + maintenance |
| 03 | [Rules and conventions](./03-rules-conventions.md) | Rules vs memory vs skills; auto-enforcement via hooks |
| 04 | [Prompt crafting](./04-prompt-crafting.md) | Universal + per-CLI techniques; model selection table |
| 05 | [Token efficiency](./05-token-efficiency.md) | Cost-aware workflows, readiness check, waste patterns |
| 06 | [Context compression](./06-context-compression.md) | Tokens-per-task, probe-based eval, anchored summary |
| 07 | [Orchestration](./07-orchestration.md) | Symphony-style daemon, verdict routing, escalation chain |
| 08 | [Skills discovery](./08-skills-discovery.md) | Why skills must be discovered; the decision tree |
| 09 | [Deep research](./09-deep-research.md) | Multi-agent research with OODA budget and wiki file-back |
| 10 | [Autonomy modes](./10-autonomy-modes.md) | M0..M3 ladder; terminal-state invariant |
| 11 | [PM tool choice](./11-pm-tool-choice.md) | Linear vs Plane decision matrix |
| 12 | [Pi integration](./12-pi-integration.md) | Pi specifics: install, CLI surface, capability packages |

## Cross-references

- `skills/` — executable patterns referenced from these docs
- `agents/` — sub-agent definitions (scrutinizer, parent-ai, operator, etc.)
- `orchestration/` — Symphony-style daemon source
- `integrations/{linear,plane}/` — PM tool adapters

These docs link out; they do not duplicate code or skill bodies. When a doc says "see `skills/foo/`", read that skill's `SKILL.md` for the runnable steps.

## Tone & scope

Terse, professional, tri-platform-aware. Each doc opens with **applies-to** scope, then the canonical Factory-style content, then per-CLI deltas, then cross-refs. Code is not generated here — link to `skills/` instead.

## What's intentionally out of scope

- Vendor pricing tables (links to vendor pages instead — pricing moves)
- Per-language style guides (live in `.agent-os/rules/<lang>.md` per project)
- Build/test runner specifics (live in each project's `AGENTS.md` slot table)
- Wiki ingest mechanics (see `skills/llm-wiki/` and the Karpathy LLM-Wiki pattern in `PROJECT-TEMPLATE-SPEC.md` §2)

## Versioning

These docs target the Framework template as of 2026-05. Per-CLI commands and flags are accurate as of that date. When a vendor changes its surface, update the per-CLI section in place and append a dated entry to `wiki/log.md`.
