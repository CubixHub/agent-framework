# TypeScript rules

## Type definitions
- Use `interface` for object shapes; `type` for unions, intersections, primitives.
- Never `any`. Use `unknown` with type guards, or define proper types.
- Brand IDs (`type UserId = string & { __brand: 'UserId' }`) at module boundaries.
- Export types alongside implementations; no separate `types.ts` barrels.

## Functions
- Early returns over nested conditionals.
- Named exports only (refactor-friendly).
- Async functions return `Promise<T>`; reject only with `Error` subclasses.
- Validate external input with `zod` at the boundary; trust internal types.

## React
- Functional components only. Props interface named `{ComponentName}Props`.
- File order: imports → types → component → exports.
- Zustand for client state, React Query for server state.
- No barrel `index.ts` files for performance (avoid re-export chains).

## Imports
- Group: React → external → internal → types.
- Absolute imports via `@/` prefix.
- No default exports except for framework-required (Next.js pages).
