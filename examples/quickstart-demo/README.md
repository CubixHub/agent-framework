# quickstart-demo

quickstart-demo is a `typescript python` project tracked in none. The
canonical entry point for both humans and agents is the master plan:

> See [`wiki/PLAN.md`](wiki/PLAN.md).

## Quick links

- **Master plan**: [`wiki/PLAN.md`](wiki/PLAN.md)
- **Current state & blockers**: [`wiki/STATUS.md`](wiki/STATUS.md)
- **Idea backlog**: [`wiki/IDEAS.md`](wiki/IDEAS.md)
- **Agent runtime guide**: [`AGENTS.md`](AGENTS.md)
- **Verification strategy**: [`wiki/plan/verification-strategy.md`](wiki/plan/verification-strategy.md)

## Getting started (human)

```bash
# 1. Clone & enter
git clone TBD && cd quickstart-demo

# 2. Set PM API key (gitignored)
cp .env.example .env && $EDITOR .env

# 3. Open with your agent of choice
claude    # Claude Code
codex     # OpenAI Codex
pi        # pi.dev
```

## Getting started (agent)

Read `AGENTS.md`. Apply rules from `.agent-os/rules/`. Update `wiki/STATUS.md`
at the end of each work session.

## License

See `LICENSE`.

<!-- END -->
