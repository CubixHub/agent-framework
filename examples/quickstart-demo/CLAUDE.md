# quickstart-demo — Claude Code Overlay

> **Source of truth: `AGENTS.md`.** Read that first. This file only adds
> Claude-Code-specific notes that don't generalize to Codex or Pi.

## What Claude Code adds on top of AGENTS.md

### Skill discovery

Skills live under two roots and are merged at session start:

| Root | Loaded for | Purpose |
|---|---|---|
| `.claude/skills/` | this project only | project-specific skills (rare; usually empty) |
| `.agent-os/skills/` | this project only | shared skills (Claude / Codex / Pi all see them) |
| `~/.claude/skills/` | every project | user-global skills |

When this Framework copies a skill into a new project, it lands in
`.agent-os/skills/<skill-name>/` and `.claude/skills/` symlinks (or copies)
it. This keeps the source of truth shared while letting Claude discover them
through its native path.

Invoke skills with the `Skill` tool. Skill SKILL.md files declare
`name`, `description`, and `triggers` (when the skill auto-loads).

### Hooks (settings.json)

`.claude/settings.json` wires:

- `UserPromptSubmit` → `.agent-os/hooks/memory-capture.py` — auto-captures
  messages beginning with `#` (project memory) or `##` (personal memory).
- `PostToolUse` with matcher `Create|Edit|ApplyPatch` →
  `.agent-os/hooks/post-edit.sh` — dispatches by file extension to the
  wiki-lint or formatter scripts.
- `PreCompact` → `.agent-os/hooks/pre-commit.sh` (optional; runs format /
  lint / typecheck before context compaction so the snapshot is clean).

### Sub-agents

Custom sub-agent definitions live in `.claude/agents/<agent-slug>.md` with
frontmatter:

```yaml
---
name: my-agent
description: When to invoke
tools: [Read, Edit, Bash]
---
```

When this Framework copies role agents from `agents/` (the sibling library),
they land in `.claude/agents/` as overlays of the shared `.agent-os/agents/`
canonical definitions.

### Slash commands

Project-specific slash commands live in `.claude/commands/<name>.md`. The
front-matter declares `description` and `argument-hint`. Claude exposes
these as `/<name>` in the prompt.

### Model selection

Claude Code picks a model from `.claude/settings.json` (`"model": "..."`)
or from the global config. Recommended:

- **Planning / reasoning**: `claude-opus-4-7` or `claude-sonnet-4-7`.
- **Quick edits / iteration**: `claude-haiku-4-7`.

### Memory commands

`#` prefix in a message → project memory (`.agent-os/memories.md`).
`##` prefix → personal memory (`~/.agent-os/memories.md`).

The `memory-capture.py` hook handles append.

### What Claude Code does NOT auto-do

- It does NOT auto-push. The user pushes.
- It does NOT bypass hooks. `--no-verify` is forbidden.
- It does NOT modify `wiki/raw/` (immutable).

## Pointers

- AGENTS.md — entry doc, conventions, slot table
- `.agent-os/rules/*.md` — coding rules
- `.agent-os/hooks/` — hook scripts
- `wiki/SCHEMA.md` — wiki conventions
- `wiki/PLAN.md` — master plan
- `wiki/STATUS.md` — current state

<!-- END -->
