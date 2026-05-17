---
name: typescript-types
description: Type-driven TypeScript development with strict rules — interface vs type, no any, branded types, exhaustive type narrowing. Use when writing or reviewing TypeScript code, when the user mentions types/typing/inference/generics, or when a PR touches `.ts`/`.tsx` files. Refuses `any`, refuses `as`-casts without justification, refuses unnamed primitives at domain boundaries.
---

# Type-Driven TypeScript

Types are the compiler-enforced design document. Write types first; the implementation follows. The compiler is the cheapest test you'll ever run.

## When to use

- Writing new TypeScript.
- Reviewing a PR that touches `.ts` / `.tsx`.
- User mentions "types", "inference", "generics", "narrowing", "discriminated union".
- A function returns `unknown` or accepts `any` — that is the trigger to do this skill.

# How to execute

## Rule 1 — `interface` for objects, `type` for unions and primitives

```typescript
// GOOD
interface User { id: UserId; email: Email; }
type Role = "admin" | "viewer";
type UserId = string & { readonly _tag: "UserId" };

// BAD
type User = { id: string; email: string };  // type, not interface — extension is awkward
interface Role { admin: never; viewer: never; }  // interface for a union — wrong shape
```

`interface` extends cleanly with declaration merging and `extends`. `type` is the only way to express unions, intersections, and conditional types.

## Rule 2 — `any` is forbidden; `unknown` is the default

```typescript
// GOOD
function parse(input: unknown): Result<User, ParseError> { ... }

// BAD
function parse(input: any): User { ... }  // erases type information at the boundary
```

`unknown` requires the caller to narrow before use. That is the point. `any` opts out of the type system entirely; ship-blocking unless an external library forces it (then localise with a single `as` at the boundary and a `// eslint-disable-next-line ts/no-explicit-any` comment naming the library).

## Rule 3 — Branded types at domain boundaries

Bare primitives at boundaries are a bug factory. Brand them.

```typescript
// GOOD
type UserId = string & { readonly _tag: "UserId" };
type Email = string & { readonly _tag: "Email" };

function getUser(id: UserId): User { ... }
const id = parseUserId(raw);  // returns UserId or throws
getUser(id);

// BAD
function getUser(id: string): User { ... }  // any string compiles, including an email
getUser(user.email);  // silent bug
```

Domain entities: brand them. Database IDs: brand them. Anything that crosses a function boundary and is not interchangeable with other strings/numbers: brand it.

## Rule 4 — Exhaustive narrowing via discriminated unions

```typescript
// GOOD
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function handle(r: Result<User, Error>): string {
  if (r.ok) return r.value.email;
  return r.error.message;
}

// BAD
interface Result<T, E> { ok: boolean; value?: T; error?: E; }
// caller has to ! and || the world to use this
```

Always discriminate on a literal tag. Always exhaust the union (compiler flags the missing case via `never`).

## Rule 5 — `as` casts must be justified inline

```typescript
// GOOD
const config = JSON.parse(raw) as Config;  // schema-validated upstream; see schemas.ts
// or, better:
const config = ConfigSchema.parse(raw);  // Zod, no cast needed

// BAD
const user = thing as User;  // unjustified
```

Every `as` is an assertion the compiler is wrong. Justify it inline. Better: replace with a parsing function (Zod, Effect Schema, valibot) that produces the typed value safely.

## Rule 6 — Return types are written, not inferred, at module boundaries

```typescript
// GOOD (exported function)
export function fetchUser(id: UserId): Promise<Result<User, FetchError>> { ... }

// BAD (exported function)
export function fetchUser(id: UserId) { ... }  // return type drifts as implementation changes
```

Inferred return types are fine inside a module. At the export boundary, the return type is part of the contract — write it explicitly so the compiler enforces stability.

# Quality bar

- [ ] Zero `any` in the changed code (search: `grep -n ': any' file.ts`).
- [ ] Every domain ID/primitive is branded.
- [ ] Every union has a literal discriminator.
- [ ] Every `as` is followed by an inline comment justifying it.
- [ ] All exported functions have explicit return types.
- [ ] `tsc --noEmit --strict` passes.

# Anti-patterns

- **`any` to silence the compiler.** The compiler is telling you something. Listen.
- **Optional fields that are actually required-but-sometimes-missing.** That is a union, not an optional. Use `T | null` (explicit absence) over `T?` (implicit absence).
- **Type assertions inside happy paths.** If you reach for `as`, the upstream parsing is wrong.
- **Mega-interfaces.** A 30-field interface is two interfaces in a trench coat. Split it.
- **`Function` and `Object` types.** Always unspecific. Use `(...args: A) => R` and `Record<K, V>`.
- **Using `Record<string, any>` as a freebie.** That is `any` with steps.
- **Generic constraints that don't constrain.** `<T extends any>` is `<T>` with extra words.

# Reference

- The TypeScript handbook is the canonical reference. Read the "Narrowing" and "Conditional Types" chapters before doing anything advanced.
- Effect/Zod/valibot for runtime validation; pick one per project and stick to it.
