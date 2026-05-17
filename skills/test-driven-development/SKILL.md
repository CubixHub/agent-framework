---
name: test-driven-development
description: Red-green-refactor for any feature or bugfix. Write a failing test BEFORE the implementation; confirm it fails for the right reason; then write the smallest code that passes; then refactor with the test as a safety net. Mandatory on every non-trivial change.
---

# When to use

- Every new feature.
- Every bugfix (the failing test reproduces the bug FIRST).
- Every refactor that changes behavior (refactors that don't change behavior
  use existing tests; refactors that do are really feature changes).

# How to execute

## Red — write the failing test FIRST

1. Write the test in the same commit-prep batch as the spec, before any impl.
2. Run it. Confirm it FAILS.
3. **Confirm it fails for the RIGHT reason.** Read the failure message. If the
   test fails because the function doesn't exist (rather than because the
   behavior is wrong), the test isn't useful — fix it.

## Green — write the smallest code that passes

1. Implement the simplest thing that makes the test pass.
2. Do not add features the test doesn't cover.
3. Do not handle cases the test doesn't exercise.
4. Run the test. Confirm GREEN.

## Refactor — clean up with the test as safety net

1. Improve naming, structure, dedup.
2. Run the test after each meaningful refactor step. Stay green.
3. Stop when the code is "good enough" — perfect is the enemy.

## Mutation test — at end of feature

1. Pick 3 random lines in your new code.
2. Mutate each: negate condition, change constant, swap operator.
3. Run tests. ≥2 of 3 MUST fail.
4. If <2 fail, your tests aren't testing — write more.

# When to write multiple tests up-front
- The feature has 3+ clear behaviors and skipping straight to "one test, then
  the next" misses overall design. Write a small test plan first, then iterate
  red-green-refactor on each.

# Anti-patterns (refuse)
- Writing the implementation first "then I'll add tests".
- Marking work "done" without running the test.
- Skipping the "fails for the right reason" check.
- Skipping mutation testing because "the tests look thorough" — they often aren't.
- Writing snapshot tests for UI without behavior assertions (assertion theater).
