# @cubixhub/agent-framework — A Tri-CLI Agent-Native Project Scaffolder

> Spin up a new software project optimized for three coding agents in parallel:
> **Claude Code** (Anthropic), **Codex** (OpenAI), **Pi** ([pi.dev](https://pi.dev/)).
> One source of truth, three CLI overlays, one wiki, one verification gate.

## Quickstart (one command)

```bash
# Scaffold a new project in any directory:
npx github:cubixhub/agent-framework my-new-app
```

That's it. The command will prompt you interactively for project name, branch,
PM tool (Linear / Plane / none), which CLIs to enable, and languages. It then
copies `template/` to your chosen target, substitutes `{{PLACEHOLDERS}}`, runs
`git init`, makes an initial commit, and prints next-step instructions.

### Alternate invocations

```bash
# Without specifying target (you'll be asked):
npx github:cubixhub/agent-framework

# Clone the repo first if you prefer:
git clone https://github.com/cubixhub/agent-framework.git
cd agent-framework
bash scripts/install-prereqs.sh   # install claude, codex, pi, jq, tmux
bash scripts/init-project.sh ~/path/to/my-new-app
```

`init-project.sh` is interactive: it prompts for project name, default branch,
PM tool (Linear / Plane / none), enabled CLIs, and language stack. It then
copies `template/` to your chosen target, substitutes `{{PLACEHOLDERS}}`,
runs `git init`, makes an initial commit, and prints next-step instructions.

## The 4 architectural pillars

1. **Tri-CLI symmetry.** `AGENTS.md` is the single source of truth; all three
   CLIs read it. `CLAUDE.md`, `CODEX.md`, `PI.md` are thin overlays. Per-CLI
   config goes under `.claude/`, `.codex/`, `.pi/` — but agent runtime rules,
   skills, hooks, and memories all live under `.agent-os/` (shared).
2. **Karpathy LLM-wiki.** Every project gets a living `wiki/` (sources →
   entities → concepts → questions → ideas → plan). Agents persist findings to
   the wiki on every session. No more re-deriving from raw on every query.
3. **Symphony-style orchestration.** A daemon under `orchestration/` lets you
   run multiple agents in parallel against the same wiki + PM backlog,
   coordinating via wiki + Linear/Plane state, not by polling each other.
4. **Verification-first.** The 7-layer + 4-tier + 4-anti-gaming verification
   stack (see `wiki/plan/verification-strategy.md`) is scaffolded from day one.
   No work is "done" until verification returns PASS.

## Directory tree

```
agent-framework/
├── README.md, INSTALL.md, CHANGELOG.md, LICENSE, DELIVERY.md
├── PROJECT-TEMPLATE-SPEC.md    full design rationale
├── package.json + bin/agent-framework.js  (npx entry point)
├── template/            copied verbatim into new projects
│   ├── AGENTS.md.tmpl   universal entry doc (all 3 CLIs)
│   ├── CLAUDE.md.tmpl   Claude Code overlay
│   ├── CODEX.md.tmpl    Codex overlay
│   ├── PI.md.tmpl       Pi overlay
│   ├── SYSTEM.md.tmpl   Pi system prompt
│   ├── LICENSE.tmpl     MIT (substitutes owner + date)
│   ├── .agent-os/       SHARED runtime config (rules, hooks, skills, memories)
│   ├── .claude/         Claude Code-specific overlay
│   ├── .codex/          Codex-specific overlay
│   ├── .pi/             Pi-specific overlay
│   └── wiki/            Karpathy LLM-wiki scaffold (SCHEMA, PLAN, IDEAS, STATUS, plan/)
├── scripts/             init-project.sh, install-prereqs.sh, verify-install.sh, skill-pull.sh
├── skills/              17 skill groups, 57 files (skill-discovery, verification-first,
│                          matt-pocock, ai-engineering, deep-research, factory-8, ...)
├── agents/              22 role definitions (architect, implementer, scrutinizer,
│                          parent-ai, wiki-curator, ml-engineer, ...)
├── orchestration/       Symphony-style poll-claim-process daemon
│                          (tri-CLI adapters + Linear/Plane PM adapters)
├── integrations/        Linear + Plane bootstrap (workflow states + role labels)
├── docs/                13 power-user guides rewritten for tri-CLI
└── examples/            quickstart-demo/ — real generated example project
```

## Links

- **Power-user docs**: see `docs/`
- **Skills library**: see `skills/`
- **Agent roles**: see `agents/`
- **Orchestration daemon**: see `orchestration/`
- **PM adapters (Linear / Plane)**: see `integrations/`
- **Design rationale**: see `PROJECT-TEMPLATE-SPEC.md`
- **Completion summary**: see `DELIVERY.md`

## License

MIT. See `LICENSE`.

## Contributing

Issues + PRs welcome at https://github.com/cubixhub/agent-framework

<!-- END -->
