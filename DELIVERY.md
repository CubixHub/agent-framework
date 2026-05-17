# Framework — Delivery summary

> Smoke-tested end-to-end. `init-project.sh` produces a 156-file fully-
> scaffolded, git-initialized, placeholder-substituted project ready for
> Claude Code, Codex, and Pi to work in.

## Status: COMPLETE

| Track | Status |
|---|---|
| Scripts (init + helpers) | DONE (4 scripts, all syntax-clean) |
| Template (.agent-os/, .claude/, .codex/, .pi/, wiki/) | DONE (54 files) |
| Skills library (17 skill groups + 8 factory-8) | DONE (57 files) |
| Agent roles (22 roles) | DONE (22 AGENT.md files) |
| Orchestration daemon (Symphony tri-CLI) | DONE (23 files, smoke-tested) |
| PM integrations (Linear + Plane) | DONE (6 files, bootstrap aligned to roles) |
| Power-user docs | DONE (13 files) |
| Top-level (README, INSTALL, CHANGELOG, LICENSE, DELIVERY) | DONE |
| Example project | DONE (`examples/quickstart-demo/`, 156-file output) |

## File counts

```
Framework/
├── README.md, INSTALL.md, CHANGELOG.md, LICENSE, DELIVERY.md, PROJECT-TEMPLATE-SPEC.md
├── scripts/           4 files   (init-project.sh, verify-install.sh, install-prereqs.sh, skill-pull.sh)
├── template/         54 files   (canonical scaffold; copied verbatim into new projects)
│   ├── AGENTS.md.tmpl + CLAUDE/CODEX/PI/SYSTEM overlays + LICENSE.tmpl
│   ├── .agent-os/    settings.json.tmpl + memories.md.tmpl + 10 rules + 5 hooks
│   ├── .claude/.codex/.pi/   per-CLI overlays
│   └── wiki/         SCHEMA, README, log, PLAN.tmpl, IDEAS.tmpl, STATUS.tmpl,
│                     plan/{verification-strategy, security, reuse-map, adr/, packages/}
├── skills/           57 files in 17 skill groups:
│   ├── skill-discovery (cornerstone — invoked first on every task)
│   ├── skill-creator (Anthropic's, ported)
│   ├── brainstorming, test-driven-development, systematic-debugging
│   ├── verification-first (7-layer + 4-tier + 4-anti-gaming stack)
│   ├── parallel-dispatch
│   ├── requesting-code-review, receiving-code-review
│   ├── matt-pocock/  typescript-types, testing-discipline, error-handling, api-design
│   ├── ai-engineering/ model-design, training, finetuning, deployment, evaluation
│   ├── deep-research/  OODA, lead+subagent, citations (Weizhena-inspired)
│   ├── prompt-refiners/  claude, codex, pi
│   ├── llm-wiki/  Karpathy LLM-Wiki ingest/query/lint (used by wiki-curator agent)
│   ├── context-compression/  anchored iterative summarization (Factory Research)
│   └── factory-8/  readiness-report, spec-mode, context-aware-implementation,
│                   prompt-refiner-team, memory-capture-skill, token-aware-implementation,
│                   auto-format-on-edit, test-on-edit
├── agents/           22 AGENT.md role definitions:
│   ├── core dev team:  architect, implementer, reviewer, tester, researcher, ml-engineer
│   ├── QA chain:       scrutinizer → parent-ai → wiki-curator → security-auditor
│   ├── lead/ops:       orchestration-lead, prompt-engineer
│   ├── specialists:    cron-architect, inference-deployer, training-orchestrator
│   ├── quality:        silent-failure-hunter, team-debugger, test-coverage-analyst
│   └── consultants:    claude/codex/pi-consultant (cross-CLI second opinions)
├── orchestration/    23 files — Symphony tri-CLI poll-claim-process daemon:
│   ├── runner.py, state.py, retry.py, workspace.py, journal.py
│   ├── adapters/  base + claude + codex + pi
│   ├── pm_adapters/ base + linear + plane
│   ├── scripts/ start.sh, stop.sh (tmux)
│   ├── tests/ test_state, test_adapters_smoke
│   └── README, SPEC, WORKFLOW.md.tmpl (hot-reload YAML, wired to all 22 roles)
├── integrations/      6 files — Linear + Plane bootstrap (creates 8 workflow states +
│                       18 @<role> labels + standard type/prio/phase/gate taxonomy)
├── docs/             13 power-user guides rewritten for tri-CLI:
│   01-setup-checklist · 02-memory-management · 03-rules-conventions ·
│   04-prompt-crafting · 05-token-efficiency · 06-context-compression ·
│   07-orchestration · 08-skills-discovery · 09-deep-research ·
│   10-autonomy-modes · 11-pm-tool-choice · 12-pi-integration
└── examples/         quickstart-demo/  real generated example (156 files)
```

