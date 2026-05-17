# Anti-gaming primitives — concrete enforcement

## AG-1 — Snapshot tests before run; restore before grading
**Why**: stops "I modified the tests to pass."

**Enforcement**:
```bash
# Before agent runs:
git stash push -- tests/  # stash test files only
# Agent runs, modifies source. If it modifies tests too — that's tracked.
# After agent claims done:
git stash pop  # restore original tests
# Re-run tests on restored set. If they still pass, real PASS.
```

## AG-2 — Compare claimed actions vs actual diffs
**Why**: catches lying about tool results.

**Enforcement**:
- Agent's session transcript lists every tool call.
- Compute `git diff --stat` after the session.
- Diff the two lists. Any file in actual but not in claimed (or vice versa) → flag.
- Tools: `claude --dump-trace`, `codex --trace`, `pi --mode json` and parse.

## AG-3 — Deliberately break code; verify tests FAIL
**Why**: closes the "no real tests = all pass" tautology.

**Enforcement**:
- After agent claims done, randomly select 3 functions in the changed code.
- Apply a syntactic mutation (negate condition, replace constant).
- Re-run the test suite. ≥2 of 3 mutants MUST cause test failures.
- If <2, the tests aren't testing — escalate.

## AG-4 — E2E asserts combine UI-text + server-state
**Why**: eliminates the #1 false-pass mode ("looks right but DB is wrong").

**Enforcement**:
```typescript
// E2E test example
await expect(page.getByText('Order placed')).toBeVisible();
const order = await db.orders.findOne({ id: lastInsertedId });
expect(order.status).toBe('pending_payment');
expect(order.line_items).toHaveLength(2);
```

If only the UI is asserted, the test passes when the DB silently fails to write.
If only the DB is asserted, the test passes when the UI shows the wrong screen.
Both, always.
