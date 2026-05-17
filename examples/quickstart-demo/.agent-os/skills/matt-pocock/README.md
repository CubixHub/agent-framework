# Matt Pocock Skills Collection

Four opinionated TypeScript engineering skills. Each one is rigid, terse, and prescriptive. They reference each other — `api-design` calls into `error-handling` and `typescript-types`; `testing-discipline` shares the vertical-slice loop with `test-driven-development`.

## Skills in this collection

| Skill | Description |
|---|---|
| [typescript-types](./typescript-types/SKILL.md) | Type-driven dev: `interface` vs `type`, no `any`, branded primitives at boundaries, exhaustive narrowing. |
| [testing-discipline](./testing-discipline/SKILL.md) | Vitest with "should X when Y" naming, MSW at HTTP boundaries, zero internal mocks, mutation-test the suite. |
| [error-handling](./error-handling/SKILL.md) | Result types for expected failures, exceptions for invariants, fail-loud at boundaries, zero silent catches. |
| [api-design](./api-design/SKILL.md) | Zod parsing at boundary, versioned URLs, idempotent mutations, RFC 9457 error shape, cursor pagination. |

## How they compose

```
api-design
  └─ uses Zod schemas at the boundary
  └─ returns Result types via error-handling
  └─ uses branded primitives from typescript-types

testing-discipline
  └─ tests public interfaces only (no internal mocks)
  └─ exercises Result branches from error-handling
  └─ asserts on branded types from typescript-types

When the team commits to all four, the codebase shifts:
- Type errors become impossible classes of bug, not classes of runtime check.
- Test failures become signal, not noise.
- Error responses become discoverable, not surprises.
- API breakage becomes versioned migration, not silent regression.
```

## Style

All four skills share a tone:

- **Imperative.** "Do X." never "Consider X."
- **Opinionated.** "Pick one library, do not mix." not "Several libraries are available."
- **GOOD / BAD code blocks.** Side-by-side. No "it depends."
- **Anti-patterns section is non-negotiable.** Every skill names ≥3 specific failure modes.

## Attribution

Patterns derived from Matt Pocock's public TypeScript work (https://www.totaltypescript.com/, https://github.com/mattpocock/skills) and adapted to the Framework's skill format. The reference skills repository (https://github.com/mattpocock/skills) covers a broader engineering discipline catalogue — see `tdd`, `diagnose`, `grill-with-docs`, `improve-codebase-architecture` for skills the Framework provides in parallel under different names.

Matt's broader pattern — terse, opinionated, vertical-slice — drove the tone here. Errors in adaptation are mine; the original work is his.

## When to invoke

These skills trigger on TypeScript file edits, on PR review for `.ts`/`.tsx`, and on user mention of any of: types, generics, narrowing, Zod, Vitest, error handling, API design, REST, RPC, OpenAPI.

Run `skill-discovery` at the top of every turn — that protocol picks among these (and the rest of the library) based on the user's task.

## Not in this collection (intentionally)

- **State management.** Project-specific; no single right answer.
- **CSS / styling.** Out of scope for a TypeScript engineering collection.
- **Build tooling.** Vite, esbuild, tsc config — adopt sensible defaults, do not skill-ify.
- **React-specific patterns.** A future `frontend-design` collection covers these. Reference `superpowers:frontend-design` skill if installed.

If you find yourself wanting one of these, invoke `skill-creator` and capture the pattern there.
