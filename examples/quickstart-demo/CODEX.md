# quickstart-demo — Codex CLI Overlay

> **Source of truth: `AGENTS.md`.** Read that first. This file only adds
> Codex-specific notes that don't generalize to Claude Code or Pi.

## What Codex adds on top of AGENTS.md

### Instructions file

Codex reads `.codex/instructions.md` on session start in addition to
`AGENTS.md`. The instructions file is short — it points at `AGENTS.md`,
declares a model preference, and lists active rule files.

### Configuration

Per-project config lives in `.codex/config.toml` (newer Codex CLI) or
`.codex/settings.json`. Relevant keys:

```toml
# .codex/config.toml
model = "gpt-5-codex"           # or "gpt-5", "o4-mini-codex", etc.
approval_mode = "suggest"        # suggest | auto-edit | full-auto
sandbox_policy = "workspace-write"
project_doc = "AGENTS.md"
```

`approval_mode = "full-auto"` corresponds to autonomy_mode M2/M3 in
`.agent-os/settings.json`.

### Sandbox policy

Codex sandboxes shell commands by default. Policies:

| Policy | What it allows |
|---|---|
| `read-only` | M0/M1 — file reads only |
| `workspace-write` | M2 — writes within the repo |
| `danger-full-access` | M3 — anything (auto-commit etc.) — avoid for shared repos |

The Framework's `init-project.sh` writes `workspace-write` by default and
notes M3 as opt-in.

### Model selection

Recommended model for this project: see `.codex/config.toml`.

- **Long planning sessions**: `gpt-5-codex` (or successor) at `reasoning_effort = "high"`.
- **Quick edits**: `gpt-5-codex` at `reasoning_effort = "low"`.

### Tool surface

Codex exposes `shell`, `apply_patch`, `read_file`, `update_plan`. The
post-edit hook still fires through the Framework's `.agent-os/hooks/`
dispatcher (Codex calls them via the project's `pre_post_tool` hook config
if present, or the user wires them).

### MCP servers

Codex supports MCP. Per-project MCP servers are declared in
`.codex/mcp.json`. The Framework leaves this empty by default.

### What Codex does NOT auto-do

- It does NOT auto-push.
- It does NOT bypass approval prompts at `approval_mode = "suggest"`.
- It does NOT modify `wiki/raw/`.

## Pointers

- `AGENTS.md` — entry doc, conventions, slot table
- `.codex/instructions.md` — short Codex-only instructions file
- `.agent-os/rules/*.md` — coding rules (read by Codex via AGENTS.md
  reference and instructions.md)
- `.agent-os/hooks/` — hook scripts (Codex invokes them post-shell)
- `wiki/SCHEMA.md` — wiki conventions
- `wiki/PLAN.md`, `wiki/STATUS.md` — plan + state

<!-- END -->
