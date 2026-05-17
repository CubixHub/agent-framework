# Testing rules

## TDD workflow (red-green-refactor)
1. Write the failing test FIRST. Confirm it fails for the RIGHT reason.
2. Write the smallest code that makes it pass.
3. Refactor with the green test as your safety net.
4. Mutation test at the end: break the code, confirm tests fail.

## File organization
- Colocate unit/component tests: `Component.tsx` → `Component.test.tsx`.
- Integration tests in `__tests__/integration/` or `tests/integration/`.
- E2E tests at project root: `e2e/`.

## Naming
- `should [action] when [condition]`.
- One behavior per test. Multiple assertions OK if they test the same behavior.

## Mocking
- Mock at boundaries (external APIs, time, randomness). Never internal modules.
- MSW for HTTP boundary in TS; `responses` / `httpx.MockTransport` in Python.
- Reset mocks in `afterEach` / `teardown`.

## Coverage
- Coverage is necessary but not sufficient. Mutation testing is the real bar.
- Target: 80% line, 70% branch, 60% mutation-survival.

## Anti-patterns
- Snapshot tests of UI without behavior assertions.
- Tests that import implementation details (private functions).
- Tests that depend on test order.
