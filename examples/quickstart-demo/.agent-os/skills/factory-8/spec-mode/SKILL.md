---
name: spec-mode
description: Plan-before-code for tasks touching >2 files, requiring architectural choice, or with unclear requirements. Outputs a SPEC.md with goals, approach, file list, test plan. The user approves the spec BEFORE implementation begins. Token-efficient — prevents expensive false starts.
---

# When to use

- Task touches more than 2 files.
- Requirements unclear; multiple plausible approaches.
- Security-sensitive (auth, crypto, data handling).
- Refactor that changes public API.
- A change you'd want a senior engineer to review BEFORE you write code.

# How to execute

## Step 1 — Read everything relevant
- `wiki/PLAN.md`, `wiki/STATUS.md` (project context).
- `.agent-os/memories.md` (past decisions).
- `.agent-os/rules/` (applicable to file types you'll touch).
- The files you'll modify (read, don't skim).

## Step 2 — Draft the SPEC

Use this skeleton in a chat message OR save as `wiki/plan/specs/<feature-slug>.md`:

```markdown
# SPEC — <feature>

## Goal
<one paragraph: what changes, what stays the same>

## Approach
<2-3 paragraphs: the chosen design. Name alternatives considered.>

## Files
| Path | Status | Nature of change |
|---|---|---|
| src/foo.ts | edit | add `bar()` function |
| src/foo.test.ts | edit | cover new branch |
| docs/api.md | edit | document `bar()` |

## Test plan
- Unit test: `bar()` returns X when input is Y.
- Integration test: `bar()` round-trips through the API.
- E2E (if user-visible): UI shows expected state + DB row exists.

## Rollback plan
<if anything goes wrong, how do we undo? Feature flag? Revert PR?>

## Open questions for the user
1. <decision point>
2. <decision point>
```

## Step 3 — Get approval
- Send the SPEC. Wait for the user to approve or request changes.
- Do not write code until the SPEC is approved.

## Step 4 — Implement against the SPEC
- Touch only the files listed.
- Apply the test plan exactly.
- If the SPEC needs a change mid-implementation, surface it — don't quietly diverge.

## Step 5 — Verify against the SPEC
- Every file in the SPEC was touched (or has a noted reason if not).
- Every test in the test plan exists and passes.
- The SPEC is updated to "implemented" with a link to the PR/commit.

# Cross-CLI notes

| CLI | How to enter spec mode |
|---|---|
| Claude Code | `Shift+Tab` to toggle Plan Mode, OR invoke this skill explicitly |
| Codex | `/spec` slash command if configured, OR invoke this skill |
| Pi | invoke this skill; Pi's plan-mode extension is the equivalent |

# Anti-patterns (refuse)
- Writing > 50 lines of code without a SPEC for a non-trivial task.
- SPEC that includes implementation details ("use `for` loop here"). SPEC is WHAT not HOW.
- Skipping the test plan.
- Approving your own SPEC.
