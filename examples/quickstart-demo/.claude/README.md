# .claude/ — Claude Code overlay

Claude Code reads:
- `../AGENTS.md` (canonical, all 3 CLIs)
- `../CLAUDE.md` (this CLI's overlay)
- `settings.json` (hooks, skill paths, agent paths)

Skills, agents, rules, and memories all live under `../.agent-os/` so they're
shared with Codex and Pi. This directory holds only Claude-Code-specific config.

## Customization
- Add or override hooks in `settings.json`.
- Per-Claude commands go in `commands/` (e.g. `commands/audit-adrs.md`).
- Per-Claude sub-agents go in `agents/` — but prefer adding role files to
  `../.agent-os/agents/` so Codex and Pi can use them too.

## Invocation
```
claude                            # interactive
claude -p "your prompt here"      # one-shot
claude --permission-mode bypassPermissions -p "..."   # what orchestration daemon uses
```
