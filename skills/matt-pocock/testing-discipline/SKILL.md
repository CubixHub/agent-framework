---
name: testing-discipline
description: Vitest-first testing with strict naming, MSW at HTTP boundaries, zero mocks of internal modules. Use when writing tests, when user mentions Vitest/Jest/coverage, when reviewing a test file, or when a bug fix needs a regression test. Refuses internal mocks. Refuses tests of implementation details.
---

# Testing Discipline

Tests verify behaviour through public interfaces. Implementation details are not the subject of tests. Mocks of internal modules are a smell.

## When to use

- Writing tests for a new feature.
- Adding a regression test for a fixed bug.
- Reviewing a `*.test.ts` / `*.spec.ts` file.
- User mentions Vitest, Jest, coverage, or test naming.

# How to execute

## Rule 1 — Tests describe behaviour, not structure

Naming: `should X when Y`.

```typescript
// GOOD
it("should reject the order when the cart is empty");
it("should return 401 when the token is expired");

// BAD
it("checkout() with empty cart");
it("auth middleware returns error");  // describes structure, not behaviour
```

If the name describes a method call, you are testing implementation. Rewrite.

## Rule 2 — Public interface only

```typescript
// GOOD
const user = await createUser({ email });
const fetched = await getUser(user.id);
expect(fetched.email).toBe(email);

// BAD
await createUser({ email });
const row = await db.query("SELECT * FROM users WHERE email = ?", [email]);
expect(row).toBeDefined();
```

Verifying through the database bypasses the contract being tested. The next refactor that switches storage breaks the test for no reason.

## Rule 3 — Mocks at boundaries, never internal

The boundary = HTTP, filesystem, clock, RNG, external SDK. Anything you do not own.

```typescript
// GOOD (MSW for HTTP)
server.use(http.get("/api/users/:id", () => HttpResponse.json(fixtureUser)));
const result = await fetchAndProcessUser(id);

// BAD
vi.mock("./user-processor", () => ({ processUser: vi.fn() }));
```

Mocking an internal module is testing whether `processUser` got called, not whether the user got processed. Different question; usually the wrong one.

## Rule 4 — Vertical slices, never horizontal

One test → one implementation → repeat. Do not batch all tests up front.

```
RIGHT:
  test1 → impl1 → test2 → impl2 → test3 → impl3

WRONG:
  test1, test2, test3 (all) → impl1, impl2, impl3 (all)
```

Horizontal slices produce fake tests that test imagined behaviour. See `test-driven-development` skill for the full red-green-refactor loop.

## Rule 5 — AAA structure, no comments needed

```typescript
it("should return 201 when payload is valid", async () => {
  const payload = makeValidPayload();           // Arrange
  const res = await app.post("/orders", payload); // Act
  expect(res.status).toBe(201);                  // Assert
});
```

The structure is obvious from indentation and blank lines. Comments labelling AAA are noise. If the structure is not obvious, the test is doing too much — split it.

## Rule 6 — One logical assertion per test

```typescript
// GOOD
it("should return 201", ...);
it("should write to the audit log", ...);

// BAD
it("should handle order creation", async () => {
  expect(res.status).toBe(201);
  expect(res.body.id).toBeDefined();
  expect(audit.entries).toHaveLength(1);
  expect(metrics.counter).toBe(prev + 1);
});  // four behaviours in one test; one failure obscures the others
```

Multiple `expect`s on the same logical assertion (e.g. `expect(res.status).toBe(201)` and `expect(res.body).toMatchObject({...})` both asserting "response is well-formed") are fine.

## Rule 7 — Mutation test the suite

After all tests pass, deliberately break the code. Tests MUST fail. If they pass, the tests do not test.

```bash
# Manually: comment out the body of a function under test. Run suite. Expect red.
# Tooling: stryker-mutator, etc. — wire into CI for hot paths.
```

Untested code that "has tests" is the most expensive kind of bug.

# Quality bar

- [ ] Every test name matches `should X when Y`.
- [ ] Zero `vi.mock` / `jest.mock` of internal (project-owned) modules.
- [ ] Boundary mocks use MSW (HTTP) / `vi.useFakeTimers()` (clock) / fixtures (filesystem).
- [ ] At least one mutation check ran against the new tests.
- [ ] No test queries the database to verify behaviour — uses the public API.

# Anti-patterns

- **`vi.mock("./neighbour")`.** The neighbour is internal. Test through it, not around it.
- **`toHaveBeenCalledWith(...)`.** Asserting that a function was called is asserting implementation. Did the behaviour change observably? That is the test.
- **Snapshot tests for everything.** Snapshots are useful for stable, hard-to-spell outputs (rendered HTML, JSON shapes). For behaviour, write an explicit assertion.
- **Tests inside `describe.each` that test 17 cases of the same logic.** That is one property test pretending to be 17 unit tests. Use a fuzz/property runner if the value matrix matters.
- **`skip` left in main.** Either delete it, fix it, or open an issue and link it.

# Reference

- Vitest docs (https://vitest.dev) — `expect`, `vi.useFakeTimers`, fixtures.
- MSW (https://mswjs.io) — HTTP boundary mocks.
- See `test-driven-development` skill for the full TDD loop.
- See `matt-pocock/error-handling` for testing error paths specifically.
