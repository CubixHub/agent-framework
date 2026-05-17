# Linear rules

## Issue body format (work item)
```
Phase: <number + name>
Deliverables:
- <concrete file or artifact>
Acceptance:
- <measurable pass/fail criterion>
Effort: ~N dev-days
Risk: <one-line note + mitigation>
```

## Issue body format (bug)
```
**Repro:**       <steps>
**Expected:**    <what should happen>
**Actual:**      <what happens>
**Severity:**    p0 | p1 | p2 | p3
**Environment:** <stack/version>
**First seen:**  <date or commit>
**Related:**     <wiki page or other issue>
**Workaround:**  <if any>
```

## Verdict comment (mandatory before state transition)
```
VERDICT: PASS | PROXY_PASS | FAIL | NEEDS_HUMAN | CONTINUE | HUMAN_APPROVAL_REQUIRED
Artifacts: <comma-separated paths or URLs>
Summary: <1-3 sentences>
Gate ref: <test plan section, e.g. "phase-1 §2.1">
```

## Labels
- `@<role>`: agent routing (e.g. `@implementer`, `@scrutinizer`, `@parent-ai`)
- `type:<x>`: feature, bug, tech-debt, research, infra
- `prio:P<n>`: P0 (urgent) ... P3
- `phase:<n>`: phase parent
- `subsystem:<x>`: per-project subsystem tag
- `gate:<x>`: acceptance gate reference

## State machine
Triage → Agent Queue → Processing → {Evaluating | Parent AI Review} → {Completed | Human Approval | Failed}.
Daemon NEVER sets Completed/Canceled — operator-owned terminals.
