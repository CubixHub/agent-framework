# Examples

Real example projects produced by `scripts/init-project.sh`. Each is a
fully-scaffolded, git-initialized project showing what your own projects will
look like after running the Framework's init script.

## `quickstart-demo/` — TypeScript + Python, all 3 CLIs, no PM tool

The minimum-config example. Generated with:

```bash
printf "quickstart-demo\nmain\ndemo\n\n3\n1\ntypescript python\n" \
  | bash scripts/init-project.sh examples/quickstart-demo
```

Inputs:
- Project name: `quickstart-demo`
- Default branch: `main`
- Owner: `demo`
- Remote URL: (blank)
- PM tool: `3) none`
- CLIs: `1) all` (claude + codex + pi)
- Languages: `typescript python`

Result: ~148 files, including:
- `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `PI.md`, `SYSTEM.md` (substituted)
- `.agent-os/` with rules, hooks, skills
- `.claude/`, `.codex/`, `.pi/` CLI overlays
- `wiki/` Karpathy LLM-Wiki scaffold (SCHEMA, PLAN, IDEAS, STATUS, log, plan/)
- `orchestration/` daemon
- An initial git commit

## Generating your own example

```bash
cd /home/boldog/Desktop/Framework
bash scripts/init-project.sh ~/my-new-project
```

The script is interactive. Pick:
- **PM tool**: `linear` if you use Linear, `plane` if self-hosted, `none` to skip.
- **CLIs**: `all` is the default; pick one specific CLI to slim the project.
- **Languages**: free text; controls which `.agent-os/rules/<lang>.md` files
  the agent reads.

## Other planned examples (not yet generated)

| Example | Inputs | Use case |
|---|---|---|
| `web-app/` | linear, all, `typescript` | Next.js + verification-first stack |
| `ml-pipeline/` | plane, claude, `python` | PyTorch + ai-engineering skills |
| `rust-cli/` | none, codex, `rust` | Cargo + clippy + mutation testing |
| `library/` | linear, all, `typescript` | Semver-disciplined headless library |

Each is `init-project.sh` with different inputs. Generate them as needed.

## Why the examples are real-generated, not static

Static example trees would lock in `{{PROJECT_NAME}}` substitutions and become
stale as `template/` evolves. Generated examples always reflect the current
state of `template/` + `scripts/init-project.sh`.

To regenerate after a Framework change:
```bash
rm -rf examples/quickstart-demo
printf "..." | bash scripts/init-project.sh examples/quickstart-demo
```
