---
title: Orchestration Core — Formal Contract
type: spec
updated: 2026-05-17
---

# Orchestration Core — Formal Contract

## Invariants (non-negotiable)

1. **Daemon never sets terminal states.** Completed/Canceled belong to the
   operator. Daemon transitions are: `Agent Queue` → `Processing` →
   `{Evaluating, Parent AI Review, Human Approval, Failed}`.
2. **Slot release is guaranteed.** Every `mark_running` is paired with a
   `mark_completed` in a `try/finally`. An uncaught exception releases the slot
   with verdict `ABORTED_BY_RECONCILIATION`.
3. **Verdict is the LAST LINE.** Adapters must emit a single line matching
   `^VERDICT:\s*<one of the seven verdicts>\b` as the final stdout line.
4. **H3 routing wins over label.** If `issue.state == "Parent AI Review"`,
   the daemon forces `subagent=parent-ai` regardless of the `@<role>` label.
5. **No two daemons claim the same issue.** Claim is a state-transition
   mutation against the PM; the PM's state machine is the lock.
6. **Hot-reload is config-only.** Code changes require restart; YAML in
   `WORKFLOW.md` is re-parsed on every tick.

## Ownership

| Concern | Daemon owns | Operator owns |
|---|---|---|
| Eligible-state polling | ✓ | |
| Claim mutation | ✓ | |
| Subprocess spawn | ✓ | |
| Verdict parsing | ✓ | |
| Routing to non-terminal states | ✓ | |
| Routing to `Completed` | | ✓ |
| Routing to `Canceled` | | ✓ |
| Approving `Human Approval` items | | ✓ |
| Retry budget exhaustion → `Failed` | ✓ (after 3 retries) | |

## RuntimeState shape

```python
@dataclass
class RuntimeState:
    claimed:        dict[str, Issue]          # claimed, not yet running
    running:        dict[str, RunSession]     # currently executing
    completed:      dict[str, CompletionInfo] # finished
    retry_attempts: dict[str, int]            # per-issue retry counter
    retry_after:    dict[str, float]          # epoch seconds; skip until ≥
```

`CompletionInfo` carries `verdict`, `duration_s`, `exit_code`,
`journal_path`. `TERMINAL_VERDICTS` short-circuits re-claim:

```
TERMINAL_VERDICTS = {
  "PASS", "PROXY_PASS", "HUMAN_APPROVAL_REQUIRED",
  "FAIL", "CONTINUE_EXHAUSTED",
  "ABORTED_BY_RECONCILIATION", "OPERATOR_ABORTED",
}
```

`NEEDS_HUMAN` and bare `CONTINUE` are **non-terminal** — they re-enter the
eligible pool. This is the LLM-294 invariant.

## Verdict semantics

| Verdict | Routing | Retry? | Notes |
|---|---|---|---|
| `PASS` | `Evaluating` | no | Operator gate. Adapter measured success. |
| `PROXY_PASS` | `Evaluating` (`gate:proxy-pass` label) | no | Soft pass; requires authorized ADR + deferred tickets. |
| `FAIL` | `Failed` after 3 retries | yes | Retry counter increments. |
| `NEEDS_HUMAN` | `Parent AI Review` | no | Forces parent-ai on re-claim. |
| `HUMAN_APPROVAL_REQUIRED` | `Human Approval` | no | Operator-owned terminal. |
| `CONTINUE` | stays in `Processing`; re-enters next tick | no | Multi-turn continuation. |
| `CONTINUE_EXHAUSTED` | `Failed` | no | After `max_turns_per_session`. |

## Retry / backoff policy

- `max_retries = 3` per issue (configurable via `WORKFLOW.md`).
- Backoff: `compute_retry_after(n) = now + base * 2**(n-1)` capped at 3600s.
- `base = 60s` default.
- Retry counter resets on PASS/PROXY_PASS routing.

## H3 routing rules

1. Read `issue.state`.
2. If state == "Parent AI Review": route to `parent-ai` subagent.
3. Else if state == "Evaluating" and `@scrutinizer` label present: route to
   `scrutinizer`.
4. Else: read `@<role>` label, look up `agent_role_routing[<role>]` in
   `WORKFLOW.md`, route to that subagent.
5. If no `@<role>` label and no state-forced agent: skip the issue and log.

## Stall detection

- `stall_timeout_ms` (default 1_800_000 = 30 min) — kill subprocess if no
  stdout/stderr writes within window.
- Killed sessions get verdict `ABORTED_BY_RECONCILIATION`.

## JSON envelope contract (Pi adapter only)

Pi `--mode json` emits newline-delimited JSON. Each object has shape:

```json
{"type": "turn_complete"|"thinking"|"tool_use"|"final",
 "verdict": "PASS"|...,  // present on type=final
 "content": "..."}
```

The adapter parses each line, accumulates content, and uses the `verdict`
field from the `final` object. Compatibility fallback: if no `final`
object is seen, parse the LAST LINE of accumulated content for the
`VERDICT:` regex (matching Claude/Codex behaviour).

## Verdict comment format (posted to PM before transition)

```
VERDICT: <one of the seven>
Artifacts: <comma-separated paths|urls>
Summary: <1-3 sentences>
Gate ref: <test-plan section or acceptance criterion ID>
```

The `VERDICT:` prefix is grep-parseable and required for reconciliation.
