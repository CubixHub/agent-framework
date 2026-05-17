# Install Prerequisites

> **One-line install:** `npx github:cubixhub/agent-framework my-app` — no
> install step needed if you have Node + bash + git.

The Framework targets three coding CLIs. Install whichever you plan to use;
the init script auto-detects which CLIs you have and configures accordingly.

## Path A — npx (no install required)

```bash
npx github:cubixhub/agent-framework my-new-app
```

Requires:
- Node 18+ (which provides `npx`)
- `bash` (built-in on macOS/Linux; on Windows use WSL or Git Bash)
- `git`

The npx command pulls the repo, runs the scaffolder, and creates your project.

## Path B — clone + install CLIs

If you want all three coding agents (Claude / Codex / Pi) installed too:

```bash
git clone https://github.com/cubixhub/agent-framework.git
cd agent-framework
bash scripts/install-prereqs.sh
bash scripts/init-project.sh ~/path/to/my-new-app
```

`install-prereqs.sh` detects macOS / Debian / Ubuntu and installs everything
below. Falls back to manual instructions on other platforms.

## The three CLIs

### Claude Code (Anthropic)

```bash
# Recommended: official installer (see https://claude.com/claude-code)
curl -fsSL https://claude.com/install.sh | sh

# Alternative: npm global
npm install -g @anthropic-ai/claude-code
```

Verify: `claude --version`. Auth: `claude login`.

### Codex (OpenAI)

```bash
npm install -g @openai/codex
```

Verify: `codex --version`. Auth: `codex login` (uses your ChatGPT credentials).

### Pi (pi.dev / Earendil Works)

```bash
# Recommended: official installer
curl -fsSL https://pi.dev/install.sh | sh

# Alternative: npm global
npm install -g @earendil-works/pi-coding-agent
```

Verify: `pi --version`. Auth: `pi config` then set `provider` and `apiKey`.

## Shared dependencies

| Tool | Min version | Use |
|---|---|---|
| `python` | 3.11+ | `memory-capture.py` hook + helper scripts |
| `jq` | any recent | hook JSON parsing |
| `tmux` | 3.0+ | orchestration daemon |
| `git` | 2.30+ | obvious |
| `bash` | 5.0+ | scripts use `set -euo pipefail` |
| `node` | 20+ | only if installing CLIs via npm |

### macOS

```bash
brew install python@3.11 jq tmux git
```

### Debian / Ubuntu

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip jq tmux git
```

### Arch

```bash
sudo pacman -S python jq tmux git
```

### Windows

Use WSL2 (Ubuntu). Run the Debian/Ubuntu instructions inside WSL.

## PM tool API keys

You'll set one of these during `init-project.sh`. They land in your project's
`.env` (gitignored).

### Linear

1. https://linear.app/settings/api
2. Create personal API key.
3. Add `LINEAR_API_KEY=lin_api_xxx` to `.env`.

### Plane

1. Plane Settings → API tokens.
2. Add to `.env`:
   ```
   PLANE_API_KEY=...
   PLANE_BASE_URL=https://app.plane.so   # or your self-hosted URL
   PLANE_WORKSPACE_SLUG=your-workspace
   ```

## Skill verification

After scaffolding a project:

```bash
cd <your-project>
bash .agent-os/hooks/wiki-lint.sh </dev/null   # exit 0 with no input
bash ../Framework/scripts/verify-install.sh
```

`verify-install.sh` reports which CLIs are found, validates wiki structure,
runs the wiki-link scanner, and prints a readiness verdict.

## Troubleshooting

- **`claude: command not found`** — installer added to a shell rc you haven't
  reloaded. `exec $SHELL -l`.
- **`pi` is shadowed by Python's `pi`** — alias `picli=$(which -a pi | tail -1)`.
- **`codex login` opens a browser** — that's expected; finish the OAuth flow.
- **`jq` parse errors in hooks** — pipe `tool_input` through `jq -e` to debug.

<!-- END -->
