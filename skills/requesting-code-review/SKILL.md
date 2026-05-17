---
name: requesting-code-review
description: Request a code review BEFORE merging, when implementing a major feature, or when finishing a task. Specifies what to review and what the reviewer should focus on. Mandatory before any merge to a protected branch.
---

# When to use

- Before merging any non-trivial PR.
- Before transitioning a PM issue to Evaluating / Completed.
- After completing a feature or major refactor.
- When you've made a security-relevant change.

# How to execute

## Step 1 — Self-review first
- Read the diff yourself. Catch obvious issues.
- Run the full verification stack (see `verification-first` skill).
- Address everything you'd catch in someone else's PR.

## Step 2 — Pick the reviewer(s)
- **scrutinizer agent** for adversarial QA (10 lenses, severity-tagged findings).
- **security-auditor** for any auth, crypto, secrets, or input-validation change.
- **parent-ai** for alignment-sensitive changes (ADR amendments, model behavior).
- A human teammate for design intent and product judgment.

Multiple reviewers in parallel where they have independent expertise.

## Step 3 — Write the review request
Include in the PR description or Linear/Plane comment:
- **Goal**: what this change accomplishes in one paragraph.
- **Approach**: 2-3 sentences on the design choice.
- **Verification evidence**: which layers ran, with PASS/FAIL output.
- **Reviewer focus areas**: 2-4 specific things you want eyes on.
  - "Concurrency in `lockFreeQueue.ts:42` — is the AcqRel ordering correct?"
  - "Auth refresh logic in `session.ts:120` — am I missing a race?"
- **Out of scope**: what NOT to expand into (keeps the review focused).
- **Followups**: known issues you're explicitly deferring, with tickets filed.

## Step 4 — Honor the review
- Read every comment. Don't argue performatively; verify technically.
- If you disagree, explain WHY with evidence, not just opinion.
- See `receiving-code-review` skill for how to process feedback.

# Output shape
```
## Summary
<one paragraph>

## Approach
<2-3 sentences>

## Verification
- [x] static, [x] unit, [x] integration, [x] e2e, [x] mutation
- output: <paste or link>

## Please look at
1. <specific file:line and what worries you>
2. <another>

## Out of scope
- <thing not to expand into>

## Followups
- <ticket #> <what was deferred>
```

# Anti-patterns (refuse)
- "LGTM-bait" — vague PRs designed to get fast approval without scrutiny.
- Merging your own PR without review.
- Skipping reviewer-focus areas — they're the highest-value part.
- Treating disagreement as the reviewer's fault.
