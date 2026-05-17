# Autonomy Modes

> Applies to: Claude Code, Codex, Pi running under the [orchestration daemon](./07-orchestration.md). Four modes from "manual" to "full autonomy with operator gate". Advance only when explicit conditions are met.

## The 4-mode ladder

| Mode | Name | Daemon behavior | Human role |
|------|------|-----------------|------------|
| **M0** | Manual | Daemon disabled. Workers spawn only from operator commands. | Drives every step |
| **M1** | Advisor-only | Daemon polls + proposes; never acts. Each ticket queues a recommendation. | Approves each action |
| **M2** | Supervised autonomy | Daemon acts; scrutinizer gates verdicts. Operator confirms terminal states. | Reviews scrutinized verdicts |
| **M3** | Full autonomy with operator gate | Daemon acts end-to-end; scrutinizer enforces; Parent AI mediates conflicts. Operator owns only terminal states. | Approves Completed / Failed only |

The ladder is unidirectional — advance one rung at a time. Skipping rungs (M0 → M3) without the intermediate evidence is the canonical autonomy mistake.

## What each mode does and doesn't

### M0 — Manual

- Operator runs `claude` / `codex` / `pi` directly.
- No daemon polling. No autoclaim.
- Use during initial bring-up of a project, when conventions are not yet stable.

### M1 — Advisor-only

- Daemon polls the PM tool.
- Daemon does NOT mutate state.
- For each new ticket, daemon posts a comment: "Recommended action: spawn `claude` with prompt X. Approve?"
- Operator approves; the spawn happens manually.
- **Purpose**: surface what the daemon *would* do without trusting it yet. Build the operator's confidence in routing.

### M2 — Supervised autonomy with scrutinizer gate

- Daemon claims tickets, spawns workers, collects verdicts.
- **Scrutinizer always runs.** No exceptions — even `PASS` verdicts go through scrutiny.
- Scrutinizer disagreements escalate to Parent AI Review.
- Operator confirms `Completed` / `Failed`.
- **Purpose**: trust the daemon's routing while retaining a human review on every artifact.

### M3 — Full autonomy with operator gate at terminal states

- Daemon does end-to-end work.
- Scrutinizer always runs; Parent AI always mediates on conflicts.
- Operator only sees tickets at terminal states (`Completed`, `Canceled`, `Failed`).
- All non-terminal routing is automatic.
- **Purpose**: maximize throughput; minimize operator interruption.

## Conditions for advancing modes

The Framework does not allow ad-hoc promotion. Each rung has explicit go criteria.

### M0 → M1

- AGENTS.md + per-CLI overlays exist and are accurate
- Rules + memories layer populated
- skill-discovery installed
- Hooks wired (post-edit, memory-capture)
- Daemon's poll/claim implementation tested in dry-run
- At least 5 tickets have been operator-driven and worked correctly

### M1 → M2

- At least 20 advisor-only recommendations reviewed
- ≥ 90% of recommendations were "would-have-done-the-same"
- Scrutinizer skill exists and has been exercised against at least 10 historical verdicts
- Parent AI sub-agent defined; cross-CLI routing tested

### M2 → M3

- ≥ 50 tickets processed under M2
- Scrutinizer agreement rate ≥ 95% with operator review
- Parent AI Review has been triggered at least 5 times and resolved correctly
- ADR coverage: every `PROXY_PASS` path has an ACCEPTED ADR
- A run-book for M3 failures exists (what to do when the operator wakes up to a `Failed` queue)

Advancement is itself an ADR. Write one before flipping the mode. Record the evidence above as the rationale.

## The terminal-state invariant

> The daemon NEVER sets `Completed` or `Canceled`. These states are operator-owned.

This invariant holds across all modes (including M3). The daemon may route a ticket *to* `Human Approval`; from there only the operator transitions to `Completed` or `Canceled`.

Why: terminal states are the audit boundary. A daemon that auto-closes its own work eliminates the place where the human verifies that the work was actually wanted. The invariant preserves the boundary.

Implementation: the daemon adapter does not include a transition function for `* → Completed`. The PM tool's workflow permissions enforce the same — operator role only.

## Reverse promotion

When evidence degrades, mode goes down. Triggers:

- Scrutinizer agreement drops below 90% → M3 → M2.
- A `PROXY_PASS` ships without an ADR → M2 → M1 until backlog is cleared.
- The daemon crashes or hangs in production → M* → M0 until root cause is fixed.

Reverse promotion is also an ADR. Don't silently downgrade — record what broke and what re-promotion will require.

## Configuration

```yaml
# .agent-os/orchestration.yaml
autonomy_mode: M2          # M0 | M1 | M2 | M3
require_scrutinizer: true  # mandatory at M2+
require_parent_ai_on_conflict: true  # mandatory at M2+
terminal_states_owner: operator      # invariant; do not change
```

## Cross-references

- [Orchestration](./07-orchestration.md) — the daemon and verdict routing
- `agents/scrutinizer/`, `agents/parent-ai/`, `agents/operator/` — sub-agent definitions
- `PROJECT-TEMPLATE-SPEC.md` §10 — verification-first principle that gates all modes
