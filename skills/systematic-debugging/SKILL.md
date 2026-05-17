---
name: systematic-debugging
description: Hypothesis-first 7-step debugging for any bug, test failure, or unexpected behavior. Spawn one agent per hypothesis if independent; otherwise sequence. Score confidence at each step. Do NOT propose fixes before reproduction is achieved.
---

# When to use

- Test failure you don't immediately understand.
- Bug report with a reproduction.
- "Works on my machine" / flaky tests.
- Production incident triage.
- Performance regression.

# How to execute

## Step 1 — Reproduce
- Get a deterministic repro. If non-deterministic, find what varies.
- Capture the exact failure: error message, stack, inputs, environment.
- Confidence rises only with reproduction. No repro → no fix.

## Step 2 — Isolate
- Bisect the inputs: what's the smallest change that triggers / hides the bug?
- Bisect the code (`git bisect`) if it's a regression.
- Bisect the environment: OS, runtime version, dependency versions, time of day.

## Step 3 — Hypothesize (3 distinct hypotheses)
For each:
- One-sentence cause.
- A prediction: "if H is true, then X will be observed."
- Confidence: 0-100.

If only one hypothesis comes to mind, you're not thinking hard enough.

## Step 4 — Predict + Test
- Run the experiment that distinguishes the hypotheses.
- If the test is expensive, dispatch one sub-agent per hypothesis IN PARALLEL.
- Update confidence after the result.

## Step 5 — Conclude
- One hypothesis should now be ≥80 confident.
- If none reaches 80, return to step 3 with new hypotheses informed by what
  the experiment revealed.

## Step 6 — Fix
- Write a failing test that captures the bug.
- Apply the minimal fix that turns it green.
- Run the full test suite.

## Step 7 — Document
- ADR if the fix encoded a non-obvious design decision.
- Memory entry if the cause was a recurring pattern.
- Wiki concept page if the bug class is reusable knowledge.
- Linear/Plane closing comment with root cause + prevention.

# Output shape
```
Hypothesis A (was 50% → now 90%): <cause>. Evidence: <experiment result>.
Hypothesis B (was 30% → 5%): ruled out by <evidence>.
Fix: <minimal change>. Test: <failing-then-green test>. Follow-up: <if any>.
```

# Anti-patterns (refuse)
- Proposing a fix before reproduction is achieved.
- "Let me try this and see" without naming a hypothesis.
- Fixing the symptom not the cause.
- Skipping the failing test.
- Skipping the documentation step.
