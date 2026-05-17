---
title: quickstart-demo — Master Plan
type: plan
updated: 2026-05-17
---

# quickstart-demo — Game Plan

## Vision
<one paragraph: what the project does, why it matters, target user>

## The N long-running failure modes — and which ideas address each
| # | Failure mode | Primary ideas |
|---|---|---|
| 1 | <e.g. context exhaustion> | <idea IDs> |
| 2 | <e.g. crash recovery> | |
| 3 | <e.g. drift> | |
| 4 | <e.g. cost runaway> | |

## Architecture — N packages, M layers
| Layer | Package | Concern |
|---|---|---|
| L0 | <foundation pkg> | <state primitives> |
| L1 | <coordination pkg> | <permissions, compaction> |
| L2 | <delegation pkg> | <subagents, knowledge objects> |
| L3 | <orchestration pkg> | <state machine, evals> |
| L4 | <verification pkg> | <judges, anti-gaming> |

## The 5-phase build plan
| Phase | Goal | Packages | Duration | "Done" criterion |
|---|---|---|---|---|
| P0 spikes | De-risk unknowns | (spikes only) | 1-2 wk | All spikes PASS |
| P1 MVP | Smallest version that doesn't crash | L0+L1+min L4 | 4-6 wk | 24h no crash |
| P2 Delegation | Bounded parallel work | L2 | 3-4 wk | Multi-file task solved |
| P3 Quality+Recovery | Survive restarts | recovery + full L4 | 3-4 wk | Resume after kill -9 |
| P4 Mission | Multi-day autonomy | L3 | 4-6 wk | 72h mission with checkpoints |
| P5 Auto-improve | Self-improving | meta-loop | open | A/B produces improvement/wk |

## Top N risks
1. <risk> — <mitigation>

## What "done" looks like per phase
### P1 — [ ] <criterion>
### P2 — [ ] <criterion>

## Open questions (resolve before P1)
1. <question>

## Idea-board cross-reference
See [[IDEAS]].
