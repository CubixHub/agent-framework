# Framework Agent Roles

Role definitions consumed by the orchestration daemon (Symphony-style) to spawn coding-CLI subprocesses. Each role works for **Claude Code**, **Codex (OpenAI)**, and **Pi (pi.dev)** — three CLIs that all read `AGENTS.md` + their own overlay (`CLAUDE.md` / `AGENTS.md` for Codex / `pi:` keys in SYSTEM.md for Pi).

A role is a directory `agents/<role>/AGENT.md`. The orchestration daemon labels work items `@<role>` and spawns the appropriate CLI subprocess with the role file as system prompt.

## Role matrix

| Role | Model (claude / codex / pi) | Tools | Verdicts | Escalates to |
|------|-----------------------------|-------|----------|--------------|
| `architect` | opus / gpt-5.5 / pi-best | Read, Glob, Grep, WebFetch | PASS_DESIGN, NEEDS_REVIEW, NEEDS_HUMAN | parent-ai |
| `implementer` | sonnet / gpt-5.5-codex / pi-fast | full | PASS, FAIL, NEEDS_HUMAN, CONTINUE | reviewer |
| `reviewer` | opus / gpt-5.5 / pi-best | Read, Glob, Grep, WebFetch | APPROVE, REQUEST_CHANGES, NEEDS_HUMAN | scrutinizer |
| `tester` | sonnet / gpt-5.5-codex / pi-fast | full | PASS, FAIL, INSUFFICIENT_COVERAGE | implementer |
| `researcher` | opus (lead), sonnet (worker) / gpt-5.5 / pi-best | WebSearch, WebFetch, Read, Glob, Grep | COMPLETE, NEEDS_BUDGET_INCREASE, NEEDS_HUMAN | wiki-curator |
| `ml-engineer` | opus / gpt-5.5-codex / pi-best | full + cluster shell | PASS, FAIL, NEEDS_HUMAN, CONTINUE | reviewer |
| `scrutinizer` | opus / gpt-5.5 / pi-best | Read, Glob, Grep, Bash (RO) | PASS, PASS_WITH_FOLLOWUPS, NEEDS_REWORK | parent-ai |
| `parent-ai` | opus / gpt-5.5 / pi-best | Read, Edit (ADR only), Write, Glob, Grep, Bash, WebFetch | APPROVE, REROUTE, AMEND_THEN_REROUTE, PROXY_PASS, ESCALATE_TO_HUMAN | human |
| `wiki-curator` | opus (top) / sonnet (worker) / gpt-5.5 / pi-best | Read, Edit, Write, Glob, Grep | INGESTED, LINTED, NEEDS_HUMAN | researcher / human |
| `security-auditor` | opus / gpt-5.5 / pi-best | Read, Glob, Grep, WebFetch | APPROVE, BLOCKS_MERGE, NEEDS_HUMAN | parent-ai |
| `prompt-engineer` | opus / gpt-5.5 / pi-best | Read, Glob, Grep, Edit, Write, WebFetch | PASS, REQUEST_CHANGES, NEEDS_HUMAN | reviewer |
| `orchestration-lead` | opus / gpt-5.5 / pi-best | Read, Edit, Write, Bash, Glob, Grep | RUNNING, PAUSED, ABORTED, NEEDS_HUMAN | human |

### Optional / consultant roles

| Role | Purpose |
|------|---------|
| `cron-architect` | Designs cron / systemd / scheduled-task units. |
| `inference-deployer` | Deploys vLLM/SGLang/TRT-LLM/TGI workloads. |
| `training-orchestrator` | Plans, launches, monitors ML training jobs. |
| `silent-failure-hunter` | Audits catch blocks / try-except for swallowed errors. |
| `team-debugger` | One agent per hypothesis; 7-step protocol; confidence scoring. |
| `test-coverage-analyst` | "Are the right behaviors tested" — not line-coverage. |
| `codex-consultant` | Wraps `codex` CLI for external opinions when running INSIDE Claude Code lead. |
| `claude-consultant` | Wraps `claude` CLI for external opinions when running INSIDE Codex or Pi lead. |
| `pi-consultant` | Wraps `pi` CLI for external opinions when running INSIDE Claude Code or Codex lead. |

## Decision tree — what role for what task

```
Is the task...
├─ a design decision (one or more options to choose)?      → architect
├─ writing code against an accepted ADR?                   → implementer
├─ writing tests (red-green-refactor)?                     → tester
├─ post-write code review (confidence ≥ 80)?               → reviewer
├─ adversarial QA across 10 lenses (confidence ≥ 75)?      → scrutinizer
├─ deciding if a NEEDS_REWORK should AMEND/REROUTE/HUMAN?  → parent-ai
├─ OWASP / lethal-trifecta / secret review?                → security-auditor
├─ answering a research question with citations?           → researcher
├─ ingesting/linting wiki content?                         → wiki-curator
├─ ML training / fine-tuning / deployment / eval?          → ml-engineer
├─ drafting/refactoring a prompt or agent role?            → prompt-engineer
├─ running the orchestration daemon?                       → orchestration-lead
└─ cross-CLI second opinion?                               → codex/claude/pi-consultant
```

## Cross-CLI invocation table

| CLI | Print mode | JSON mode | Reads | Overlay |
|-----|------------|-----------|-------|---------|
| Claude Code | `claude -p "@<role> <prompt>" --permission-mode <mode> --model <m>` | n/a (uses tool calls) | `AGENTS.md`, `CLAUDE.md` | `CLAUDE.md` + `.claude/` |
| Codex | `codex -p "@<role> <prompt>" --model <m>` | `codex --mode json` | `AGENTS.md` | `.codex/` overlay |
| Pi | `pi -p "@<role> <prompt>"` | `pi --mode json` (envelope: `{"agent":"<role>","prompt":"..."}`) | `AGENTS.md` + `SYSTEM.md` | `pi:` keys, TS sub-agents |

All three CLIs read `AGENTS.md` (the framework-level canonical doc) plus their own overlay. Role-specific behavior comes from `agents/<role>/AGENT.md`, which the orchestration daemon injects as the system prompt for the spawned subprocess.

## Escalation chain (summary)

```
implementer  → reviewer → scrutinizer → parent-ai → human
architect    → parent-ai → human
tester       → implementer → reviewer → ...
researcher   → wiki-curator → (then handoff back)
ml-engineer  → reviewer + scrutinizer → parent-ai → human
security-auditor → parent-ai → human
prompt-engineer  → reviewer → ...
wiki-curator → (parent-ai for contradictions) → human
orchestration-lead → human (operator)
```

The unique terminal escalation across the system is **parent-ai → human**. No other role may emit a verdict that moves a ticket to "Human Approval" directly; everything flows through parent-ai's 5-loop alignment check first.

<!-- END -->
