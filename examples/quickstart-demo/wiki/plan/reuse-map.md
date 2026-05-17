---
title: quickstart-demo — Reuse map
type: plan
tags: [adopt-vs-build, dependencies]
updated: 2026-05-17
---

# Reuse map — adopt / build / extend decisions

For every external dependency we consider, record:
- The decision (Adopt as-is / Adopt + extend / Build / Defer)
- The reasoning
- The fallback if the adopt path breaks

| Dependency | Decision | Reasoning | Fallback |
|---|---|---|---|
| <e.g. zod> | Adopt as-is | Industry standard for TS input validation | valibot if perf becomes a concern |
| <e.g. our-own-thing> | Build | No existing solution covers our X requirement | — |

## Review cadence
Re-review this table at the start of each phase. Decisions that aged out get a
follow-up ADR.
