---
name: verification-first
description: Block work from being called "done" until the 7-layer defense-in-depth verification stack returns PASS. Invoke before reporting any implementation complete.
---

# When to use

- Before saying "task complete", "done", "ready for review", or "fixed".
- Before merging a PR.
- Before transitioning a PM issue to a terminal state.
- When you're tempted to skip testing because "the change is small".

# How to execute

## Step 1 — Run the 7-layer stack (skip layers only if provably impossible)
1. **Static**: lint, type-check, format-check, secret-scan, LSP errors.
2. **Unit + property**: every changed unit has tests; properties cover invariants.
3. **Integration**: cross-component contracts (DB ↔ service, service ↔ service).
4. **End-to-end user-flow**: drive the app as a real user, asserting both UI text AND server state.
5. **Behavioural fingerprinting**: compare metric trends (latency, accuracy, output distribution) against baseline.
6. **Mutation testing**: deliberately break code; verify tests FAIL.
7. **Trace audit**: compare claimed actions vs actual diffs / tool-result logs.

ANY FAIL on ANY layer = hard block. Surface as a blocker, never as "mostly done".

## Step 2 — Enforce the 4 anti-gaming primitives
- **AG-1**: snapshot test files before agent run; restore before grading.
- **AG-2**: compare claimed actions vs actual diffs (`git diff` vs reported actions).
- **AG-3**: deliberately break code; verify tests FAIL — closes "no real tests" tautology.
- **AG-4**: every E2E assertion combines UI-text + server-state — eliminates #1 false-pass.

## Step 3 — Use the judge stack (when LLM grading is needed)
| Tier | When |
|---|---|
| J0 deterministic (exit codes, schemas) | Whenever ground truth exists |
| J1 distilled small judge | Production: every action |
| J2 OS structured judge (Prometheus 2) | Batch/nightly |
| J3 frontier spot-check (Opus / GPT-frontier) | 1% sampling, quarterly |
| J4 pairwise + self-consistency vote | Version comparisons |

**Non-negotiable**: the model that generated the artifact must NOT grade it.

## Step 4 — Pick a sandbox tier
- S0 (~s) headless container — default.
- S1 (~10s) container + display — native GUI.
- S2 (~30s) microVM — malicious-persona / untrusted code.
- S3 (~min) real VM — top-level mission validation.

## Step 5 — Drive personas, not scripts
novice / expert / distracted / malicious / mobile / edge-case. If "novice" and
"expert" produce the same verdict, you're not testing what users do.

## Step 6 — Record every session
Recordings drive replay (regression), mutation testing, and judge calibration.

# Reference
- [reference/seven-layers.md](reference/seven-layers.md) — per-layer commands per language
- [reference/anti-gaming.md](reference/anti-gaming.md) — AG-1..AG-4 enforcement
- [reference/judge-stack.md](reference/judge-stack.md) — tier cost analysis

# Anti-patterns (refuse)
- "Tests later" — verification stack is upstream of feature work.
- Skipping layers because "the change is small" — small changes regress in surprising places.
- Letting the generating model grade its own work.
- Auto-PASS on the basis of green CI alone — CI is layer 1-2 only.
