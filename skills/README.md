# Skills library

Reusable agent capability packages. Loaded on-demand by Claude Code, Codex, and Pi.

**Cornerstone rule**: invoke `skill-discovery` BEFORE any other tool call on every
task. If no skill matches with ≥30% confidence, invoke `skill-creator` to make one.
Never improvise where a skill could exist.

## Discovery & meta
- [skill-discovery](skill-discovery/SKILL.md) — must be invoked first on every task
- [skill-creator](skill-creator/SKILL.md) — port of Anthropic's; build new skills

## Process (rigid — follow exactly)
- [brainstorming](brainstorming/SKILL.md) — explore intent before any creative work
- [test-driven-development](test-driven-development/SKILL.md) — red-green-refactor
- [systematic-debugging](systematic-debugging/SKILL.md) — hypothesis-first, 7-step
- [verification-first](verification-first/SKILL.md) — 7-layer + 4-tier + 4-anti-gaming
- [parallel-dispatch](parallel-dispatch/SKILL.md) — strict-chunked sub-agents
- [requesting-code-review](requesting-code-review/SKILL.md) — mandatory before merge
- [receiving-code-review](receiving-code-review/SKILL.md) — rigor over performative agreement

## Engineering domains
- [matt-pocock/](matt-pocock/README.md) — TypeScript / testing / errors / API design
- [ai-engineering/](ai-engineering/README.md) — model design / train / finetune / deploy / eval
- [deep-research/](deep-research/SKILL.md) — OODA multi-step research with citations
- [llm-wiki](llm-wiki/SKILL.md) — Karpathy LLM-Wiki ingest/query/lint (used by the `wiki-curator` agent)
- [context-compression](context-compression/SKILL.md) — anchored iterative summarization

## Prompting
- [prompt-refiners/](prompt-refiners/README.md) — Claude / Codex / Pi pattern refiners

## How agents load skills

| CLI | Mechanism |
|---|---|
| Claude Code | `.claude/skills/` or via `Skill` tool over `.agent-os/skills/` |
| Codex | AGENTS.md reference + skill files in `.agent-os/skills/` |
| Pi | Capability packages installed on-demand from `.agent-os/skills/` |

## Skill anatomy

```
skill-name/
├── SKILL.md            # frontmatter + when-to-use + how-to-execute
└── reference/          # depth material referenced by SKILL.md
    ├── flowchart.md
    └── examples.md
```
