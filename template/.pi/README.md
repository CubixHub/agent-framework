# .pi/ — Pi overlay

Pi (https://pi.dev/) reads:
- `../AGENTS.md` (canonical)
- `../PI.md` (this CLI's overlay)
- `SYSTEM.md` (system prompt)

## Invocation
```
pi                          # interactive TUI
pi -p "your prompt"         # one-shot print mode
pi --mode json              # JSON RPC over stdin/stdout (orchestration uses this)
```

## Pi's extension model
Pi deliberately omits MCP, sub-agents, and plan mode from the core. These come
via TypeScript extensions or third-party packages from npm/git. To add them:
- `npm install <pi-extension>` (or git clone)
- Reference in `pi config` or `~/.pi/config.json`

## Skills as capability packages
Pi loads skills on-demand from `.agent-os/skills/`. The `skill-pull.sh` script
in `Framework/scripts/` can pull a skill from the Framework library into this
project on demand.

## Customization
- `SYSTEM.md` here overrides default behavior.
- Sub-agents are TypeScript extensions; install separately.
- For full feature parity with Claude Code, install the Pi extensions for
  sub-agents and plan mode.
