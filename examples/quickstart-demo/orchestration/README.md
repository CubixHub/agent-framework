---
title: Orchestration Core — Framework Daemon
type: overview
updated: 2026-05-17
---

# Orchestration Core

Symphony-style poll-claim-process daemon that dispatches PM-tracked work
(Linear or Plane) to three coding-CLI flavors: **Claude Code**, **Codex**, **Pi**.

## Quickstart

```bash
export PROJECT_DIR="$(pwd)"
export LINEAR_API_KEY=...           # OR PLANE_API_KEY + PLANE_WORKSPACE_SLUG
cp orchestration/WORKFLOW.md.tmpl orchestration/WORKFLOW.md
bash orchestration/scripts/start.sh
tail -f /tmp/orchestration-daemon-master.log
```

Stop: `bash orchestration/scripts/stop.sh`.

## Daemon loop (ASCII)

```
                ┌──────── 30s tick ─────────┐
                ▼                            │
     ┌───────────────────────┐               │
     │  pm_adapter.fetch_    │               │
     │  queue()              │               │
     └───────────┬───────────┘               │
                 │ list[Issue]               │
                 ▼                           │
     ┌───────────────────────┐               │
     │  for each issue:      │               │
     │   - state.can_claim?  │               │
     │   - claim mutation    │               │
     │   - mark_claimed      │               │
     └───────────┬───────────┘               │
                 ▼                           │
     ┌───────────────────────┐               │
     │  spawn cli_adapter    │               │
     │   (claude|codex|pi)   │               │
     │   in per-issue cwd    │               │
     └───────────┬───────────┘               │
                 ▼                           │
     ┌───────────────────────┐               │
     │ parse LAST LINE       │               │
     │ VERDICT: ...          │               │
     └───────────┬───────────┘               │
                 ▼                           │
     ┌───────────────────────┐               │
     │ post comment +        │               │
     │ transition state      │               │
     │ journal run           │               │
     └───────────┬───────────┘               │
                 │ try/finally               │
                 ▼                           │
     ┌───────────────────────┐               │
     │ mark_completed +      │               │
     │ release slot          ├───────────────┘
     └───────────────────────┘
```

## State-machine diagram

```
   Triage ──op──▶ Agent Queue ──daemon─▶ Processing ──verdict─▶
                                                              │
   ┌────────────┬──────────────────┬─────────────┬────────────┘
   ▼            ▼                  ▼             ▼
Evaluating  Parent AI Review   Human Approval   Failed
 (op gate) (forces parent-ai)   (op only)   (after 3 retries)
   │                                  
   ▼                                  
Completed (operator-owned terminal)   
```

Symphony NEVER writes Completed/Canceled — those are operator-owned.

## Adding a new CLI adapter

1. Create `orchestration/adapters/<cli>_adapter.py` subclassing `CLIAdapter`.
2. Implement `spawn(prompt, workspace, max_turns)` returning a `SubprocessResult`
   whose `verdict` is parsed from the **last line** of stdout (regex
   `^VERDICT:\s*(PASS|PROXY_PASS|FAIL|NEEDS_HUMAN|CONTINUE|HUMAN_APPROVAL_REQUIRED)\b`).
3. Register the adapter in `runner._build_cli_adapter()` keyed by the
   `cli_provider` string in `WORKFLOW.md` (e.g. `cli_provider: pi`).
4. Document any CLI-specific install / extensions in the adapter docstring.
5. Smoke-test by mocking the subprocess (see `tests/test_adapters_smoke.py`).

## Adding a new PM adapter

Same shape as CLI: subclass `PMAdapter`, register in `runner._build_pm_adapter()`
keyed by `pm_provider` in `WORKFLOW.md`. Each PM adapter is responsible for
mapping its native states/labels onto the canonical `Issue` shape and the
`eligible_states` / `terminal_states` config.

## Files

| Path | Purpose |
|---|---|
| `runner.py` | Main loop |
| `state.py` | RuntimeState + verdict semantics |
| `journal.py` | Per-iteration run journal writer |
| `retry.py` | Exponential backoff |
| `workspace.py` | Per-issue tempdir |
| `adapters/*.py` | CLI adapters (claude/codex/pi) |
| `pm_adapters/*.py` | PM adapters (linear/plane) |
| `WORKFLOW.md.tmpl` | Hot-reload config template |
| `SPEC.md` | Formal contract |
| `tests/` | pytest smoke + invariants |

See `SPEC.md` for the formal contract before adding adapters.
