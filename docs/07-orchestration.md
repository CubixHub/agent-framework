# Orchestration (Symphony-Style Daemon)

> Applies to: Claude Code, Codex, Pi as worker CLIs; Linear or Plane as the PM tool. The daemon polls a PM tool, claims tickets, spawns a worker CLI per ticket, validates the verdict, routes to a reviewer, and surfaces terminal-state decisions to a human operator.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  PM Tool (Linear or Plane) — state machine of tickets            │
│                                                                  │
│   Triage → Agent Queue → Processing → Evaluating                 │
│            → Parent AI Review → Human Approval → Completed       │
│                                              ↘ Failed            │
└──────────────────────────────────────────────────────────────────┘
       ▲             │ poll 30s             │ verdict
       │             ▼                       ▼
   ┌────────────────────────────────────────────────────────┐
   │  orchestration/symphony — single-process Rust daemon   │
   │                                                        │
   │   poll → claim → spawn CLI (claude|codex|pi) → wait    │
   │        → read verdict → route by verdict → next loop   │
   └────────────────────────────────────────────────────────┘
```

The loop is intentionally simple: a 30-second poll cycle, one ticket at a time per worker slot, a small state machine. Complexity lives in the **routing** (what to do with a verdict), not the loop.

## RuntimeState

The daemon's in-memory state per ticket:

```rust
struct RuntimeState {
  ticket_id: String,
  current_state: TicketState,    // mirrors PM state
  worker_cli: WorkerCli,         // Claude | Codex | Pi
  worker_pid: Option<Pid>,
  spawned_at: Instant,
  attempts: u8,
  last_verdict: Option<Verdict>,
  adr_refs: Vec<AdrRef>,         // ADRs touched by this ticket
}
```

State transitions are append-only — the daemon never *forgets* a verdict; it records all of them and the latest one wins for routing.

## State machine

| State | Owner | Daemon does |
|-------|-------|-------------|
| **Triage** | Human or triage-bot | Nothing — out of scope |
| **Agent Queue** | Daemon (claim candidate) | Poll, claim, transition → Processing |
| **Processing** | Worker CLI | Spawn worker; wait for verdict |
| **Evaluating** | Scrutinizer sub-agent | Spawn scrutinizer with the diff + verdict; route by scrutinizer verdict |
| **Parent AI Review** | Parent-AI sub-agent (H3 routing) | Force a cross-CLI parent-AI review on contested verdicts |
| **Human Approval** | Operator | Surface the artifact + verdicts; wait for operator decision |
| **Completed** | Operator only | Daemon NEVER sets this; operator-owned |
| **Failed** | Operator or daemon (with override) | Append failure record |

## Verdict routing

The worker CLI returns a verdict from a closed enum. The daemon routes by verdict:

| Verdict | Meaning | Next state |
|---------|---------|------------|
| `PASS` | All verification layers pass | Evaluating (scrutinizer confirms) |
| `PROXY_PASS` | Could not run a layer; proxied via measured artifact OR an authorized ADR | Parent AI Review (always) |
| `FAIL` | At least one layer failed | Processing (loop with feedback) — bounded by attempts |
| `BLOCKED` | Cannot proceed; needs human input | Human Approval |
| `OUT_OF_SCOPE` | Ticket asks for work the daemon refuses | Human Approval (operator reclassifies) |

## H3 routing — Parent AI Review

When the scrutinizer's verdict conflicts with the worker's verdict (or the worker returned `PROXY_PASS`), the daemon enters the Parent AI Review state. This state **forces a parent-ai sub-agent run** — typically a different CLI than the worker used. The parent-ai resolves the conflict.

```
worker: PASS → scrutinizer: FAIL → Parent AI Review → parent-ai (different model) decides
```

H3 = the third level in the escalation chain. The pattern is intentional: never let the worker grade itself, and never let the scrutinizer overrule alone if there's a real conflict.

## Escalation chain

```
Worker CLI    →   Scrutinizer    →   Parent AI    →   Operator (human)
(generator)       (verifier)         (mediator)        (terminal)
```

- **Worker** generates artifacts. Returns a verdict.
- **Scrutinizer** verifies. Different model from worker (anti-gaming rule).
- **Parent AI** mediates on conflict. Different CLI ideally. Reads both diffs and verdicts, decides.
- **Operator** is the human. Only the operator sets `Completed` or `Canceled`.

See `agents/scrutinizer/`, `agents/parent-ai/`, `agents/operator/` for sub-agent definitions.

## Verdict honesty rules

The daemon rejects a verdict if it violates any of these:

1. **No fake PASS.** A `PASS` verdict requires verification-layer artifacts: lint output, test output, typecheck output. Missing artifacts → re-spawn the worker.
2. **`PROXY_PASS` requires a measured artifact OR an authorized ADR.** When a layer cannot run (e.g., no E2E rig available for a CLI-only target), the worker may return `PROXY_PASS` only if it links to a *measured proxy* (e.g., trace-audit log) OR an `ADR` with `status: accepted` authorizing the proxy.
3. **`PROXY_PASS` opens new tracking issues.** Every `PROXY_PASS` creates one or more follow-up tickets in the PM tool tagged `proxy-debt`. The operator reviews them on a cadence.
4. **An ACCEPTED ADR is required to retire the debt.** Closing a `proxy-debt` ticket without an `ADR` that justifies removal is forbidden.

The daemon enforces these mechanically — they are not advisory.

## Tri-platform CLI adapter

Workers are CLIs, not language bindings. The daemon spawns them as subprocesses with a standard contract:

- Input: ticket JSON on stdin (or `--ticket <id>` flag pulling from PM API)
- Output: verdict JSON on stdout (or a file at a known path)
- Side effects: file mutations in the working tree; git commits; PM ticket comments

Adapter responsibilities per CLI:

| CLI | Spawn command | Verdict source |
|-----|---------------|----------------|
| Claude Code | `claude --headless --ticket <id>` (or via Claude Agent SDK) | `.symphony/verdict-<id>.json` |
| Codex | `codex --headless --ticket <id>` | `.symphony/verdict-<id>.json` |
| Pi | `pi --mode json` with the ticket as the initial JSON-RPC frame | stdout JSON-RPC reply |

The adapter normalizes verdict shape. The daemon does not see CLI-specific differences past the adapter boundary.

## PM tool adapter

The PM tool (Linear or Plane) is the source of truth for ticket state. The daemon adapter abstracts the difference:

| Operation | Linear | Plane |
|-----------|--------|-------|
| Poll new | GraphQL `viewer.assignedIssues` filtered by state | REST `/api/v1/workspaces/.../issues/` filtered |
| Claim | Mutation `issueUpdate(state: Processing)` | PATCH `/issues/{id}` `state=processing` |
| Comment | Mutation `commentCreate` | POST `/issues/{id}/comments/` |
| Transition | Mutation `issueUpdate(state: ...)` | PATCH state |

See `integrations/linear/` and `integrations/plane/`. The daemon picks the adapter from `.agent-os/orchestration.yaml` → `pm_tool: linear | plane`.

## Configuration

```yaml
# .agent-os/orchestration.yaml
pm_tool: linear           # or: plane
worker_default: claude    # or: codex | pi
worker_slots: 2           # max concurrent tickets
poll_interval_s: 30
terminal_states_owner: operator  # invariant — never override
```

## Cross-references

- `orchestration/symphony/README.md` — daemon source and run instructions
- `agents/scrutinizer/`, `agents/parent-ai/`, `agents/operator/` — sub-agent definitions
- `integrations/linear/`, `integrations/plane/` — PM adapters
- [Autonomy modes](./10-autonomy-modes.md) — when to advance from advisor-only to full autonomy
- [PM tool choice](./11-pm-tool-choice.md) — Linear vs Plane decision matrix
