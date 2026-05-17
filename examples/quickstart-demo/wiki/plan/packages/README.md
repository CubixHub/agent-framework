---
title: quickstart-demo — Packages overview
type: plan
updated: 2026-05-17
---

# Packages — master overview

## Elevator pitch
<1-paragraph: the project's package decomposition strategy and why>

## The N packages by layer

### L0 — Foundations (no internal deps)
- <pkg> — <concern>

### L1 — Coordination (depends on L0)
- <pkg> — <concern>

### L2 — Delegation & memory (depends on L0-L1)
- <pkg> — <concern>

### L3 — Orchestration (depends on L0-L2)
- <pkg> — <concern>

### L4 — Verification (orthogonal; reads L0-L3, writes verdicts)
- <pkg> — <concern>

### L5 — Embedded SDKs (consumed by targets)
- <pkg> — <concern>

## Failure-mode ownership map
| Failure mode | Owner package |
|---|---|
| <e.g. context exhaustion> | <pkg> |
| <e.g. crash recovery> | <pkg> |

## Cross-cutting infrastructure (shared, not packaged)
- Shared schema set — versioned schemas every package speaks
- Manifest contract — single YAML at repo root declaring active packages
- Extension protocol — hooks + tools + slash commands

## Related
- [[../verification-strategy]]
- [[ARCHITECTURE]]
- [[INTEGRATION]]
- [[PHASES]]
