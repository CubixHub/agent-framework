---
name: error-handling
description: Result types for expected failures, exceptions for invariant violations, fail-loud at boundaries, zero silent catches. Use when writing functions that can fail, when reviewing try/catch blocks, when designing a public API surface, or when the user mentions error handling/exceptions/Result types. Refuses empty catches. Refuses catch-and-log without rethrow.
---

# Error Handling

Errors are not exceptional. They are part of the contract. Encode them in the type system so callers cannot ignore them.

## When to use

- Writing any function whose failure is part of normal operation (HTTP requests, parsing, file I/O, validation).
- Reviewing a try/catch block.
- Designing a public API.
- User mentions "exception", "error handling", "Result type", "Either".

# How to execute

## Rule 1 — Expected failure: Result type. Invariant violation: throw.

```typescript
// GOOD — expected failure (network can fail, parse can fail)
async function fetchUser(id: UserId): Promise<Result<User, FetchError>> { ... }

// GOOD — invariant violation (this never happens in correct code)
function getEnv(key: string): string {
  const v = process.env[key];
  if (!v) throw new Error(`Missing required env var: ${key}`);
  return v;
}

// BAD — expected failure thrown as exception
async function fetchUser(id: UserId): Promise<User> {
  const res = await fetch(`/users/${id}`);
  if (!res.ok) throw new Error("not found");  // caller has no compiler reminder to handle
  return res.json();
}
```

If the caller is expected to handle this failure on a normal day, it's a Result. If the failure means the program is broken and should crash, it's an exception.

## Rule 2 — Result type shape

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// Construction
const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
const err = <E>(error: E): Result<never, E> => ({ ok: false, error });

// Use
const r = await fetchUser(id);
if (r.ok) handle(r.value);
else log(r.error);
```

Library options if you want them: `neverthrow`, `effect`, `fp-ts`. Pick one per project. Do not mix.

## Rule 3 — Error types are discriminated unions

```typescript
// GOOD
type FetchError =
  | { kind: "network"; cause: Error }
  | { kind: "not-found"; id: UserId }
  | { kind: "unauthorised" }
  | { kind: "rate-limited"; retryAfter: number };

// caller exhausts:
switch (err.kind) {
  case "network": return retry();
  case "not-found": return null;
  case "unauthorised": return refreshToken();
  case "rate-limited": return wait(err.retryAfter);
}

// BAD
class FetchError extends Error {}  // single error class, caller can't disambiguate
```

A `FetchError` you can't introspect is a `Error` with extra ceremony. Use a tagged union.

## Rule 4 — Fail loud at boundaries

```typescript
// GOOD (top of the request handler)
app.post("/users", async (req, res) => {
  const body = UserSchema.parse(req.body);  // throws on invalid, becomes 400 via middleware
  ...
});

// BAD
app.post("/users", async (req, res) => {
  const body = req.body as UserCreate;  // silent garbage in, surprising errors deep
  ...
});
```

Parse, don't validate. The boundary throws on invalid input; the inside operates on already-validated, typed data.

## Rule 5 — `catch` without rethrow or transform is a bug

```typescript
// BAD
try { await foo(); } catch (e) {}  // silenced; the program continues in undefined state

// BAD
try { await foo(); } catch (e) { console.log(e); }  // logged and swallowed

// GOOD — rethrow
try { await foo(); } catch (e) { logger.error({ e, op: "foo" }); throw e; }

// GOOD — transform to Result
const r = await tryAsync(foo);
if (!r.ok) return err({ kind: "foo-failed", cause: r.error });
```

A `catch` either rethrows, returns a Result, or escalates with new information. "Catch and log" is the most common source of bugs that look like "the system did nothing".

## Rule 6 — Errors carry causes

```typescript
// GOOD
throw new Error("failed to load config", { cause: e });

// or, branded:
throw new ConfigLoadError("invalid YAML", { cause: e, path: "/etc/app.yaml" });

// BAD
throw new Error("failed to load config");  // the underlying cause is lost
```

Use the `cause` field (ES2022). Loggers print the chain. Debuggers thank you.

## Rule 7 — Tests cover the error paths

For every Result-returning function, at least one test asserts the error case.

```typescript
it("should return network error when fetch fails", async () => {
  server.use(http.get("/api/users/:id", () => HttpResponse.error()));
  const r = await fetchUser(userId);
  expect(r.ok).toBe(false);
  expect(r.ok || r.error.kind).toBe("network");
});
```

Untested error paths are not error handling.

# Quality bar

- [ ] Every catch block ends with rethrow, Result construction, or escalation with new info.
- [ ] Every public function that can fail returns `Result<T, E>` with E discriminated.
- [ ] Every `throw` carries a `cause` when wrapping another error.
- [ ] Every Result type has at least one test covering its error case.
- [ ] No `as` casts in error-handling code.

# Anti-patterns

- **Empty catch (`catch (e) {}`).** Always wrong. Always.
- **Catch-and-log (`catch (e) { log(e) }`).** Silently continues in undefined state.
- **`throw "string"` or `throw { kind: ... }`.** Throw `Error` (or subclass). Stacks matter.
- **Single `Error` class for the whole subsystem.** Caller can't disambiguate. Use a discriminated union.
- **Promise rejection without await.** Floating rejections crash Node 20+. Always `await` or attach `.catch`.
- **Defensive try/catch around code that cannot throw.** Dead code, false safety, noise.

# Reference

- ES2022 Error.cause: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/cause
- Libraries: neverthrow (lightweight Result), effect (full ecosystem).
- See `matt-pocock/api-design` for boundary parsing patterns.
