# 12 — Pi integration

[Pi](https://pi.dev/) is a minimal terminal coding harness from earendil-works.
It's deliberately less feature-rich than Claude Code or Codex out of the box —
features like MCP, sub-agents, and plan mode are extensions you install
separately. This makes Pi the leanest of the three CLIs and an excellent third
voice in a multi-agent setup.

## Install

```bash
curl -fsSL https://pi.dev/install.sh | sh
# or
npm install -g @earendil-works/pi-coding-agent
```

## Invocation modes

| Mode | Command | Use case |
|---|---|---|
| Interactive TUI | `pi` | Manual work |
| Print | `pi -p "prompt"` | One-shot, shell-scriptable |
| JSON | `pi --mode json` | JSON RPC over stdin/stdout — orchestration daemon |
| Embedded | (SDK) | Programmatic from your own program |

## Config files Pi reads

- `AGENTS.md` (canonical, shared across all 3 CLIs)
- `PI.md` (Pi-specific overlay)
- `SYSTEM.md` (Pi's system-prompt customization)
- `.pi/` (Pi-local config)
- `~/.pi/config.json` (per-user)

## How the Framework wires Pi

When you run `init-project.sh` with Pi enabled:
- `template/PI.md.tmpl` → `PI.md` (project root)
- `template/SYSTEM.md.tmpl` → `SYSTEM.md` (project root)
- `template/.pi/SYSTEM.md.tmpl` → `.pi/SYSTEM.md` (overlay)
- `template/.pi/README.md` → `.pi/README.md`

Skills, agent role files, rules, hooks, memories — all live in `.agent-os/`,
shared across Claude Code, Codex, and Pi. Pi loads skills as **capability
packages** on demand; the framework's `scripts/skill-pull.sh` is how you fetch
a named skill into a project's `.agent-os/skills/`.

## Pi extensions you'll likely want

Pi's core omits MCP, sub-agents, and plan mode. For feature parity with Claude
Code / Codex:
- `pi-subagents` — TypeScript-based sub-agent dispatch
- `pi-plan-mode` — separates planning from execution
- `pi-mcp-bridge` — talks to Anthropic MCP servers
- (your team's own) — custom extensions via the Pi TS SDK

Install with `pi extension add <name>` or `npm i -g @<scope>/<pkg>`.

## Differences vs Claude Code / Codex

| Capability | Claude Code | Codex | Pi |
|---|---|---|---|
| Sub-agents | built-in | built-in (newer) | extension |
| Plan mode | built-in | built-in (newer) | extension |
| MCP | built-in | extension | extension |
| Skills | built-in | via AGENTS.md | capability packages |
| Mid-session model switch | yes | yes | yes (`/model`, `Ctrl+L`) |
| Session branching | no | no | yes (tree-structured history) |
| Real-time steering | partial | partial | `Enter` interrupts, `Alt+Enter` follow-up |
| JSON-RPC stdin/stdout | no | partial | yes — first-class |
| 15+ model providers | no | no | yes (Anthropic/OpenAI/Google/Bedrock/...) |

## Pi-specific patterns the Framework leverages

1. **Provider switching mid-task**. Pi can hand off from a strong reasoner
   (Opus/GPT-frontier) to a fast cheap model (Haiku/Flash) for the
   implementation phase, without restarting the session.

2. **Session branching**. When exploring a risky approach, branch off, try it,
   and discard or merge. The orchestration daemon does this implicitly via the
   verdict-loop, but for interactive use it's a strong Pi feature.

3. **JSON-RPC adapter**. The orchestration daemon's `pi_adapter.py` uses Pi's
   `--mode json` for structured I/O, which is more reliable than stdout parsing.

## Verdict envelope (Pi-specific)

When the orchestration daemon spawns Pi, it parses verdict from the LAST LINE of
Pi's stdout (same format as Claude/Codex). For the JSON-RPC path, the verdict
is the final message of type `assistant.completion` with a `verdict` field.

See `orchestration/adapters/pi_adapter.py` for the exact contract.

## Related
- [.pi/README](../template/.pi/README.md)
- [PI.md.tmpl](../template/PI.md.tmpl)
- [orchestration/adapters/pi_adapter.py](../orchestration/adapters/pi_adapter.py)
- [prompt-refiners/pi/SKILL.md](../skills/prompt-refiners/pi/SKILL.md)
