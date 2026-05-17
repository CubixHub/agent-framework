# quickstart-demo — Pi CLI Overlay

> **Source of truth: `AGENTS.md`.** Pi also reads `SYSTEM.md` as its system
> prompt. This file points at AGENTS.md + adds Pi-specific notes.

Pi (pi.dev / Earendil Works) is a TypeScript-extensible coding agent built
around **capability packages**. Skills, sub-agents, and integrations are all
distributed as Pi capability packages.

## What Pi adds on top of AGENTS.md

### Files Pi reads on startup

| File | Role |
|---|---|
| `AGENTS.md` | Project context (canonical, shared with Claude / Codex) |
| `SYSTEM.md` | Pi-specific system prompt customization |
| `.pi/SYSTEM.md` | (optional) further overlay; loaded after `SYSTEM.md` |
| `.pi/config.json` | Pi CLI settings (provider, model, capability packages) |

### Capability packages

Pi loads "capability packages" — TypeScript bundles that expose skills,
sub-agents, and tools. Skills from this Framework are distributed in two
shapes:

1. **As `.agent-os/skills/<name>/`** (canonical, shared with Claude / Codex).
   Pi loads them through its `agent-os-adapter` package which scans
   `.agent-os/skills/` and registers each SKILL.md as a Pi skill.
2. **As native Pi capability packages** under `.pi/capabilities/<name>/`,
   for skills that need TypeScript runtime extensions.

Configure which packages auto-load via `pi config capabilities add <pkg>`
or by editing `.pi/config.json`.

### Print mode vs JSON mode

Pi supports two invocation modes:

- **Print mode** (`pi run "<task>"`): one-shot, streams output. Use for
  scripted automation, CI checks, smoke tests.
- **JSON mode** (`pi run --json`): emits structured events on stdout.
  Use for the orchestration daemon (see `orchestration/` in the Framework).

The Framework's `orchestration/` daemon talks to Pi via JSON mode.

### Settings

```bash
# Set provider + model
pi config set provider anthropic            # or openai, google, etc.
pi config set model claude-sonnet-4-7        # provider-dependent

# Set approval mode (similar to autonomy_mode in .agent-os/settings.json)
pi config set approvalMode suggest          # suggest | auto-edit | full-auto
```

The Framework's `init-project.sh` writes a starter `.pi/config.json` and
prompts you to set the provider + model.

### Hooks

Pi has its own hook system distinct from Claude/Codex. The Framework
provides a thin Pi adapter that invokes `.agent-os/hooks/post-edit.sh`
from Pi's `onFileWrite` event. Set up via:

```bash
pi config hooks add onFileWrite ".agent-os/hooks/post-edit.sh"
```

### Sub-agents

Pi sub-agents are TypeScript classes. The Framework's `agents/` library
ships TypeScript stubs that Pi can register. The shared role definitions
live in `.agent-os/agents/<role>.md` (markdown spec); Pi's TypeScript
shim under `.pi/agents/<role>.ts` reads them.

### What Pi does NOT auto-do

- It does NOT auto-push.
- It does NOT modify `wiki/raw/`.

## Pointers

- `AGENTS.md` — entry doc, conventions, slot table
- `SYSTEM.md` — Pi system prompt customization
- `.pi/config.json` — Pi CLI settings
- `.agent-os/rules/*.md` — coding rules
- `.agent-os/skills/` — shared skills (Pi loads via agent-os-adapter)
- `wiki/PLAN.md`, `wiki/STATUS.md` — plan + state

<!-- END -->
