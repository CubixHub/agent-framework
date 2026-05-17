# Memory & Context Management (Tri-Platform)

> Applies to: Claude Code, Codex, Pi. Memory is a three-layer hierarchy plus capture triggers plus maintenance discipline. Rewrites Factory.ai's Memory & Context guide.

## The three layers

```
AGENTS.md              (references → personal → project → rules)
   └─ ~/.agent-os/memories.md          personal, all projects (your style)
   └─ .agent-os/memories.md            project, committed to repo
   └─ .agent-os/rules/<cat>.md         project, enforced on edits
```

`AGENTS.md` is the index. It does not contain memories — it points to them. CLIs read `AGENTS.md` first on every session, then load the layers it references.

| Layer | Path | Scope | Mutability |
|-------|------|-------|------------|
| Personal | `~/.agent-os/memories.md` | All your projects | Append-only by you |
| Project | `.agent-os/memories.md` | One project | Append-only by team |
| Rules | `.agent-os/rules/*.md` | One project, file-matched | Curated; review on change |
| Per-CLI overlay | `~/.claude/memories.md`, `~/.codex/memories.md`, `~/.pi/MEMORIES.md` | CLI-specific quirks only | Append-only |

**Rules vs memory**: rules are enforced on file edits (a hook will reformat or flag). Memories are read at session start and influence decisions but don't gate edits. If you want behavior to be enforced, write a rule + hook. If you want behavior to be considered, write a memory.

## Capture triggers

Memories are captured when something non-obvious is learned or decided. Two trigger mechanisms:

### `#` prefix (explicit)

Any line in chat starting with `#` is interpreted as a memory candidate by the framework's pre-submit hook. Example:

```
# Use pnpm in this repo, not npm — workspaces depend on it
```

The hook proposes the destination (personal vs project) and appends with a dated bullet.

### Phrase triggers (implicit)

The hook also scans for phrases that signal a decision-shaped statement:
- "we decided…", "going forward…", "remember that…", "from now on…", "note that…"

When matched, the hook surfaces a confirm prompt: *propose appending to <path>?*

## Per-CLI hook config

The triggers are wired the same way conceptually; each CLI's hook surface differs.

### Claude Code

`~/.claude/settings.json` → `hooks.UserPromptSubmit`:

```jsonc
{
  "hooks": {
    "UserPromptSubmit": [
      { "matcher": "*", "command": "${HOME}/.agent-os/hooks/memory-capture.sh" }
    ]
  }
}
```

The hook receives the prompt on stdin, scans for `#` or phrase triggers, and emits a `systemMessage` proposing the append.

### Codex

`~/.codex/config.toml` → `[hooks]` table with `on_prompt_submit` pointing to the same script. Codex passes the prompt via the `CODEX_PROMPT` env var; the shared script reads both stdin and env for portability.

### Pi

Pi has no built-in hooks. Install the `memory-capture` capability package (Pi extension) which subscribes to the `prompt.submit` event in Pi's JSON-RPC stream:

```bash
pi install @framework/memory-capture
```

The extension forwards to the same script. See [Pi integration](./12-pi-integration.md) for the extension model.

## Maintenance

Memories rot. Schedule:

- **Monthly review** — read `.agent-os/memories.md` top-to-bottom; archive entries that are no longer true.
- **Archive, don't delete** — move stale entries to `.agent-os/memories-archive.md` with a dated note explaining why they're archived. Deletion erases the audit trail.
- **Promote recurring decisions to rules** — if a memory is referenced more than 3 times in a quarter, it's a rule, not a memory. Move it to `.agent-os/rules/<cat>.md` and wire enforcement.
- **Demote rules with no enforcement** — if a rule has no hook to enforce it, it's a memory pretending to be a rule. Move it back.

### Cap entries

- Personal: ~50 entries. Beyond that, file by topic into `~/.agent-os/memories/<topic>.md` and have the main file index them.
- Project: ~30 entries. Same overflow pattern under `.agent-os/memories/<topic>.md`.

### Audit log

Every memory mutation is a single-line append to `wiki/log.md`:

```
2026-05-17  memory  +.agent-os/memories.md  "Use pnpm; workspaces depend on it"
```

The memory-capture hook writes this entry automatically when it accepts an append. The log is the audit trail when a decision is later challenged.

## Memory-aware skills

A skill is memory-aware when its `SKILL.md` declares `reads:` in its frontmatter:

```yaml
---
name: <skill>
description: <one line>
reads:
  - .agent-os/memories.md
  - .agent-os/rules/<cat>.md
---
```

The agent loads those files into context before running the skill body. This keeps skills honest — a skill that says "follow the project's lint rules" but doesn't read `.agent-os/rules/_base/general.md` is performative.

Two reference skills:

- `skills/llm-wiki/` reads the wiki layout and SCHEMA before any ingest.
- `skills/post-edit-hook/` reads the matched rule file before deciding what enforcement step to run.

## Cross-references

- [Rules and conventions](./03-rules-conventions.md) — how rules diverge from memories
- [Context compression](./06-context-compression.md) — what to do when memories grow past the context window
- `skills/skill-discovery/SKILL.md` — the mandatory pre-task scan that itself reads memory layers
- `PROJECT-TEMPLATE-SPEC.md` §4 — the project-wide config surfaces