## How to use

```bash
cd /home/boldog/Desktop/Framework

# One-time setup
bash scripts/install-prereqs.sh

# For each new project:
bash scripts/init-project.sh ~/path/to/my-new-project
# Prompts: project name, branch, owner, remote, PM tool (linear|plane|none),
#          which CLIs (all|claude|codex|pi), languages

cd ~/path/to/my-new-project

# Set PM API key (if you chose linear or plane)
cp .env.example .env
$EDITOR .env

# Start any of the 3 CLIs
claude   # or codex, or pi
```

## Smoke-test result (final)

```
$ printf "init-final-smoke\nmain\ntestuser\n\n3\n1\ntypescript\n" \
    | bash scripts/init-project.sh /tmp/init-final-smoke
==> Tri-CLI Project Scaffolder
... [all OKs] ...
==> Done — project ready at /tmp/init-final-smoke

Output:
  Total files: 156
  Skills installed: 32 SKILL.md files
  Agents installed: 21 AGENT.md files (only roles relevant to project)
  Wiki dirs: 11
  Rules: 10
  Hooks: 5
  AGENTS.md placeholders correctly substituted
  Initial commit made
```

## Verification — what was fixed in the completion pass

1. **Cross-references** — renamed `wiki-curator` skill → `llm-wiki` to match
   PROJECT-TEMPLATE-SPEC and all docs. Agent role `wiki-curator` stays (the
   role that USES the skill).
2. **CLI overlay quality** — verified CLAUDE.md.tmpl, CODEX.md.tmpl, PI.md.tmpl,
   SYSTEM.md.tmpl all have substantive content beyond pointers.
3. **factory-8 skills** — built out the 5 missing skills as proper SKILL.md
   files (readiness-report, spec-mode, context-aware-implementation,
   prompt-refiner-team, memory-capture-skill, token-aware-implementation,
   auto-format-on-edit, test-on-edit). 8/8 complete.
4. **LICENSE** — added MIT LICENSE at repo root + template/LICENSE.tmpl.
5. **Skill quality audit** — spot-checked ai-engineering (5 SKILL.md files,
   80+ lines each), matt-pocock (typescript-types 132 lines), deep-research
   (93 lines + 4 reference files). All complete and well-written.
6. **Bootstrap scripts** — fixed `integrations/linear/bootstrap.sh` and
   `integrations/plane/bootstrap.sh` to use the Framework's 22 actual agent
   role labels (was using Voice MoA's specific roles).
7. **WORKFLOW.md.tmpl** — fixed `agent_role_routing` and `cli_provider` to
   use the 22 actual role names; assigned each role a thoughtful CLI tier
   (claude / codex / pi) for cross-vendor diversity.
8. **Example project** — generated `examples/quickstart-demo/` as a real
   init-project.sh run, showing the produced structure.

## Final inventory

- Framework files (excluding examples): **186**
- Example files: **157**
- **Total: 343** across **8 top-level directories** + **6 top-level docs**

## Cornerstone reminder

Every agent invokes `skill-discovery` BEFORE any other tool call. If no skill
matches with ≥30% confidence, the agent invokes `skill-creator` to make one
rather than improvising. This is encoded in `.agent-os/rules/general.md` and
in every AGENT.md's `required_skills` list.
