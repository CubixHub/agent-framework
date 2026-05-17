---
name: prompt-refiners
description: Index for the three platform-specific prompt refiners — Claude, Codex/GPT, Pi — with a decision tree for which pattern to apply to a given target CLI
---

# When to use

User says any of: "rewrite this prompt for X", "make this work better with model Y", "port this prompt to Claude/Codex/Pi", "my prompt isn't getting good results from <model>". Pick the refiner matching the target model family.

# Decision tree

```
Target model family:
├── Claude (Anthropic) / Claude Code / Sonnet / Opus / Haiku  → claude/SKILL.md
├── GPT / Codex / OpenAI / o-series / GPT-4/5                 → codex/SKILL.md
└── Pi (pi.dev) / pi -p / pi --mode json                      → pi/SKILL.md
```

Cross-cutting rule: the same prompt rewritten for different model families WILL diverge. Stop trying to write one prompt that works everywhere; that produces lowest-common-denominator results.

# How to execute

1. Read the source prompt. Identify intent, context, constraints, expected output format, examples.
2. Read the target sub-skill's SKILL.md.
3. Apply the platform-specific pattern (XML tags for Claude, role+steps for GPT, AGENTS/SYSTEM split for Pi).
4. Present before/after as a worked transformation.
5. If user requests, test the new prompt on the target CLI and iterate once.

# Refiner pattern summary (decision-shortcut)

| Target | Structuring primitive | Reasoning trigger | Output format trigger |
|---|---|---|---|
| Claude | XML tags `<context>/<task>/<requirements>/<constraints>` | "Think through" or `<thinking>` block | Tell Claude the exact shape; show 1-2 examples |
| Codex/GPT | "You are a ..." role + numbered steps | "Step by step" / "Let's think" | Explicit "Respond as JSON matching schema X" |
| Pi | `AGENTS.md` for project, `SYSTEM.md` for role, capability-package for on-demand skills | Pi reasons by default — don't over-trigger | `pi -p` for print mode, `--mode json` for parseable |

# Anti-patterns (all three platforms)

- "Be helpful" — instruct, don't hope.
- Examples that don't match the task. Examples teach format; mismatched examples mislead.
- 5 nested levels of constraints. Flatten.
- Output format ambiguity. Pick one shape and exemplify it.

# Reference

- Anthropic prompt engineering docs (Claude pattern)
- OpenAI prompt engineering guide (GPT pattern)
- Pi docs at https://pi.dev/ (Pi pattern)
