---
name: receiving-code-review
description: Process code review feedback with technical rigor instead of performative agreement. Verify suggestions before implementing. Push back with evidence when the reviewer is wrong. Required when feedback is unclear or technically questionable.
---

# When to use

- You've received a code review (from scrutinizer agent, parent-ai, human, or other CLI).
- The feedback contains suggestions to implement.
- Especially when the feedback feels wrong, unclear, or you're tempted to "just
  do it to make them happy".

# How to execute

## Step 1 — Read everything before responding
- Don't dispatch fixes piecemeal. Read all comments first.
- Group related comments. Identify patterns the reviewer noticed.

## Step 2 — Classify each comment

| Class | What | Response |
|---|---|---|
| **Clear bug** | Reviewer correctly identifies a defect | Fix. Add a test that would have caught it. |
| **Style nit** | Genuinely subjective | Adopt if cheap. Push back if expensive and you disagree. |
| **Design disagreement** | Different architectural opinion | Discuss with rationale; don't auto-adopt. |
| **Unclear** | You don't understand what they want | Ask a clarifying question. Don't guess. |
| **Wrong** | Reviewer mistaken about behavior, API, or context | Push back with evidence. |

## Step 3 — Verify before implementing
For "fix this" feedback:
- Does the suggested fix actually solve the problem? Read it carefully.
- Does it introduce a new issue (perf, security, complexity)?
- Run the test suite with the suggested change before committing.

For "this is wrong" feedback:
- Reproduce what the reviewer saw. If you can't reproduce, ask for steps.
- Check the actual code, not the reviewer's paraphrase of it.

## Step 4 — Push back when you have evidence

Never:
- "You're right, sorry!" (when you're not sure they are)
- "Done!" (without actually understanding why)
- Implementing a change you disagree with to avoid friction

Always:
- "I checked X — actually it does Y because of Z. Here's the test that proves it."
- "I'd push back on this because [evidence]. Open to it if you can show me [counter-evidence]."

## Step 5 — Resolve every thread
- Either implement (with the fix), defer (with a ticket), or close (with rationale).
- No comments left in limbo at merge time.

# Anti-patterns (refuse)
- "LGTM, fixing now" → vague compliance without understanding.
- Blindly implementing reviewer suggestions.
- Defending an obvious mistake out of pride.
- Re-litigating the same point across multiple threads.
- Marking threads resolved without addressing them.
