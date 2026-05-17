# .codex/ — Codex overlay

Codex (OpenAI) reads:
- `../AGENTS.md` (canonical)
- `../CODEX.md` (this CLI's overlay)
- `instructions.md` (this directory)

Skills, agents, rules, and memories live under `../.agent-os/` so they're shared
across Claude, Codex, and Pi.

## Invocation
```
codex                              # interactive
codex -p "your prompt here"        # one-shot
codex exec --sandbox-mode workspace-write -p "..."  # bypass for orchestration
```

## Customization
- `instructions.md` is loaded as Codex's project context.
- Per-Codex sub-agents (if Codex adds them) go here. Prefer `../.agent-os/agents/`
  for portability.

## Model selection
The orchestration daemon picks the model per-role from each AGENT.md's
`model_preference.codex` field.
